"""Catalog seed: names, categories, aliases, a few well-known cultivar names.

This is naming data only. No cultivation recommendations are seeded here; every
variety is stored as 'unverified' until backed by research evidence.
"""

CATEGORIES = [
    ("vegetables", "Vegetables", "காய்கறிகள்"),
    ("leafy-greens", "Leafy greens (Keerai)", "கீரைகள்"),
    ("fruits", "Fruits", "பழங்கள்"),
    ("paddy-cereals", "Paddy and cereals", "நெல் மற்றும் தானியங்கள்"),
    ("millets", "Millets", "சிறுதானியங்கள்"),
    ("pulses", "Pulses", "பயறு வகைகள்"),
    ("oilseeds", "Oilseeds", "எண்ணெய் வித்துகள்"),
    ("spices", "Spices", "மசாலா பயிர்கள்"),
    ("turmeric", "Turmeric", "மஞ்சள்"),
    ("sugarcane", "Sugarcane", "கரும்பு"),
    ("cotton", "Cotton", "பருத்தி"),
    ("flowers", "Flowers", "மலர்கள்"),
    ("coconut", "Coconut", "தென்னை"),
    ("plantation", "Plantation crops", "தோட்டப் பயிர்கள்"),
    ("tubers", "Tubers and root crops", "கிழங்கு வகைகள்"),
    ("other", "Other locally cultivated crops", "பிற பயிர்கள்"),
]

# slug, category, English, Tamil, scientific, crop_type, english aliases, thanglish aliases
CROPS = [
    # Vegetables
    ("tomato", "vegetables", "Tomato", "தக்காளி", "Solanum lycopersicum", "repeated_harvest", "", "thakkali, takkali, thakali"),
    ("brinjal", "vegetables", "Brinjal", "கத்தரிக்காய்", "Solanum melongena", "repeated_harvest", "eggplant, aubergine", "kathirikai, kathirikkai, kathrikai"),
    ("okra", "vegetables", "Lady's Finger (Okra)", "வெண்டைக்காய்", "Abelmoschus esculentus", "repeated_harvest", "ladys finger, lady finger, ladies finger, okra, bhendi", "vendakkai, vendaikai, vendakai"),
    ("small-onion", "vegetables", "Small Onion (Shallot)", "சின்ன வெங்காயம்", "Allium cepa var. aggregatum", "short_duration", "shallot, small onion, sambar onion", "chinna vengayam, chinnavengayam"),
    ("big-onion", "vegetables", "Big Onion", "பெரிய வெங்காயம்", "Allium cepa", "short_duration", "onion, bellary onion", "periya vengayam, vengayam"),
    ("chilli", "vegetables", "Chilli", "மிளகாய்", "Capsicum annuum", "repeated_harvest", "chili, chilly, green chilli, red chilli", "milagai, mulagai, milakai"),
    ("capsicum", "vegetables", "Capsicum (Bell Pepper)", "குடைமிளகாய்", "Capsicum annuum var. grossum", "repeated_harvest", "bell pepper, sweet pepper", "kudai milagai, kudaimilagai"),
    ("pumpkin", "vegetables", "Pumpkin", "பூசணிக்காய்", "Cucurbita moschata", "short_duration", "yellow pumpkin", "poosanikai, poosanikkai, pumpkin kai"),
    ("ash-gourd", "vegetables", "Ash Gourd", "வெள்ளைப் பூசணி", "Benincasa hispida", "short_duration", "winter melon, white pumpkin", "venpoosani, vellai poosani"),
    ("bottle-gourd", "vegetables", "Bottle Gourd", "சுரைக்காய்", "Lagenaria siceraria", "short_duration", "calabash, lauki", "suraikai, suraikkai"),
    ("bitter-gourd", "vegetables", "Bitter Gourd", "பாகற்காய்", "Momordica charantia", "repeated_harvest", "bitter melon, karela", "pavakkai, pagarkai, pavakai"),
    ("ridge-gourd", "vegetables", "Ridge Gourd", "பீர்க்கங்காய்", "Luffa acutangula", "repeated_harvest", "turai, ribbed gourd", "peerkangai, peerkankai"),
    ("snake-gourd", "vegetables", "Snake Gourd", "புடலங்காய்", "Trichosanthes cucumerina", "repeated_harvest", "", "pudalangai, pudalankai"),
    ("cucumber", "vegetables", "Cucumber", "வெள்ளரிக்காய்", "Cucumis sativus", "short_duration", "", "vellarikai, vellarikkai"),
    ("cluster-bean", "vegetables", "Cluster Bean", "கொத்தவரங்காய்", "Cyamopsis tetragonoloba", "short_duration", "guar", "kothavarangai, kothavarai"),
    ("lablab-bean", "vegetables", "Hyacinth Bean (Avarai)", "அவரைக்காய்", "Lablab purpureus", "repeated_harvest", "lablab, broad bean, field bean", "avarakkai, avarai"),
    ("french-bean", "vegetables", "French Bean", "பீன்ஸ்", "Phaseolus vulgaris", "short_duration", "beans, green beans", "beans"),
    ("drumstick", "vegetables", "Drumstick", "முருங்கைக்காய்", "Moringa oleifera", "perennial", "moringa", "murungai, murungaikai, murungakkai"),
    ("carrot", "vegetables", "Carrot", "கேரட்", "Daucus carota", "short_duration", "", "carrot"),
    ("beetroot", "vegetables", "Beetroot", "பீட்ரூட்", "Beta vulgaris", "short_duration", "beet", "beetroot"),
    ("cabbage", "vegetables", "Cabbage", "முட்டைக்கோஸ்", "Brassica oleracea var. capitata", "short_duration", "", "muttaikose, muttai kos, cabbage"),
    ("cauliflower", "vegetables", "Cauliflower", "காலிஃபிளவர்", "Brassica oleracea var. botrytis", "short_duration", "", "cauliflower, kaliflower"),
    ("radish", "vegetables", "Radish", "முள்ளங்கி", "Raphanus sativus", "short_duration", "", "mullangi, mulangi"),
    ("potato", "vegetables", "Potato", "உருளைக்கிழங்கு", "Solanum tuberosum", "short_duration", "", "urulaikizhangu, urulai kilangu, urulaikilangu"),
    # Leafy greens
    ("thandu-keerai", "leafy-greens", "Amaranth (Thandu Keerai)", "தண்டுக்கீரை", "Amaranthus tricolor", "short_duration", "amaranth, amaranthus", "thandu keerai, thandukeerai"),
    ("arai-keerai", "leafy-greens", "Arai Keerai", "அரைக்கீரை", "Amaranthus dubius", "short_duration", "spleen amaranth", "arai keerai, araikeerai"),
    ("spinach", "leafy-greens", "Spinach", "பாலக்கீரை", "Spinacia oleracea", "short_duration", "palak", "palak keerai, palakkeerai"),
    ("coriander", "leafy-greens", "Coriander", "கொத்தமல்லி", "Coriandrum sativum", "short_duration", "cilantro, dhania", "kothamalli, kothamalli keerai"),
    ("fenugreek-leaf", "leafy-greens", "Fenugreek Leaves", "வெந்தயக்கீரை", "Trigonella foenum-graecum", "short_duration", "methi", "vendhaya keerai, venthaya keerai"),
    ("manathakkali", "leafy-greens", "Black Nightshade (Manathakkali)", "மணத்தக்காளி", "Solanum nigrum", "short_duration", "black nightshade", "manathakkali, manathakali"),
    ("ponnanganni", "leafy-greens", "Ponnanganni", "பொன்னாங்கண்ணி", "Alternanthera sessilis", "perennial", "sessile joyweed", "ponnanganni keerai, ponnangkanni"),
    ("mint", "leafy-greens", "Mint", "புதினா", "Mentha spicata", "perennial", "spearmint, pudina", "pudhina, pudina"),
    ("curry-leaf", "leafy-greens", "Curry Leaf", "கறிவேப்பிலை", "Murraya koenigii", "perennial", "curry leaves", "karuveppilai, kariveppilai, kariveppilai"),
    # Fruits
    ("banana", "fruits", "Banana", "வாழை", "Musa spp.", "plantation", "plantain", "vazhai, vaazhai, vazhaipazham, valaipalam"),
    ("mango", "fruits", "Mango", "மா", "Mangifera indica", "perennial", "", "maa, mambazham, mangai, maambazham"),
    ("guava", "fruits", "Guava", "கொய்யா", "Psidium guajava", "perennial", "", "koyya, koyyapazham, goiya"),
    ("papaya", "fruits", "Papaya", "பப்பாளி", "Carica papaya", "perennial", "pawpaw", "pappali, pappaya, papali"),
    ("pomegranate", "fruits", "Pomegranate", "மாதுளை", "Punica granatum", "perennial", "", "mathulai, madhulai"),
    ("sapota", "fruits", "Sapota (Chikoo)", "சப்போட்டா", "Manilkara zapota", "perennial", "chikoo, chiku", "sapota, sappota"),
    ("jackfruit", "fruits", "Jackfruit", "பலா", "Artocarpus heterophyllus", "perennial", "", "pala, palapazham, pallapalam"),
    ("lemon", "fruits", "Lemon", "எலுமிச்சை", "Citrus limon", "perennial", "lime", "elumichai, elumichchai, elumichampazham"),
    ("watermelon", "fruits", "Watermelon", "தர்பூசணி", "Citrullus lanatus", "short_duration", "", "tharbusani, tharpoosani, dharbusani"),
    ("muskmelon", "fruits", "Muskmelon", "முலாம்பழம்", "Cucumis melo", "short_duration", "cantaloupe", "mulampazham, mulam pazham"),
    ("grapes", "fruits", "Grapes", "திராட்சை", "Vitis vinifera", "perennial", "grape", "thiratchai, dratchai, draksha"),
    ("pineapple", "fruits", "Pineapple", "அன்னாசி", "Ananas comosus", "perennial", "", "annasi, annachi, annasipazham"),
    ("amla", "fruits", "Amla (Indian Gooseberry)", "நெல்லிக்காய்", "Phyllanthus emblica", "perennial", "indian gooseberry, gooseberry", "nellikai, nellikkai"),
    ("custard-apple", "fruits", "Custard Apple", "சீத்தாப்பழம்", "Annona squamosa", "perennial", "sugar apple, sitaphal", "seethapazham, sitaphalam"),
    ("tamarind", "fruits", "Tamarind", "புளி", "Tamarindus indica", "perennial", "", "puli, pulia"),
    # Paddy / cereals
    ("paddy", "paddy-cereals", "Paddy (Rice)", "நெல்", "Oryza sativa", "annual", "rice, paddy rice", "nel, arisi, nellu"),
    ("maize", "paddy-cereals", "Maize", "மக்காச்சோளம்", "Zea mays", "annual", "corn", "makkachozham, makka cholam, makkacholam"),
    # Millets
    ("sorghum", "millets", "Sorghum", "சோளம்", "Sorghum bicolor", "annual", "jowar, great millet", "cholam, solam"),
    ("pearl-millet", "millets", "Pearl Millet", "கம்பு", "Pennisetum glaucum", "annual", "bajra", "kambu"),
    ("finger-millet", "millets", "Finger Millet", "கேழ்வரகு", "Eleusine coracana", "annual", "ragi", "keppai, kezhvaragu, ragi, kelvaragu"),
    ("foxtail-millet", "millets", "Foxtail Millet", "தினை", "Setaria italica", "annual", "italian millet", "thinai, tinai"),
    ("little-millet", "millets", "Little Millet", "சாமை", "Panicum sumatrense", "annual", "", "samai, saamai"),
    ("kodo-millet", "millets", "Kodo Millet", "வரகு", "Paspalum scrobiculatum", "annual", "", "varagu, varaku"),
    ("barnyard-millet", "millets", "Barnyard Millet", "குதிரைவாலி", "Echinochloa frumentacea", "annual", "", "kuthiraivali, kudiraivali"),
    ("proso-millet", "millets", "Proso Millet", "பனிவரகு", "Panicum miliaceum", "annual", "common millet", "panivaragu, pani varagu"),
    # Pulses
    ("blackgram", "pulses", "Blackgram", "உளுந்து", "Vigna mungo", "annual", "black gram, urad, urd bean", "ulundhu, ulunthu, ulundu"),
    ("greengram", "pulses", "Greengram", "பச்சைப்பயறு", "Vigna radiata", "annual", "green gram, mung bean, moong", "pachai payaru, pasi payaru, payaru"),
    ("redgram", "pulses", "Redgram (Pigeon Pea)", "துவரை", "Cajanus cajan", "annual", "red gram, pigeon pea, toor, arhar", "thuvarai, thuvaram paruppu, tuvarai"),
    ("horsegram", "pulses", "Horsegram", "கொள்ளு", "Macrotyloma uniflorum", "annual", "horse gram", "kollu"),
    ("cowpea", "pulses", "Cowpea", "தட்டைப்பயறு", "Vigna unguiculata", "annual", "black-eyed pea, lobia", "thattai payaru, karamani, thattaipayaru"),
    ("bengalgram", "pulses", "Bengal Gram (Chickpea)", "கொண்டைக்கடலை", "Cicer arietinum", "annual", "chickpea, chana, gram", "kondakadalai, kondai kadalai"),
    # Oilseeds
    ("groundnut", "oilseeds", "Groundnut", "நிலக்கடலை", "Arachis hypogaea", "annual", "peanut", "nilakadalai, verkadalai, nilakkadalai, manilakottai"),
    ("gingelly", "oilseeds", "Gingelly (Sesame)", "எள்", "Sesamum indicum", "annual", "sesame, til", "ellu, yellu"),
    ("sunflower", "oilseeds", "Sunflower", "சூரியகாந்தி", "Helianthus annuus", "annual", "", "suriyakanthi, sooriyakanthi"),
    ("castor", "oilseeds", "Castor", "ஆமணக்கு", "Ricinus communis", "annual", "", "amanakku, aamanakku"),
    # Spices
    ("black-pepper", "spices", "Black Pepper", "மிளகு", "Piper nigrum", "perennial", "pepper", "milagu, melagu"),
    ("cardamom", "spices", "Cardamom", "ஏலக்காய்", "Elettaria cardamomum", "perennial", "", "elakkai, yelakkai, elaichi"),
    ("clove", "spices", "Clove", "கிராம்பு", "Syzygium aromaticum", "perennial", "", "kirambu, krambu"),
    ("ginger", "spices", "Ginger", "இஞ்சி", "Zingiber officinale", "annual", "", "inji, injee"),
    ("garlic", "spices", "Garlic", "பூண்டு", "Allium sativum", "annual", "", "poondu, poondoo"),
    # Turmeric
    ("turmeric", "turmeric", "Turmeric", "மஞ்சள்", "Curcuma longa", "annual", "haldi", "manjal, manjall"),
    # Sugarcane / cotton
    ("sugarcane", "sugarcane", "Sugarcane", "கரும்பு", "Saccharum officinarum", "annual", "cane", "karumbu, karumpu"),
    ("cotton", "cotton", "Cotton", "பருத்தி", "Gossypium hirsutum", "annual", "", "paruthi, parutthi"),
    # Flowers
    ("jasmine", "flowers", "Jasmine", "மல்லிகை", "Jasminum sambac", "perennial", "", "malligai, malligai, malli"),
    ("marigold", "flowers", "Marigold", "சாமந்தி", "Tagetes erecta", "short_duration", "", "samanthi, saamanthi, chamanthi"),
    ("rose", "flowers", "Rose", "ரோஜா", "Rosa spp.", "perennial", "", "roja, rose"),
    ("crossandra", "flowers", "Crossandra", "கனகாம்பரம்", "Crossandra infundibuliformis", "perennial", "firecracker flower", "kanakambaram, kanagambaram"),
    ("tuberose", "flowers", "Tuberose", "சம்பங்கி", "Polianthes tuberosa", "perennial", "", "sambangi, sampangi"),
    ("chrysanthemum", "flowers", "Chrysanthemum", "செவ்வந்தி", "Chrysanthemum spp.", "perennial", "", "sevanthi, sevvanthi"),
    # Coconut
    ("coconut", "coconut", "Coconut", "தென்னை", "Cocos nucifera", "perennial", "coconut palm", "thennai, thenga, thengai, thennai maram"),
    # Plantation
    ("tea", "plantation", "Tea", "தேயிலை", "Camellia sinensis", "plantation", "", "theyilai, tea"),
    ("coffee", "plantation", "Coffee", "காபி", "Coffea arabica", "plantation", "", "coffee, kapi"),
    ("rubber", "plantation", "Rubber", "ரப்பர்", "Hevea brasiliensis", "plantation", "", "rubber"),
    ("cashew", "plantation", "Cashew", "முந்திரி", "Anacardium occidentale", "plantation", "cashew nut", "munthiri, mundhiri"),
    ("arecanut", "plantation", "Arecanut", "பாக்கு", "Areca catechu", "plantation", "areca nut, betel nut", "paakku, pakku"),
    ("palmyra", "plantation", "Palmyra Palm", "பனை", "Borassus flabellifer", "plantation", "palmyrah, toddy palm", "panai, panai maram"),
    # Tubers
    ("tapioca", "tubers", "Tapioca (Cassava)", "மரவள்ளிக்கிழங்கு", "Manihot esculenta", "annual", "cassava, tapioca", "maravalli kizhangu, kappa, maravalli"),
    ("sweet-potato", "tubers", "Sweet Potato", "சர்க்கரைவள்ளிக்கிழங்கு", "Ipomoea batatas", "short_duration", "", "sarkaravalli kizhangu, valli kizhangu"),
    ("elephant-foot-yam", "tubers", "Elephant Foot Yam", "கருணைக்கிழங்கு", "Amorphophallus paeoniifolius", "annual", "yam, suran", "karunai kizhangu, karunaikilangu"),
    ("colocasia", "tubers", "Colocasia (Taro)", "சேப்பங்கிழங்கு", "Colocasia esculenta", "annual", "taro, arbi", "seppankizhangu, seppankilangu"),
    # Other
    ("mulberry", "other", "Mulberry", "மல்பெரி", "Morus alba", "perennial", "", "malberi, mulberry"),
    ("daincha", "other", "Daincha (Green Manure)", "தக்கைப்பூண்டு", "Sesbania bispinosa", "short_duration", "sesbania, dhaincha", "thakkaipoondu, thaikkai poondu"),
]

# Well-known cultivar NAMES only (catalog data, status unverified): crop slug -> names
VARIETIES = {
    "paddy": ["ADT 43", "ADT 45", "CO 51", "ASD 16", "IR 20", "Ponni", "BPT 5204 (Samba Mahsuri)"],
    "tomato": ["PKM 1", "Arka Vikas", "Arka Rakshak"],
    "brinjal": ["PKM 1", "CO 2"],
    "okra": ["Arka Anamika"],
    "groundnut": ["TMV 7", "VRI 2"],
    "sugarcane": ["Co 86032", "Co 0238", "CoC 671"],
    "cotton": ["MCU 5", "Suvin"],
    "blackgram": ["VBN 4", "VBN 8"],
    "greengram": ["CO 6", "VBN 2"],
    "sorghum": ["CO 30"],
    "pearl-millet": ["CO 7"],
    "finger-millet": ["CO 15"],
    "maize": ["CO 6"],
    "turmeric": ["BSR 2"],
    "banana": ["Poovan", "Nendran", "Robusta", "Grand Naine", "Rasthali", "Karpooravalli"],
    "mango": ["Banganapalli", "Neelam", "Alphonso", "Imam Pasand"],
    "coconut": ["Chowghat Orange Dwarf", "West Coast Tall", "East Coast Tall"],
}

# State-level SAMPLE seasons, deliberately 'unverified' (shown with a warning in the UI).
# (slug, season, sow(start,end), nursery, transplant, harvest, notes)
SAMPLE_SEASONS = [
    ("paddy", "Kuruvai", (6, 7), None, None, (9, 10)),
    ("paddy", "Samba", (8, 9), (8, 8), (9, 9), (1, 2)),
    ("paddy", "Navarai", (12, 1), None, None, (4, 5)),
]
SAMPLE_NOTE = "Representative sample record pending source verification. Not an agronomic recommendation."
