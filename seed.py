"""Loads the sample destinations and packages from data.py into an empty database."""
import data

POPULAR = {"bali", "maldives", "kerala", "manali", "dubai", "switzerland"}


def seed(conn):
    if conn.execute("SELECT COUNT(*) FROM destinations").fetchone()[0]:
        return False
    ids = {}
    for d in data.DESTINATIONS:
        cur = conn.execute(
            "INSERT INTO destinations (slug, name, country, region, category, image, blurb, is_popular) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (d["slug"], d["name"], d["country"], d["region"], d["category"], d["image"], d["blurb"],
             1 if d["slug"] in POPULAR else 0))
        ids[d["slug"]] = cur.lastrowid
    featured = {p["slug"] for p in data.FEATURED}
    for p in data.PACKAGES:
        full = data.get_package(p["slug"])
        cur = conn.execute(
            "INSERT INTO packages (slug, destination_id, name, days, nights, price, summary, hotel, transport, "
            "image, highlights, included, excluded, is_featured) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (p["slug"], ids[p["dest"]], p["name"], p["days"], p["nights"], p["price"], p["summary"],
             full["hotel"], full["transport"], p["image"], "\n".join(p["highlights"]),
             "\n".join(full["included"]), "\n".join(full["excluded"]), 1 if p["slug"] in featured else 0))
        pid = cur.lastrowid
        conn.executemany("INSERT INTO package_categories (package_id, category) VALUES (?, ?)",
                         [(pid, c) for c in p["categories"]])
        conn.executemany("INSERT INTO itinerary_days (package_id, day_no, title, description) VALUES (?,?,?,?)",
                         [(pid, i, t, x) for i, (t, x) in enumerate(full["itinerary"], 1)])
        conn.executemany("INSERT INTO package_images (package_id, position, url) VALUES (?, ?, ?)",
                         [(pid, i, u) for i, u in enumerate(full["gallery"])])
    conn.commit()
    return True
