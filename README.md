# OUT OF BOUND — Explore Beyond Boundaries.

Travel agency website: Flask + SQLite + vanilla JS. Bookings happen over WhatsApp (no online payment).

## Run locally
    python -m venv venv && source venv/bin/activate        # Windows: venv\Scripts\activate
    pip install -r requirements.txt
    cp .env.example .env                                    # set SECRET_KEY and WHATSAPP_NUMBER
    flask --app app create-admin                            # prompts for username + password (min 10 chars)
    python app.py                                           # http://127.0.0.1:5000  (admin: /admin/)

The database (`instance/out_of_bound.db`) is created with sample content on first run.
`flask --app app init-db --reset` wipes and rebuilds it. There is no default admin account.

## Before going live (checklist)
- [ ] `SECRET_KEY` is 32+ random characters: `python -c "import secrets; print(secrets.token_hex(32))"` (the app refuses weak keys outside debug mode)
- [ ] `WHATSAPP_NUMBER` is the real number: digits only, with country code, no "+"
- [ ] `CONTACT_PHONE`, `CONTACT_EMAIL`, `OFFICE_ADDRESS` (config.py / .env) updated; social links in `templates/base.html`
- [ ] `COOKIE_SECURE=1` (HTTPS only), `TRUST_PROXY=1` (behind nginx / a platform proxy), `FLASK_DEBUG=0`
- [ ] Real photos in `static/images/` (use `/static/images/name.jpg` in the admin) instead of the sample Unsplash links
- [ ] Sample prices, hotels and testimonials replaced with real ones
- [ ] Admin account created; database backups scheduled (`deploy/backup.sh`)

## Tests
    pip install -r requirements-dev.txt
    python -m pytest -q

Covers public pages, search/filters, WhatsApp message generation, enquiry validation and rate limiting, CSRF,
admin login/lockout, all admin CRUD, XSS escaping, SQL-injection inputs, error pages, and a crawler that checks
internal links, local assets, image alt text and form labels on every page.

## Deploy
**VPS (Ubuntu) with nginx + gunicorn**

    sudo apt install python3-venv nginx
    sudo mkdir -p /srv/out_of_bound && sudo chown $USER /srv/out_of_bound   # copy the project here
    cd /srv/out_of_bound && python3 -m venv venv && venv/bin/pip install -r requirements.txt
    cp .env.example .env && nano .env                        # production values (see checklist)
    venv/bin/flask --app app create-admin
    sudo chown -R www-data:www-data instance
    sudo cp deploy/out_of_bound.service /etc/systemd/system/ && sudo systemctl enable --now out_of_bound
    sudo cp deploy/nginx.conf /etc/nginx/sites-available/outofbound   # edit server_name, then:
    sudo ln -s /etc/nginx/sites-available/outofbound /etc/nginx/sites-enabled/ && sudo nginx -t && sudo systemctl reload nginx
    sudo certbot --nginx                                      # free HTTPS

**Docker**

    docker build -t out-of-bound .
    docker run -d -p 8000:8000 --env-file .env -v oob-data:/app/instance out-of-bound

**Notes**
- SQLite lives in `instance/`. Use a host with a persistent disk (or a Docker volume). Free tiers with ephemeral
  disks lose enquiries on every restart.
- Run one gunicorn worker (with threads), as configured. Rate limits and the login lockout are kept in memory per
  process; with several workers each one counts separately.
- Static files are versioned (`?v=`) so they can be cached for a long time; nginx serves and gzips them.
- `/healthz` is for uptime monitors; `/robots.txt` and `/sitemap.xml` are generated automatically.
