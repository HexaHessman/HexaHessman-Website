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
  side         the client's own words beside the photos in PRODUCT TYPES (their mock-ups, 2026-11-12): a list of
               paragraphs; a (label, text) pair is a paragraph that opens with a bold label. With it, the page has no
               separate overview block under the hero.
  pics         [(picture, alt)] two photos without captions beside those words, for a product whose types are grades
               (sulphuric acid, bitumen: the grade cards follow underneath) or that has none (methanol)
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
            # every figure to two decimal places (client, 2026-11-12). Acidity is the exception: its limits are thousandths of a
            # percent (0.0015, 0.003, 0.004), which two places would turn into 0.00, so that row keeps four places.
            ["Sulphur Content (S), % min", "99.98", "99.95", "99.90", "99.50", "99.20"],
            ["Ash Content, % max", "0.02", "0.03", "0.05", "0.20", "0.40"],
            ["Organic Matter, % max", "0.01", "0.03", "0.06", "0.25", "0.50"],
            ["Acidity (as H₂SO₄), % max", "0.0015", "0.0030", "0.0040", "0.0100", "0.0200"],
            ["Moisture Content, % max", "0.20", "0.20", "0.20", "0.20", "1.00"],
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
    "sulphuric-acid": {
        "pics": [(T + "sulphuric-acid-1.jpg", "Sulphuric acid in an ISO tank container"), (T + "sulphuric-acid-2.jpg", "A storage tank of 98% sulphuric acid")],
        "side": ["Sulfuric acid (H₂SO₄) is a highly corrosive industrial chemical widely used in fertilizer production, mineral processing, petroleum refining, and chemical manufacturing. It is primarily produced from elemental sulfur through the Contact Process, with commercial concentrations typically ranging from 93% to 98%.",
                 "Global demand is driven largely by phosphate fertilizer production and mining operations, particularly nickel extraction through high-pressure acid leaching (HPAL). Due to its hazardous nature, sulfuric acid requires specialized storage, transportation, and handling procedures to ensure safety and regulatory compliance."],
        "types": [
        ("Industrial Grade", "93–98% H₂SO₄ for fertilizer, mining and chemical plants.", None),
        ("Battery Grade", "35–38% H₂SO₄, diluted for lead-acid batteries.", None),
        ("Technical Grade", "90–98% H₂SO₄ for general industrial use.", None),
        ("Electronic Grade", "99.999% purity for the semiconductor industry.", None),
        ("Food / Pharma Grade", "Highly purified, for specialised applications.", None)]},
    # Rock Phosphate and Phosphoric Acid: the client's second batch of mock-ups (2026-11-12), copied as sent
    "rock-phosphate": {
        "side": ["Rock phosphate is a naturally occurring mineral rich in P₂O₅. Commercial grades contain at least 25% P₂O₅ and are the primary raw material for phosphoric acid, DAP, MAP, TSP, SSP and NPK fertilizers, as well as elemental phosphorus.",
                 "Our rock phosphate comes from high-quality sedimentary deposits with 28–31% P₂O₅ and 62–68% BPL (bone phosphate of lime).",
                 "Its reactivity (35–40% soluble in 2% citric acid and 55–65% in 2% formic acid) also makes it suitable for direct application on acidic soils."],
        "types": [
        ("Granular Form", "", T + "rock-phosphate-1.jpg"),
        ("Powder Form", "", T + "rock-phosphate-2.jpg")]},
    "phosphoric-acid": {
        "pics": [(T + "phosphoric-acid-1.jpg", "85% phosphoric acid poured from a bottle into a beaker"), (T + "phosphoric-acid-2.jpg", "An IBC container of 85% phosphoric acid")],
        "side": ["Produced primarily through the wet-process method, phosphoric acid is manufactured by reacting phosphate rock with sulfuric acid. Its quality is determined by P₂O₅ concentration, impurity levels, and consistency, making it suitable for applications ranging from fertilizer manufacturing to industrial chemical production.",
                 "Global demand is largely driven by agricultural fertilizer consumption, particularly in major markets across Asia, the Middle East, and Latin America. Reliable sourcing, consistent product specifications, and efficient logistics are essential to ensuring uninterrupted supply for industrial and agricultural applications."],
        "types": [
        ("Merchant-Grade Acid (MGA)", "52–54% P₂O₅ for MAP, DAP, TSP and NPK fertilizer manufacture.", None),
        ("Technical Grade 85%", "Purified 85% H₃PO₄ for industrial use and metal treatment.", None)]},
    "map": {
        "side": ["Monoammonium Phosphate (MAP) is a concentrated, water-soluble fertilizer that provides essential nitrogen and phosphorus for healthy crop development. Its high phosphorus content and mildly acidic properties promote strong root establishment, early plant growth, and efficient nutrient uptake, making it widely used in field crops, horticulture, and plantation agriculture.",
                 "MAP is suitable for direct soil application, fertilizer blending, and precision fertilization programmes. Its consistent nutrient composition, excellent solubility, and compatibility with various agricultural practices make it a preferred choice for commercial farming."],
        "types": [
        ("Granular MAP 11-52-0", "Granular grade with 11% nitrogen and 52% P₂O₅.", T + "map-granular.jpg"),
        ("Water-Soluble MAP 12-61-0", "Water-soluble grade with 12% nitrogen and 61% P₂O₅.", T + "map-soluble.jpg")]},
    "dap": {
        "side": ["Diammonium Phosphate (DAP) is the most widely used phosphate-based fertilizer in global agriculture. DAP is a dual-nutrient source fertilizer that contains 18% ammoniacal nitrogen (N) and 46% phosphorus pentoxide (P₂O₅), making it an essential input for promoting early root development, vigorous growth, and enhanced crop yields.",
                 "DAP is produced through the chemical reaction of anhydrous ammonia (NH₃) and phosphoric acid (H₃PO₄). The result is a dry, granular fertilizer with excellent handling and storage properties, suitable for both direct application and blending in customized NPK formulas."],
        "types": [
        ("Agricultural Grade DAP Granules", "", T + "dap-1.jpg"),
        ("Technical Grade DAP Powder", "", T + "dap-2.jpg")]},
    "urea": {
        "side": ["Urea (CO(NH₂)₂), the most widely used nitrogen fertilizer in the world, delivering 46% nitrogen in a highly concentrated, readily available form. As a cost-effective and efficient nutrient source, urea supports vigorous crop growth and improved yields across a broad spectrum of farming systems.",
                 "Urea is a white crystalline compound composed of 46% nitrogen, making it the highest nitrogen-content solid fertilizer available. It is non-flammable, water-soluble, and compatible with a wide variety of other fertilizers and micronutrients. Urea plays a critical role in protein synthesis in plants and is especially important during the vegetative growth phase."],
        "types": [
        ("Prilled Urea", "Smaller round particles that dissolve quickly, suited to foliar application and fertigation.", T + "urea-prilled.jpg"),
        ("Granular Urea", "Larger, harder, uniform particles that resist caking, suited to mechanical spreading and blending.", T + "urea-granular.jpg")]},
    "ammonium-sulphate": {
        "side": ["Ammonium Sulphate ((NH₄)₂SO₄) is a premium nitrogen-based fertilizer and industrial chemical valued for its versatility, purity, and stability. As one of the most widely used inorganic fertilizers, it provides an efficient source of nitrogen and sulfur, two essential nutrients that promote healthy plant growth, chlorophyll formation, and protein synthesis. Beyond agriculture, its balanced composition and high solubility make it suitable for a range of industrial and laboratory applications.",
                 "Both crystalline and granular forms, offering users flexibility based on their specific handling and application needs. The crystalline form dissolves rapidly, ideal for fertigation and blending, while the granular form provides superior flow characteristics for mechanical spreading and storage stability."],
        "types": [
        ("Crystalline", "Fast-dissolving crystals, ideal for fertigation and blending.", T + "as-crystalline.jpg"),
        ("Granular", "Free-flowing granules, ideal for mechanical spreading and storage.", T + "as-granular.jpg")]},
    "caustic-soda": {"types": [
        ("Flakes", "Membrane-grade solid, NaOH 99% min., in moisture-proof bags.", T + "caustic-flakes.jpg"),
        ("Pearls", "Free-flowing prills, NaOH 99% min., in moisture-proof bags.", T + "caustic-pearls.jpg"),
        ("Liquid Lye", "32% and 48–50% solutions in ISO tanks and bulk chemical tankers.", T + "caustic-lye.jpg")]},
    "soda-ash": {
        "side": ["Sodium carbonate (Na₂CO₃), commonly known as soda ash, is a versatile chemical utilized broadly across industries for pH modification, detergent formulation, and chemical processing.",
                 "Our Soda Ash represents a shift from conventional mineral-based sources by being derived entirely from the renewable raw material, wood. It is a purified, odorless, white granulate, supplied in two product grades: soda ash light and soda ash dense.",
                 ("Safety Information:", "Avoid inhalation; use PPE; store in dry, ventilated area")],
        "types": [
        ("Dense Soda Ash", "Coarse granulate for glass making and bulk handling.", T + "soda-dense.jpg"),
        ("Light Soda Ash", "Fine powder for detergents and chemicals.", T + "soda-light.jpg")]},
    "semi-coke": {"rename": {"How we supply": "Source of origin"},
        "side": ["Semi-coke is a critical input in nickel ferroalloy production, particularly within the Rotary Kiln–Electric Furnace (RKEF) process widely used across Asia. Acting as both a reducing agent and energy source, it enables the efficient conversion of nickel ore into nickel pig iron (NPI), a key material in stainless steel manufacturing.",
                 "Its cost efficiency, high reactivity, and stable performance make semi-coke the preferred alternative to metallurgical coke for large-scale smelters. As Indonesia continues to lead global nickel production, demand for reliable semi-coke supply remains strong across major industrial hubs."],
        "types": [
        ("Lumps", "Large, porous, dull black lumps designed for use in nickel smelting furnaces.", T + "semi-coke-1.jpg"),
        ("Granular / Nut Coke", "Small, black granular pieces ideal for smelting applications.", T + "semi-coke-2.jpg")]},
    "metallurgical-coke": {"rename": {"How we supply": "Source of origin"},
        "side": ["Metallurgical coke (met coke) is produced through the high-temperature carbonization of coking coal in the absence of oxygen. It is a key raw material in blast furnace ironmaking, where it functions as both a high-energy fuel and a structural support medium, ensuring proper gas flow and furnace permeability during smelting.",
                 "In blast furnace operations, met coke enables the reduction of iron ore into molten iron by generating the intense heat required while also acting as the primary carbon source for chemical reduction reactions. Its strength, low impurity levels, and high carbon content make it essential for stable and efficient steel production, directly impacting furnace productivity and output quality."],
        "types": [
        ("Lumps", "Large, hard, and porous greyish-black lumps used primarily for blast furnaces and foundries.", T + "metallurgical-coke-1.jpg"),
        ("Breeze / Fine Powder", "Fine, dark metallic powder (breeze) for industrial factory processes.", T + "metallurgical-coke-2.jpg")]},
    "calcined-pet-coke": {
        "side": ["Calcined petroleum coke (CPC) is a crucial raw material in both the aluminum smelting and steelmaking industries. In the aluminum sector, it serves as the primary carbon source for manufacturing the consumable anodes required in the Hall-Héroult electrolysis process. For steel and foundry applications, particularly in Electric Arc Furnaces (EAF), low-sulphur CPC acts as a highly efficient carbon raiser to precisely control the carbon content of the final alloy.",
                 "Its high carbon purity, low electrical resistance, and minimal impurities (such as sulphur and ash) make calcined pet coke vital for producing high-quality metals. As global demand accelerates for lightweight aluminum in electric vehicles and sustainable EAF steel production, the reliance on a consistent, premium supply of calcined pet coke continues to grow across heavy industries."],
        "types": [
        ("Sponge / Granules", "Dark grey, porous granules featuring low-sulphur content for anodes and carbon raising.", T + "calcined-pet-coke-1.jpg"),
        ("Fine Powder", "A fine, dark black powder used for carbon raising.", T + "calcined-pet-coke-2.jpg")]},
    "graphite-pet-coke": {
        "side": ["Graphitized petroleum coke (GPC) is a premium carbon additive utilized extensively in the production of high-quality steel, ductile iron, and specialized iron castings. Manufactured by heating high-grade petroleum coke to extreme temperatures, its molecular structure is transformed into artificial graphite, ensuring rapid carbon dissolution and exceptionally high carbon recovery during the melting process.",
                 "Its ultra-high carbon purity, superior absorption rate, and negligible sulphur and nitrogen content make it the preferred carbon raiser for precision metallurgy and high-end automotive components. As foundries and advanced manufacturing sectors increasingly require strict metallurgical control to reduce casting defects, the strategic demand for high-grade graphite pet coke remains robust."],
        "types": [
        ("Granular", "Shiny, metallic grey graphitized granules used as a carbon raiser for steel and ductile iron.", T + "graphite-pet-coke-1.jpg"),
        ("Powder / Dust", "A highly reflective, fine metallic grey graphitized dust.", T + "graphite-pet-coke-2.jpg")]},
    "methanol": {
        "pics": [(T + "methanol-1.jpg", "Methanol in an ISO tank container"), (T + "methanol-2.jpg", "Methanol in steel drums on a pallet")],
        "side": ["Methanol (CH₃OH) is a critical chemical input and versatile solvent used extensively across the global chemical, energy, and manufacturing sectors. Primarily produced from natural gas or biomass, it acts as a fundamental building block for producing formaldehydes, plastics, synthetic fibers, and fuel additives like MTBE, which are essential for countless everyday consumer and industrial products. As a clean-burning fuel and a key agent in wastewater denitrification, its utility as an eco-friendly energy source has seen rapid global adoption.",
                 "Its high chemical reactivity, ease of transport, and function as a precursor for biodiesel and marine fuels make methanol indispensable for modern industrial hubs. As international markets prioritize low-carbon energy transition and chemical diversification, the consistent and safe global distribution of methanol, via both heavy-duty drums for precision manufacturing and massive ISO tanks for large-scale operations, remains a cornerstone of the global industrial supply chain."]},
    "bitumen": {
        "pics": [(T + "bitumen-1.jpg", "Bitumen in IBC containers"), (T + "bitumen-2.jpg", "Bitumen in steel drums on a pallet")],
        "side": ["Bitumen is a critical, highly viscous material and key binding agent used extensively across the global infrastructure, construction, and manufacturing sectors. Primarily obtained through the refinery process of heavy crude oil, it acts as the essential binder in asphalt, which is required for paving highways, airport runways, and parking lots. Because of its excellent waterproofing and adhesive properties, it also serves as a fundamental material in manufacturing roofing felts, sealing compounds, and protective coatings for industrial pipelines.",
                 "Its remarkable durability, resistance to wear and water, and capacity to withstand heavy vehicular loads make bitumen indispensable for modern infrastructure and transit networks. As international markets prioritize robust, climate-resilient transport networks and urban development, the consistent and safe global distribution of bitumen, via specially insulated ISO tanks for heated bulk transport and heavy-duty steel drums for versatile site delivery, remains a cornerstone of the global industrial supply chain."],
        "types": [
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
    "barite-powder": {
        "side": ["Barite, or Barium Sulfate (BaSO₄), is more than just a mineral, it is a high-performance solution for industries that demand precision, reliability, and efficiency. Known for its exceptional density, chemical inertness, and non-toxic nature, barite enables companies to optimize processes, improve product performance, and maintain safety standards. Its versatility makes it an indispensable material across drilling, chemical, and manufacturing applications.",
                 "High-grade barite ensures consistent particle size and purity, giving customers the confidence that their drilling fluids remain stable, paints maintain desired density, and plastics or rubber products achieve uniform quality. By delivering a product that combines natural strength with industrial precision, we help businesses streamline operations and reduce variability."],
        "types": [
        ("Barite Powder", "Milled to a consistent particle size, in API 13A drilling grade and filler grades.", T + "barite-powder.jpg"),
        ("Barite Lumps", "Lump form, supplied in bulk.", T + "barite-lumps.jpg")]},
    "bentonite": {
        "side": ["Bentonite is a highly versatile, absorbent clay consisting primarily of montmorillonite, typically formed from the weathering of volcanic ash in seawater. It is utilized extensively across heavy industries, construction, and manufacturing due to its unique physical properties. Its primary industrial applications include serving as a critical lubricating and cooling agent in drilling muds for the oil and gas sector, a powerful binding agent in the production of iron ore pellets for steelmaking, and a crucial structural component in foundry sand molds for metal casting.",
                 "The remarkable characteristics of bentonite, specifically its ability to swell up to several times its original volume when exposed to water, its high viscosity, and its superior absorption capabilities, make it an indispensable sealant in civil engineering, tunneling, and environmental protection projects such as landfill liners. As global infrastructure expands and the demand for efficient, safe resource extraction continues, the reliance on a stable, high-quality supply of bentonite remains vital for ensuring operational efficiency across a diverse range of industrial hubs."],
        "types": [
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
