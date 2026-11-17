"""Database queries. Every query is parameterized; no user input is formatted into SQL."""
import data
from db import get_db

PACKAGE_CATEGORIES = data.PACKAGE_CATEGORIES
_ESC = " ESCAPE '\\'"


def _like(text):
    """Escape LIKE wildcards so a search for % or _ matches literally."""
    return "%" + text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"


def _lines(text):
    return [ln.strip() for ln in (text or "").splitlines() if ln.strip()]


def _dest(row):
    d = dict(row)
    d["tag"] = d["region"]
    return d


# ---------------------------------------------------------------- destinations
def destinations(q="", region="", country="", category=""):
    sql, args = "SELECT * FROM destinations WHERE 1=1", []
    if q:
        sql += " AND (name LIKE ?{e} OR country LIKE ?{e} OR category LIKE ?{e} OR blurb LIKE ?{e})".format(e=_ESC)
        args += [_like(q)] * 4
    for col, val in (("region", region), ("country", country), ("category", category)):
        if val:
            sql += f" AND {col} = ?"          # column names are fixed literals above, never user input
            args.append(val)
    return [_dest(r) for r in get_db().execute(sql + " ORDER BY id", args)]


def destination(slug):
    row = get_db().execute("SELECT * FROM destinations WHERE slug = ?", (slug,)).fetchone()
    return _dest(row) if row else None


def popular_destinations():
    return [_dest(r) for r in get_db().execute("SELECT * FROM destinations WHERE is_popular = 1 ORDER BY id")]


def destination_countries():
    return [r[0] for r in get_db().execute("SELECT DISTINCT country FROM destinations ORDER BY country")]


def destination_categories():
    return [r[0] for r in get_db().execute("SELECT DISTINCT category FROM destinations ORDER BY category")]


# ---------------------------------------------------------------- packages
def _hydrate(rows):
    rows = [dict(r) for r in rows]
    if not rows:
        return rows
    ids = [r["id"] for r in rows]
    marks = ",".join("?" * len(ids))          # only "?" characters are interpolated
    cats = {}
    for r in get_db().execute(
            f"SELECT package_id, category FROM package_categories WHERE package_id IN ({marks}) ORDER BY rowid", ids):
        cats.setdefault(r["package_id"], []).append(r["category"])
    for r in rows:
        r["categories"] = cats.get(r["id"], [])
        r["category"] = r["categories"][0] if r["categories"] else ""
        r["highlights"] = _lines(r["highlights"])
    return rows


def packages(category="", dest_slug="", q="", featured=False):
    sql = ("SELECT p.*, d.slug AS dest FROM packages p JOIN destinations d ON d.id = p.destination_id "
           "WHERE p.is_active = 1")
    args = []
    if category:
        sql += " AND EXISTS (SELECT 1 FROM package_categories pc WHERE pc.package_id = p.id AND pc.category = ?)"
        args.append(category)
    if dest_slug:
        sql += " AND d.slug = ?"
        args.append(dest_slug)
    if q:
        sql += " AND (p.name LIKE ?{e} OR p.summary LIKE ?{e})".format(e=_ESC)
        args += [_like(q)] * 2
    if featured:
        sql += " AND p.is_featured = 1"
    return _hydrate(get_db().execute(sql + " ORDER BY p.id", args).fetchall())


def get_package(slug):
    db = get_db()
    row = db.execute(
        "SELECT p.*, d.slug AS dest FROM packages p JOIN destinations d ON d.id = p.destination_id "
        "WHERE p.slug = ? AND p.is_active = 1", (slug,)).fetchone()
    if not row:
        return None
    p = _hydrate([row])[0]
    dest = _dest(db.execute("SELECT * FROM destinations WHERE id = ?", (p["destination_id"],)).fetchone())
    p["destination"] = dest
    p["itinerary"] = [(r["title"], r["description"]) for r in db.execute(
        "SELECT title, description FROM itinerary_days WHERE package_id = ? ORDER BY day_no", (p["id"],))]
    p["gallery"] = [r["url"] for r in db.execute(
        "SELECT url FROM package_images WHERE package_id = ? ORDER BY position, id", (p["id"],))] or [p["image"]]
    p["included"] = _lines(p["included"])
    p["excluded"] = _lines(p["excluded"])
    p["intl"] = dest["region"] == "International"
    p["faqs"] = data.faqs_for(p["intl"])
    return p


def related_packages(pkg, limit=3):
    mine = set(pkg["categories"])
    return [p for p in packages() if p["slug"] != pkg["slug"] and mine & set(p["categories"])][:limit]


# ---------------------------------------------------------------- enquiries and stats
def add_enquiry(c):
    pkg = c["package"]
    db = get_db()
    cur = db.execute(
        "INSERT INTO enquiries (name, phone, destination, package_id, package_name, travellers, travel_date, message) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (c["name"], c["phone"], pkg["destination"]["name"] if pkg else c["destination"],
         pkg["id"] if pkg else None, pkg["name"] if pkg else None, c["travellers"],
         c["date"].isoformat() if c["date"] else None, c["message"]))
    db.commit()
    return cur.lastrowid


def counts():
    db = get_db()
    return {
        "packages": db.execute("SELECT COUNT(*) FROM packages").fetchone()[0],
        "destinations": db.execute("SELECT COUNT(*) FROM destinations").fetchone()[0],
        "enquiries": db.execute("SELECT COUNT(*) FROM enquiries").fetchone()[0],
    }
