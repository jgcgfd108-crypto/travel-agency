"""OUT OF BOUND - Flask application."""
import hmac
import logging
import os
import re
import secrets
import sqlite3
from urllib.parse import quote

import click
from flask import Flask, Response, abort, jsonify, render_template, request, session, url_for
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import generate_password_hash

import admin
import data
import db
import enquiry
import repo
from ratelimit import RateLimiter
from config import Config

log = logging.getLogger("out_of_bound")


def create_app(overrides=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    if overrides:
        app.config.update(overrides)

    key = app.config["SECRET_KEY"]
    dev = os.environ.get("FLASK_DEBUG") == "1" or app.config.get("TESTING")
    if not key:
        raise RuntimeError("SECRET_KEY is not set. Copy .env.example to .env and set it.")
    if not dev and (len(key) < 32 or key.startswith("change-me")):
        raise RuntimeError("SECRET_KEY is too weak for production. Use: python -c \"import secrets; print(secrets.token_hex(32))\"")
    if not dev and app.config["WHATSAPP_NUMBER"] == enquiry.PLACEHOLDER_NUMBER:
        log.warning("WHATSAPP_NUMBER is still the placeholder; enquiries will not reach a real chat.")
    if app.config["TRUST_PROXY"]:
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
    enquiry_limiter = RateLimiter(app.config["ENQUIRY_LIMIT"], app.config["ENQUIRY_WINDOW"])
    os.makedirs(app.instance_path, exist_ok=True)
    app.teardown_appcontext(db.close_db)
    if not os.path.exists(app.config["DATABASE"]):
        db.init_db(app.config["DATABASE"], seed_data=True)   # schema + sample content, no admin account

    @app.context_processor
    def inject_site():
        return {"site": app.config}

    # ------------------------------------------------------------ CSRF
    def csrf_token():
        if "_csrf" not in session:
            session["_csrf"] = secrets.token_hex(32)
        return session["_csrf"]

    app.jinja_env.globals["csrf_token"] = csrf_token

    @app.before_request
    def csrf_protect():
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            sent = request.headers.get("X-CSRF-Token") or request.form.get("csrf_token", "")
            expected = session.get("_csrf", "")
            if not expected or not sent or not hmac.compare_digest(sent, expected):
                abort(400)

    @app.after_request
    def security_headers(resp):
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        resp.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        resp.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        return resp

    app.register_blueprint(admin.bp)

    # ------------------------------------------------------------ template helpers
    @app.template_global()
    def static_url(filename):
        """Static URL with a file-modified version so browsers can cache it long and still see updates."""
        try:
            version = int(os.path.getmtime(os.path.join(app.static_folder, filename)))
        except OSError:
            version = 0
        return url_for("static", filename=filename, v=version)

    @app.template_filter("inr")
    def inr(value):
        return f"₹{int(value):,}"

    @app.template_global()
    def wa_package(p):
        """Prefilled WhatsApp link for a package card (the full form lives on the package page)."""
        msg = (f"Hello OUT OF BOUND!\n\nI am interested in booking the following tour package:\n\n"
               f"Package: {p['name']}\nDuration: {p['days']} Days / {p['nights']} Nights\n"
               f"Travellers: 2\nPreferred Date: Not selected\n\n"
               f"Please share the package details and availability.")
        return f"https://wa.me/{app.config['WHATSAPP_NUMBER']}?text={quote(msg)}"

    # ------------------------------------------------------------ public pages
    @app.route("/")
    def index():
        return render_template(
            "index.html", hero_image=data.HERO_IMAGE, destinations=repo.popular_destinations(),
            packages=repo.packages(featured=True), experiences=data.EXPERIENCES, reasons=data.REASONS,
            testimonials=data.TESTIMONIALS)

    @app.route("/destinations")
    def destinations():
        q = request.args.get("q", "").strip()[:80]
        region = request.args.get("region", "")
        country = request.args.get("country", "")
        category = request.args.get("category", "")
        if region not in ("Domestic", "International"):
            region = ""
        return render_template(
            "destinations.html", items=repo.destinations(q, region, country, category),
            q=q, region=region, country=country, category=category,
            countries=repo.destination_countries(), categories=repo.destination_categories(),
            active=bool(q or region or country or category))

    @app.route("/destinations/<slug>")
    def destination_details(slug):
        dest = repo.destination(slug)
        if not dest:
            abort(404)
        return render_template("destination_details.html", d=dest, packages=repo.packages(dest_slug=slug))

    @app.route("/packages")
    def packages():
        category = request.args.get("category", "")
        if category not in repo.PACKAGE_CATEGORIES:
            category = ""
        dest_obj = repo.destination(request.args.get("destination", ""))
        q = request.args.get("q", "").strip()[:80]
        items = repo.packages(category, dest_obj["slug"] if dest_obj else "", q)
        return render_template("packages.html", items=items, category=category, q=q,
                               categories=repo.PACKAGE_CATEGORIES, dest=dest_obj)

    @app.route("/packages/<slug>")
    def package_details(slug):
        pkg = repo.get_package(slug)
        if not pkg:
            abort(404)
        return render_template("package_details.html", p=pkg, related=repo.related_packages(pkg))

    @app.route("/about")
    def about():
        return render_template("about.html", reasons=data.REASONS)

    @app.route("/contact")
    def contact():
        return render_template("contact.html", destinations=repo.destinations())

    @app.post("/enquiry/whatsapp")
    def whatsapp_enquiry():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify(ok=False, errors={"form": "Invalid request."}), 400
        cleaned, errors = enquiry.validate(payload, repo.get_package)
        if errors:
            return jsonify(ok=False, errors=errors), 422
        if not enquiry_limiter.allow(request.remote_addr or "unknown"):
            return jsonify(ok=False, errors={"form": "Too many enquiries from this connection. "
                                                      "Please try again in a few minutes or message us on WhatsApp."}), 429
        try:
            repo.add_enquiry(cleaned)
        except sqlite3.Error:
            # Never lose a lead because of a storage problem: log it and still open WhatsApp.
            log.exception("Could not save enquiry")
        number = app.config["WHATSAPP_NUMBER"]
        url = enquiry.whatsapp_url(number, enquiry.build_message(cleaned))
        return jsonify(ok=True, url=url, placeholder=number == enquiry.PLACEHOLDER_NUMBER)

    # ------------------------------------------------------------ utility routes
    @app.route("/healthz")
    def healthz():
        db.get_db().execute("SELECT 1").fetchone()
        return jsonify(status="ok")

    @app.route("/robots.txt")
    def robots():
        body = f"User-agent: *\nDisallow: /admin/\nDisallow: /enquiry/\nSitemap: {url_for('sitemap', _external=True)}\n"
        return Response(body, mimetype="text/plain")

    @app.route("/sitemap.xml")
    def sitemap():
        urls = [url_for(e, _external=True) for e in ("index", "destinations", "packages", "about", "contact")]
        urls += [url_for("destination_details", slug=d["slug"], _external=True) for d in repo.destinations()]
        urls += [url_for("package_details", slug=p["slug"], _external=True) for p in repo.packages()]
        xml = ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
               + "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n")
        return Response(xml, mimetype="application/xml")

    # ------------------------------------------------------------ errors
    def error_page(code, title, message):
        return render_template("error.html", title=title, message=message), code

    @app.errorhandler(400)
    def bad_request(_e):
        if request.is_json:
            return jsonify(ok=False, errors={"form": "Session expired. Refresh the page and try again."}), 400
        return error_page(400, "Request not valid", "Please go back, refresh the page and try again.")

    @app.errorhandler(404)
    def not_found(_e):
        return error_page(404, "Page not found", "We could not find that page.")

    @app.errorhandler(405)
    def not_allowed(_e):
        return error_page(405, "Not allowed", "That action is not available on this page.")

    @app.errorhandler(500)
    def server_error(_e):
        return error_page(500, "Something went wrong", "Sorry, that was our mistake. Please try again in a moment.")

    # ------------------------------------------------------------ CLI
    @app.cli.command("init-db")
    @click.option("--reset", is_flag=True, help="Delete the existing database first.")
    @click.option("--no-seed", is_flag=True, help="Create empty tables without the sample content.")
    def init_db_command(reset, no_seed):
        """Create the database (and load sample content)."""
        path = app.config["DATABASE"]
        if reset and os.path.exists(path):
            click.confirm(f"This deletes {path} including all enquiries and admin accounts. Continue?", abort=True)
            os.remove(path)
        seeded = db.init_db(path, seed_data=not no_seed)
        click.echo(f"Database ready at {path}" + (" (sample content loaded)." if seeded else "."))
        click.echo("Next: flask --app app create-admin")

    @app.cli.command("create-admin")
    @click.option("--username", prompt=True, envvar="ADMIN_USERNAME")
    @click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True, envvar="ADMIN_PASSWORD")
    def create_admin_command(username, password):
        """Create an admin account, or reset its password if the username exists."""
        username = username.strip()
        if not re.fullmatch(r"[A-Za-z0-9_.-]{3,32}", username):
            raise click.ClickException("Username must be 3-32 characters: letters, digits, . _ -")
        if len(password) < 10:
            raise click.ClickException("Password must be at least 10 characters.")
        conn = db.get_db()
        hashed = generate_password_hash(password)
        row = conn.execute("SELECT id FROM admin_users WHERE username = ?", (username,)).fetchone()
        if row:
            conn.execute("UPDATE admin_users SET password_hash = ? WHERE id = ?", (hashed, row["id"]))
            click.echo(f"Password updated for '{username}'.")
        else:
            conn.execute("INSERT INTO admin_users (username, password_hash) VALUES (?, ?)", (username, hashed))
            click.echo(f"Admin '{username}' created.")
        conn.commit()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
