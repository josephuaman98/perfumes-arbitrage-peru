def calculate_store_unit_cost(
    price_usd: float,
    store_name: str,
    lot_size: int = 30,
    usa_shipping_total: float = 50.0,
    freight_peru_usd: float = 8.0,
    exchange_rate: float = 3.36
):
    """
    Calcula la estructura de costos según la regla fiscal de cada tienda:
    - Crist Fragrances: 0% Tax (No cobra impuesto de Florida)
    - Perfumes Wholesale USA: 7% Tax (Florida Sales Tax) + Precio Mayorista (>=12 unid)
    - Envío USA: $50 prorrateado entre el tamaño del lote (lot_size)
    - Flete a Perú: $8.00 por unidad
    """
    if price_usd <= 0:
        return {
            "price_usd": 0.0,
            "tax_fl_rate": 0.0,
            "tax_fl_usd": 0.0,
            "shipping_usa_unit_usd": 0.0,
            "cost_miami_usd": 0.0,
            "freight_peru_usd": 0.0,
            "final_cost_usd": 0.0,
            "final_cost_pen": 0.0,
            "margins": {}
        }

    lot_size = max(1, lot_size)
    # Regla diferenciada de Tax y Envío USA según la tienda
    if "crist" in store_name.lower():
        tax_fl_rate = 0.00
        tax_fl_unit = 0.00
        shipping_usa_unit = 0.00  # Crist Fragrances NO cobra envío dentro de USA (Envío Gratis)
    else:
        tax_fl_rate = 0.07
        tax_fl_unit = price_usd * 0.07
        shipping_usa_unit = usa_shipping_total / lot_size  # PW USA cobra $50 flat prorrateado

    cost_miami_usd = price_usd + tax_fl_unit + shipping_usa_unit
    final_cost_usd = cost_miami_usd + freight_peru_usd
    final_cost_pen = final_cost_usd * exchange_rate

    # Simulador de márgenes sugeridos
    margins = {}
    for margin_pct in [30, 40, 50, 70, 100]:
        pvp_pen = round(final_cost_pen * (1 + margin_pct / 100), 2)
        profit_pen = round(pvp_pen - final_cost_pen, 2)
        margins[f"{margin_pct}%"] = {
            "pvp_pen": pvp_pen,
            "profit_pen": profit_pen
        }

    return {
        "price_usd": round(price_usd, 2),
        "tax_fl_rate": tax_fl_rate,
        "tax_fl_usd": round(tax_fl_unit, 2),
        "shipping_usa_unit_usd": round(shipping_usa_unit, 2),
        "cost_miami_usd": round(cost_miami_usd, 2),
        "freight_peru_usd": round(freight_peru_usd, 2),
        "final_cost_usd": round(final_cost_usd, 2),
        "final_cost_pen": round(final_cost_pen, 2),
        "margins": margins
    }

def compare_perfumes(
    cf_product: dict,
    pw_product: dict,
    lot_size: int = 30,
    exchange_rate: float = 3.36
):
    """
    Compara Crist Fragrances (0% Tax) vs Perfumes Wholesale USA (7% Tax + Precio Distribuidor >=12u).
    Determina el ganador real puesto en Perú.
    """
    cf_price = cf_product.get("price_usd", 0.0) if cf_product else 0.0
    
    # En PW USA, usamos el precio de distribuidor (para pedidos >= 12 unidades)
    pw_price = 0.0
    if pw_product:
        pw_price = float(pw_product.get("distributor_price") or pw_product.get("price_usd") or pw_product.get("retail_price_usa") or 0.0)

    cf_cost = calculate_store_unit_cost(cf_price, "Crist Fragrances", lot_size=lot_size, exchange_rate=exchange_rate) if cf_price > 0 else None
    pw_cost = calculate_store_unit_cost(pw_price, "Perfumes Wholesale USA", lot_size=lot_size, exchange_rate=exchange_rate) if pw_price > 0 else None

    winner = None
    saving_usd = 0.0
    saving_pen = 0.0
    saving_pct = 0.0

    if cf_cost and pw_cost:
        diff_usd = pw_cost["final_cost_usd"] - cf_cost["final_cost_usd"]
        if diff_usd > 0.01:
            winner = "Crist Fragrances"
            saving_usd = round(diff_usd, 2)
            saving_pen = round(saving_usd * exchange_rate, 2)
            saving_pct = round((diff_usd / pw_cost["final_cost_usd"]) * 100, 1)
        elif diff_usd < -0.01:
            winner = "Perfumes Wholesale USA"
            saving_usd = round(abs(diff_usd), 2)
            saving_pen = round(saving_usd * exchange_rate, 2)
            saving_pct = round((abs(diff_usd) / cf_cost["final_cost_usd"]) * 100, 1)
        else:
            winner = "Empate"
    elif cf_cost:
        winner = "Crist Fragrances (Solo disponible aquí)"
    elif pw_cost:
        winner = "Perfumes Wholesale USA (Solo disponible aquí)"

    return {
        "winner": winner,
        "saving_usd": saving_usd,
        "saving_pen": saving_pen,
        "saving_pct": saving_pct,
        "cf_cost": cf_cost,
        "pw_cost": pw_cost,
        "lot_size": lot_size
    }
