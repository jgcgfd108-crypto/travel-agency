"""WhatsApp enquiry: server-side validation and message building (single source of truth)."""
import re
from datetime import date, datetime
from urllib.parse import quote

_CTRL = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")
PLACEHOLDER_NUMBER = "916385047042"


def _clean(value, limit):
    text = _CTRL.sub("", str(value if value is not None else ""))
    text = re.sub(r"[ \t]+", " ", text).strip()
    return text[:limit + 1]  # one extra char so over-length input is detected


def validate(payload, find_package):
    """Return (cleaned, errors). `errors` maps field name -> message."""
    errors, out = {}, {}

    out["name"] = _clean(payload.get("name"), 60)
    if not 2 <= len(out["name"]) <= 60:
        errors["name"] = "Enter your name (2 to 60 characters)."

    phone = re.sub(r"[\s\-()]", "", _clean(payload.get("phone"), 20))
    if not re.fullmatch(r"\+?\d{7,15}", phone):
        errors["phone"] = "Enter a valid phone number (7 to 15 digits)."
    out["phone"] = phone

    slug = _clean(payload.get("package"), 80)
    pkg = find_package(slug) if slug else None
    if slug and not pkg:
        errors["form"] = "That package was not found."
    out["package"] = pkg

    out["destination"] = _clean(payload.get("destination"), 80)
    if not pkg and not 2 <= len(out["destination"]) <= 80:
        errors["destination"] = "Enter where you want to go."

    try:
        travellers = int(str(payload.get("travellers", "")).strip())
        if not 1 <= travellers <= 50:
            raise ValueError
        out["travellers"] = travellers
    except ValueError:
        errors["travellers"] = "Travellers must be a number from 1 to 50."

    raw_date = _clean(payload.get("date"), 10)
    out["date"] = None
    if raw_date:
        try:
            d = datetime.strptime(raw_date, "%Y-%m-%d").date()
            if d < date.today():
                errors["date"] = "Choose today or a later date."
            out["date"] = d
        except ValueError:
            errors["date"] = "Enter a valid date."

    out["message"] = _clean(payload.get("message"), 500)
    if len(out["message"]) > 500:
        errors["message"] = "Keep the message under 500 characters."
    return out, errors


def build_message(c):
    when = c["date"].strftime("%d %b %Y") if c["date"] else "Not selected"
    lines = ["Hello OUT OF BOUND!", ""]
    pkg = c["package"]
    if pkg:
        lines += ["I am interested in booking the following tour package:", "",
                  f"Package: {pkg['name']}",
                  f"Duration: {pkg['days']} Days / {pkg['nights']} Nights"]
    else:
        lines += ["I would like to plan a trip.", "", f"Destination: {c['destination']}"]
    lines += [f"Travellers: {c['travellers']}", f"Preferred Date: {when}",
              f"Name: {c['name']}", f"Phone: {c['phone']}"]
    if c["message"]:
        lines += ["", f"Message: {c['message']}"]
    lines += ["", "Please share the package details and availability." if pkg
              else "Please share suitable options and availability."]
    return "\n".join(lines)


def whatsapp_url(number, message):
    return f"https://wa.me/{number}?text={quote(message)}"
