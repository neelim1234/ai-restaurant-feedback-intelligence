"""
dataset/patterns.py - Pure data configuration for the synthetic dataset generator.

No imports from the application. This file must be self-contained so the
generator can run as a standalone script in both csv and db modes.

ALL hidden pattern adjustments are defined here as named dictionaries.
The generator resolves which config to use based on row context.
"""

# ---------------------------------------------------------------------------
# City distribution weights  (target: 8500 rows)
# ---------------------------------------------------------------------------
CITY_WEIGHTS = {
    "Mumbai":    0.30,   # ~2550 rows
    "Bangalore": 0.25,   # ~2125 rows
    "Pune":      0.20,   # ~1700 rows
    "Delhi":     0.15,   # ~1275 rows
    "Hyderabad": 0.10,   #  ~850 rows
}

# ---------------------------------------------------------------------------
# Branch definitions
# Order matches the seed insertion order in seed.py — this determines
# the expected sequential IDs (1..17) used in --mode csv output.
# ---------------------------------------------------------------------------
BRANCH_DEFINITIONS = [
    # Urban Tandoor (brand_id=1) — Indian cuisine only
    {"id": 1,  "brand": "Urban Tandoor", "name": "Bandra Branch",           "city": "Mumbai",    "cuisines": ["Indian"]},
    {"id": 2,  "brand": "Urban Tandoor", "name": "FC Road Branch",           "city": "Pune",      "cuisines": ["Indian"]},
    {"id": 3,  "brand": "Urban Tandoor", "name": "Connaught Place Branch",   "city": "Delhi",     "cuisines": ["Indian"]},
    {"id": 4,  "brand": "Urban Tandoor", "name": "Banjara Hills Branch",     "city": "Hyderabad", "cuisines": ["Indian"]},
    # Thai Bowl (brand_id=2) — Thai + Chinese
    {"id": 5,  "brand": "Thai Bowl",    "name": "Andheri Branch",            "city": "Mumbai",    "cuisines": ["Thai", "Chinese"]},
    {"id": 6,  "brand": "Thai Bowl",    "name": "Kothrud Branch",            "city": "Pune",      "cuisines": ["Thai", "Chinese"]},
    {"id": 7,  "brand": "Thai Bowl",    "name": "Indiranagar Branch",        "city": "Bangalore", "cuisines": ["Thai", "Chinese"]},
    {"id": 8,  "brand": "Thai Bowl",    "name": "Lajpat Nagar Branch",       "city": "Delhi",     "cuisines": ["Thai", "Chinese"]},
    # La Cucina (brand_id=3) — Italian only
    {"id": 9,  "brand": "La Cucina",   "name": "Koramangala Branch",        "city": "Bangalore", "cuisines": ["Italian"]},
    {"id": 10, "brand": "La Cucina",   "name": "Juhu Branch",               "city": "Mumbai",    "cuisines": ["Italian"]},
    {"id": 11, "brand": "La Cucina",   "name": "Aundh Branch",              "city": "Pune",      "cuisines": ["Italian"]},
    {"id": 12, "brand": "La Cucina",   "name": "Hauz Khas Branch",          "city": "Delhi",     "cuisines": ["Italian"]},
    # QuickBite (brand_id=4) — Chinese + Fast Food
    {"id": 13, "brand": "QuickBite",   "name": "Dadar Branch",              "city": "Mumbai",    "cuisines": ["Chinese", "Fast Food"]},
    {"id": 14, "brand": "QuickBite",   "name": "Whitefield Branch",         "city": "Bangalore", "cuisines": ["Chinese", "Fast Food"]},
    {"id": 15, "brand": "QuickBite",   "name": "Saket Branch",              "city": "Delhi",     "cuisines": ["Chinese", "Fast Food"]},
    {"id": 16, "brand": "QuickBite",   "name": "HITEC City Branch",         "city": "Hyderabad", "cuisines": ["Chinese", "Fast Food"]},
    {"id": 17, "brand": "QuickBite",   "name": "Hinjewadi Branch",          "city": "Pune",      "cuisines": ["Chinese", "Fast Food"]},
]

# Pre-build city → branches lookup (used during generation)
BRANCHES_BY_CITY: dict[str, list[dict]] = {}
for _b in BRANCH_DEFINITIONS:
    BRANCHES_BY_CITY.setdefault(_b["city"], []).append(_b)

# ---------------------------------------------------------------------------
# Date configuration
# ---------------------------------------------------------------------------
DATE_CONFIG = {
    "start":  "2024-01-01",
    "end":    "2025-06-30",
    # Day-of-week weights: Mon=0, Tue=1, Wed=2, Thu=3, Fri=4, Sat=5, Sun=6
    # P7: Friday + Saturday have 40% higher volume
    "dow_weights": [1.0, 1.0, 1.0, 1.0, 1.4, 1.4, 1.0],
    # P7: Weekend rating dip (shift distribution downward)
    "weekend_rating_dip": 0.3,
    # P8: Q4 months get a rating uplift (festive season)
    "q4_months": [10, 11, 12],
    "q4_rating_uplift": 0.2,
}

# ---------------------------------------------------------------------------
# Service type weights  [delivery, dine-in, takeaway]
#
# Named configs — resolved in generator.get_service_type()
# ---------------------------------------------------------------------------
SERVICE_TYPE_WEIGHTS = {
    # Baseline
    "default":              [0.45, 0.40, 0.15],
    # P1: Mumbai — high delivery volume
    "mumbai":               [0.55, 0.30, 0.15],
    # P3: Bangalore La Cucina — skews strongly to dine-in (fine dining)
    "bangalore_lacucina":   [0.20, 0.65, 0.15],
    # P4: Delhi QuickBite — high delivery volume
    "delhi_quickbite":      [0.60, 0.25, 0.15],
    # P9: Hyderabad — skews to dine-in
    "hyderabad":            [0.30, 0.55, 0.15],
}

# ---------------------------------------------------------------------------
# Rating weights  [r1, r2, r3, r4, r5]
#
# Named configs — resolved in generator.get_rating()
# Applied BEFORE P7/P8 date-based adjustments.
# ---------------------------------------------------------------------------
RATING_WEIGHTS = {
    # Baseline: avg ~3.7
    "default":                      [0.05, 0.10, 0.20, 0.40, 0.25],
    # P1: Mumbai + delivery → avg ~2.7
    "mumbai_delivery":              [0.20, 0.30, 0.25, 0.15, 0.10],
    # P2: Pune + Thai Bowl → avg ~2.2
    "pune_thai_bowl":               [0.35, 0.30, 0.20, 0.10, 0.05],
    # P3: Bangalore + La Cucina + dine-in → avg ~4.3
    "bangalore_lacucina_dinein":    [0.01, 0.02, 0.08, 0.39, 0.50],
    # P4: Delhi + QuickBite → avg ~2.9
    "delhi_quickbite":              [0.15, 0.25, 0.30, 0.20, 0.10],
    # P9: Hyderabad + dine-in → avg ~3.1
    "hyderabad_dinein":             [0.10, 0.20, 0.30, 0.25, 0.15],
}

# ---------------------------------------------------------------------------
# Price segment weights per brand
# ---------------------------------------------------------------------------
PRICE_SEGMENT_WEIGHTS = {
    # name: {segment: weight}
    "default":       {"budget": 0.30, "mid-range": 0.55, "premium": 0.15},
    "La Cucina":     {"budget": 0.05, "mid-range": 0.40, "premium": 0.55},
    "Thai Bowl":     {"budget": 0.35, "mid-range": 0.55, "premium": 0.10},
    "Urban Tandoor": {"budget": 0.25, "mid-range": 0.60, "premium": 0.15},
    "QuickBite":     {"budget": 0.65, "mid-range": 0.30, "premium": 0.05},
}

# ---------------------------------------------------------------------------
# Complaint category weights for NEGATIVE reviews (rating <= 3)
#
# All 8 categories must sum to 1.0 per config.
# Named configs — resolved in generator.get_complaint_weights()
# Priority order in generator: most specific pattern first.
# ---------------------------------------------------------------------------
COMPLAINT_WEIGHTS = {
    "default": {
        "delivery_delay":  0.15,
        "food_quality":    0.20,
        "pricing":         0.12,
        "packaging":       0.10,
        "hygiene":         0.12,
        "staff_behavior":  0.12,
        "ambience":        0.10,
        "portion_size":    0.09,
    },
    # P1: Mumbai + delivery → delivery_delay dominates
    "mumbai_delivery": {
        "delivery_delay":  0.55,
        "food_quality":    0.15,
        "pricing":         0.04,
        "packaging":       0.10,
        "hygiene":         0.05,
        "staff_behavior":  0.05,
        "ambience":        0.02,
        "portion_size":    0.04,
    },
    # P2: Pune + Thai Bowl → pricing + portion_size dominate
    "pune_thai_bowl": {
        "delivery_delay":  0.05,
        "food_quality":    0.10,
        "pricing":         0.40,
        "packaging":       0.05,
        "hygiene":         0.04,
        "staff_behavior":  0.05,
        "ambience":        0.06,
        "portion_size":    0.25,
    },
    # P4: Delhi + QuickBite + delivery → packaging spike
    "delhi_quickbite_delivery": {
        "delivery_delay":  0.15,
        "food_quality":    0.10,
        "pricing":         0.05,
        "packaging":       0.45,
        "hygiene":         0.10,
        "staff_behavior":  0.05,
        "ambience":        0.02,
        "portion_size":    0.08,
    },
    # P6: Premium segment — rare complaints but pricing + portion_size when it occurs
    "premium": {
        "delivery_delay":  0.05,
        "food_quality":    0.15,
        "pricing":         0.35,
        "packaging":       0.05,
        "hygiene":         0.05,
        "staff_behavior":  0.10,
        "ambience":        0.05,
        "portion_size":    0.20,
    },
    # P9: Hyderabad + dine-in → ambience + staff_behavior dominate
    "hyderabad_dinein": {
        "delivery_delay":  0.02,
        "food_quality":    0.10,
        "pricing":         0.07,
        "packaging":       0.03,
        "hygiene":         0.10,
        "staff_behavior":  0.35,
        "ambience":        0.28,
        "portion_size":    0.05,
    },
    # P10: Fast Food + delivery → packaging + portion_size
    "fastfood_delivery": {
        "delivery_delay":  0.15,
        "food_quality":    0.08,
        "pricing":         0.05,
        "packaging":       0.40,
        "hygiene":         0.05,
        "staff_behavior":  0.02,
        "ambience":        0.02,
        "portion_size":    0.23,
    },
}

# ---------------------------------------------------------------------------
# Wait time configuration (minutes)
#
# Values used with random.gauss(mean, std), then clamped to [min, max].
# ---------------------------------------------------------------------------
WAIT_TIME_CONFIG = {
    # Standard delivery / takeaway
    "default":           {"mean": 25, "std": 10, "min": 10, "max": 75},
    # P1: Mumbai delivery → systematically high wait times
    "mumbai_delivery":   {"mean": 52, "std": 12, "min": 35, "max": 90},
    # P5: Low rating (1-2) + delivery → high wait time correlation
    "negative_delivery": {"mean": 47, "std": 13, "min": 30, "max": 90},
    # Dine-in: wait time = in-restaurant wait, shorter
    "dinein":            {"mean": 15, "std":  7, "min":  5, "max": 55},
}

# ---------------------------------------------------------------------------
# Order value ranges (INR) per price segment
# ---------------------------------------------------------------------------
ORDER_VALUE_RANGES = {
    "budget":    (150,  450),
    "mid-range": (400,  900),
    "premium":   (800, 2500),
}

# ---------------------------------------------------------------------------
# Review text templates
#
# All templates may use any of these format keys (unused ones are ignored):
#   {wait}     — wait_time_mins value (for delay templates)
#   {cuisine}  — ordered cuisine name
#   {city}     — city name
# ---------------------------------------------------------------------------

POSITIVE_TEMPLATES = [
    "Absolutely loved the food! Fresh ingredients and excellent taste. Will definitely come back.",
    "Great experience overall. The service was prompt and the staff were very friendly.",
    "Food was delicious and arrived hot. Highly recommend the {cuisine} options here.",
    "One of the best {cuisine} meals I have had in {city}. Excellent quality and great value.",
    "Very impressed with the quality. Top-notch food and wonderful presentation.",
    "Fresh, flavorful, and fast. Exactly what I needed. Will definitely order again.",
    "The {cuisine} food here is authentic and the portions are very generous.",
    "Fantastic service and amazing food. The staff went above and beyond to help.",
    "Really enjoyed the dining experience. Food was fresh and the flavors were spot on.",
    "Prompt delivery, hot food, and great packaging. Couldn't ask for more.",
    "Excellent taste and presentation. My whole family loved every dish we ordered.",
    "The quality has been consistently great across all my visits. Highly recommend.",
    "Outstanding {cuisine} cuisine at a very reasonable price. Great value for money.",
    "Love this place! The food is always fresh and the service is top-notch.",
    "Very satisfied with the order. Food was exactly as described and tasted amazing.",
    "The ambience was wonderful and the food matched the setting perfectly. Loved it.",
    "Staff were extremely attentive and the food quality was exceptional. Five stars.",
    "Consistent quality every single time. This is my go-to place for {cuisine} in {city}.",
    "Brilliant food at a great price. The {cuisine} dishes were particularly outstanding.",
    "Everything was perfect — from the packaging to the taste to the delivery speed.",
]

NEUTRAL_TEMPLATES = [
    "Food was decent, nothing extraordinary. Delivery was on time though.",
    "Average experience overall. The food was okay but nothing to write home about.",
    "It was fine. Food quality was acceptable and the service was normal.",
    "Mediocre experience. Some items were good, others were a bit disappointing.",
    "The food was average. Expected a bit more for the price charged.",
    "Not bad but not great either. Might give it another try sometime.",
    "Service was okay, food was acceptable. Nothing really exceptional to report.",
    "Decent meal for the price. Some items could be improved.",
    "Mixed feelings about this order. Some dishes were good, some were not.",
    "It was satisfactory. Food arrived on time but quality was just average.",
]

NEGATIVE_TEMPLATES = {
    "delivery_delay": [
        "Waited over {wait} minutes for the delivery. By the time the food arrived, it was completely cold. Unacceptable.",
        "Delivery took {wait} minutes! The food was cold and stale by then. Very disappointing experience.",
        "Extremely late delivery — {wait} minutes! How is this acceptable? The food was ruined by the time it came.",
        "Order took {wait} minutes to arrive. Cold food, terrible experience overall. Will not order again.",
        "The delivery was terribly late — {wait} minutes. Food quality suffered massively because of the delay.",
        "{wait} minute wait for delivery is absolutely not okay. Cold food, ruined evening. Very bad service.",
        "Waited almost {wait} minutes and the food arrived completely cold. This is absolutely unacceptable.",
        "Very slow delivery — {wait} minutes. The food was stone cold by the time it reached me.",
        "I ordered at 7pm and the food showed up {wait} minutes later, cold and inedible. Never again.",
        "Disgraceful delivery time of {wait} minutes. The food was meant to be served hot. Completely ruined.",
    ],
    "food_quality": [
        "The food was completely cold and stale. Clearly not freshly prepared. Very disappointed.",
        "Terrible food quality. The dishes were tasteless and appeared to be reheated leftovers.",
        "Cold, stale food that had clearly been sitting for too long before it was sent out. Not worth the money.",
        "The food quality was awful. Tasteless and not fresh at all. Expected much better from this place.",
        "Undercooked food that was also cold. This is a health hazard. Will not be ordering again.",
        "The dishes arrived cold and overcooked simultaneously. No resemblance to what was advertised.",
        "Extremely disappointing food quality. Stale ingredients and absolutely no flavor whatsoever.",
        "Food was soggy and tasteless. The ingredients seemed far from fresh. Very bad experience.",
        "The {cuisine} food was nothing like what I expected. Bland, cold, and not fresh at all.",
        "Absolutely terrible quality. Food was cold, tasteless, and the ingredients were clearly not fresh.",
    ],
    "pricing": [
        "Way overpriced for the quality you get. Definitely not worth it. Much better options elsewhere.",
        "Too expensive for such average quality food. This is definitely not value for money.",
        "The prices are completely unjustified by the food quality. Highway robbery!",
        "Overpriced and deeply disappointing. You can get much better food elsewhere at half the cost.",
        "Not worth the cost at all. The portions are small and the food quality is below average.",
        "The pricing is completely unreasonable. I expected a lot more for what I paid.",
        "Far too expensive. The food does absolutely not justify the price tag charged.",
        "Ridiculously expensive for what you actually get. Definitely not value for money at all.",
        "I paid premium prices for absolutely mediocre food. Completely unjustified pricing.",
        "The price-to-quality ratio here is terrible. Overpriced by at least 40% for what you receive.",
    ],
    "packaging": [
        "The packaging was terrible — everything leaked and spilled all over the inside of the bag.",
        "Food arrived with the container completely damaged. The packaging needs serious improvement.",
        "The packaging is pathetic. Everything was crushed and the gravy had spilled everywhere.",
        "Leaking containers completely ruined the entire order. Fix your packaging immediately.",
        "Food was all over the bag because of poor packaging. Completely unacceptable service.",
        "The box was damaged and the food had spilled out. Poor packaging cost me an entire meal.",
        "Everything leaked during delivery. Please use proper sealed containers for your food.",
        "Terrible packaging — food was mixed up and spilled all over inside the delivery bag.",
        "The packaging is completely inadequate. My entire order was a soggy mess on arrival.",
        "Arrived with a crushed container and spilled contents. The packaging is absolutely substandard.",
    ],
    "hygiene": [
        "Found a hair in my food. This is absolutely disgusting and completely unacceptable.",
        "The food smelled off and had visible contamination. Seriously unhygienic conditions.",
        "Terrible hygiene standards. Found foreign objects in the food. Filing a complaint.",
        "The restaurant premises looked very dirty when I visited. The food was unhygienic too.",
        "Found something unidentifiable in the food. Extremely unhygienic and potentially dangerous.",
        "The food quality raises serious hygiene concerns. It did not seem safe to eat at all.",
        "Unclean kitchen practices are very evident from the food quality. Absolutely disgusting.",
        "Dirty utensils and unhygienic food. This place needs a thorough health inspection immediately.",
        "Found insects near the food preparation area. The hygiene standards here are unacceptable.",
        "The kitchen looked filthy and the food reflected that. Serious hygiene issues at this place.",
    ],
    "staff_behavior": [
        "The staff was incredibly rude and completely unprofessional. No basic courtesy whatsoever.",
        "Terrible customer service. The staff behaved very rudely when I raised a complaint.",
        "The staff attitude is absolutely appalling. Very disrespectful and extremely dismissive.",
        "Rude and dismissive staff who made me feel completely unwelcome. Will not return here.",
        "The behavior of the staff was totally unacceptable. Zero professionalism on display.",
        "Staff were extremely rude and had absolutely no regard for customer experience.",
        "Very poor staff behavior. Rude responses and zero accountability for their mistakes.",
        "The staff's completely unprofessional attitude ruined the entire dining experience for us.",
        "I was spoken to rudely when I asked a simple question. Staff training is clearly lacking.",
        "The server was dismissive and rude throughout. No basic courtesy or professionalism at all.",
    ],
    "ambience": [
        "The restaurant was incredibly noisy — it was impossible to have any conversation.",
        "Very uncomfortable seating and a generally very unpleasant atmosphere throughout.",
        "The place was dirty and the overall ambience was terrible. Not what I expected at all.",
        "Extremely loud and overcrowded. No effort was made to maintain a decent atmosphere.",
        "The dining area was filthy and the ambience was awful. Very disappointing experience.",
        "Uncomfortable seating, poor lighting, and far too noisy to actually enjoy the meal.",
        "The overall atmosphere was very unpleasant. Dirty, loud, and completely unwelcoming.",
        "Terrible ambience completely ruined what could have been a decent dining experience.",
        "The restaurant was unkempt and dirty. Tables were not cleaned between customers.",
        "Very noisy environment with poor ventilation. The ambience was below par in every way.",
    ],
    "portion_size": [
        "The portions were shockingly small for the price being charged. Not at all filling.",
        "Very small portions that left me still hungry. Definitely not worth the money at all.",
        "The quantity of food was pathetically small. Completely did not justify the price.",
        "Extremely small portions. I had to order additional food from elsewhere just to feel full.",
        "Not filling at all. The portion sizes are way too small for the price point they charge.",
        "Tiny portions that are a complete rip-off. This is definitely not value for money.",
        "Skimpy portions at high prices. Very, very poor value for money at this place.",
        "The food quantity was deeply disappointing. Very small portions for the price charged.",
        "I was still hungry after finishing the entire order. The portions are simply too small.",
        "Paid a lot and received very little food in return. The portion sizes are unacceptably small.",
    ],
}
