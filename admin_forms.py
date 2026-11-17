"""Server-side validation for the admin forms. Returns (clean_data, errors)."""
import re

from data import PACKAGE_CATEGORIES

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
URL_RE = re.compile(r"""^(?:https?://[^\s"'<>]+|/static/[^\s"'<>]+)$""")
_CTRL = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:80]


def _s(form, key):
    return _CTRL.sub("", form.get(key, "")).strip()


def _int(form, key):
    try:
        return int(form.get(key, "").strip())
    except (ValueError, AttributeError):
        return None


def _lines(form, key):
    return [_CTRL.sub("", ln).strip() for ln in form.get(key, "").splitlines() if ln.strip()]


def _bad_lines(lines, max_count, max_len, label):
    if len(lines) > max_count:
        return f"{label}: at most {max_count} lines."
    if any(len(ln) > max_len for ln in lines):
        return f"{label}: each line must be {max_len} characters or fewer."
    return ""


def form_values(form):
    vals = {k: form.get(k, "") for k in form}
    vals["categories"] = form.getlist("categories")
    return vals


def _slug(form, name, errors):
    slug = _s(form, "slug") or slugify(name)
    if not SLUG_RE.fullmatch(slug) or len(slug) > 80:
        errors["slug"] = "Use lowercase letters, digits and single hyphens (max 80)."
    return slug


def _url(value, errors, key, required=True):
    if not value:
        if required:
            errors[key] = "Enter an image URL."
    elif len(value) > 500 or not URL_RE.fullmatch(value):
        errors[key] = "Use an https:// URL or a /static/... path."


def validate_package(form, destination_ids):
    e, d = {}, {}
    d["name"] = _s(form, "name")
    if not 3 <= len(d["name"]) <= 80:
        e["name"] = "Name must be 3 to 80 characters."
    d["slug"] = _slug(form, d["name"], e)

    d["destination_id"] = _int(form, "destination_id")
    if d["destination_id"] not in destination_ids:
        e["destination_id"] = "Choose a destination."

    d["days"], d["nights"], d["price"] = _int(form, "days"), _int(form, "nights"), _int(form, "price")
    if d["days"] is None or not 1 <= d["days"] <= 60:
        e["days"] = "Days must be 1 to 60."
    if d["nights"] is None or d["nights"] < 0 or (d["days"] and d["nights"] > d["days"]):
        e["nights"] = "Nights must be 0 and not more than days."
    if d["price"] is None or not 1 <= d["price"] <= 10_000_000:
        e["price"] = "Price must be a whole number of rupees (1 to 10,000,000)."

    d["summary"] = _s(form, "summary")
    if len(d["summary"]) > 200:
        e["summary"] = "Keep the summary under 200 characters."
    for key in ("hotel", "transport"):
        d[key] = _s(form, key)
        if len(d[key]) > 300:
            e[key] = "Keep this under 300 characters."

    d["image"] = _s(form, "image")
    _url(d["image"], e, "image")

    for key, n, m in (("highlights", 8, 80), ("included", 15, 100), ("excluded", 15, 100)):
        d[key] = _lines(form, key)
        if msg := _bad_lines(d[key], n, m, key.capitalize()):
            e[key] = msg

    d["categories"] = [c for c in PACKAGE_CATEGORIES if c in form.getlist("categories")]
    if not d["categories"]:
        e["categories"] = "Choose at least one category."

    d["itinerary"] = []
    for ln in _lines(form, "itinerary"):
        title, _, desc = ln.partition("|")
        d["itinerary"].append((title.strip(), desc.strip()))
    if not d["itinerary"]:
        e["itinerary"] = "Add the day-wise itinerary, one day per line."
    elif d["days"] and len(d["itinerary"]) != d["days"]:
        e["itinerary"] = f"The itinerary has {len(d['itinerary'])} lines but the package is {d['days']} days."
    elif any(not 1 <= len(t) <= 80 or len(x) > 300 for t, x in d["itinerary"]):
        e["itinerary"] = "Each day needs a title (max 80) and a description of at most 300 characters."

    d["gallery"] = _lines(form, "gallery")
    if len(d["gallery"]) > 8 or any(len(u) > 500 or not URL_RE.fullmatch(u) for u in d["gallery"]):
        e["gallery"] = "At most 8 image URLs (https:// or /static/...), one per line."
    if not d["gallery"] and d["image"]:
        d["gallery"] = [d["image"]]

    d["is_featured"] = 1 if form.get("is_featured") else 0
    d["is_active"] = 1 if form.get("is_active") else 0
    return d, e


def package_to_form(p):
    return {"name": p["name"], "slug": p["slug"], "destination_id": str(p["destination_id"]), "days": str(p["days"]),
            "nights": str(p["nights"]), "price": str(p["price"]), "summary": p["summary"], "hotel": p["hotel"],
            "transport": p["transport"], "image": p["image"], "highlights": p["highlights"],
            "included": p["included"], "excluded": p["excluded"], "categories": p["categories"],
            "itinerary": "\n".join(f"{t} | {x}" for t, x in p["itinerary"]), "gallery": "\n".join(p["gallery"]),
            "is_featured": "on" if p["is_featured"] else "", "is_active": "on" if p["is_active"] else ""}


def validate_destination(form):
    e, d = {}, {}
    d["name"] = _s(form, "name")
    if not 2 <= len(d["name"]) <= 60:
        e["name"] = "Name must be 2 to 60 characters."
    d["slug"] = _slug(form, d["name"], e)
    d["country"] = _s(form, "country")
    if not 2 <= len(d["country"]) <= 60:
        e["country"] = "Country must be 2 to 60 characters."
    d["region"] = _s(form, "region")
    if d["region"] not in ("Domestic", "International"):
        e["region"] = "Choose Domestic or International."
    d["category"] = _s(form, "category")
    if not 2 <= len(d["category"]) <= 40:
        e["category"] = "Category must be 2 to 40 characters (for example Beach, Hill Station)."
    d["image"] = _s(form, "image")
    _url(d["image"], e, "image")
    d["blurb"] = _s(form, "blurb")
    if len(d["blurb"]) > 300:
        e["blurb"] = "Keep the description under 300 characters."
    d["is_popular"] = 1 if form.get("is_popular") else 0
    return d, e


def destination_to_form(r):
    return {"name": r["name"], "slug": r["slug"], "country": r["country"], "region": r["region"],
            "category": r["category"], "image": r["image"], "blurb": r["blurb"],
            "is_popular": "on" if r["is_popular"] else ""}
