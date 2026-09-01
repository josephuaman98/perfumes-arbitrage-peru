import re

# Catálogo curado y enriquecido con inteligencia de mercado sobre los perfumes más vendidos y virales en Perú y TikTok/Instagram
TRENDING_CATALOG = [
    {
        "name": "Khamrah / Khamrah Qahwa",
        "brand": "Lattafa",
        "category": "Árabe / Nicho Dupe",
        "inspired_by": "Angels' Share by Kilian",
        "demand_level": "Extrema (Top 1 Viral)",
        "trend_score": 99,
        "keywords": ["khamrah", "qahwa"],
        "description": "El perfume árabe más vendido del mundo. Notas dulces de canela, praliné, dátiles y café (Qahwa). Rotación asegurada."
    },
    {
        "name": "Yara / Yara Tous / Yara Moi / Yara Candy",
        "brand": "Lattafa",
        "category": "Árabe Femenino",
        "inspired_by": "Original / Dulce Frutal Gourmand",
        "demand_level": "Extrema (Superventas Femenino)",
        "trend_score": 98,
        "keywords": ["yara", "tous", "moi", "candy"],
        "description": "Fenómeno en TikTok. El aroma a fresas con crema, malvavisco y frutas tropicales más pedido por el público femenino en Perú."
    },
    {
        "name": "Club De Nuit Intense Man (EDT / EDP / Pure Parfum)",
        "brand": "Armaf",
        "category": "Árabe Masculino",
        "inspired_by": "Creed Aventus",
        "demand_level": "Extrema (Rey de Cumplidos)",
        "trend_score": 98,
        "keywords": ["club de nuit", "cdnim", "intense man"],
        "description": "El clon indiscutible de Creed Aventus. Es el perfume masculino más vendido en importación por su increíble proyección y duración."
    },
    {
        "name": "9 PM / 9 AM",
        "brand": "Afnan",
        "category": "Árabe Masculino",
        "inspired_by": "Jean Paul Gaultier Ultra Male",
        "demand_level": "Muy Alta (Viral Juvenil / Fiesta)",
        "trend_score": 96,
        "keywords": ["9pm", "9 pm", "9am", "9 am"],
        "description": "Aroma a manzana dulce, canela y vainilla. El perfume de noche y salidas más solicitado por jóvenes y adultos."
    },
    {
        "name": "Asad / Asad Zanzibar",
        "brand": "Lattafa",
        "category": "Árabe Masculino",
        "inspired_by": "Dior Sauvage Elixir",
        "demand_level": "Muy Alta (Top Masculino)",
        "trend_score": 95,
        "keywords": ["asad", "zanzibar"],
        "description": "Clon fiel de Sauvage Elixir a una fracción de precio. Notas de pimienta negra, tabaco, café y vainilla."
    },
    {
        "name": "Hawas for Him / Hawas Ice / Hawas Black",
        "brand": "Rasasi",
        "category": "Árabe / Acuático Dulce",
        "inspired_by": "Invictus Aqua",
        "demand_level": "Muy Alta (Rey de Verano y Versatilidad)",
        "trend_score": 94,
        "keywords": ["hawas", "hawas ice", "hawas black"],
        "description": "Best seller absoluto para clima cálido y uso diario. Rendimiento bestial de más de 10 horas."
    },
    {
        "name": "Amber Oud (Gold / Tobacco / Ruby / Carbon Edition)",
        "brand": "Al Haramain",
        "category": "Árabe Lujo",
        "inspired_by": "Xerjoff Erba Pura / Tom Ford / Baccarat Rouge",
        "demand_level": "Muy Alta (Calidad Premium)",
        "trend_score": 93,
        "keywords": ["amber oud", "gold edition", "ruby edition"],
        "description": "Presentación de lujo en caja metálica. El Gold Edition (clon de Erba Pura) es el más codiciado en Lima."
    },
    {
        "name": "Fakhar Black / Fakhar Rose / Fakhar Extrait",
        "brand": "Lattafa",
        "category": "Árabe",
        "inspired_by": "YSL Y EDP (Black) / Givenchy L'Interdit (Rose) / 1 Million Parfum (Extrait)",
        "demand_level": "Alta (Diseño Impactante)",
        "trend_score": 91,
        "keywords": ["fakhar"],
        "description": "Frasco icónico plateado/dorado. Fakhar Black es el clon exacto de YSL Y EDP con excelente margen de ganancia."
    },
    {
        "name": "Bade'e Al Oud (Oud for Glory / Honor & Glory / Sublime / Amethyst)",
        "brand": "Lattafa",
        "category": "Árabe Unisex",
        "inspired_by": "Initio Oud for Greatness / Tribeca Bond No 9",
        "demand_level": "Alta (Gourmand / Elegante)",
        "trend_score": 90,
        "keywords": ["bade'e al oud", "oud for glory", "honor & glory", "sublime", "amethyst"],
        "description": "Honor & Glory (aroma a piña brûlée) y Sublime (manzana roja dulce) tienen rotación masiva inmediata."
    },
    {
        "name": "Nebras / Eclair",
        "brand": "Lattafa",
        "category": "Árabe Gourmand",
        "inspired_by": "Billie Eilish No 1 / Bianco Latte",
        "demand_level": "Alta (Tendencia Gourmand)",
        "trend_score": 89,
        "keywords": ["nebras", "eclair"],
        "description": "Eclair es el clon viral del perfume de caramelo y leche condensada Bianco Latte. Agotado rápidamente en todo el mundo."
    },
    {
        "name": "Eros (EDT / EDP / Flame / Energy)",
        "brand": "Versace",
        "category": "Diseñador Masculino",
        "inspired_by": "Original Diseñador",
        "demand_level": "Extrema (Clásico Diseñador)",
        "trend_score": 95,
        "keywords": ["versace eros", "eros flame", "eros energy"],
        "description": "Uno de los perfumes de diseñador con mayor volumen de venta constante en Perú."
    },
    {
        "name": "Light Blue (Women / Men / Intense)",
        "brand": "Dolce & Gabbana",
        "category": "Diseñador Cítrico / Fresco",
        "inspired_by": "Original Diseñador",
        "demand_level": "Muy Alta (Básico de Todo el Año)",
        "trend_score": 92,
        "keywords": ["light blue"],
        "description": "El perfume cítrico por excelencia para mujeres y hombres. Siempre buscado para regalos."
    },
    {
        "name": "Cloud / Cloud 2.0 / Sweet Like Candy",
        "brand": "Ariana Grande",
        "category": "Celebrity / Femenino",
        "inspired_by": "Baccarat Rouge 540 Dupe",
        "demand_level": "Alta (Juvenil Femenino)",
        "trend_score": 88,
        "keywords": ["cloud", "ariana grande"],
        "description": "El perfume de celebridad más vendido de la década. Olor a coco dulce y malvavisco."
    }
]

def find_trending_matches(all_products: list):
    """
    Busca dentro de la lista de productos descargados cuáles corresponden a perfumes en tendencia.
    """
    results = []
    
    for trend in TRENDING_CATALOG:
        matched_items = []
        for p in all_products:
            title_lower = (p.get("title") or "").lower()
            brand_lower = (p.get("brand") or "").lower()
            
            # Check brand match or keyword match
            has_brand = trend["brand"].lower() in brand_lower or trend["brand"].lower() in title_lower
            has_keyword = any(kw in title_lower for kw in trend["keywords"])
            
            if has_keyword and (has_brand or trend["brand"] == "Various" or "light blue" in title_lower or "eros" in title_lower):
                matched_items.append(p)
                
        # Group by store
        cf_items = [i for i in matched_items if i.get("store") == "Crist Fragrances"]
        pw_items = [i for i in matched_items if i.get("store") == "Perfumes Wholesale USA"]
        
        # Pick lowest price in each store
        best_cf = min(cf_items, key=lambda x: x.get("price_usd", 999999)) if cf_items else None
        best_pw = min(pw_items, key=lambda x: x.get("price_usd", 999999)) if pw_items else None
        
        results.append({
            "trend_info": trend,
            "best_cf": best_cf,
            "best_pw": best_pw,
            "all_matches": matched_items
        })
        
    return sorted(results, key=lambda x: x["trend_info"]["trend_score"], reverse=True)
