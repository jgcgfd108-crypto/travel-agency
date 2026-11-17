"""Admin dashboard blueprint: login, packages, destinations, enquiries."""
import sqlite3
import time
from functools import wraps

from flask import (Blueprint, abort, flash, g, redirect, render_template, request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

import admin_forms as forms
import admin_repo as ar
from data import PACKAGE_CATEGORIES

bp = Blueprint("admin", __name__, url_prefix="/admin")

# Failed-login throttle (per process). 5 failures in 10 minutes locks that IP + username.
_FAILS = {}
_MAX_FAILS, _WINDOW = 5, 600
_DUMMY_HASH = generate_password_hash("not-a-real-password")  # keeps timing similar for unknown usernames


def _recent(key):
    now = time.time()
    _FAILS[key] = [t for t in _FAILS.get(key, []) if now - t < _WINDOW]
    return _FAILS[key]


def _safe_next(value):
    ok = value == "/admin" or (value.startswith("/admin/") and "\\" not in value and "//" not in value)
    return value if ok else url_for("admin.dashboard")


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        admin = ar.get_admin(session["admin_id"]) if session.get("admin_id") else None
        if not admin:
            session.pop("admin_id", None)
            nxt = request.full_path.rstrip("?") if request.method == "GET" else None
            return redirect(url_for("admin.login", next=nxt))
        g.admin = admin
        return view(*args, **kwargs)
    return wrapped


@bp.after_request
def no_store(resp):
    resp.headers["Cache-Control"] = "no-store"
    resp.headers["X-Robots-Tag"] = "noindex, nofollow"
    return resp


# ---------------------------------------------------------------- auth
@bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("admin_id") and ar.get_admin(session["admin_id"]):
        return redirect(url_for("admin.dashboard"))
    error, status = None, 200
    nxt = request.values.get("next", "")
    if request.method == "POST":
        username = request.form.get("username", "").strip()[:32]
        password = request.form.get("password", "")[:200]
        key = (request.remote_addr, username.lower())
        if len(_recent(key)) >= _MAX_FAILS:
            error, status = "Too many failed attempts. Try again in a few minutes.", 429
        else:
            row = ar.get_admin_by_username(username)
            valid = check_password_hash(row["password_hash"] if row else _DUMMY_HASH, password) and row is not None
            if valid:
                _FAILS.pop(key, None)
                session.clear()                       # new session on login (prevents fixation)
                session["admin_id"] = row["id"]
                session.permanent = True
                return redirect(_safe_next(nxt))
            _recent(key).append(time.time())
            error, status = "Incorrect username or password.", 401
    return render_template("admin/login.html", error=error, next=nxt), status


@bp.post("/logout")
@login_required
def logout():
    session.clear()
    flash("You have been signed out.", "ok")
    return redirect(url_for("admin.login"))


# ---------------------------------------------------------------- dashboard
@bp.route("/")
@login_required
def dashboard():
    return render_template("admin/dashboard.html", s=ar.stats())


# ---------------------------------------------------------------- packages
@bp.route("/packages")
@login_required
def packages():
    return render_template("admin/packages.html", items=ar.list_packages())


def _package_page(template, form, errors, pid=None):
    return render_template(template, form=form, errors=errors, pid=pid, categories=PACKAGE_CATEGORIES,
                           destinations=ar_destinations())


def ar_destinations():
    return ar.list_destinations()


def _save_package(pid=None):
    dest_ids = {r["id"] for r in ar.list_destinations()}
    data, errors = forms.validate_package(request.form, dest_ids)
    if not errors:
        try:
            return ar.save_package(data, pid), None, None
        except sqlite3.IntegrityError as exc:
            if "slug" in str(exc):
                errors["slug"] = "That slug is already used by another package."
            else:
                raise
    return None, forms.form_values(request.form), errors


@bp.route("/packages/new", methods=["GET", "POST"])
@login_required
def add_package():
    if request.method == "POST":
        pid, form, errors = _save_package()
        if pid:
            flash("Package created.", "ok")
            return redirect(url_for("admin.packages"))
        return _package_page("admin/add_package.html", form, errors), 422
    return _package_page("admin/add_package.html", {"is_active": "on", "days": "3", "nights": "2", "categories": []}, {})


@bp.route("/packages/<int:pid>/edit", methods=["GET", "POST"])
@login_required
def edit_package(pid):
    pkg = ar.get_package(pid)
    if not pkg:
        abort(404)
    if request.method == "POST":
        saved, form, errors = _save_package(pid)
        if saved:
            flash("Package updated.", "ok")
            return redirect(url_for("admin.packages"))
        return _package_page("admin/edit_package.html", form, errors, pid), 422
    return _package_page("admin/edit_package.html", forms.package_to_form(pkg), {}, pid)


@bp.post("/packages/<int:pid>/delete")
@login_required
def delete_package(pid):
    if ar.delete_package(pid):
        flash("Package deleted. Existing enquiries were kept.", "ok")
    else:
        abort(404)
    return redirect(url_for("admin.packages"))


# ---------------------------------------------------------------- destinations
@bp.route("/destinations")
@login_required
def destinations():
    return render_template("admin/destinations.html", items=ar.list_destinations())


def _destination_page(form, errors, did=None):
    return render_template("admin/destination_form.html", form=form, errors=errors, did=did)


def _save_destination(did=None):
    data, errors = forms.validate_destination(request.form)
    if not errors:
        try:
            return ar.save_destination(data, did), None, None
        except sqlite3.IntegrityError as exc:
            if "slug" in str(exc):
                errors["slug"] = "That slug is already used by another destination."
            else:
                raise
    return None, forms.form_values(request.form), errors


@bp.route("/destinations/new", methods=["GET", "POST"])
@login_required
def add_destination():
    if request.method == "POST":
        did, form, errors = _save_destination()
        if did:
            flash("Destination created.", "ok")
            return redirect(url_for("admin.destinations"))
        return _destination_page(form, errors), 422
    return _destination_page({"region": "Domestic"}, {})


@bp.route("/destinations/<int:did>/edit", methods=["GET", "POST"])
@login_required
def edit_destination(did):
    row = ar.get_destination(did)
    if not row:
        abort(404)
    if request.method == "POST":
        saved, form, errors = _save_destination(did)
        if saved:
            flash("Destination updated.", "ok")
            return redirect(url_for("admin.destinations"))
        return _destination_page(form, errors, did), 422
    return _destination_page(forms.destination_to_form(row), {}, did)


@bp.post("/destinations/<int:did>/delete")
@login_required
def delete_destination(did):
    try:
        if not ar.delete_destination(did):
            abort(404)
        flash("Destination deleted.", "ok")
    except sqlite3.IntegrityError:
        flash("This destination still has packages. Delete or move them first.", "error")
    return redirect(url_for("admin.destinations"))


# ---------------------------------------------------------------- enquiries
@bp.route("/enquiries")
@login_required
def enquiries():
    status = request.args.get("status", "")
    if status not in ar.STATUSES:
        status = ""
    return render_template("admin/enquiries.html", items=ar.list_enquiries(status), status=status,
                           counts=ar.enquiry_counts(), statuses=ar.STATUSES)


@bp.post("/enquiries/<int:eid>/status")
@login_required
def enquiry_status(eid):
    back = request.form.get("filter", "")
    target = url_for("admin.enquiries", status=back if back in ar.STATUSES else None)
    if ar.set_enquiry_status(eid, request.form.get("status", "")):
        flash("Enquiry status updated.", "ok")
    else:
        flash("Could not update that enquiry.", "error")
    return redirect(target)
