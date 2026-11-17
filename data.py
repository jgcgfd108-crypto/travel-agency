"""Sample content for Phases 1-2. Replaced by SQLite queries in Phase 6."""


def img(photo_id, w=900):
    return f"https://images.unsplash.com/photo-{photo_id}?auto=format&fit=crop&w={w}&q=70"


HERO_IMAGE = img("1469854523086-cc02fe5d8800", 1920)

def _d(slug, name, country, region, category, photo, blurb):
    return {"slug": slug, "name": name, "country": country, "tag": region, "region": region,
            "category": category, "image": img(photo), "blurb": blurb}


DESTINATIONS = [
    _d("ooty", "Ooty", "India", "Domestic", "Hill Station", "1593693397690-362cb9666fc2", "Tea gardens, toy train and cool misty mornings in the Nilgiris."),
    _d("kodaikanal", "Kodaikanal", "India", "Domestic", "Hill Station", "1626621341517-bbf3d9990a23", "A star-shaped lake, pine forests and viewpoints over the Palani hills."),
    _d("munnar", "Munnar", "India", "Domestic", "Hill Station", "1593693397690-362cb9666fc2", "Rolling tea estates and waterfalls in the Western Ghats."),
    _d("kerala", "Kerala", "India", "Domestic", "Backwaters", "1602216056096-3b40cc0c9944", "Houseboats, palm-lined canals and slow, green days."),
    _d("goa", "Goa", "India", "Domestic", "Beach", "1512343879784-a960bf40e7f2", "Sunset beaches, old Portuguese lanes and great seafood."),
    _d("manali", "Manali", "India", "Domestic", "Mountains", "1626621341517-bbf3d9990a23", "Snow passes, river rafting and Himalayan cafes."),
    _d("bali", "Bali", "Indonesia", "International", "Beach", "1537996194471-e657df975ab4", "Temples, rice terraces and surf breaks."),
    _d("maldives", "Maldives", "Maldives", "International", "Beach", "1514282401047-d79a71a590e8", "Overwater villas and lagoons in every shade of blue."),
    _d("dubai", "Dubai", "UAE", "International", "City", "1512453979798-5ea266f8880c", "Record-breaking skyline, desert safaris and big shopping."),
    _d("singapore", "Singapore", "Singapore", "International", "City", "1525625293386-3f8f99389edd", "Gardens, hawker food and an easy, walkable city."),
    _d("thailand", "Thailand", "Thailand", "International", "Beach", "1552465011-b4e21bf6e79a", "Island hopping, street food and golden temples."),
    _d("switzerland", "Switzerland", "Switzerland", "International", "Mountains", "1530122037265-a5f1f91d3b99", "Alpine trains, lakes and snow-capped peaks."),
]
DEST_BY_SLUG = {d["slug"]: d for d in DESTINATIONS}


def _p(slug, dest, name, days, price, cats, summary, highlights):
    d = DEST_BY_SLUG[dest]
    return {"slug": slug, "dest": dest, "name": name, "days": days, "nights": days - 1, "price": price,
            "categories": cats, "category": cats[0], "image": d["image"], "summary": summary,
            "highlights": highlights}


# Prices are sample figures. Replace with real rates in the admin panel (Phase 7).
PACKAGES = [
    _p("bali-adventure", "bali", "Bali Adventure", 5, 38999, ["Adventure", "International"], "Temples, rice terraces and surf mornings.", ["Ubud rice terraces", "Uluwatu sunset", "Nusa Penida day trip"]),
    _p("munnar-family-escape", "munnar", "Munnar Family Escape", 3, 11499, ["Family", "Weekend"], "Tea hills, cool air and easy days together.", ["Tea estate walk", "Eravikulam National Park", "Family resort stay"]),
    _p("maldives-honeymoon", "maldives", "Maldives Honeymoon", 4, 67999, ["Honeymoon", "International"], "Overwater villa, lagoon dinners, total quiet.", ["Water villa stay", "Private sandbank dinner", "Snorkelling"]),
    _p("ooty-weekend-getaway", "ooty", "Ooty Weekend Getaway", 2, 6999, ["Weekend", "Family"], "A quick hill-station reset from Coimbatore.", ["Toy train ride", "Botanical Garden", "Doddabetta Peak"]),
    _p("kodaikanal-lake-retreat", "kodaikanal", "Kodaikanal Lake Retreat", 3, 9499, ["Weekend", "Group"], "Lakeside walks and misty viewpoints.", ["Coaker's Walk", "Boating on the lake", "Pillar Rocks"]),
    _p("kerala-backwaters-honeymoon", "kerala", "Kerala Backwaters Honeymoon", 5, 24999, ["Honeymoon"], "Houseboat nights and hill-station mornings.", ["Alleppey houseboat", "Munnar tea trails", "Candlelight dinner"]),
    _p("goa-group-fiesta", "goa", "Goa Group Fiesta", 4, 14999, ["Group"], "Beaches, water sports and nightlife for the crew.", ["North Goa beaches", "Water sports", "Old Goa heritage walk"]),
    _p("manali-snow-adventure", "manali", "Manali Snow Adventure", 6, 21999, ["Adventure", "Group"], "Snow, rivers and Himalayan roads.", ["Solang Valley", "Rohtang Pass*", "River rafting"]),
    _p("dubai-family-holiday", "dubai", "Dubai Family Holiday", 5, 54999, ["Family", "International"], "Theme parks, desert safari and skyline views.", ["Burj Khalifa", "Desert safari", "Dubai Mall and fountain"]),
    _p("singapore-city-escape", "singapore", "Singapore City Escape", 5, 59999, ["Family", "International"], "Gardens, Sentosa and food at every turn.", ["Gardens by the Bay", "Sentosa Island", "Night Safari"]),
    _p("thailand-island-hopper", "thailand", "Thailand Island Hopper", 6, 42999, ["Group", "Adventure", "International"], "Phuket, Phi Phi and Bangkok in one trip.", ["Phi Phi boat tour", "Bangkok temples", "Street food tour"]),
    _p("switzerland-alpine-honeymoon", "switzerland", "Switzerland Alpine Honeymoon", 7, 159999, ["Honeymoon", "International"], "Scenic trains, lakes and mountain-top views.", ["Jungfraujoch", "Lucerne lake cruise", "Glacier Express"]),
]
PKG_BY_SLUG = {p["slug"]: p for p in PACKAGES}
FEATURED = [PKG_BY_SLUG[s] for s in ("bali-adventure", "munnar-family-escape", "maldives-honeymoon")]
PACKAGE_CATEGORIES = ["Family", "Honeymoon", "Adventure", "Group", "Weekend", "International"]

EXPERIENCES = [
    {"title": "Mountain escapes", "text": "Treks, snow and sunrise camps.", "image": img("1626621341517-bbf3d9990a23", 700)},
    {"title": "Beach and island", "text": "Slow days, clear water, great food.", "image": img("1512343879784-a960bf40e7f2", 700)},
    {"title": "City and culture", "text": "Skylines, markets and local guides.", "image": img("1512453979798-5ea266f8880c", 700)},
]

REASONS = [
    ("shield-check", "Trusted planning", "Verified hotels, transport and guides on every trip."),
    ("wallet", "Clear pricing", "Prices in INR with inclusions and exclusions listed up front."),
    ("message-circle", "Talk to a person", "Plan and book over WhatsApp. No call centre queues."),
    ("map-pinned", "Made for you", "Every itinerary can be adjusted to your dates and pace."),
]

TESTIMONIALS = [
    {"name": "Sample Customer", "trip": "Bali Adventure", "text": "Placeholder review: replace with a real customer testimonial."},
    {"name": "Sample Customer", "trip": "Munnar Family Escape", "text": "Placeholder review: replace with a real customer testimonial."},
    {"name": "Sample Customer", "trip": "Maldives Honeymoon", "text": "Placeholder review: replace with a real customer testimonial."},
]


# ---------------------------------------------------------------- Phase 4: package details
# Hotel/transport lines are generic samples. Replace with real partners in the admin panel.
_DETAILS = {
 "bali-adventure": {"hotel": "3-4 star resort in Ubud and a beach hotel in Seminyak (or similar), breakfast included.",
  "transport": "Private air-conditioned car with driver for all transfers and sightseeing. Return flights to Bali are extra.",
  "days": [("Arrive in Bali", "Airport pickup, hotel check-in and a relaxed evening."),
           ("Ubud and rice terraces", "Tegalalang terraces, monkey forest and local markets."),
           ("Waterfalls and swing", "Waterfall visit, jungle swing and a cooking class."),
           ("Uluwatu and beach", "Free morning, Uluwatu temple and Kecak dance at sunset."),
           ("Departure", "Breakfast, checkout and airport drop.")]},
 "munnar-family-escape": {"hotel": "Family resort or cottage with valley view (or similar), breakfast and dinner included.",
  "transport": "AC tempo traveller or sedan from Coimbatore, used for all transfers and sightseeing.",
  "days": [("Coimbatore to Munnar", "Scenic drive, check-in and an evening tea-estate walk."),
           ("Munnar sightseeing", "Eravikulam National Park, Mattupetty Dam and Echo Point."),
           ("Return", "Tea museum visit and drive back to Coimbatore.")]},
 "maldives-honeymoon": {"hotel": "Water villa at a 4-star island resort (or similar) with breakfast and dinner.",
  "transport": "Speedboat or seaplane transfers between airport and resort. Return flights are extra.",
  "days": [("Arrival", "Welcome drink, transfer to the resort and villa check-in."),
           ("Lagoon day", "Snorkelling, sunset cruise and a romantic dinner."),
           ("Leisure day", "Spa, water sports or just the beach. Private sandbank dinner."),
           ("Departure", "Breakfast, checkout and transfer to the airport.")]},
 "ooty-weekend-getaway": {"hotel": "3-star hill hotel near the lake (or similar), breakfast included.",
  "transport": "Private cab from Coimbatore for transfers and local sightseeing.",
  "days": [("Coimbatore to Ooty", "Drive up the ghat road, Botanical Garden and Rose Garden."),
           ("Ooty sightseeing", "Doddabetta Peak, Ooty Lake, then return to Coimbatore.")]},
 "kodaikanal-lake-retreat": {"hotel": "Lake-view hotel or resort (or similar), breakfast included.",
  "transport": "AC tempo traveller or cab from Coimbatore for the whole trip.",
  "days": [("Arrival", "Drive to Kodaikanal, check-in and a stroll by the lake."),
           ("Viewpoints", "Coaker's Walk, Pillar Rocks, Guna Caves and Pine Forest."),
           ("Return", "Bryant Park and shopping, then drive back.")]},
 "kerala-backwaters-honeymoon": {"hotel": "Resort in Munnar and a deluxe houseboat in Alleppey (or similar), most meals included.",
  "transport": "Private car with driver from Kochi airport. Houseboat cruise included.",
  "days": [("Kochi to Munnar", "Scenic drive with waterfall stops and hotel check-in."),
           ("Munnar tea trails", "Tea estates, viewpoints and an evening bonfire."),
           ("Munnar to Thekkady", "Spice plantation walk and an optional evening show."),
           ("Alleppey houseboat", "Board the houseboat for a day on the backwaters and a candlelight dinner."),
           ("Departure", "Disembark and transfer to Kochi airport or station.")]},
 "goa-group-fiesta": {"hotel": "3-star beachside hotel with pool (or similar), breakfast included.",
  "transport": "AC coach or tempo traveller for the group. Local scooters can be arranged on request.",
  "days": [("Arrival", "Check-in, beach evening and a welcome dinner."),
           ("North Goa", "Calangute, Baga and Fort Aguada, with water sports."),
           ("South Goa and Old Goa", "Churches, quiet beaches and a sunset spot."),
           ("Departure", "Free morning, checkout and transfers.")]},
 "manali-snow-adventure": {"hotel": "Mountain hotel in Manali (or similar), breakfast and dinner included.",
  "transport": "Volvo or tempo traveller from Delhi/Chandigarh plus local cabs. Snow-point taxis are extra.",
  "days": [("Journey to Manali", "Overnight travel and arrival at the hotel."),
           ("Local Manali", "Hadimba Temple, Vashisht hot springs and Mall Road."),
           ("Solang Valley", "Snow activities such as zorbing and skiing (own cost)."),
           ("Rohtang Pass*", "Visit subject to permit and weather. Alternative: Atal Tunnel."),
           ("River rafting", "Rafting on the Beas and a free evening."),
           ("Departure", "Breakfast, checkout and journey back.")]},
 "dubai-family-holiday": {"hotel": "4-star hotel in Deira or Bur Dubai (or similar), breakfast included.",
  "transport": "Airport transfers and sightseeing by private or shared vehicle. Flights are extra.",
  "days": [("Arrival", "Airport pickup, hotel check-in and Dubai Marina evening."),
           ("City tour", "Jumeirah Mosque, Burj Al Arab view, Dubai Frame and old souks."),
           ("Desert safari", "Dune bashing, camel ride and BBQ dinner."),
           ("Burj Khalifa and Mall", "Observation deck visit and the fountain show."),
           ("Departure", "Shopping time, checkout and airport drop.")]},
 "singapore-city-escape": {"hotel": "3-4 star city hotel (or similar), breakfast included.",
  "transport": "Airport transfers and an MRT travel pass. Flights are extra.",
  "days": [("Arrival", "Hotel check-in and an evening at Marina Bay."),
           ("City highlights", "Merlion, Gardens by the Bay and the light show."),
           ("Sentosa", "Island rides, beaches and Universal Studios (ticket extra)."),
           ("Night Safari", "Zoo and Night Safari after a free afternoon."),
           ("Departure", "Last-minute shopping and airport drop.")]},
 "thailand-island-hopper": {"hotel": "3-star hotels in Phuket and Bangkok (or similar), breakfast included.",
  "transport": "Airport transfers, boat tours and an internal flight or transfer between cities. International flights are extra.",
  "days": [("Arrive in Phuket", "Transfer to the hotel and Patong evening."),
           ("Phi Phi Islands", "Speedboat tour with snorkelling and beach stops."),
           ("Phuket leisure", "Old Town, Big Buddha or free time."),
           ("Fly to Bangkok", "Transfer and an evening at a night market."),
           ("Bangkok temples", "Grand Palace, Wat Pho and a river cruise."),
           ("Departure", "Shopping and airport drop.")]},
 "switzerland-alpine-honeymoon": {"hotel": "3-4 star hotels in Lucerne, Interlaken and Zermatt (or similar), breakfast included.",
  "transport": "Swiss Travel Pass for trains, boats and buses. International flights and Schengen visa are extra.",
  "days": [("Arrive in Zurich", "Transfer to Lucerne and an old-town walk."),
           ("Lucerne", "Chapel Bridge and a lake cruise."),
           ("Mount Titlis", "Cable car to the glacier cave and snow activities."),
           ("Interlaken", "Scenic train and a lakeside evening."),
           ("Jungfraujoch", "Top of Europe by cogwheel train (weather permitting)."),
           ("Zermatt", "Glacier Express-style scenic ride and Matterhorn views."),
           ("Departure", "Transfer to Zurich airport.")]},
}

_INC_COMMON = ["Accommodation as listed", "Daily breakfast (other meals where noted)", "Airport / station transfers",
               "Sightseeing as per itinerary", "All current taxes"]
_EXC_COMMON = ["Meals not mentioned", "Personal expenses, tips and shopping", "Entry tickets not listed",
               "Travel insurance", "Anything not mentioned under Included"]


def _is_intl(p):
    return DEST_BY_SLUG[p["dest"]]["region"] == "International"


def faqs_for(intl):
    faqs = [
        ("Is the price per person?", "Yes, the starting price is per person on twin sharing. Final cost depends on dates, hotel category and group size."),
        ("Can the itinerary be changed?", "Yes. Message us on WhatsApp with your dates and preferences and we will adjust it."),
        ("How do I book?", "Send an enquiry on WhatsApp. We confirm availability and share payment details there. There is no online payment on this site."),
        ("What if the weather affects a plan?", "We swap activities where possible, such as an alternative sightseeing day, and keep you informed."),
    ]
    if intl:
        faqs.append(("Do I need a visa?", "Most international trips need a visa or entry permit. We guide you on documents; fees are paid by the traveller."))
    return faqs


def get_package(slug):
    """Return a package merged with its detail content, or None."""
    p = PKG_BY_SLUG.get(slug)
    if not p:
        return None
    det = _DETAILS[slug]
    intl = _is_intl(p)
    d = DEST_BY_SLUG[p["dest"]]
    # Gallery: own photo plus photos from similar destinations (replace with real shots).
    gallery = [p["image"]]
    for x in DESTINATIONS:
        if x["category"] == d["category"] and x["image"] not in gallery:
            gallery.append(x["image"])
    for x in DESTINATIONS:
        if len(gallery) >= 4:
            break
        if x["image"] not in gallery:
            gallery.append(x["image"])
    included = _INC_COMMON + (["Visa assistance guidance"] if intl else [])
    excluded = _EXC_COMMON + (["International flights", "Visa fees"] if intl else ["Train / flight tickets to the start point"])
    faqs = faqs_for(intl)
    return {**p, "destination": d, "hotel": det["hotel"], "transport": det["transport"],
            "itinerary": det["days"], "gallery": gallery, "included": included, "excluded": excluded,
            "faqs": faqs, "intl": intl}
