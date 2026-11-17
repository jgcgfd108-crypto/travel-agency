"""Central configuration. All business details live here (or in .env)."""
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")  # validated in app.py
    DATABASE = os.path.join(os.path.dirname(__file__), "instance", "out_of_bound.db")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("COOKIE_SECURE") == "1"   # set COOKIE_SECURE=1 behind HTTPS
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    SEND_FILE_MAX_AGE_DEFAULT = timedelta(days=30)             # CSS/JS URLs are versioned (?v=), see static_url()
    TRUST_PROXY = os.environ.get("TRUST_PROXY") == "1"          # set TRUST_PROXY=1 behind nginx / a platform proxy
    ENQUIRY_LIMIT = 8                                           # saved enquiries per IP ...
    ENQUIRY_WINDOW = 600                                        # ... per 10 minutes

    # --- Editable placeholders until real business details are provided ---
    AGENCY_NAME = "OUT OF BOUND"
    TAGLINE = "Explore Beyond Boundaries."
    WHATSAPP_NUMBER = os.environ.get("WHATSAPP_NUMBER", "910000000000")  # PLACEHOLDER
    CONTACT_PHONE = os.environ.get("CONTACT_PHONE", "+91 00000 00000")   # PLACEHOLDER
    CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL", "hello@outofbound.example")
    OFFICE_ADDRESS = "Coimbatore, Tamil Nadu, India"                     # PLACEHOLDER: use the real office address
