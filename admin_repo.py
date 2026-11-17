"""Database operations for the admin dashboard. All queries are parameterized."""
import sqlite3

from db import get_db

STATUSES = ("new", "contacted", "booked", "closed")


# ---------------------------------------------------------------- admins
def get_admin(admin_id):
    return get_db().execute("SELECT id, username FROM admin_users WHERE id = ?", (admin_id,)).fetchone()


def get_admin_by_username(username):
    return get_db().execute("SELECT id, username, password_hash FROM admin_users WHERE username = ?",
                            (username,)).fetchone()


# ---------------------------------------------------------------- dashboard
def stats():
    db = get_db()
    one = lambda sql: db.execute(sql).fetchone()[0]
    by_status = {s: 0 for s in STATUSES}
    for r in db.execute("SELECT status, COUNT(*) AS n FROM enquiries GROUP BY status"):
        by_status[r["status"]] = r["n"]
    return {"packages": one("SELECT COUNT(*) FROM packages"), "destinations": one("SELECT COUNT(*) FROM destinations"),
            "enquiries": one("SELECT COUNT(*) FROM enquiries"), "by_status": by_status,
            "recent": db.execute("SELECT * FROM enquiries ORDER BY id DESC LIMIT 5").fetchall()}


# ---------------------------------------------------------------- packages
def list_packages():
    return get_db().execute(
        "SELECT p.id, p.slug, p.name, p.days, p.nights, p.price, p.is_featured, p.is_active, d.name AS dest_name, "
        "(SELECT GROUP_CONCAT(category, ', ') FROM package_categories WHERE package_id = p.id) AS cats "
        "FROM packages p JOIN destinations d ON d.id = p.destination_id ORDER BY p.id DESC").fetchall()


def get_package(pid):
    db = get_db()
    row = db.execute("SELECT * FROM packages WHERE id = ?", (pid,)).fetchone()
    if not row:
        return None
    p = dict(row)
    p["categories"] = [r[0] for r in db.execute("SELECT category FROM package_categories WHERE package_id = ?", (pid,))]
    p["itinerary"] = [(r[0], r[1]) for r in db.execute(
        "SELECT title, description FROM itinerary_days WHERE package_id = ? ORDER BY day_no", (pid,))]
    p["gallery"] = [r[0] for r in db.execute(
        "SELECT url FROM package_images WHERE package_id = ? ORDER BY position, id", (pid,))]
    return p


def save_package(d, pid=None):
    """Insert or update a package with its categories, itinerary and gallery in one transaction."""
    db = get_db()
    vals = (d["slug"], d["destination_id"], d["name"], d["days"], d["nights"], d["price"], d["summary"], d["hotel"],
            d["transport"], d["image"], "\n".join(d["highlights"]), "\n".join(d["included"]),
            "\n".join(d["excluded"]), d["is_featured"], d["is_active"])
    try:
        if pid is None:
            pid = db.execute(
                "INSERT INTO packages (slug, destination_id, name, days, nights, price, summary, hotel, transport, "
                "image, highlights, included, excluded, is_featured, is_active) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                vals).lastrowid
        else:
            db.execute(
                "UPDATE packages SET slug=?, destination_id=?, name=?, days=?, nights=?, price=?, summary=?, hotel=?, "
                "transport=?, image=?, highlights=?, included=?, excluded=?, is_featured=?, is_active=? WHERE id=?",
                vals + (pid,))
        for table in ("package_categories", "itinerary_days", "package_images"):
            db.execute(f"DELETE FROM {table} WHERE package_id = ?", (pid,))      # table names are fixed literals
        db.executemany("INSERT INTO package_categories (package_id, category) VALUES (?, ?)",
                       [(pid, c) for c in d["categories"]])
        db.executemany("INSERT INTO itinerary_days (package_id, day_no, title, description) VALUES (?,?,?,?)",
                       [(pid, i, t, x) for i, (t, x) in enumerate(d["itinerary"], 1)])
        db.executemany("INSERT INTO package_images (package_id, position, url) VALUES (?, ?, ?)",
                       [(pid, i, u) for i, u in enumerate(d["gallery"])])
        db.commit()
        return pid
    except sqlite3.Error:
        db.rollback()
        raise


def delete_package(pid):
    db = get_db()
    cur = db.execute("DELETE FROM packages WHERE id = ?", (pid,))
    db.commit()
    return cur.rowcount


# ---------------------------------------------------------------- destinations
def list_destinations():
    return get_db().execute(
        "SELECT d.*, (SELECT COUNT(*) FROM packages WHERE destination_id = d.id) AS pkg_count "
        "FROM destinations d ORDER BY d.name").fetchall()


def get_destination(did):
    return get_db().execute("SELECT * FROM destinations WHERE id = ?", (did,)).fetchone()


def save_destination(d, did=None):
    db = get_db()
    vals = (d["slug"], d["name"], d["country"], d["region"], d["category"], d["image"], d["blurb"], d["is_popular"])
    try:
        if did is None:
            did = db.execute("INSERT INTO destinations (slug, name, country, region, category, image, blurb, is_popular) "
                             "VALUES (?,?,?,?,?,?,?,?)", vals).lastrowid
        else:
            db.execute("UPDATE destinations SET slug=?, name=?, country=?, region=?, category=?, image=?, blurb=?, "
                       "is_popular=? WHERE id=?", vals + (did,))
        db.commit()
        return did
    except sqlite3.Error:
        db.rollback()
        raise


def delete_destination(did):
    """Raises sqlite3.IntegrityError while packages still use the destination."""
    db = get_db()
    try:
        cur = db.execute("DELETE FROM destinations WHERE id = ?", (did,))
        db.commit()
        return cur.rowcount
    except sqlite3.Error:
        db.rollback()
        raise


# ---------------------------------------------------------------- enquiries
def enquiry_counts():
    counts = {s: 0 for s in STATUSES}
    for r in get_db().execute("SELECT status, COUNT(*) AS n FROM enquiries GROUP BY status"):
        counts[r["status"]] = r["n"]
    return counts


def list_enquiries(status=""):
    sql, args = "SELECT * FROM enquiries", []
    if status in STATUSES:
        sql += " WHERE status = ?"
        args.append(status)
    return get_db().execute(sql + " ORDER BY id DESC LIMIT 200", args).fetchall()


def set_enquiry_status(eid, status):
    if status not in STATUSES:
        return 0
    db = get_db()
    cur = db.execute("UPDATE enquiries SET status = ? WHERE id = ?", (status, eid))
    db.commit()
    return cur.rowcount
