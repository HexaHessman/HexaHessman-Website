# Content for the HexaHessman static pages, transcribed from the customer's skeleton
# (scratchpad/content/skeleton.txt). Bracketed "[confirm]" / "[e.g. …]" notes are kept here where
# they were in the source; build.py strips "[confirm…]" tags and drops rows that are only a placeholder.

CONTACT = "/contact/"
WHATSAPP = "https://wa.me/6580619119"

# Button label -> href
BUTTONS = {
    "Request a quote": CONTACT + "#quote",
    "Request a quotation": CONTACT + "#quote",
    "Request datasheet / SDS": CONTACT + "#datasheet",
    "Request pricing": CONTACT + "#quote",
    "Request a sample": CONTACT + "#sample",
    "Talk to the supply desk": CONTACT + "#quote",
    "Discuss a project": CONTACT + "#quote",
    "Request service / maintenance": CONTACT + "#service",
    "Message us on WhatsApp": WHATSAPP,
    "Message us on WhatsApp (+65 8061 9119)": WHATSAPP,
    "Contact the Engineering team": CONTACT + "#quote",
    "Request fender sizing / quotation": CONTACT + "#quote",
    "Book a service visit": CONTACT + "#service",
    "Request a demo": CONTACT + "#quote",
    "Work with us": CONTACT,
    "Talk to our team": CONTACT,
    "Partner with us": CONTACT + "#quote",
    "Contact our team": CONTACT + "#quote",
    "View all commodities": "/commodities/",
}

# ---------------------------------------------------------------- groups
GROUPS = [
    {
        "slug": "fertilizer-phosphate",
        "name": "Fertilizer & Phosphate Value Chain",
        "hero3d": True,
        "lead": "We supply the full phosphate and nitrogen chain, from raw sulphur and rock phosphate, through sulphuric and phosphoric acid, to finished MAP, DAP, urea and ammonium sulphate. Knowing every stage of fertilizer manufacture lets us match inputs to process and finished grades to crop.",
        "who": "Supplying fertilizer producers, acid plants, blenders and distributors across South and Southeast Asia.",
        "serves": "Fertilizer producers, blenders and distributors",
        "hub_products": "Sulphur, Sulphuric Acid, Phosphoric Acid, Rock Phosphate, MAP, DAP, Urea, Ammonium Sulphate",
        "products": [
            ("sulphur", "Sulphur", "Granular, prilled and lump sulphur, 99.5% min. purity"),
            ("sulphuric-acid", "Sulphuric Acid", "H₂SO₄ 98% min. for phosphate and ammonium sulphate production"),
            ("phosphoric-acid", "Phosphoric Acid", "Merchant-grade 52–54% P₂O₅ and technical 85% H₃PO₄"),
            ("rock-phosphate", "Rock Phosphate", "28–31% P₂O₅, BPL 62–68%"),
            ("map", "Mono Ammonium Phosphate (MAP)", "11-52-0 granular and 12-61-0 water-soluble"),
            ("dap", "Diammonium Phosphate (DAP)", "18-46-0 hard, free-flowing granules"),
            ("urea", "Urea", "46% N, prilled and granular"),
            ("ammonium-sulphate", "Ammonium Sulphate", "21% N, 24% S, crystalline and granular"),
        ],
    },
    {
        "slug": "metallurgical-reductants",
        "name": "Metallurgical Reductants",
        "hero3d": True,
        "lead": "Carbon reductants and carbon raisers for smelters and steelmakers: semi coke for RKEF nickel pig iron, metallurgical coke for blast furnaces, and calcined and graphitized pet coke for foundries and steel.",
        "who": "Reductants for NPI, ferroalloy, steel and foundry producers, with a focus on Indonesia’s nickel smelting sector.",
        "serves": "NPI, ferroalloy, steel and foundry producers",
        "hub_products": "Semi Coke, Metallurgical Coke, Calcined Pet Coke, Graphite Pet Coke",
        "products": [
            ("semi-coke", "Semi Coke", "Fixed carbon 80–88%, for RKEF nickel smelting"),
            ("metallurgical-coke", "Metallurgical Coke", "Fixed carbon 85–92%, for blast furnaces and foundries"),
            ("calcined-pet-coke", "Calcined Pet Coke", "Fixed carbon 98.5% min., carbon raiser and anode grade"),
            ("graphite-pet-coke", "Graphite Pet Coke", "Graphitized, low-sulphur carbon raiser for steel and ductile iron"),
        ],
    },
    {
        "slug": "industrial-chemicals",
        "name": "Industrial Chemicals",
        "lead": "High-volume base chemicals supplied to international specifications, in bulk, ISO tank and bagged form.",
        "who": "Supplying chemical, glass, detergent, pulp & paper, alumina and water-treatment industries.",
        "serves": "Chemical, glass, detergent, pulp and water-treatment industries",
        "hub_products": "Methanol, Caustic Soda, Soda Ash",
        "products": [
            ("methanol", "Methanol", "IMPCA-grade, 99.85% min. purity"),
            ("caustic-soda", "Caustic Soda", "NaOH flakes, pearls and lye (32% / 48–50%)"),
            ("soda-ash", "Soda Ash", "Na₂CO₃ 99.2% min., dense and light grades"),
        ],
    },
    {
        "slug": "petroleum-oilfield",
        "name": "Petroleum & Oilfield Products",
        "lead": "Refinery products and drilling-fluid minerals for infrastructure, lubricants and oil & gas operations.",
        "who": "Supplying road contractors, waterproofing manufacturers, lubricant blenders and drilling contractors.",
        "serves": "Road contractors, lubricant blenders and drilling contractors",
        "hub_products": "Bitumen, Base Oil, Barite Powder, Bentonite",
        "products": [
            ("bitumen", "Bitumen", "Penetration, viscosity, performance and oxidised grades"),
            ("base-oil", "Base Oil", "Group I / II, SN150 and SN500"),
            ("barite-powder", "Barite Powder", "API 13A drilling grade, SG 4.1–4.2"),
            ("bentonite", "Bentonite", "Sec 9, 10 and 11 grades for drilling and foundry"),
        ],
    },
    {
        "slug": "biomass",
        "name": "Biomass & Renewable Fuels",
        "lead": "Sustainably sourced biomass from Southeast Asian plantations and processors, for energy, panel-board and carbon production.",
        "who": "Supplying biomass power and industrial furnace operators, MDF and pulp mills, and activated carbon producers.",
        "serves": "Biomass energy, panel-board and carbon producers",
        "hub_products": "Wood Chips, Coconut Shell Charcoal",
        "products": [
            ("wood-chips", "Wood Chips", "Eucalyptus, pine and acacia, fuel and fibre grades"),
            ("coconut-shell-charcoal", "Coconut Shell Charcoal", "Fixed carbon 75% min., activated-carbon feedstock"),
        ],
    },
]

GROUP_CTA = "Send your specification, quantity and destination and our team will respond with availability and pricing."
GROUP_CTA_BUTTONS = ["Request a quote", "Request datasheet / SDS"]

# ---------------------------------------------------------------- products
# Each product: slug, group, title, hero (list of paragraphs; first is the lead), sections (ordered),
# related (names). Section dict keys, rendered in this order when present:
#   title, paras[], items[], defs[(term, desc)], sublists[(head, items)], spec[blocks], note
# Spec block: {"title":..., "headers":[...], "rows":[[...], ...]}
DIST = "{} supplier in Southeast Asia: Singapore, Malaysia, Thailand, Vietnam and Indonesia. [Add India / Türkiye / other markets where supplied]"

PRODUCTS = [
    # ---------------- 1.1 Fertilizer & Phosphate
    {
        "slug": "sulphur", "group": "fertilizer-phosphate",
        "title": "Sulphur (Granular / Prills / Lumps)",
        "hero": ["Elemental sulphur in granular, prilled and lump form, produced to international standards for sulphuric acid, fertilizer, refining and industrial users."],
        "sections": [
            {"title": "Forms", "defs": [
                ("Granular sulphur", "Formed from molten refinery sulphur into hard, uniform granules with low dust and good flow. It is the preferred form for long-distance bulk shipment and acid plants."),
                ("Prilled sulphur [and pastilles]", "Formed sulphur with controlled particle size, high purity and low dust, widely used as feedstock for sulphuric acid, fertilizers, chemicals and rubber."),
                ("Lump sulphur", "Crushed solid sulphur from open stockpiles, ready for melting. Lower cost, but irregular and more prone to breakage and dust, which is why the industry favours formed sulphur for cleaner handling."),
            ]},
            {"title": "Applications", "items": [
                "Sulphuric acid production", "Phosphate fertilizer manufacture", "Petroleum refining and petrochemicals",
                "Rubber vulcanisation", "Nickel HPAL leaching (via sulphuric acid)", "Water treatment"]},
            {"title": "Specifications", "spec": [{"rows": [
                ["Purity (S)", "99.5% min."], ["Ash", "0.05% max. [confirm]"], ["Acidity (as H₂SO₄)", "0.01% max. [confirm]"],
                ["Carbon", "0.05% max. [confirm]"], ["Moisture", "0.5% max. (formed) / 2.0% max. (lump) [confirm]"],
                ["Arsenic, selenium, tellurium", "Trace [confirm limits]"],
                # source: "Granular 2–6 mm · lumps [range] [confirm]" — the lump range is unconfirmed, so only the granular size is shown
                ["Size", "Granular 2–6 mm"]]}]},
            {"title": "Packaging", "items": [
                "Bulk, for large-scale users and port facilities with direct offloading",
                "Jumbo bags (1 MT), for reduced dust, safe storage and inland transport"]},
            {"title": "Distribution", "paras": [DIST.format("Sulphur")]},
        ],
        "related": ["Sulphuric Acid", "Phosphoric Acid", "Ammonium Sulphate"],
    },
    {
        "slug": "sulphuric-acid", "group": "fertilizer-phosphate", "title": "Sulphuric Acid",
        "hero": ["High-purity sulphuric acid (H₂SO₄) produced to GB/T 534-2002 and other global quality norms, for phosphate fertilizer, metal leaching and chemical manufacture."],
        "sections": [
            {"title": "Applications", "items": [
                "Phosphoric acid and phosphate fertilizer manufacture", "Ammonium sulphate production", "Nickel HPAL and copper leaching",
                "Petroleum refining (alkylation)", "Battery acid", "Water and wastewater treatment",
                "Chemical intermediates: detergents, dyes, pharmaceuticals"]},
            {"title": "Specifications", "spec": [{"headers": ["Parameter", "Specification", "Typical batch"], "rows": [
                ["Purity (H₂SO₄)", "≥98.0%", "98.58%"], ["Iron (Fe)", "≤0.005%", "0.002%"], ["Arsenic (As)", "≤0.0001%", "0.00005%"],
                ["Mercury (Hg)", "≤0.001%", "0.0003%"], ["Lead (Pb)", "≤0.005%", "0.001%"], ["Transparency", "≥80 mm", "90 mm"],
                ["Chroma", "≤2.0 ml", "2.0 ml"], ["UN number / class", "UN1830 · Class 8", ""]]}]},
            {"title": "Packaging", "items": ["Bulk chemical tanker", "ISO tanks", "IBC (1,000 L)"]},
            {"title": "Distribution", "paras": [DIST.format("Sulphuric Acid")]},
        ],
        "related": ["Sulphur", "Phosphoric Acid", "Rock Phosphate"],
    },
    {
        "slug": "phosphoric-acid", "group": "fertilizer-phosphate", "title": "Phosphoric Acid",
        "hero": ["Phosphoric acid (H₃PO₄) is the key intermediate between rock phosphate and finished fertilizers such as MAP, DAP and TSP. We supply merchant-grade acid for fertilizer producers and purified technical grade for industrial users."],
        "sections": [
            {"title": "Key features", "items": [
                "Merchant-grade (MGA) 52–54% P₂O₅ for fertilizer manufacture", "Technical grade 85% H₃PO₄ for industrial and metal treatment",
                "Consistent impurity profile for stable downstream production", "Shipped in stainless-steel chemical tankers or ISO tanks"]},
            {"title": "Applications", "items": [
                "MAP, DAP, TSP and NPK fertilizer production", "Water-soluble and liquid fertilizers", "Metal surface treatment and rust removal",
                "Detergents, water treatment and phosphate salts", "Food and feed phosphates (food grade only)"]},
            {"title": "Specifications", "spec": [
                {"title": "Merchant-grade acid (MGA), typical values [confirm]", "rows": [
                    ["P₂O₅", "52–54%"], ["Solids", "≤1.0%"], ["Sulphate (SO₄)", "≤4.0%"], ["Fluorine (F)", "≤1.0%"],
                    ["Iron (Fe₂O₃)", "≤1.5%"], ["Aluminium (Al₂O₃)", "≤1.2%"], ["Magnesium (MgO)", "≤1.0%"]]},
                {"title": "Technical grade 85%, typical values [confirm]", "rows": [
                    ["H₃PO₄", "≥85.0%"], ["Chloride (Cl)", "≤0.0005%"], ["Sulphate (SO₄)", "≤0.005%"], ["Iron (Fe)", "≤0.002%"],
                    ["Heavy metals (as Pb)", "≤0.001%"], ["Arsenic (As)", "≤0.0001%"], ["CAS No. / UN", "7664-38-2 · UN1805, Class 8"]]}]},
            {"title": "Packaging", "items": ["Bulk stainless-steel chemical tanker", "ISO tanks", "IBC (1,000 L) and 35 kg drums (technical grade)"]},
            {"title": "Distribution", "paras": [DIST.format("Phosphoric Acid")]},
        ],
        "related": ["Sulphuric Acid", "Rock Phosphate", "MAP", "DAP"],
    },
    {
        "slug": "rock-phosphate", "group": "fertilizer-phosphate", "title": "Rock Phosphate",
        "hero": ["Essential resource for agriculture and industry.",
                 "Rock phosphate is a naturally occurring mineral rich in P₂O₅. Commercial grades contain at least 25% P₂O₅ and are the primary raw material for phosphoric acid, DAP, MAP, TSP, SSP and NPK fertilizers, as well as elemental phosphorus.",
                 "Our rock phosphate comes from high-quality sedimentary deposits with 28–31% P₂O₅ and 62–68% BPL (bone phosphate of lime). Its reactivity (35–40% soluble in 2% citric acid and 55–65% in 2% formic acid) also makes it suitable for direct application on acidic soils."],
        "sections": [
            {"title": "Specifications", "spec": [{"rows": [
                ["P₂O₅", "28–31%"], ["BPL", "62–68%"], ["Solubility in 2% citric acid", "35–40%"], ["Solubility in 2% formic acid", "55–65%"],
                # "Origin: [Country of origin]" and "Form: Soil / [granular]" are unconfirmed in the skeleton, so both rows are left out
                ["Origin", "[Country of origin]"], ["Form", "[Soil / granular]"]]}]},
            {"title": "Packaging", "items": ["[Packaging options, e.g. bulk, 1 MT jumbo bags, 25/50 kg bags, custom labelling]"]},
            {"title": "Distribution", "paras": [DIST.format("Rock Phosphate")]},
        ],
        "related": ["Phosphoric Acid", "MAP", "DAP"],
    },
    {
        "slug": "map", "group": "fertilizer-phosphate", "title": "Mono Ammonium Phosphate (MAP)",
        "hero": ["High-analysis nitrogen and phosphorus fertilizer.",
                 "MAP (NH₄H₂PO₄) supplies readily available nitrogen and phosphorus in a concentrated, water-soluble form. Its high phosphorus content and moderately acidic reaction make it a staple wherever early crop development matters, in both conventional and precision fertilisation programmes."],
        "sections": [
            {"title": "Nutrient benefits", "sublists": [
                ("Phosphorus (P₂O₅)", ["Early root development and seedling establishment", "Flowering and fruit development", "Energy transfer, crop maturity and yield formation"]),
                ("Ammonium nitrogen", ["Early vegetative growth", "Stem and leaf development", "Protein synthesis and balanced nutrient uptake"])]},
            {"title": "Compatibility", "paras": ["MAP can be combined with compatible nitrogen, potassium and micronutrient fertilizers. Avoid direct mixing with strongly alkaline materials, including high-calcium products, unless compatibility has been established."]},
            {"title": "Specifications", "spec": [{"headers": ["Parameter", "11-52-0 granular", "12-61-0 water-soluble"], "rows": [
                ["Total nitrogen (N)", "11% min.", "12% min."], ["Available P₂O₅", "52% min.", "61% min."],
                ["Water-soluble P₂O₅", "[confirm]", "60% min. [confirm]"], ["Moisture", "1.0% max. [confirm]", "0.5% max. [confirm]"],
                ["Water insolubles", "—", "0.1% max. [confirm]"], ["Physical form", "Granules 2–4 mm", "Crystalline powder"],
                ["Reaction", "Moderately acidic", "Moderately acidic"]]}]},
            {"title": "Packaging", "items": ["Bulk", "25 kg and 50 kg PP bags", "1 MT jumbo bags"]},
            {"title": "Distribution", "paras": ["MAP supplier in Southeast Asia: Singapore, Malaysia, Thailand, Vietnam and Indonesia."]},
        ],
        "related": ["DAP", "Urea", "Rock Phosphate"],
    },
    {
        "slug": "dap", "group": "fertilizer-phosphate", "title": "Diammonium Phosphate (DAP)",
        "hero": ["Balanced crop nutrition for strong early growth.",
                 "DAP is the world’s most widely used phosphate fertilizer, with 18% ammoniacal nitrogen and 46% P₂O₅ for early root development, vigorous growth and higher yields.",
                 "Produced by reacting ammonia with phosphoric acid, DAP is a dry granular fertilizer with excellent handling and storage properties, for direct application or as a base for custom NPK blends."],
        "sections": [
            {"title": "Performance in the field", "paras": ["DAP dissolves quickly in soil moisture. Its ammoniacal nitrogen drives early shoot and leaf growth, while phosphorus promotes root expansion and energy transfer. Its initial alkaline reaction (pH > 7.5) can help neutralise acidic soils early in the season; correct placement and timing avoid nitrogen loss through volatilisation."]},
            {"title": "Storage & handling", "items": ["Store cool and dry, away from moisture and direct sunlight", "Compatible with most fertilizers and micronutrients for blending", "Stable in standard storage conditions"]},
            {"title": "Applications", "items": ["Cereals: wheat, maize, rice, barley", "Vegetables: potatoes, onions, tomatoes, carrots", "Fruit orchards: early fertilisation for root establishment", "Blended fertilizers: base input for custom NPK"]},
            {"title": "Specifications", "spec": [{"rows": [
                ["Chemical formula", "(NH₄)₂HPO₄"], ["Nitrogen (N)", "18% min. (ammoniacal)"], ["Available P₂O₅", "46% min."],
                ["Moisture", "2.5% max. [confirm]"], ["Granule size", "2–4 mm, 90% min. [confirm]"], ["Physical form", "Hard, free-flowing granules"]]}]},
            {"title": "Packaging", "items": ["Bulk", "50 kg PP bags", "1 MT jumbo bags"]},
            {"title": "Distribution", "paras": [DIST.format("DAP")]},
        ],
        "related": ["MAP", "Urea", "Rock Phosphate"],
    },
    {
        "slug": "urea", "group": "fertilizer-phosphate", "title": "Urea",
        "hero": ["Powering agricultural productivity with precision nutrition.",
                 "Urea (CO(NH₂)₂) is the world’s most widely used nitrogen fertilizer, delivering 46% nitrogen, the highest of any solid fertilizer, in a concentrated, readily available form. It is non-flammable, water-soluble and compatible with a wide range of fertilizers and micronutrients."],
        "sections": [
            {"title": "Available forms", "defs": [
                ("Prilled urea", "Smaller round particles · quick dissolution · suited to foliar application and fertigation"),
                ("Granular urea", "Larger, harder, uniform particles · resists caking · suited to mechanical spreading and blends")]},
            {"title": "Application & agronomic value",
             "paras": ["Suitable for cereals, fruit, vegetables, rice, corn and oilseeds. Use it as a basal fertilizer, as a top dressing or through fertigation. To limit nitrogen loss in warm, moist, alkaline soils:"],
             "items": ["Incorporate into the soil", "Apply before rainfall or irrigation", "Use urease inhibitors where needed"]},
            {"title": "Applications", "items": ["Agricultural fertilizer", "NPK blending", "Industrial: resins, AdBlue / DEF (technical grade), animal feed"]},
            {"title": "Specifications", "spec": [{"rows": [
                ["Nitrogen", "46.0% min."], ["Biuret", "1.0% max. [confirm]"], ["Moisture", "0.5% max. [confirm]"],
                ["Granule size", "Granular 2–4 mm, 90% min. · prilled 0.85–2.8 mm, 90% min. [confirm]"], ["Free ammonia", "150 ppm max. [confirm]"]]}]},
            {"title": "Packaging", "items": ["Bulk", "50 kg PP bags", "500–1,000 kg jumbo bags", "Custom labelling on request"]},
            {"title": "Distribution", "paras": [DIST.format("Urea")]},
        ],
        "related": ["MAP", "DAP", "Ammonium Sulphate"],
    },
    {
        "slug": "ammonium-sulphate", "group": "fertilizer-phosphate", "title": "Ammonium Sulphate",
        "hero": ["Ammonium sulphate ((NH₄)₂SO₄) is a nitrogen-and-sulphur fertilizer and industrial chemical valued for purity, stability and versatility. It promotes healthy growth, chlorophyll formation and protein synthesis.",
                 "We supply crystalline (fast-dissolving, ideal for fertigation and blending) and granular (free-flowing, ideal for mechanical spreading and storage) forms."],
        "sections": [
            {"title": "Key features", "items": ["Crystalline and granular forms", "21% nitrogen and 24% sulphur, readily available", "Acidifying effect improves nutrient uptake in alkaline soils", "Excellent solubility and compatibility with other fertilizers"]},
            {"title": "Applications", "items": ["Agricultural fertilizer: rice, maize, oilseeds, palm oil, fruit and vegetables", "Soil amendment: improves uptake of P, Fe and Zn in alkaline soils", "Industrial: water treatment, textiles, food acidity regulator, flame retardants"]},
            {"title": "Specifications", "spec": [{"rows": [
                ["Chemical formula", "(NH₄)₂SO₄"], ["Nitrogen", "21.0% min."], ["Sulphur", "24.0% min."],
                ["Moisture", "0.5% max. (granular) / 1.0% max. (crystalline) [confirm]"], ["Free acidity (as H₂SO₄)", "0.05% max. [confirm]"],
                ["Appearance", "White to off-white crystals or granules"], ["CAS No.", "7783-20-2"]]}]},
            {"title": "Packaging", "items": ["25 kg and 50 kg bags", "1 MT jumbo bags", "Bulk"]},
            {"title": "Distribution", "paras": [DIST.format("Ammonium Sulphate")]},
        ],
        "related": ["Urea", "Sulphuric Acid", "Sulphur"],
    },
    # ---------------- 1.2 Metallurgical Reductants
    {
        "slug": "semi-coke", "group": "metallurgical-reductants", "title": "Semi Coke",
        "hero": ["Semi coke (兰炭) is a critical input in nickel ferroalloy production, particularly the Rotary Kiln-Electric Furnace (RKEF) process widely used across Indonesia. Acting as both reducing agent and energy source, it enables efficient conversion of nickel ore into nickel pig iron (NPI) for stainless steel.",
                 "Its cost efficiency, high reactivity and stable performance make semi coke the preferred alternative to metallurgical coke for large-scale smelters."],
        "sections": [
            {"title": "Key features", "items": ["High fixed carbon content", "Low ash and sulphur", "High reactivity and combustion efficiency", "Lower cost than metallurgical coke"]},
            {"title": "Applications", "items": ["RKEF nickel pig iron (NPI) smelting", "Ferroalloy production: ferrosilicon, silicomanganese", "Calcium carbide manufacture", "Partial replacement for anthracite"]},
            {"title": "Specifications", "spec": [{"rows": [
                ["Fixed carbon", "80–88%"], ["Ash", "8–15%"], ["Volatile matter", "5–10%"], ["Sulphur", "≤0.5%"], ["Moisture", "≤12% [confirm]"], ["Size", "10–30 mm / 30–80 mm"]]}]},
            {"title": "Packaging", "items": ["Bulk vessel", "1 MT jumbo bags [confirm]"]},
            {"title": "Distribution", "paras": [DIST.format("Semi Coke")]},
        ],
        "related": ["Metallurgical Coke", "Calcined Pet Coke"],
    },
    {
        "slug": "metallurgical-coke", "group": "metallurgical-reductants", "title": "Metallurgical Coke",
        "hero": ["Metallurgical coke is produced by high-temperature carbonisation of coking coal. In blast-furnace ironmaking it acts as fuel, reductant and structural support, keeping the furnace permeable for gas flow. Its strength, low impurities and high carbon content are essential for stable, efficient steel production."],
        "sections": [
            {"title": "Key features", "items": ["High mechanical strength and stability", "High fixed carbon content", "Low moisture, ash and volatile matter", "Excellent permeability for blast-furnace efficiency"]},
            {"title": "Applications", "items": ["Blast-furnace ironmaking", "Foundries and cupola furnaces", "Ferroalloy manufacturing"]},
            {"title": "Specifications", "spec": [{"rows": [
                ["Fixed carbon", "85–92%"], ["Ash", "8–12%"], ["Volatile matter", "≤2%"], ["Sulphur", "≤0.7%"], ["CSR / CRI", "[if applicable]"], ["Size", "[e.g. 30–80 mm] [confirm]"]]}]},
            {"title": "Packaging", "items": ["Bulk vessel", "1 MT jumbo bags [confirm]"]},
            {"title": "Distribution", "paras": [DIST.format("Metallurgical Coke")]},
        ],
        "related": ["Semi Coke", "Calcined Pet Coke"],
    },
    {
        "slug": "calcined-pet-coke", "group": "metallurgical-reductants", "title": "Calcined Pet Coke",
        "hero": ["Calcined petroleum coke (CPC) is green pet coke heated to around 1,200–1,350°C to drive off moisture and volatiles, leaving a high-purity, electrically conductive carbon. It is the main carbon source for aluminium anodes and a widely used carbon raiser in steel and foundry melting."],
        "sections": [
            {"title": "Key features", "items": ["Fixed carbon 98.5% min.", "Low ash and volatile matter", "Sulphur grades from low to standard", "Sized to customer requirements"]},
            {"title": "Applications", "items": ["Carbon raiser for steel and foundry melting", "Prebaked anodes for aluminium smelting", "Titanium dioxide production", "Graphite electrodes and carbon products"]},
            {"title": "Specifications", "spec": [{"rows": [
                ["Fixed carbon", "≥98.5%"], ["Sulphur", "≤0.5% / ≤1.0% / ≤3.0% (by grade) [confirm]"], ["Volatile matter", "≤0.5%"], ["Ash", "≤0.5%"],
                ["Moisture", "≤0.5%"], ["Real density", "≥2.04 g/cm³"], ["Size", "0–1 mm, 1–5 mm, 3–8 mm or to order"]]}]},
            {"title": "Packaging", "items": ["25 kg bags", "1 MT jumbo bags", "Containerised or bulk"]},
            {"title": "Distribution", "paras": [DIST.format("Calcined Pet Coke")]},
        ],
        "related": ["Graphite Pet Coke", "Metallurgical Coke"],
    },
    {
        "slug": "graphite-pet-coke", "group": "metallurgical-reductants", "title": "Graphite Pet Coke",
        "hero": ["Graphitized petroleum coke (GPC) is calcined pet coke treated at around 2,800–3,000°C, converting its carbon into a graphite structure. With very low sulphur and nitrogen, it dissolves quickly in molten metal and is the preferred carbon raiser for ductile iron and high-grade steel."],
        "sections": [
            {"title": "Key features", "items": ["Fixed carbon 98.5–99% min.", "Ultra-low sulphur and nitrogen", "Fast absorption and high recovery rate", "Reduces slag and gas defects in castings"]},
            {"title": "Applications", "items": ["Carbon raiser for ductile and grey iron foundries", "Electric arc and induction furnace steelmaking", "Brake pads and friction materials"]},
            {"title": "Specifications", "spec": [{"rows": [
                ["Fixed carbon", "≥98.5%"], ["Sulphur", "≤0.05%"], ["Nitrogen", "≤300 ppm"], ["Ash", "≤0.5%"], ["Volatile matter", "≤0.5%"], ["Moisture", "≤0.5%"], ["Size", "0.2–1 mm, 1–5 mm or to order"]]}]},
            {"title": "Packaging", "items": ["25 kg bags", "1 MT jumbo bags"]},
            {"title": "Distribution", "paras": [DIST.format("Graphite Pet Coke")]},
        ],
        "related": ["Calcined Pet Coke", "Semi Coke"],
    },
    # ---------------- 1.3 Industrial Chemicals
    {
        "slug": "methanol", "group": "industrial-chemicals", "title": "Methanol",
        "hero": ["Methanol (CH₃OH) is one of the world’s most traded chemicals. It is a building block for formaldehyde, acetic acid and olefins, a fuel and fuel additive, and a fast-growing low-carbon marine fuel.",
                 "We supply IMPCA-grade methanol in bulk and ISO tanks, inspected at load port by independent surveyors."],
        "sections": [
            {"title": "Key features", "items": ["Purity 99.85% wt min., meeting the IMPCA reference specification", "Also available to ASTM D1152 / US Federal O-M-232 Grade AA on request", "Independent load-port inspection (SGS / Intertek / BV)", "Bulk parcels and ISO-tank shipments"]},
            {"title": "Applications", "items": ["Formaldehyde and resins (MDF, plywood adhesives)", "Acetic acid, MTBE and methylamines", "Methanol-to-olefins (MTO)", "Biodiesel production (transesterification)", "Marine fuel and fuel blending", "Solvents, antifreeze and wastewater denitrification"]},
            {"title": "Specifications", "spec": [
                {"title": "IMPCA reference specification", "headers": ["Parameter", "Specification", "Test method"], "rows": [
                    ["Purity (on dry basis)", "≥99.85% wt", "IMPCA 001"], ["Appearance", "Clear, free of suspended matter", "IMPCA 003"],
                    ["Colour", "≤5 Pt-Co", "ASTM D1209"], ["Density at 20°C", "0.791–0.793 kg/L", "ASTM D4052"], ["Water", "≤0.10% wt", "ASTM E1064"],
                    ["Acetone", "≤30 mg/kg", "IMPCA 001"], ["Ethanol", "≤50 mg/kg", "IMPCA 001"], ["Acidity (as acetic acid)", "≤30 mg/kg", "ASTM D1613"],
                    ["Permanganate time at 15°C", "≥60 minutes", "ASTM D1363"], ["Distillation range at 760 mmHg", "≤1.0°C, to include 64.6°C ± 0.1°C", "ASTM D1078"],
                    ["Carbonisable substances", "≤30 Pt-Co", "ASTM E346"], ["Hydrocarbons", "Pass", "ASTM D1722"], ["Chloride (as Cl⁻)", "≤0.5 mg/kg", "IMPCA 002"],
                    ["Sulphur", "≤0.5 mg/kg", "ASTM D5453"], ["Total iron", "≤0.1 mg/kg", "ASTM E394"], ["Non-volatile matter", "≤8 mg/L", "ASTM D1353"]]},
                {"title": "Product data", "rows": [
                    ["Chemical formula", "CH₃OH"], ["CAS No.", "67-56-1"], ["UN number / class", "UN1230 · Class 3 (6.1 subsidiary) · PG II"],
                    ["Boiling point", "64.7°C"], ["Flash point", "11°C (closed cup)"],
                    ["Safety", "Highly flammable and toxic if swallowed, inhaled or absorbed through skin; store in sealed, earthed tanks away from ignition sources; use PPE"]]}]},
            {"title": "Packaging", "items": ["Bulk chemical tanker", "ISO tanks (approx. 20 MT)", "IBC (approx. 800 kg) and 160 kg steel drums"]},
            {"title": "Distribution", "paras": [DIST.format("Methanol")]},
        ],
        "related": ["Caustic Soda", "Soda Ash", "Base Oil"],
    },
    {
        "slug": "caustic-soda", "group": "industrial-chemicals", "title": "Caustic Soda",
        "hero": ["Caustic soda (sodium hydroxide, NaOH) is one of the most essential industrial chemicals: a strong alkali for chemical synthesis, neutralisation and pH control.",
                 "We supply membrane-grade flakes, pearls and liquid lye, quality-tested for consistent reactivity in alumina refining, chemical processing, pulp and paper, textiles, water treatment and soap manufacture."],
        "sections": [
            {"title": "Key features", "items": ["Membrane-process grade, NaOH 99% min. (solid)", "Flakes, pearls (prills) and liquid lye 32% / 48–50%", "Low chloride and iron for sensitive processes", "Highly reactive and hygroscopic, so supplied in moisture-proof packaging"]},
            {"title": "Applications", "items": ["Alumina refining (Bayer process)", "Chemical manufacture: solvents, plastics, dyes", "Pulp & paper: pulping and bleaching", "Soap and detergent production", "Textiles: mercerisation of cotton", "Water treatment: pH regulation", "Biodiesel and petroleum refining"]},
            {"title": "Specifications", "spec": [
                {"headers": ["Parameter", "Flakes / pearls 99%", "Liquid lye 48–50%", "Liquid lye 32%"], "rows": [
                    ["NaOH", "≥99.0%", "≥48.0%", "≥32.0%"], ["Sodium carbonate (Na₂CO₃)", "≤0.5%", "≤0.2%", "≤0.1%"],
                    ["Sodium chloride (NaCl)", "≤0.03%", "≤0.02%", "≤0.01%"], ["Iron (as Fe₂O₃)", "≤0.005%", "≤0.002%", "≤0.001%"],
                    ["Sodium chlorate (NaClO₃)", "≤0.005%", "≤0.002%", "≤0.001%"],
                    ["Appearance", "White flakes or pearls", "Clear to slightly turbid liquid", "Clear to slightly turbid liquid"]]},
                {"title": "Product data", "rows": [
                    ["Chemical formula", "NaOH"], ["CAS No.", "1310-73-2"], ["Standard", "GB/T 209-2018 (or equivalent) [confirm]"],
                    ["UN number / class", "Solid UN1823 · liquid UN1824 · Class 8 · PG II"], ["Melting point", "318°C (solid)"],
                    ["Safety", "Corrosive: causes severe skin burns and eye damage; reacts exothermically with water and acids; store sealed and dry; use full PPE"]]}]},
            {"title": "Packaging", "items": ["25 kg PP woven bags with PE liner", "1 MT jumbo bags", "ISO tanks and bulk chemical tanker (liquid lye)"]},
            {"title": "Distribution", "paras": [DIST.format("Caustic Soda")]},
        ],
        "related": ["Soda Ash", "Methanol", "Sulphuric Acid"],
    },
    {
        "slug": "soda-ash", "group": "industrial-chemicals", "title": "Soda Ash",
        "hero": ["Sodium carbonate (Na₂CO₃), or soda ash, is a versatile alkali used in glass, detergents, chemicals and water treatment.",
                 "We supply dense and light grades of [synthetic (Solvay / Hou process) / natural (trona)] soda ash, as an odourless white granulate or powder with consistent quality across batches."],
        "sections": [
            {"title": "Key features", "items": ["Na₂CO₃ 99.2% min.", "Dense grade for glass and bulk handling; light grade for detergents and chemicals", "Low chloride and iron", "Not classified as dangerous goods for transport"]},
            {"title": "Applications", "items": ["Flat, container and specialty glass", "Soaps, detergents and cleaning products", "Sodium silicate, sodium bicarbonate and other chemicals", "Water treatment: pH adjustment and softening", "Mining and flue-gas desulphurisation"]},
            {"title": "Specifications", "spec": [
                {"headers": ["Parameter", "Dense", "Light"], "rows": [
                    ["Na₂CO₃ (dry basis)", "≥99.2%", "≥99.2%"], ["Sodium chloride (NaCl)", "≤0.70%", "≤0.70%"], ["Iron (Fe)", "≤0.0035%", "≤0.0035%"],
                    ["Sulphate (SO₄)", "≤0.03%", "≤0.03%"], ["Water insolubles", "≤0.03%", "≤0.03%"], ["Loss on heating (moisture)", "≤0.8%", "≤0.8%"],
                    ["Bulk density", "0.90–1.10 g/cm³", "0.50–0.65 g/cm³"], ["Particle size", "≥70% retained on 180 µm", "Fine powder"]]},
                {"title": "Product data", "rows": [
                    ["Chemical formula", "Na₂CO₃"], ["CAS No.", "497-19-8"], ["Standard", "GB/T 210.1-2004 Class I (or equivalent) [confirm]"],
                    ["pH (1% solution)", "≈11.5"], ["Transport", "Not regulated as dangerous goods"],
                    ["Safety", "Causes serious eye irritation; avoid dust inhalation; store dry and ventilated; use PPE"]]}]},
            {"title": "Packaging", "items": ["25 kg and 50 kg PP woven bags with PE liner", "1 MT jumbo bags", "Bulk"]},
            {"title": "Distribution", "paras": [DIST.format("Soda Ash")]},
        ],
        "related": ["Caustic Soda", "Methanol"],
    },
    # ---------------- 1.4 Petroleum & Oilfield
    {
        "slug": "bitumen", "group": "petroleum-oilfield", "title": "Bitumen",
        "hero": ["Penetration, viscosity, performance and oxidised bitumen grades for road construction, roofing, waterproofing and industrial use, packed to suit every route to site."],
        "sections": [
            {"title": "Penetration grade",
             "paras": ["Common grades are 40/50, 60/70 and 80/100, classified by the depth (in tenths of a millimetre) that a standard needle penetrates the sample. 40/50 suits warmer climates, 60/70 moderate climates and 80/100 cooler regions."],
             "spec": [{"rows": [["Penetration at 25°C", "By grade"], ["Softening point", "42–52°C typical"], ["Ductility at 25°C", "100 cm min."]]}]},
            {"title": "Viscosity grade (VG)", "defs": [
                ("VG-10", "800–1,200 poise · spraying and surface dressing in cold climates"), ("VG-20", "1,600–2,400 poise · paving in cold regions"),
                ("VG-30", "2,400–3,600 poise · paving in moderate climates"), ("VG-40", "3,200–4,800 poise · heavy-traffic roads in hot climates")]},
            {"title": "Performance grade (PG)", "defs": [
                ("PG 64-10", "Up to 64°C / down to –10°C · moderate temperatures and traffic"),
                ("PG 76-22", "Up to 76°C / down to –22°C · heavy traffic; resists rutting and thermal cracking")]},
            {"title": "Oxidised bitumen (blown asphalt)",
             "paras": ["Produced by blowing air through penetration-grade bitumen at high temperature, for roofing felts, damp-proofing, pipe coatings and adhesives."],
             "defs": [("85/25", "Softening point ≈85°C · penetration ≈25 dmm"), ("90/40", "Softening point ≈90°C · penetration ≈40 dmm")]},
            {"title": "Packaging", "items": ["New steel drums, 150 to 200 kg", "Polymer jumbo bags, 1 MT", "Kraft paper bags, 25 to 50 kg", "PolyCube containers, 1 to 1.5 MT", "Bulk in heated tankers for large projects"]},
            {"title": "Distribution", "paras": [DIST.format("Bitumen")]},
        ],
        "related": ["Base Oil", "Barite Powder"],
    },
    {
        "slug": "base-oil", "group": "petroleum-oilfield", "title": "Base Oil (Group I/II, SN150, SN500)",
        "hero": ["Base oils are the main component of finished lubricants, making up 70–90% of most engine, gear and industrial oils. We supply solvent-refined Group I and hydro-processed Group II base oils in the two most widely blended viscosity grades, SN150 and SN500."],
        "sections": [
            {"title": "Key features", "items": ["Group I (solvent-refined) and Group II (hydro-processed)", "SN150 light and SN500 heavy neutral grades", "Consistent viscosity index and low pour point", "Bulk, flexitank and drum supply"]},
            {"title": "Applications", "items": ["Automotive engine oils", "Hydraulic and industrial oils", "Gear and transmission oils", "Metalworking fluids and greases", "Process and rubber oils"]},
            {"title": "Specifications", "spec": [{"headers": ["Parameter", "SN150", "SN500", "Method"], "rows": [
                ["Kinematic viscosity at 40°C", "28–34 cSt", "90–110 cSt", "ASTM D445"], ["Kinematic viscosity at 100°C", "5.0–5.5 cSt", "10.5–12.0 cSt", "ASTM D445"],
                ["Viscosity index", "≥95", "≥90", "ASTM D2270"], ["Flash point (COC)", "≥200°C", "≥230°C", "ASTM D92"], ["Pour point", "≤ –6°C", "≤ –6°C", "ASTM D97"],
                ["Colour", "≤1.0 ASTM", "≤2.0 ASTM", "ASTM D1500"], ["Density at 15°C", "0.86–0.87 kg/L", "0.88–0.89 kg/L", "ASTM D4052"],
                ["Total acid number", "≤0.05 mg KOH/g", "≤0.05 mg KOH/g", "ASTM D974"]]}],
             "note": "Group II grades: saturates ≥90% and sulphur ≤0.03%, with viscosity index 80–120 (API 1509). [confirm values per supplier]"},
            {"title": "Packaging", "items": ["Bulk tanker", "Flexitanks (approx. 20–22 MT per 20 ft container)", "180–200 L steel drums", "IBC"]},
            {"title": "Distribution", "paras": [DIST.format("Base Oil")]},
        ],
        "related": ["Bitumen", "Methanol"],
    },
    {
        "slug": "barite-powder", "group": "petroleum-oilfield", "title": "Barite Powder",
        "hero": ["Barite (barium sulphate, BaSO₄) is a high-density, chemically inert mineral essential to drilling, chemical and manufacturing applications.",
                 "We supply powder and lump forms processed for consistent particle size and purity, in API 13A drilling grade for oil & gas and in specialised grades for chemical and filler applications."],
        "sections": [
            {"title": "Key features", "items": ["Specific gravity 4.1–4.5 for weighting drilling fluids", "API 13A drilling grade (SG 4.1 / 4.2) available", "Chemically inert and resistant to most acids", "Customisable grades and particle sizes"]},
            {"title": "Applications", "items": ["Weighting agent in oil & gas drilling fluids", "Filler in paints, rubber and plastics", "Radiation shielding", "Barium chemicals"]},
            {"title": "Specifications", "spec": [{"rows": [
                ["BaSO₄", "90–97%"], ["Specific gravity", "4.1–4.5 g/cm³"], ["Particle size (powder)", "97% min. passing 75 µm (API 13A) / customisable"],
                ["Lump size", "10–50 mm (customisable)"], ["Water-soluble alkaline earth metals (as Ca)", "≤250 mg/kg (API 13A)"], ["Moisture", "≤0.5%"],
                ["Appearance", "White to light grey powder / lumps"], ["CAS No.", "7727-43-7"]]}]},
            {"title": "Packaging", "items": ["50 kg bags", "1 MT / 1.5 MT jumbo bags", "Bulk (lumps)"]},
            {"title": "Distribution", "paras": [DIST.format("Barite Powder")]},
        ],
        "related": ["Bentonite", "Bitumen"],
    },
    {
        "slug": "bentonite", "group": "petroleum-oilfield", "title": "Bentonite",
        "hero": ["Bentonite is a natural clay composed mainly of montmorillonite, known for exceptional water absorption and swelling. We supply powder and lump forms, grades Sec 9, 10 and 11, for drilling, foundry and environmental applications."],
        "sections": [
            {"title": "Key features", "items": ["Superior swelling and water retention", "High cation exchange capacity", "Non-toxic and environmentally friendly", "Grades Sec 9, 10 and 11"]},
            {"title": "Applications", "items": ["Drilling muds for oil, gas and water wells", "Foundry sands and casting", "Iron ore pelletising", "Civil engineering: piling and diaphragm walls", "Sealants, cat litter and environmental containment"]},
            {"title": "Specifications", "spec": [{"rows": [
                ["Composition", "SiO₂ 55–65% · Al₂O₃ 15–20% · Na₂O 2–5%"], ["Swelling index", "24–30 mL/2 g"], ["Moisture", "≤10%"], ["pH", "8–10"],
                ["Bulk density (powder)", "0.7–1.0 g/cm³"], ["Particle size (powder)", "2–250 µm"], ["CAS No.", "1302-78-9"]]}]},
            {"title": "Packaging", "items": ["25 kg and 50 kg bags", "1 MT jumbo bags", "Bulk (lumps)"]},
            {"title": "Distribution", "paras": [DIST.format("Bentonite")]},
        ],
        "related": ["Barite Powder"],
    },
    # ---------------- 1.5 Biomass
    {
        "slug": "wood-chips", "group": "biomass", "title": "Wood Chips (Eucalyptus / Pine / Acacia)",
        "hero": ["Wood chips from plantation-grown eucalyptus, acacia and pine in Indonesia and the wider region, supplied as fibre grade for pulp and panel-board mills and as fuel grade for biomass boilers and industrial furnaces."],
        "sections": [
            {"title": "Key features", "items": ["Plantation-grown, traceable origins", "Fibre and fuel grades", "Screened for uniform size and low bark", "Phytosanitary certification and fumigation where required"]},
            {"title": "Applications", "items": ["Pulp and paper", "MDF and particleboard", "Biomass power and CHP plants", "Industrial furnace and boiler fuel"]},
            {"title": "Specifications", "spec": [{"headers": ["Parameter", "Fibre grade", "Fuel grade"], "rows": [
                ["Species", "Eucalyptus / acacia / pine", "Mixed plantation hardwood"],
                ["Chip size", "[e.g. 15–35 mm length, 2–8 mm thick]", "[e.g. ≤50 mm]"], ["Moisture", "[e.g. 35–45%]", "[e.g. ≤35%]"],
                ["Bark content", "[e.g. ≤1%]", "[e.g. ≤5%]"], ["Ash", "—", "[e.g. ≤3%]"], ["Calorific value (as received)", "—", "[e.g. 2,800–3,300 kcal/kg]"]]}]},
            {"title": "Packaging", "items": ["Bulk, in dedicated wood chip carriers", "Containerised (40 ft HC) for smaller lots"]},
            {"title": "Distribution", "paras": [DIST.format("Wood Chips")]},
        ],
        "related": ["Coconut Shell Charcoal"],
    },
    {
        "slug": "coconut-shell-charcoal", "group": "biomass", "title": "Coconut Shell Charcoal",
        "hero": ["Charcoal carbonised from coconut shells: a renewable, high-carbon, low-ash material and the preferred feedstock for coconut-shell activated carbon."],
        "sections": [
            {"title": "Key features", "items": ["High fixed carbon and low ash", "Hard, dense structure suited to activation", "Renewable by-product of coconut processing", "Lump, granular and crushed sizes"]},
            {"title": "Applications", "items": ["Activated carbon production", "Metallurgical and chemical reductant", "Industrial and household fuel", "Briquettes and shisha charcoal"]},
            {"title": "Specifications", "spec": [{"rows": [
                ["Fixed carbon", "≥75% [confirm]"], ["Ash", "≤3% [confirm]"], ["Volatile matter", "≤15% [confirm]"], ["Moisture", "≤10% [confirm]"],
                ["Size", "[e.g. 3–8 mm granules / 5–30 mm lumps]"]]}]},
            {"title": "Packaging", "items": ["25–50 kg PP bags", "1 MT jumbo bags", "Containerised"]},
            {"title": "Distribution", "paras": [DIST.format("Coconut Shell Charcoal")]},
        ],
        "related": ["Wood Chips"],
    },
]

# Names used in "Related products" lines that differ from page titles
RELATED_ALIASES = {
    "MAP": "map", "DAP": "dap", "Base Oil": "base-oil", "Sulphur": "sulphur", "Wood Chips": "wood-chips",
}

ENQUIRY = {
    "h2": "Let’s connect",
    "p": "For technical datasheets, pricing or samples, message our supply team on WhatsApp.",
    "buttons": ["Request datasheet / SDS", "Request pricing", "Request a sample"],
    "partner_h": "Your partner in quality",
    "partner_p": "We source high-grade materials, apply strict quality control and inspect every shipment. Our dedicated support team ensures reliability and a seamless post-sale partnership.",
}

# ---------------------------------------------------------------- commodities hub
COMMODITIES_HUB = {
    "eyebrow": "Commodities Supply Division",
    "h1": "Specialist supply across five industrial value chains",
    "lead": "Five product groups where we have direct producer relationships and technical depth.",   # one sentence (client, 2026-11-10)
    "buttons": ["Request a quote", "Talk to the supply desk"],
    "how": [
        ["Origins", "[e.g. China, Middle East, Indonesia, India; confirm]"],
        ["Terms", "FOB, CFR, CIF and DAP; bulk, containerised and ISO-tank shipments"],
        ["Documentation", "CoA, SGS / BV / Intertek inspection, certificate of origin, SDS, phytosanitary certificates where required"],
        ["Payment", "Documentary L/C and TT, subject to counterparty onboarding"],
    ],
    "cta_h": "Innovating Supply, Empowering Growth.",
    "cta_p": "Our supply team is accessible 24/7. Send your specification, quantity, destination port and Incoterm and we will come back with availability and pricing.",
    "cta_buttons": ["Request a quote", "Request datasheet / SDS"],
}

# ---------------------------------------------------------------- engineering
# ---------------------------------------------------------------- about
ABOUT = {
    "eyebrow": "About HexaHessman",
    "h1": "From Precision Engineering to Global Markets",
    "lead": "Founded 2007. Reimagined 2024.",
    "story": [
        "Established in 2007, HexaHessman was founded on a legacy of engineering expertise and precision-driven solutions. Over time our vision expanded, turning specialised technical knowledge into a platform for the supply of fertilizers, reductants, chemicals and energy products.",
        "Our leaders have always looked beyond the immediate horizon, combining engineering rigour with entrepreneurial insight. In 2024 HexaHessman unified these legacy strengths with fresh ambition, establishing itself as a reliable partner for structured supply and engineering solutions.",
        "Today we are guided by operational discipline, strategic insight and people-first values, connecting trusted partners worldwide and delivering what our clients need with precision and dependability.",
    ],
    # the voyage timeline: (year, title, text, photo). 2007 and 2024 are the client's facts; the years between and their
    # words are PLACEHOLDER copy written for the layout (user, 2026-11-05: "find filler words") — confirm with the client.
    "timeline_h": "Our voyage",
    "timeline_lead": "The course so far, from a single engineering drawing to a group trading across nine markets.",
    "timeline": [
        ("2007", "The first drawing", "HexaHessman is founded on a legacy of precision engineering: specifying, sourcing and commissioning equipment for marine and industrial clients who needed it done right the first time.", "/assets/about/tl-coupling.jpg"),
        ("2011", "First principals", "European manufacturers of couplings, fenders and mooring systems appoint us to represent them in Southeast Asia, and our engineers train alongside theirs at the factory.", "/assets/about/tl-team.jpg"),
        ("2015", "Into commodities", "The trading desk opens with sulphur and fertilizers, moving bulk cargo from producer to plant with the same discipline we bring to engineering. Every cargo is inspected, documented and delivered on schedule.", "/assets/about/tl-sulphur.jpg"),
        ("2018", "A regional network", "Offices open across Indonesia, Malaysia and Thailand, putting our people on site at the refineries, plants and terminals we serve.", "/assets/about/tl-refinery.jpg"),
        ("2021", "Cleaner fuels", "As shipping turns to LNG, methanol and ammonia, we commission our principals’ dry-disconnect and emergency-release couplings on board, side by side with the crews.", "/assets/about/tl-commissioning.jpg"),
        ("2023", "Sharing what we know", "Technical seminars for terminal operators and shipowners on safe transfer, PERC control units and bunkering practice, across the region.", "/assets/about/tl-perc-talk.jpg"),
        ("2024", "Group reimagined", "HexaHessman Pte. Ltd. is incorporated in Singapore (UEN 202419032H), uniting commodities, engineering and investment under HexaHessman Global Group.", "/assets/about/tl-sulphur-talk.jpg"),
        ("Today", "Eight offices, nine markets", "From Singapore to London, our people keep cargo moving and equipment running for clients across Asia, the Middle East and Europe, in our own colours.", "/assets/about/tl-bags.jpg"),
    ],
    "group_h": "HexaHessman Global Group",
    "group_p": "HexaHessman Global Group (HHGG) is the holding company overseeing operating entities across multiple countries, delivering diversified solutions across commodities, engineering and strategic investments. Its investment arm, HexaHessman Asset Management (HHAM), identifies and manages high-value opportunities for long-term value creation.",
    "specialise": [
        ("Commodities Supply", "Five specialist product groups: fertilizer & phosphate, metallurgical reductants, industrial chemicals, petroleum & oilfield products and biomass.", "/commodities/"),
        ("Engineering Solutions", "Fendering, mooring, fluid transfer and gas detection from world-leading principals, with project management and after-sales support.", "/engineering/"),
        # "Local presence, regional reach" removed: the two divisions only (client, 2026-11-10)
    ],
    "values": ["Operational discipline", "Strategic insight", "People-first", "Integrity, excellence, performance"],
    "reach_h": "Global reach, local impact",
    "reach_p": "Headquartered in Singapore, HexaHessman has a presence in Malaysia, Thailand, Indonesia, India, South Korea, Türkiye, the United Kingdom and the United States, delivering solutions tailored to regional markets while drawing on global expertise.",
    "markets": ["Singapore", "Malaysia", "Thailand", "Indonesia", "India", "South Korea", "Türkiye", "United Kingdom", "United States"],
    # the people, in the order of the customer's team sheet (left to right, top to bottom; cutout portraits in
    # /assets/team/cut/<slug>.webp): (name, role, entity, photo slug, office, blurb). The blurbs are placeholder
    # copy written by us for the customer to replace. Yani Lee's JWHexaHessman office is Indonesia (confirmed by the user).
    "team_h": "Leveraging global expertise for strategic advantage",   # one colour, like Our story (user, 2026-11-06)
    "team_lead": "A growing team across eight offices, from Singapore to London. Press through the line to meet some of them.",   # no head count: the team is bigger (user)
    "team": [
        ("Adam Yeoh", "Business Development Manager", "HexaHessman Singapore", "adam-yeoh", "sg",
         "Adam develops new supply relationships across Southeast Asia, matching buyers with the right product, origin and shipping terms."),
        ("Aizat Amin", "Business Development Manager", "HexaHessman Singapore", "aizat-amin", "sg",
         "Aizat looks after client accounts from first enquiry to delivery, keeping specifications, documents and timelines on track."),
        ("Parin Udornwong", "Supply Chain Manager", "HexaHessman Thailand", "parin-udornwong", "th",
         "Parin runs logistics for the Thai market, from port handling and inland transport to warehousing and customs."),
        ("Ensari Inci", "Trade Specialist", "HexaHessman Türkiye", "ensari-inci", "tr",
         "Ensari sources fertilizer and industrial chemicals from Turkish and Black Sea producers for the group’s buyers."),
        ("Dr. Sang Joon Park", "Trade Specialist", "HexaHessman South Korea", "sang-joon-park", "kr",
         "Dr. Park brings a technical background to the Korean trade desk, advising steel and chemical customers on product grades."),
        ("Raja Sekhar", "Trade Specialist", "HexaHessman India", "raja-sekhar", "in",
         "Raja covers the Indian subcontinent, linking fertilizer and reductant demand with reliable origins."),
        ("Hasareeyan Amin", "Regional Business Director", "HexaHessman Thailand", "hasareeyan-amin", "th",   # replaces Thanin Amin (client, 2026-11-12)
         "Hasareeyan leads the Thai business, building long-term supply agreements with agricultural and industrial buyers."),
        ("Cemal Koc", "Regional Business Director", "HexaHessman Türkiye", "cemal-koc", "tr",
         "Cemal heads the Ankara office, developing trade between Türkiye, the Middle East and Southeast Asia."),
        ("Yos Rizaldy", "Regional Business Director", "PT Hexa Hessman Indonesia", "yos-rizaldy", "id",
         "Yos leads commodity supply in Indonesia, serving the nickel, steel and fertilizer sectors."),
        ("Krishna Hartono", "Regional Business Director", "PT Hexa Hessman Indonesia", "krishna-hartono", "id",
         "Krishna leads the engineering business in Indonesia, representing the group’s principals to ports, terminals and shipyards."),
        ("Larbi Neron", "Regional Business Director", "HexaHessman United Kingdom", "larbi-neron", "uk",
         "Larbi runs the London office, connecting European producers and financiers with the group’s Asian markets."),
        ("Eddie Jeong", "Regional Business Director", "HexaHessman South Korea", "eddie-jeong", "kr",
         "Eddie leads the Korean business, working with the country’s steel, chemical and shipbuilding industries."),
        ("Yani Lee", "President Director", "JWHexaHessman", "yani-lee", "id",
         "Yani heads JWHexaHessman, the group’s joint venture in Indonesia, overseeing operations and local partnerships."),
        ("Ibrahim Koc", "Principal Advisor", "HexaHessman Türkiye", "ibrahim-koc", "tr",
         "Ibrahim advises the group on trade and government relations in Türkiye, drawing on decades in the region’s industry."),
        ("Anuar Ebrahim", "Director of Trading", "HexaHessman Malaysia", "anuar-ebrahim", "my",
         "Anuar directs trading from Kuala Lumpur, managing pricing, risk and counterparties across the product groups."),
        ("Azmi Mahmood", "Principal Advisor", "HexaHessman Singapore", "azmi-mahmood", "sg",
         "Azmi advises the leadership on strategy, governance and new markets."),
        ("Connie Tai", "Chief Financial Officer", "HexaHessman Singapore", "connie-tai", "sg",
         "Connie oversees the group’s finances, trade financing and reporting across all of its offices."),
        ("Hafriz Razif", "Chief Executive Officer", "HexaHessman Singapore", "hafriz-razif", "sg",
         "Hafriz leads HexaHessman Global Group, setting its direction across commodities, engineering and investment."),
    ],
    # where each office is, for the globe beside the line: id -> (city, country, lat, lon)
    "office_pins": {"sg": ("Singapore", "Singapore", 1.3005, 103.859), "id": ("Jakarta", "Indonesia", -6.29, 106.80),
                    "kr": ("Seoul", "South Korea", 37.505, 127.11), "my": ("Kuala Lumpur", "Malaysia", 3.158, 101.72),
                    "th": ("Samut Prakan", "Thailand", 13.56, 100.80), "in": ("Bengaluru", "India", 12.955, 77.59),
                    "uk": ("London", "United Kingdom", 51.527, -0.089), "tr": ("Ankara", "Türkiye", 39.91, 32.80)},
    "cta_eyebrow": "Work with us",
    "cta_h": "Let’s build something that lasts.",
    "cta_p": "From Singapore to London, our people are ready to talk about your next supply contract or engineering project.",
    "cta_buttons": ["Talk to our team", "Partner with us"],
}

# ---------------------------------------------------------------- engineering
ENGINEERING_HUB = {
    "eyebrow": "Engineering Solutions Division",
    "h1": "Engineered for excellence, supported for life",
    "lead": "With deep consultancy expertise in project identification, strategic development and stakeholder engagement, we deliver marine and energy systems from world-leading principals and stand behind them with local after-sales service across Southeast Asia.",
    "buttons": ["Discuss a project", "Request service / maintenance"],
    "principals": [
        ("shibata", "ShibataFenderTeam", "Cone, element, cylindrical, pneumatic, foam and roller fender systems."),
        ("manntek", "MannTek", "Dry cryogenic couplings, breakaway couplings and emergency release systems for LNG, ammonia, methanol and hydrogen."),
        ("straatman", "Straatman", "Quick release mooring hooks, ship-to-shore links, smart bollards and berthing aid systems."),
        ("raythink", "Raythink", "AR, optical and AI-driven gas-leak detection and real-time hazard monitoring."),
    ],
    "territories": "Territories: MannTek in Singapore, Malaysia, Indonesia, Vietnam and Thailand · Straatman in Indonesia and Thailand",
    # the word-by-word statement between the logo carousel and the principals
    "statement": "With deep consultancy expertise in project identification, strategic development and stakeholder engagement, we deliver marine and energy systems from world-leading principals and stand behind them with local after-sales service across Southeast Asia.",
    # key products shown on each principal's stop in the hub scroll (from the principal pages and the company profile PDF)
    "principal_tags": {
        "shibata": ["SPC cone fenders", "Element fenders", "Cylindrical fenders", "Pneumatic fenders", "Foam fenders"],
        "manntek": ["Dry cryogenic couplings", "Breakaway couplings", "Powered emergency release (PERC)", "Vessel separation device"],
        "straatman": ["Quick release mooring hooks", "Ship-to-shore link", "Smart bollard", "Berthing aid system"],
        "raythink": ["Optical gas imaging", "Explosion-proof gas imaging PTZ", "Handheld thermal cameras", "Online thermal monitoring"],
    },
    # company profile PDF p.17 "Engineering Components"
    "components_list": [
        ("Pumping systems", ["Submerged fuel pumps", "Offshore pumping systems", "Retractable submerged pumps", "Cryogenic pumps", "Reciprocating pumps"]),
        ("Couplings", ["Dry break couplings", "Dry cryogenic couplings", "Dry disconnect couplings", "Safety breakaway couplings"]),
        ("Static & automatic filters", ["Micronic self-cleaning filters", "Skid-mounted filtering systems", "Self-cleaning lamellar filters"]),
        ("Fire & gas detection", ["Multi-gas instruments", "Ultrasonic gas detectors", "Optical area monitoring systems", "Multi-flame detectors"]),
        ("Valves", ["Ball, gate, globe, check and control valves", "Pressure safety and relief valves", "Actuated valves (electric, pneumatic, hydraulic)"]),
        ("Seals", ["O-rings, packing, mechanical and lip seals", "Diaphragm, bellows and labyrinth seals", "Tank roof tension seals", "Thermoplastic seals (PEEK, PFA, Kalrez)"]),
        ("Gaskets", ["Spiral wound, RTJ and kammprofile gaskets", "Jacketed and corrugated metal gaskets", "Graphite, PTFE and rubber gaskets", "Insulating kits, manway and handhole gaskets"]),
    ],
    # S3: the skeleton leaves the components line as a placeholder; the home-page H8 "Marine & Energy
    # Solutions" line is the only skeleton copy that describes the components range, so it is reused here.
    "components": "Fit-for-purpose systems for offshore, shipping and energy infrastructure: fenders, mooring hooks, breakaway couplings and fluid transfer technologies.",
    "services": [
        ("Project Management & EPC Support", "End-to-end support from feasibility to handover, covering planning, design, procurement, production oversight and execution, with a single point of accountability."),
        # ("Storage Tank Solutions" removed with its menu item, client 2026-11-06)
        ("After-sales service", "Repairs, maintenance, spares and standby services, with a face-to-face response within 48 hours."),
    ],
    "sectors": ["LNG and alternative-fuel bunkering (ammonia, methanol, hydrogen)", "Oil, gas and chemical terminals", "Ports, harbours and container terminals",
                "FPSO, FSRU and offshore structures", "Dredging and marine construction", "Navy and government berths"],
    "lifecycle": [("Identify", "Project identification and feasibility"), ("Design", "Specification, engineering and principal selection"),
                  ("Procure", "Sourcing, logistics and production oversight"), ("Execute", "Installation, testing and commissioning"),
                  ("Support", "Training, maintenance and spares for life")],
    "cta_h": "Engineered for excellence, supported for life.",
    "cta_buttons": ["Contact the Engineering team"],   # one button on every engineering page (client, 2026-11-10)
}

PRINCIPALS = [
    {
        "slug": "shibata", "name": "ShibataFenderTeam", "h1": "ShibataFenderTeam", "eyebrow": "Principal · Fender systems",
        "logo": "/assets/engineering/logo-shibata.svg?v=3", "hero_img": "/assets/engineering/shibata/hero.jpg?v=2",   # SPC cone fenders along a general cargo terminal (from SFT's page on hexahessman.com); a photo hero like MannTek's (user, 2026-11-06)
        "hero": ["HexaHessman is an official Southeast Asia representative of ShibataFenderTeam (SFT), a global leader in the design, engineering, manufacture and supply of high-performance fender systems. For more than five decades SFT has safeguarded ports, harbours, terminals and offshore structures around the world."],
        "sections": [
            # one block per fender, photo and words side by side, alternating (as on hexahessman.com/shibata-fenders-team).
            # media: "layers" = the orange panels arrive one by one (tools/drawings/orange_layers.py), "loop" = a floating clip
            {"title": "SPC Cone Fender", "drawing": "/assets/engineering/shibata/spc-cone-drawing.webp", "media": {"appear": "/assets/engineering/shibata/spc-cone-appear"}, "side": "left",   # Seedance: bare quay → fenders fitted one by one
             "paras": ["The SPC Cone Fender is an efficient rubber fender used in many applications. Its conical body and fully rubber-embedded mounting flanges give a refined geometry with outstanding performance."],
             "lists": [("Characteristics", ["Exceptional energy absorption to reaction force ratio (E/R)", "Outstanding energy absorption per fender weight", "High shear stability",
                                            "No loss of performance up to 10° approach angle", "Sophisticated, optimised fender geometry", "Optional overload stopper"]),
                       ("Applications", ["Container & bulk terminals", "Oil & gas terminals", "General cargo terminals", "Cruise terminals", "Ferry & RoRo terminals", "Navy"])]},
            {"title": "FE Element Fenders", "drawing": "/assets/engineering/shibata/fe-element-drawing.webp", "media": {"image": "/assets/engineering/shibata/fe-element.jpg"}, "side": "right",
             "paras": ["Fully moulded rubber legs with embedded mounting plates. Based on V Fenders but with separate legs, the FE Element Fender gives high layout flexibility behind steel panels or where mounting space is limited."],
             "lists": [("Characteristics", ["Good energy absorption to reaction force ratio (E/R)", "High energy absorption per fender weight", "Modular, compact design with a small footprint",
                                            "Vertical and horizontal mounting, typically in pairs", "Pile fender designs may use single units", "Easy maintenance & replacement"]),
                       ("Applications", ["Container & bulk terminals", "General cargo terminals", "RoRo terminals", "Navy", "Barges"])]},
            {"title": "Cylindrical Fender", "drawing": "/assets/engineering/shibata/cylindrical-drawing.webp", "media": {"image": "/assets/engineering/shibata/cylindrical.jpg"}, "side": "left",
             "paras": ["The first rubber fender type produced with a defined performance. It installs simply with chains, bars, ropes or ladder brackets, and its reaction force and energy rise in proportion to deflection for softer berthing.",
                       "Extruded or wrapped depending on size: outside diameters up to 2,700 mm, inside diameters 50–1,300 mm, lengths up to 20 m. Supplied with the matching fixings: chains, brackets, support bar or ladder brackets."]},
            {"title": "Pneumatic Fender", "drawing": "/assets/engineering/shibata/pneumatic-drawing.webp", "media": {"loop": "/assets/engineering/shibata/pneumatic-float"}, "side": "right",
             "paras": ["An abrasion-resistant rubber fender filled with high-pressure air. It deflates easily for simple, low-cost relocation and re-commissioning elsewhere.",
                       "Diameters from 300 mm to 4,500 mm and lengths from 500 mm to 9,000 mm, plus special sizes."],
             "lists": [("Characteristics", ["Proportional increase of energy and reaction", "Low hull pressure", "Economical", "Deflates for use in other locations or storage on deck", "Built to ISO 17357-1:2014"]),
                       ("Applications", ["Ports with extreme tidal variations", "Ship-to-ship lightering", "Oil & gas (typically FSRU)", "Temporary berthing"])]},
            # Parallel Motion Fenders and Hydropneumatic Fender removed (client, 2026-11-10)
            {"title": "Ocean Guard Foam Fender", "drawing": "/assets/engineering/shibata/ocean-guard-drawing.webp", "media": {"loop": "/assets/engineering/shibata/ocean-guard-float"}, "side": "left",
             "paras": ["A heat-laminated, 100% closed-cell foam core under a thick, nylon-reinforced polyurethane skin with embedded end fittings: high energy absorption, hull-conforming, non-marking and low maintenance.",
                       "Diameters from 500 mm to 4,500 mm and lengths from 800 mm to 10,600 mm, in several foam grades and special shapes, with two- or four-point mounting."],
             "lists": [("Characteristics", ["Proportional increase of energy and reaction", "Extremely robust", "No performance loss and unsinkable even if damaged", "Small skin damage repairable on site", "Low hull pressure, non-marking skin"]),
                       ("Applications", ["Navy berths and cruise terminals", "Ship-to-ship operations", "Ship-to-shore operations", "Oil & gas terminals"])]},
            {"title": "Roller / Wheel Fender", "drawing": "/assets/engineering/shibata/roller-drawing.webp", "media": {"loop": "/assets/engineering/shibata/roller-float"}, "side": "right",   # Seedance: the pontoon floats, the tyres turn on their shafts (client, 2026-11-10)
             "paras": ["An energy-absorbing elastomer unit on a single rotating shaft with maintenance-free stainless and composite bearings."],
             "lists": [("Installed as", ["Stacked double or triple to cover tidal heights", "Side by side to guide vessels through narrow passages", "At an angle to suit the hull's flare"]),
                       ("Applications", ["Entrances to locks, dry docks and other narrow or exposed areas"])]},
        ],
        "cta_p": "Backed by local support for sizing, supply, installation and after-sales service.",
        "cta_buttons": ["Contact the Engineering team"],
    },
    {
        "slug": "manntek", "name": "MannTek", "h1": "MannTek Solutions", "eyebrow": "Principal · Marine & energy transfer",
        "logo": "/assets/engineering/logo-manntek.svg?v=3",
        "hero_img": "/assets/engineering/manntek-hero.jpg?v=2",   # upscaled 4K (client, 2026-11-10). MannTek couplings at a methanol bunkering (from the principal's page on hexahessman.com)
        "subhead": "Dry cryogenic couplings, breakaway couplings and emergency release systems for LNG, methanol, hydrogen and ammonia.",   # the principal's own logo, centred over the intro like their site
        # The skeleton offers "[exclusive / official]"; "official" is used, matching the other principals.
        "hero": ["HexaHessman is the official representative of MannTek Solutions in Southeast Asia, delivering tailored solutions with comprehensive after-sales service, including repairs and maintenance."],
        "coverage": "Coverage: Singapore · Malaysia · Indonesia · Vietnam · Thailand",
        "sections": [
            # four photo tiles in a row (assets/engineering/fuel-<id>.jpg), rising and dropping in alternately; each opens a drop-down
            {"title": "Solutions by fuel", "fuels": [
                ("LNG", "lng", "Dry cryogenic couplings, breakaway couplings and powered emergency release for LNG bunkering and truck, rail and ship transfer, down to –196°C.", "https://www.manntek.se/"),
                ("Methanol", "methanol", "Dry disconnect and safety breakaway couplings for methanol bunkering, keeping a toxic, flammable product contained at connection and disconnection.", "https://www.manntek.se/"),
                ("Hydrogen", "hydrogen", "Couplings and breakaways for liquid hydrogen transfer, built for –253°C and the tightest tolerances in cryogenic handling.", "https://www.manntek.se/"),
                ("Ammonia", "ammonia", "Dry disconnect couplings, breakaways and emergency release couplings for ammonia transfer, with spill-free connection for a toxic product.", "https://www.manntek.se/"),
            ]},
            # the whole ship-to-ship transfer line, labels popping out one by one; the left-hand tags share one column, clear of the edge (client, 2026-11-10) (label x, y → part x, y, in the image's 1672×941 pixels)
            {"title": "A complete transfer system", "diagram": {"img": "/assets/engineering/manntek-system.webp", "w": 1672, "h": 941, "labels": [
                ("Dry Disconnect Coupling (DDC)", 270, 330, 378, 410), ("Insulation flange", 270, 230, 403, 406), ("Hose tail", 470, 300, 455, 410),
                ("PERC", 560, 520, 552, 414), ("Cryogenic breakaway coupling (CBC)", 270, 560, 510, 412), ("Hose saddle", 640, 650, 760, 470),
                ("Transfer hose", 820, 330, 930, 498), ("PERC activation line", 1040, 280, 995, 522), ("VSD wire", 980, 690, 1060, 603),
                ("Fall arrest", 1190, 770, 1300, 600), ("Vessel Separation Device (VSD)", 1380, 870, 1470, 622), ("PERC control unit", 1330, 320, 1530, 382),
                ("Alternative placement CBC", 1430, 170, 1600, 428), ("Ship manifold", 1540, 520, 1645, 432)]}},
            {"title": "Dry Cryogenic Couplings (DCC)", "media": {"video": "/assets/engineering/spin/dcc"}, "side": "left",
             "paras": ["MannTek QCDC couplings load and unload cryogenic liquefied gases (LNG, nitrogen, oxygen, argon, ethylene) down to −196°C, connecting quickly and safely with minimal product loss and no re-tightening during cool-down. Built to ISO 21593 and ISO TS 18683."],
             "spec": [{"rows": [["Size", "1\" to 8\""], ["Material", "Stainless steel"], ["Seals", "PTFE"]]}]},
            {"title": "Cryogenic Breakaway Couplings (CBC)", "media": {"video": "/assets/engineering/spin/cbc"}, "side": "right",
             "paras": ["Designed as the weakest link of the hose line or loading arm, CBCs prevent spillage and damage from drive-away or pull-away incidents. Available in breaking-pin and cable-release versions."],
             "spec": [{"rows": [["Size", "1\"–8\" breaking pin · 2\"–8\" cable release"], ["Material", "Stainless steel"], ["Seals", "PTFE"], ["Working pressure", "25 bar"]]}]},
            {"title": "Powered Emergency Release Coupling (PERC)", "media": {"video": "/assets/engineering/spin/perc"}, "side": "left",
             # PERC and VSD as charts, like the couplings above (client, 2026-11-12); the same words as before, row by row
             "paras": ["The highest safety level, with three ways to release."],
             "spec": [{"headers": ["Function", "Description"], "rows": [
                 ["Release 1", "By ESD signal"], ["Release 2", "By manual override"], ["Release 3", "By reverting to a passive breaking pin"],
                 ["In a blackout", "Falls back to a passive breakaway coupling, protecting the manifold in any situation"]]}]},
            {"title": "Vessel Separation Device (VSD)", "media": {"image": "/assets/engineering/manntek-vsd.webp"}, "side": "right",
             "spec": [{"headers": ["Function", "Description"], "rows": [
                 ["System", "Three wires with pendants of different lengths"], ["First wire", "Alarm on vessel movement"],
                 ["Second wire", "Initiates ESD 1, stopping the pumps and closing the ESD valves"], ["Third wire", "Initiates ESD 2, activating the PERC"]]}]},
            {"title": "PERC control unit", "media": {"image": "/assets/engineering/manntek-pcu.webp"}, "side": "left", "defs": [
                ("PLC version", "Monitors the whole transfer operation and ensures every step and periodic test is carried out"),
                ("SIL2 version", "Assessed by DNV and certified to SIL2 under IEC 61511 and IEC 61508")]},
            {"title": "Videos", "videos": [("MannTek (QCDC) Design 2.0: DGC", "kSuzHS0QLxM"), ("Safety Breakaway Couplings", "ruqJJZ1Y6Qk"),
                                           ("Connections: Liquid Hydrogen", "xwyUOaJOzM8"), ("MannTek LNG / cryogenic couplings", "VYfQASPLDGM")]},
        ],
        "cta_h": "After-sales",
        "cta_p": "Repairs, maintenance and spares across the region, with a face-to-face response within 48 hours.",
        "cta_buttons": ["Contact the Engineering team"],
    },
    {
        "slug": "straatman", "name": "Straatman", "h1": "Straatman Mooring Systems", "eyebrow": "Principal · Mooring & berthing",
        "logo": "/assets/engineering/logo-straatman.svg?v=3",
        "hero_img": "/assets/engineering/straatman/hero.jpg?v=2",   # transfer lines and an LNG carrier at dusk (from Straatman's page on hexahessman.com)
        # The skeleton offers "[more than 50 years / since 1902]"; "more than 50 years" is used.
        "hero": ["HexaHessman is an official representative of Straatman in Southeast Asia. With more than 50 years of maritime experience, Straatman is an established manufacturer of mooring, berthing and dredging equipment. In 2024 it reorganised into Straatman Mooring Systems and Straatman Dredging & Construction."],
        "coverage": "Coverage: Indonesia · Thailand",
        # laid out like MannTek (user, 2026-11-06): the four products in one line, the videos straight under them, then one
        # section per product; the hook's layout drawing, redrawn in code (tools/drawings/qrh.py), faint behind its words
        "sections": [
            {"title": "Products and solutions", "tile_dir": "/assets/engineering/straatman/tile-", "fuels": [
                ("Quick Release Hooks", "qrh", "Hooks that release a mooring line in seconds, even under full load, for tankers, FSRUs, FPSOs and bulk carriers.", "#quick-release-mooring-hooks"),
                ("Ship-to-Shore Link", "ssl", "The SafeCom link that shuts ship and shore down together the moment either side detects a problem during a transfer.", "#ship-to-shore-link-ssl"),
                ("Smart Bollard", "bollard", "A bollard that measures the load on every mooring line in real time and logs it, so nobody has to assume the worst.", "#smart-bollard"),
                ("Berthing Aid Systems", "bas", "Speed, distance and angle of an approaching vessel, measured and shown on large displays for a safe berthing.", "#berthing-aid-system-bas"),
            ]},
            {"title": "Videos", "videos": [("Quick release mooring hooks with electric release", "9ibN4cYJUJo"), ("Smart Bollard explained", "HUaGkqjp3RY"),
                                           ("Straatman company film", "gaFLosB-x_o"), ("Quick release hooks with solar power, Port of Rotterdam", "n8tIGkDgjsc")]},
            {"title": "Quick Release Mooring Hooks", "drawing": "/assets/engineering/straatman/qrh-drawing.svg?v=1", "drawing_w": "92%", "media": {"image": "/assets/engineering/straatman/qrh-terminal.jpg"}, "side": "left",
             "paras": ["Quick release mooring hooks are a key safety feature for oil and gas tankers, FSRUs, FPSOs and other vessels: they can be released quickly and easily, even under load, when the situation at the berth demands it.",
                       "Straatman hooks are built for oil, gas, chemical, iron ore, coal and grain terminals, with options for electric-hydraulic release, load monitoring, remote control and rope keepers."],
             "items": ["Single, double, triple and quadruple hook assemblies", "FPSO / FLNG and offshore hooks (FPSO and FSRU)", "Quick release towing hooks", "Strainstall and AMTS hooks and spares"]},
            {"title": "Ship-to-Shore Link (SSL)", "drawing": "/assets/engineering/straatman/ssl-drawing.svg?v=1", "drawing_w": "84%", "media": {"image": "/assets/engineering/straatman/ssl.jpg?v=2"}, "side": "right",   # drawings behind every product like the hook (client, 2026-11-10; tools/drawings/straatman_more.py)
             "paras": ["During LNG, oil and chemical transfers the ship-shore link guards against fire, explosion and spills. Its job is to shut down ship and shore at the same moment whenever the Safety Instrumented System on either side detects an issue.",
                       "Straatman’s SafeCom Ship-to-Shore Link is built to each client’s needs, in a range of sizes and configurations, with standby services for extra reliability."]},
            {"title": "Smart Bollard", "drawing": "/assets/engineering/straatman/bollard-drawing.svg?v=1", "drawing_w": "84%", "media": {"image": "/assets/engineering/straatman/smart-bollard.jpg"}, "side": "left",
             "paras": ["Without load data, ports have to assume maximum mooring loads. In high waves, strong currents and gusts an overloaded line can part and a ship can break away from the quay.",
                       "Smart Bollards measure the load on each mooring line in real time and log it, giving the port and the terminal a clear picture of the mooring forces and the warning they need."]},
            {"title": "Berthing Aid System (BAS)", "drawing": "/assets/engineering/straatman/bas-drawing.svg?v=1", "drawing_w": "92%", "media": {"image": "/assets/engineering/straatman/bas.jpg"}, "side": "right",
             "paras": ["Lasers on the quay measure an approaching vessel’s speed, distance and angle, and large displays show them to the pilot and crew so every berthing stays within safe limits. Available with a carry-on-board system for the mooring master."]},
            # "Full product range" removed (client, 2026-11-10)
        ],
        "cta_buttons": ["Contact the Engineering team"],
    },
    {
        "slug": "raythink", "name": "Raythink", "h1": "Raythink", "eyebrow": "Principal · Gas detection & hazard monitoring",
        "logo": "/assets/engineering/logo-raythink.svg?v=3", "hero_img": "/assets/engineering/raythink-hero.jpg",   # a thermal image of a gas leak at a tank: a photo hero like MannTek (user, 2026-11-06)
        "hero": ["Raythink provides advanced visualisation and monitoring solutions for critical industries, including oil & gas and marine. Building on core expertise in augmented reality (AR), optical systems and AI-driven perception, Raythink supports gas-leak detection and real-time hazard monitoring."],
        "sections": [
            {"title": "Applications", "items": ["Gas-leak detection at terminals, refineries and FSRUs", "Real-time hazard monitoring"]},
        ],
        "cta_buttons": ["Contact the Engineering team"],
    },
]

# ---------------------------------------------------------------- about
# ---------------------------------------------------------------- contact
CONTACT_PAGE = {
    "eyebrow": "Contact",
    "h1": "Navigating with Excellence",
    "lead": "We are pleased to offer our full assistance and address any queries you may have.",
    "commitments": [
        ("Commodities Supply", "Our supply team is accessible 24/7, with real-time market responsiveness and support across all time zones."),
        ("Engineering Solutions", "A face-to-face response within 48 hours for all servicing and maintenance enquiries."),
    ],
    "form_h": "Drop us a line",
    "enquiring": ["Commodities Supply", "Engineering Solutions", "Engineering Components", "Other"],
    "direct": [
        ("All enquiries", None, None, "inquiry@hexahessman.com"),
        ("Commodities Supply", "Adam Yeoh", "Head of Commodity Supply, HexaHessman Singapore", "Adam.Yeoh@HexaHessman.com"),
        ("Engineering Solutions", "Aizat Amin", "Head of Engineering Solutions, HexaHessman Singapore", "Aizat.Amin@HexaHessman.com"),
        ("Engineering Solutions · Indonesia", "Krishna Hartono", "Regional Business Director, PT HexaHessman Indonesia", "Krishna.Hartono@HexaHessman.com"),
    ],
    "offices": [
        ("Singapore", "Headquarters", "39 Arab Street, Singapore 199738 · Warehouse: 10 Buroh Street, West Connect Building, Singapore 627564"),
        ("Indonesia", "PT. HexaHessman Indonesia", "The CEO Building Level 12, Jl. TB Simatupang No. 18 C, Jakarta Selatan 12430"),
        ("South Korea", "HexaHessman Korea", "#619, 87 Ogeum-ro, Songpa-gu, Seoul 05542"),
        ("Malaysia", "HexaHessman Sdn Bhd", "Unit 9-6, Binjai 8 Premium Soho, 2 Lorong Binjai, 50450 Kuala Lumpur"),
        ("Thailand", "HexaHessman Thailand", "118/3 Moo 7, Tambon Bang Sao Thong, Amphoe Bang Sao Thong, Samut Prakan 10570"),
        ("India", "HexaHessman India", "129/1, Lal Bagh Main Road, Bengaluru 560027"),
        ("United Kingdom", "HexaHessman UK", "128 City Road, London EC1V 2NX"),
        ("Türkiye", "HexaHessman Turkey", "Gökçe Apartmanı No: 22/12, Mustafa Kemal Mahallesi, 2124. Cadde, Çankaya, Ankara 06530"),
        ("United States", "HexaHessman US", "730 N Milwaukee Ave, Chicago, IL 60642"),
    ],
    "hours": [("Monday – Friday", "09:00 – 17:00 (SGT)"), ("Saturday – Sunday", "Closed (supply desk 24/7)")],
}

LEGAL = [
    ("privacy", "Privacy Policy"),
    ("terms", "Terms of Use"),
    ("cookies", "Cookie Notice"),
]


# ---------------------------------------------------------------- 2026 business profile (PDF) updates
# Figures, lists and pictures from "HEXAHESSMAN - Business Profile 2026R14 (Ver7)" (pages 7–15), applied over the
# skeleton text above (user, 2026-11-06: "do all products"). Pictures: assets/products/pdf/ (cut-outs keep their
# see-through backgrounds). Where the profile and the skeleton disagree, the profile (newer) wins.
PDF = "/assets/products/pdf/"


def _p(slug):
    return next(p for p in PRODUCTS if p["slug"] == slug)


def _s(p, title):
    return next((s for s in p["sections"] if s.get("title") == title), None)


def _add(p, sec, before="Distribution"):
    i = next((k for k, s in enumerate(p["sections"]) if s.get("title") == before), len(p["sections"]))
    p["sections"].insert(i, sec)


def _apply_profile():
    # Sulphur (p.7): lump vs granular chart with test methods, packaging, industries, terms, quality
    p = _p("sulphur")
    _s(p, "Forms")["imgs"] = {"Granular sulphur": PDF + "sulphur-granular-bags.webp", "Lump sulphur": PDF + "sulphur-lumps.webp"}
    _s(p, "Specifications")["spec"] = [{"headers": ["Property", "Lump sulphur", "Granular sulphur", "Test method"], "rows": [
        ["Physical form", "Lumps & powder", "Granular", "Visual"], ["Appearance", "Bright yellow", "Bright yellow", "Visual"],
        ["Purity, dry basis (wt%)", "99.80% min.", "99.80% min.", "ASTM D-4239"], ["Moisture (wt%)", "0.02% max.", "0.5% max.", "ASTM D-2790"],
        ["Ash (wt%)", "0.015% max.", "0.05% max.", "ASTM D-1509"], ["Organic solid matter (wt%)", "0.01% max.", "0.01% max.", "—"],
        ["Acidity (wt%)", "0.0001% max.", "0.02% max.", "ASTM D-1613"], ["Mechanical impurities", "0.01% max.", "—", "—"],
        ["Hydrocarbons (wt%)", "—", "0.05% max.", "ASTM D-2360"]]}]
    pk = _s(p, "Packaging")
    pk["items"] = ["Loose bulk, for break-bulk or direct vessel loading", "Jumbo bags (FIBC / big bags) and bulk containers", "Palletised bagging, shrink-wrapped"]
    pk["img"] = PDF + "sulphur-bag-stack.webp"
    _add(p, {"title": "How we supply", "paras": ["Recovered from natural-gas purification and crude-oil refining, sulphur is the feedstock for sulphuric acid, phosphate fertilisers and metal leaching. Our supply is built on direct access to end buyers and a network of trading professionals with more than 30 years in the industry. That means reliable execution, consistent quality and competitive terms through compliant channels."]})
    _add(p, {"title": "Industries served", "items": ["Fertilizer producers", "Steel and metallurgy", "Energy and power generation", "Mining and chemical industries"]})
    _add(p, {"title": "Commercial terms", "items": ["Flexible pricing: formula pricing or an Argus-linked index", "Contracting options to suit each buyer"]})
    _add(p, {"title": "Quality assurance", "items": ["Inspection and certification", "Specification compliance", "Sampling and quality-control processes"]})

    # Sulphuric acid (p.7): grades, our own production
    p = _p("sulphuric-acid")
    _s(p, "Specifications")["spec"].append({"title": "Grades", "headers": ["Grade", "Typical purity", "Main application"], "rows": [
        ["Industrial grade", "93–98%", "Fertilizer, mining, chemicals"], ["Battery grade", "35–38%", "Lead-acid batteries"],
        ["Technical grade", "90–98%", "General industrial use"], ["Electronic grade", "99.999%", "Semiconductor industry"],
        ["Food / pharma grade", "Highly purified", "Specialised applications"]]})
    _s(p, "Packaging")["img"] = PDF + "acid-ibc.webp"
    _add(p, {"title": "Our production", "img": PDF + "acid-iso-tanks.webp", "paras": [
        "HexaHessman operates sulphuric acid manufacturing facilities in Vietnam and Laos, close to customers across Southeast Asia, supplying consistent volumes of industrial-grade acid efficiently and competitively.",
        "Integrated production and logistics, strong regional partnerships and export infrastructure support fertiliser, mining and chemical clients with reliable, cost-effective supply."]})

    # Bitumen (p.8): one chart of every grade, applications and strengths
    p = _p("bitumen")
    p["sections"] = [s for s in p["sections"] if s.get("title") not in ("Viscosity grade (VG)", "Performance grade (PG)")]
    i = next(k for k, s in enumerate(p["sections"]) if s.get("title") == "Penetration grade") + 1
    p["sections"].insert(i, {"title": "Grades", "spec": [{"headers": ["Bitumen type", "Grade", "Use case"], "rows": [
        ["Penetration grade", "40/50", "Roads in hot climates"], ["Penetration grade", "60/70", "General road paving"], ["Penetration grade", "80/100", "Roads in cold climates"],
        ["Viscosity grade", "VG-10", "Cold-region roads"], ["Viscosity grade", "VG-20", "Moderate-climate roads"], ["Viscosity grade", "VG-30", "High-traffic roads"], ["Viscosity grade", "VG-40", "Heavy-duty pavements"],
        ["Performance grade", "PG 58-22", "–22°C to 58°C"], ["Performance grade", "PG 64-22", "Highways, flexible pavements"], ["Performance grade", "PG 70-28", "Extreme climates"],
        ["Polymer-modified (PMB)", "PMB 40", "Medium-traffic roads"], ["Polymer-modified (PMB)", "PMB 70", "Expressways, heavy-load areas"],
        ["Cutback bitumen", "RC-70", "Cold-weather applications"], ["Cutback bitumen", "MC-30", "Prime coating, patching"], ["Cutback bitumen", "SC-250", "Dust control, base coat"]]}]})
    _s(p, "Packaging")["img"] = PDF + "bitumen-drums.webp"
    _add(p, {"title": "Applications", "img": PDF + "bitumen-paving.jpg", "items": ["Road construction and highway surfacing", "Airport runways and heavy-duty pavements", "Waterproofing and industrial coatings", "Infrastructure development projects"]}, before="Packaging")
    _add(p, {"title": "Our strengths", "items": ["Reliable supply through strategic refinery partnerships", "Consistent quality to ASTM / EN / JIS standards", "Technical support and formulations for local climate and project conditions"]})

    # Barite (p.10): results by API grade with test methods
    p = _p("barite-powder")
    sp = _s(p, "Specifications")
    sp["spec"][0]["title"] = "General properties"
    sp["spec"].insert(0, {"title": "Typical values by API grade", "headers": ["Parameter", "API grade 4.0", "API grade 4.1", "API grade 4.2", "Test method"], "rows": [
        ["Density", "4.01 g/cc min.", "4.124 g/cc min.", "4.205 g/cc min.", "API 13A / ISO 13500:2009"],
        ["Water-soluble alkaline earth metals (as Ca)", "36 mg/kg", "36 mg/kg", "252 mg/kg", "API 13A / ISO 13500:2009"],
        ["Residue > 75 µm", "1.7% (w/w)", "1.7% (w/w)", "3% (w/w)", "API 13A / ISO 13500:2009"],
        ["Total barium (as BaSO₄)", "83.53% (w/w)", "86.23% (w/w)", "85.1% (w/w)", "API 13K, 18th ed."],
        ["Magnesium (as MgO)", "0.17% (w/w)", "0.18% (w/w)", "0.19% (w/w)", "API 13K"],
        ["Cadmium (Cd)", "Not detected", "Not detected", "Not detected", "API 131 / ISO 10416:2002"],
        ["Mercury (Hg)", "Not detected", "Not detected", "Not detected", "API 131 / ISO 10416:2002"],
        ["Particle size < 6 µm", "18.26%", "18.26%", "30.00%", "Particle size analyser"]]})
    _s(p, "Key features")["img"] = PDF + "barite-rocks.jpg"
    _s(p, "Packaging")["img"] = PDF + "barite-bag.jpg"

    # Semi coke and metallurgical coke (p.11): Shaanxi supply, extra features and uses
    supply = {"title": "How we supply", "paras": ["We supply semi coke and metallurgical coke from Shaanxi, China, to clients in Asia, the Middle East and beyond, with consistent quality, reliable sourcing and every shipment to specification."]}
    p = _p("semi-coke")
    _s(p, "Key features")["items"].append("Environmentally favourable alternative fuel")
    _s(p, "Key features")["img"] = PDF + "semi-coke-lumps.jpg"
    _s(p, "Applications")["items"] += ["Chemical and industrial processes", "Energy generation and heating systems"]
    _add(p, dict(supply))
    p = _p("metallurgical-coke")
    _s(p, "Key features")["items"].append("High calorific value")
    _s(p, "Key features")["img"] = PDF + "met-coke-lumps.webp"
    _s(p, "Applications")["items"] = ["Iron and steel production (blast furnaces)", "Foundries and smelting operations", "Ferroalloy manufacturing", "Heavy industrial fuel applications"]
    for r in _s(p, "Specifications")["spec"][0]["rows"]:
        if r[0] == "Size":
            r[1] = "10–100 mm"
    _add(p, dict(supply))

    # Calcined and graphite petroleum coke (p.12)
    p = _p("calcined-pet-coke")
    _s(p, "Key features")["items"] = ["High carbon purity", "Low volatile matter", "High electrical conductivity", "Excellent thermal stability", "Strong mechanical strength", "Consistent particle distribution"]
    _s(p, "Key features")["img"] = PDF + "cpc-granules.jpg"
    _s(p, "Applications")["items"] = ["Aluminium anode production", "Steel industry", "Graphite electrode manufacturing", "Titanium dioxide production", "Carbon paste manufacturing", "Metallurgical additives"]
    _s(p, "Packaging")["img"] = PDF + "pet-coke-plant.jpg"
    rows = _s(p, "Specifications")["spec"][0]["rows"]
    for r in rows:
        if r[0] == "Sulphur": r[1] = "1.5–3.5%"
        if r[0] == "Size": r[1] = "0–5 mm / 1–5 mm / 1–10 mm"
    rows.insert(next(k for k, r in enumerate(rows) if r[0] == "Real density"), ["Resistivity", "450–550 μΩm"])
    p = _p("graphite-pet-coke")
    _s(p, "Key features")["items"] = ["High fixed carbon content", "Low sulphur and low nitrogen", "Excellent absorption rate", "Stable, consistent quality", "Superior graphitisation level", "Reduced slag generation"]
    _s(p, "Key features")["img"] = PDF + "gpc-pile.jpg"
    _s(p, "Applications")["items"] = ["Steel manufacturing", "Foundry casting", "Ductile iron production", "Friction materials", "Carbon additive for metallurgy", "Ferroalloy production"]
    for r in _s(p, "Specifications")["spec"][0]["rows"]:
        if r[0] == "Nitrogen": r[1] = "≤0.03%"
        if r[0] == "Size": r[1] = "0–1 mm / 1–5 mm / 1–10 mm"

    # pictures only
    _s(_p("caustic-soda"), "Key features")["img"] = PDF + "caustic-flakes.jpg"
    _s(_p("urea"), "Available forms")["imgs"] = {"Granular urea": PDF + "urea-granules.webp"}


_apply_profile()
