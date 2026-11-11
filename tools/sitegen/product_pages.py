"""Product pages in the client's format (Hafriz's "70%" PDF of the sulphur page, 2026-11-11).

Every product page now reads: wide photo hero with the name in capitals -> PRODUCT TYPES (photos) -> PRODUCT
SPECIFICATIONS (charts with a dark green header row, then the applications chart) -> PRODUCT RESOURCES (key figures,
pictures, "where it comes from" bar) -> drop-downs (Source of origin, Logistics, Procedures...) -> related products.

Sulphur is taken word for word from the PDF. The other products are mapped into the same layout from what the site
already says about them (content.py, the 2026 business profile). What only the client can supply stays out until they
send it: key figures, the origin photo and trade map, and the route details. A block shows only when it has data.

PAGES[slug] keys (all optional):
  title        the hero title (shown in capitals)
  types_title  heading of the first block ("Product types" by default)
  types        [(name, description, picture or None)]
  specs        spec charts that replace the product's own ([{title?, headers?, rows}])
  apps         {"headers": [...], "rows": [[...]]}  the applications chart, when it has more than one column
  resources    {"stats": [(figure, unit, label)], "images": [(src, alt)], "bar": {...}, "note": str}
  drops        [(title, html)] drop-downs that come first (the rest are built from the product's sections)
  loading      the loading rate in the Procedures drop-down ("at about 2,000 MT per day")
"""
T = "/assets/products/types/"
R = "/assets/products/resources/"

# the trade procedure from the PDF's PROCEDURES drop-down; {loading} is the product's loading rate, where known
PROCEDURES = [
    ("Phase I · Pre-contract", [
        ("LOI", "Buyer states intent, including any broker commission details. The LOI must come from the entity that will open the L/C."),
        ("FCO", "Seller sends the offer with KYC documents."),
        ("ICPO", "Buyer sends the purchase order with KYC documents."),
        ("SPA", "Seller issues the agreement; Buyer signs it and sends it back."),
        ("Proforma Invoice", "Seller issues it; Buyer signs it."),
    ]),
    ("Phase II · L/C and loading", [
        ("L/C Issuance", "Buyer’s bank opens a 100% irrevocable MT700 L/C at sight that matches the SPA and PI."),
        ("L/C Verification", "Seller’s bank confirms the L/C, and loading preparations begin."),
        ("Insurance", "Seller insures the cargo before the vessel sails."),
        ("Vessel and Loading", "Seller nominates the vessel and loads{loading}."),
        ("SGS Inspection", "Seller pays for SGS to certify quantity and quality at the loading port. Buyer approves the inspector."),
        ("B/L and Title", "A Clean On Board B/L is issued. Title passes to the Buyer at the loading port."),
        ("Documents", "Seller sends the full set of shipping documents, and the vessel sails."),
    ]),
    ("Phase III · Payment", [
        ("L/C Payment", "Buyer’s bank pays at sight when compliant documents are presented."),
        ("Discharge Inspection (Optional)", "Buyer may inspect at the discharge port at its own cost. This cannot delay payment."),
    ]),
]
PROCEDURES_NOTE = "Any change to these terms needs written agreement from both parties."

# the person behind the floating Contact button on every commodity page (PDF p.5)
CONTACT = {"name": "Adam Yeoh", "role": "Business Development Manager", "entity": "HexaHessman Singapore",
           "email": "Adam.Yeoh@HexaHessman.com", "photo": "/assets/team/cut/adam-yeoh.webp", "linkedin": ""}   # LinkedIn link still to come from the client

PAGES = {
    # ------------------------------------------------------------------ sulphur: the PDF, word for word
    "sulphur": {
        "title": "Solid Sulphur",
        "types": [
            ("Granular Sulphur", "Formed from molten refinery sulphur into hard, uniform granules with low dust and good flow. It is the preferred form for long-distance bulk shipment and acid plants.", T + "sulphur-granular.jpg"),
            ("Lump Sulphur", "Crushed solid sulphur from open stockpiles, ready for melting. Lower cost, but irregular and more prone to breakage and dust, which is why the industry favours formed sulphur for cleaner handling.", T + "sulphur-lump.jpg"),
            ("Pastilles Sulphur", "Formed sulphur with controlled particle size, high purity and low dust, widely used as feedstock for sulphuric acid, fertilizers, chemicals and rubber.", T + "sulphur-pastilles.jpg"),
        ],
        "specs": [{"headers": ["Parameter", "9998", "9995", "9990", "9950", "9920"], "rows": [
            ["Sulphur Content (S), % min", "99.98", "99.95", "99.9", "99.5", "99.2"],
            ["Ash Content, % max", "0.02", "0.03", "0.05", "0.2", "0.4"],
            ["Organic Matter, % max", "0.01", "0.03", "0.06", "0.25", "0.5"],
            ["Acidity (as H₂SO₄), % max", "0.0015", "0.003", "0.004", "0.01", "0.02"],
            ["Moisture Content, % max", "0.2", "0.2", "0.2", "0.2", "1"],
            ["Mechanical Impurities", "None", "None", "None", "None", "None"]]}],
        "apps": {"headers": ["Industry / Application", "Sulphur purity", "Technical & commercial considerations"], "rows": [
            ["Phosphate Fertilizers (DAP, MAP, TSP)", "99.50–99.90%", "Sulphur is converted into sulphuric acid for phosphate rock processing. Grade 9950 can offer cost savings where plant specifications permit."],
            ["Nickel Processing (HPAL & Leaching)", "99.20–99.50%", "Large-volume acid production. Cost competitiveness is important, subject to acceptable ash, moisture and contaminant limits."],
            ["Sulphuric Acid Production (Merchant Acid)", "99.50–99.95%", "Low ash and organic matter are critical for catalyst performance, maintenance and acid quality."],
            ["Rubber & Tyre Manufacturing", "99.95–99.98%", "High purity and low acidity support consistent vulcanisation and product quality."],
            ["Specialty Chemicals, Pharmaceuticals & Food-Related Uses", "≥99.98%", "Requires stringent impurity controls, particularly trace metals. Additional application-specific certification may be necessary."],
            ["Agriculture (Direct Soil Application)", "≥99.20%", "Lower-purity grades may be economical for soil amendment, subject to agricultural quality and contaminant requirements."]]},
        "resources": {
            "stats": [("39–40", "Mt/yr", "global seaborne sulphur trade"), ("~47", "%", "of seaborne trade loads in the Middle East"),
                      ("5.13", "Mt", "projected global deficit in 2026 (HDIN Research)"), ("4", "", "export restrictions in twelve months")],
            "images": [(R + "sulphur-source.jpg", "The Galkynyş gas field plant in Turkmenistan, seen from above"), (R + "sulphur-trade-map.svg", "World map of sulphur export sources and major import markets")],
            "bar": {"title": "Where the world’s sulphur comes from", "parts": [("Oil refining", 65, "#E6CF2E"), ("Gas processing", 32, "#B5A019"), ("Mining & other", 3, "#8A8A80")],
                    "total": "Total production ~85.8 Mt (2025E)"},
            "note": "~10 t of sulphur for every tonne of nickel from Indonesian HPAL, the new driver of demand.",
        },
        "loading": " at about 2,000 MT per day",
        "drops": [
            ("Source of origin", """<h4>Source: Galkynyş Gas Field, Turkmenistan</h4>
<p>Our sulphur comes from the Galkynyş Gas Field. The field was formerly known as Ýolöten or South Ýolöten–Osman. It sits near Ýolöten in Mary Province, about 75 km southeast of the city of Mary and about 400 km southeast of Ashgabat.</p>
<p>Turkmenistan’s government describes it as the world’s second-largest gas field, with estimated reserves of around 26 trillion cubic metres.</p>
<p>The raw gas from the field is sour: it contains up to 6% H₂S. That is why the development was built with large gas treatment and sulphur handling facilities, and why sulphur is a steady by-product of every cubic metre processed.</p>
<p>The plant’s first and second purification units recently produced about 182,000 tonnes of sulphur in one reporting period. The field is owned by Turkmengaz, the state gas company. China’s national oil company (CNPC) has now started the fourth of seven planned development phases, so sulphur supply should keep growing.</p>"""),
            ("Logistics", """<p><b>Stage 1 · Rail to Türkmenbaşy Port (3–5 days)</b><br>Wagons are loaded at the plant and run about 1,000 km west to Türkmenbaşy on the Caspian Sea.</p>
<p><b>Stage 2 · Rail ferry to Baku (Alat)</b><br>The loaded wagons roll straight onto the ferry, so the cargo is never unloaded at sea. (1–2 days, up to 5 with queuing)</p>
<p><b>Stage 3 · Rail to Poti / Batumi (2–3 days)</b><br>A scheduled block train carries the cargo across Azerbaijan and Georgia to the Black Sea. Plant to Black Sea: about 8–14 days</p>
<p><b>Mediterranean Option: Iskenderun / Mersin, Türkiye</b></p>
<p><b>Option A ·</b> Rail via Baku–Tbilisi–Kars (5–8 days from Baku)<br>The cargo goes straight by rail to Türkiye’s Mediterranean coast, replacing Stage 3. The track gauge changes at Akhalkalaki in Georgia.</p>
<p><b>Option B ·</b> Sea from Poti / Batumi (adds 7–10 days)<br>The cargo sails from Georgia through the Bosphorus to Iskenderun or Mersin.</p>"""),
        ],
        "spec_note": "Trace elements (As, Se, Te) are maintained at negligible levels (≤0.01 ppm).",   # hexahessman.com, sulphur page
        "skip": ["Applications", "Industries served"],   # the PDF's applications chart replaces these
        "rename": {"How we supply": "Supply structure"},   # the profile's paragraph, after the PDF's three drop-downs
    },

    # ------------------------------------------------------------------ the others: types from what the site already says
    "sulphuric-acid": {"types": [
        ("Industrial Grade", "93–98% H₂SO₄ for fertilizer, mining and chemical plants.", None),
        ("Battery Grade", "35–38% H₂SO₄, diluted for lead-acid batteries.", None),
        ("Technical Grade", "90–98% H₂SO₄ for general industrial use.", None),
        ("Electronic Grade", "99.999% purity for the semiconductor industry.", None),
        ("Food / Pharma Grade", "Highly purified, for specialised applications.", None)]},
    "phosphoric-acid": {"types": [
        ("Merchant-Grade Acid (MGA)", "52–54% P₂O₅ for MAP, DAP, TSP and NPK fertilizer manufacture.", None),
        ("Technical Grade 85%", "Purified 85% H₃PO₄ for industrial use and metal treatment.", None)]},
    "map": {"types": [
        ("Granular MAP 11-52-0", "Granular grade with 11% nitrogen and 52% P₂O₅.", T + "map-granular.jpg"),
        ("Water-Soluble MAP 12-61-0", "Water-soluble grade with 12% nitrogen and 61% P₂O₅.", T + "map-soluble.jpg")]},
    "urea": {"types": [
        ("Prilled Urea", "Smaller round particles that dissolve quickly, suited to foliar application and fertigation.", T + "urea-prilled.jpg"),
        ("Granular Urea", "Larger, harder, uniform particles that resist caking, suited to mechanical spreading and blending.", T + "urea-granular.jpg")]},
    "ammonium-sulphate": {"types": [
        ("Crystalline", "Fast-dissolving crystals, ideal for fertigation and blending.", T + "as-crystalline.jpg"),
        ("Granular", "Free-flowing granules, ideal for mechanical spreading and storage.", T + "as-granular.jpg")]},
    "caustic-soda": {"types": [
        ("Flakes", "Membrane-grade solid, NaOH 99% min., in moisture-proof bags.", T + "caustic-flakes.jpg"),
        ("Pearls", "Free-flowing prills, NaOH 99% min., in moisture-proof bags.", T + "caustic-pearls.jpg"),
        ("Liquid Lye", "32% and 48–50% solutions in ISO tanks and bulk chemical tankers.", T + "caustic-lye.jpg")]},
    "soda-ash": {"types": [
        ("Dense Soda Ash", "Coarse granulate for glass making and bulk handling.", T + "soda-dense.jpg"),
        ("Light Soda Ash", "Fine powder for detergents and chemicals.", T + "soda-light.jpg")]},
    "semi-coke": {"rename": {"How we supply": "Source of origin"}},
    "metallurgical-coke": {"rename": {"How we supply": "Source of origin"}},
    "bitumen": {"types": [
        ("Penetration Grade", "40/50, 60/70 and 80/100, chosen by climate from hot to cold.", None),
        ("Viscosity Grade", "VG-10 to VG-40, from cold-region roads to heavy-duty pavements.", None),
        ("Performance Grade", "PG 58-22, PG 64-22 and PG 70-28 for highways and extreme climates.", None),
        ("Polymer-Modified (PMB)", "PMB 40 and PMB 70 for medium-traffic roads and expressways.", None),
        ("Cutback Bitumen", "RC-70, MC-30 and SC-250 for cold weather, priming and dust control.", None),
        ("Oxidised Bitumen", "85/25 and 90/40 blown grades for roofing, damp-proofing and pipe coatings.", None)]},
    "base-oil": {"types": [
        ("Group I", "Solvent-refined base oil.", None),
        ("Group II", "Hydro-processed base oil.", None),
        ("SN150", "Light neutral viscosity grade.", None),
        ("SN500", "Heavy neutral viscosity grade.", None)]},
    "barite-powder": {"types": [
        ("Barite Powder", "Milled to a consistent particle size, in API 13A drilling grade and filler grades.", T + "barite-powder.jpg"),
        ("Barite Lumps", "Lump form, supplied in bulk.", T + "barite-lumps.jpg")]},
    "bentonite": {"types": [
        ("Bentonite Powder", "Milled grades Sec 9, 10 and 11 for drilling, foundry and civil works.", T + "bentonite-powder.jpg"),
        ("Bentonite Lumps", "Lump form, supplied in bulk.", T + "bentonite-lumps.jpg")]},
    "wood-chips": {"types": [
        ("Eucalyptus", "Plantation-grown hardwood chips, supplied in fibre and fuel grades.", T + "chips-eucalyptus.jpg"),
        ("Acacia", "Plantation-grown hardwood chips, supplied in fibre and fuel grades.", T + "chips-acacia.jpg"),
        ("Pine", "Plantation-grown softwood chips, supplied in fibre and fuel grades.", T + "chips-pine.jpg")]},
    "coconut-shell-charcoal": {"types": [
        ("Lump", "Whole carbonised shell pieces, hard and dense.", T + "charcoal-lump.jpg"),
        ("Granular", "Screened granules of uniform size.", T + "charcoal-granular.jpg"),
        ("Crushed", "Finely crushed charcoal in small fragments.", T + "charcoal-crushed.jpg")]},
}


# ---------------------------------------------------------------------------------------------------------------------
# More from the client's own material (2026-11-11, user: every fact on a commodity page comes from their PDF or their
# website). Sources: the 2026 business profile (p.5 commodity supply, p.7 sulphur, p.8 bitumen, p.11 cokes, p.14
# fertilizers) and the product pages on hexahessman.com. Nothing here is researched or written from outside knowledge.
SUPPLY_NET = "By leveraging decades of industry experience and a vast international network of trusted partners, HexaHessman anticipates and responds to the evolving energy and feedstock needs of clients worldwide, with solutions that are both precise and dependable."   # profile p.5
SUPPLY_REFINERY = "We deliver products direct from refinery with consistency and reliability."   # profile p.5
FERT_SUPPLY = ["HexaHessman is committed to supporting Indonesia’s agricultural sector with reliable fertilizer solutions tailored to local crop requirements, combining global sourcing strength with local market insight.",
               "We maintain a reliable supply chain through direct sourcing from trusted global producers, ensuring quality-assured products and consistent availability for bulk buyers. We coordinate efficient logistics and delivery, and offer competitive pricing for distributors and large-scale buyers."]   # profile p.14
CROPS_N = "Supports vegetative growth, yield formation and overall crop productivity. Widely used in rice, corn, sugarcane, oil palm and other plantation crops."   # profile p.14, nitrogenous fertilizers
CROPS_P = "Promotes root development, early plant establishment, flowering and yield formation. Used across corn, rice, horticulture and high-value crops."   # profile p.14, phosphatic fertilizers


def enrich(products):
    by = {p["slug"]: p for p in products}
    sec = lambda slug, t: next((x for x in by[slug]["sections"] if x.get("title") == t), None)
    def add(slug, s):
        secs = by[slug]["sections"]; i = next((k for k, x in enumerate(secs) if x.get("title") == "Distribution"), len(secs)); secs.insert(i, s)
    def rows(slug, new, block=None):   # extend a spec chart (by its title; None = the first chart)
        blocks = [b for x in by[slug]["sections"] if x.get("spec") for b in x["spec"]]
        b = next(b for b in blocks if block is None or b.get("title") == block); have = {r[0] for r in b["rows"]}
        cas = next((k for k, r in enumerate(b["rows"]) if r[0].startswith("CAS")), len(b["rows"]))
        b["rows"][cas:cas] = [r for r in new if r[0] not in have]
    def supply(slug, paras):
        x = sec(slug, "How we supply")
        if x: x["paras"] = x.get("paras", []) + [t for t in paras if t not in x.get("paras", [])]
        else: add(slug, {"title": "How we supply", "paras": list(paras)})

    # fertilizers (profile p.14)
    for slug, crops in (("urea", CROPS_N), ("ammonium-sulphate", CROPS_N), ("dap", CROPS_P), ("map", CROPS_P), ("rock-phosphate", CROPS_P + " Rock phosphate serves as a natural phosphate source.")):
        supply(slug, FERT_SUPPLY); add(slug, {"title": "Crop focus", "paras": [crops]})
    supply("map", ["HexaHessman can support MAP supply requirements for agricultural distributors, fertilizer blenders, plantation operators and industrial buyers, subject to origin, specification and availability."])   # hexahessman.com
    sec("urea", "Packaging")["items"].insert(1, "25 kg PP bags")   # hexahessman.com
    # ammonium sulphate (hexahessman.com)
    rows("ammonium-sulphate", [["Molecular weight", "132.14 g/mol"], ["Solubility", "Highly soluble in water"], ["pH (0.1 M solution)", "Approx. 5.5"], ["Bulk density", "0.95–1.1 g/cm³"]])
    sec("ammonium-sulphate", "Applications")["items"].append("Laboratory: a standard reagent for protein precipitation in biochemical research")
    sec("ammonium-sulphate", "Packaging")["items"].append("Custom packaging on request")
    add("ammonium-sulphate", {"title": "Safety information", "items": ["Avoid inhalation of dust; it may cause mild respiratory irritation", "Use personal protective equipment such as gloves, goggles and masks when handling",
        "Store in a cool, dry and well-ventilated area, away from strong oxidisers and moisture", "Not classified as hazardous under normal use; handle in line with good industrial hygiene practice"]})
    # cokes (hexahessman.com)
    supply("semi-coke", ["As Indonesia continues to lead global nickel production, demand for reliable semi coke supply remains strong across major industrial hubs. Through strategic sourcing and strong partnerships, we ensure a dependable supply chain that supports performance, efficiency and growth."])
    supply("metallurgical-coke", ["Through strategic sourcing and reliable logistics networks, we ensure a stable supply chain that supports uninterrupted blast furnace operations and long-term industrial performance."])
    # bitumen (profile p.8, and the viscosity figures on hexahessman.com)
    supply("bitumen", ["HexaHessman is strategically positioned as a reliable and competitive supplier of premium bitumen products throughout the Asia region. Leveraging strong partnerships with leading refineries and global logistics networks, we deliver a consistent and secure supply of bitumen that meets international quality standards and project-specific requirements."])
    g = sec("bitumen", "Grades")
    g["spec"].append({"title": "Viscosity grade: viscosity at 60°C", "headers": ["Grade", "Viscosity at 60°C", "Use"], "rows": [
        ["VG-10", "800–1,200 poise", "Spraying and surface dressing in cold climates"], ["VG-20", "1,600–2,400 poise", "Paving in cold regions"],
        ["VG-30", "2,400–3,600 poise", "Paving in moderate climates"], ["VG-40", "3,200–4,800 poise", "Heavy-traffic roads in hot climates"]]})
    sec("bitumen", "Packaging")["items"].append("Custom packaging to client requirements and destination regulations")
    # barite and bentonite (hexahessman.com)
    rows("barite-powder", [["Mohs hardness", "3–3.5"], ["Loss on ignition (LOI)", "≤1.0%"], ["Insoluble matter", "≤0.3%"], ["Bulk density (powder)", "1.2–1.6 g/cm³"]], "General properties")
    supply("barite-powder", ["Whether your project requires bulk supply for oil and gas operations or specialised grades for chemical production, our barite is tailored to meet diverse needs. With stringent quality controls, every batch supports your industrial goals efficiently, safely and sustainably."])
    add("barite-powder", {"title": "Safety information", "items": ["Avoid inhalation of fine dust", "Use appropriate PPE", "Store in a dry, ventilated area away from incompatible chemicals"]})
    rows("bentonite", [["Loss on ignition (LOI)", "≤12%"], ["Appearance", "White to light grey powder / lumps"]])
    add("bentonite", {"title": "Safety information", "items": ["Avoid inhalation of fine particles", "Use PPE", "Store in a dry, ventilated area"]})
    # soda ash (hexahessman.com)
    rows("soda-ash", [["pH (10% solution)", "11.5–12.5"], ["Solubility", "High solubility in water"]], "Product data")
    add("soda-ash", {"title": "Source of origin", "paras": ["Our soda ash represents a shift from conventional mineral-based sources: it is derived entirely from the renewable raw material, wood.",
        "It is a purified, odourless, white granulate supplied in two grades, light and dense. A result of our significant investment in research and development, HexaHessman’s dissolving wood pulp production now yields several valuable biorefinery co-products."]})
    # every other product: the profile's own statement of how commodities are supplied (p.5)
    for p in products:
        if not any(x.get("title") in ("How we supply", "Our production", "Source of origin") for x in p["sections"]) and p["slug"] != "sulphur":
            supply(p["slug"], ([SUPPLY_REFINERY + " " + SUPPLY_NET] if p["group"] in ("petroleum-oilfield", "industrial-chemicals") else [SUPPLY_NET]))
