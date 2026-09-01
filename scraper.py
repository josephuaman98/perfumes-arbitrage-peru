import urllib.request
import json
import re
import os
import time

CACHE_FILE = os.path.join(os.path.dirname(__file__), "data", "perfumes_cache.json")

def get_json(url, headers=None, timeout=15):
    if headers is None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Accept': 'application/json'
        }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read().decode('utf-8', errors='ignore')
        return json.loads(data)

def fetch_crist_fragrances(max_pages=50):
    print("Sincronizando Crist Fragrances...")
    all_products = []
    page = 1
    while page <= max_pages:
        try:
            url = f"https://wholesale.cristfragances.com/products.json?limit=250&page={page}"
            data = get_json(url)
            products = data.get("products", [])
            if not products:
                break
            for p in products:
                variants = p.get("variants", [])
                price = float(variants[0].get("price", 0)) if variants else 0.0
                sku = variants[0].get("sku", "") if variants else ""
                available = variants[0].get("available", True) if variants else True
                images = p.get("images", [])
                image_url = images[0].get("src", "") if images else ""

                all_products.append({
                    "id": f"cf_{p.get('id')}",
                    "title": p.get("title", "").strip(),
                    "brand": (p.get("vendor") or "Various").strip(),
                    "price_usd": price,
                    "sku": sku,
                    "image": image_url,
                    "in_stock": available,
                    "store": "Crist Fragrances",
                    "store_url": f"https://wholesale.cristfragances.com/products/{p.get('handle', '')}",
                    "raw_type": p.get("product_type", "")
                })
            print(f"  CF Página {page}: {len(products)} productos obtenidos.")
            if len(products) < 250:
                break
            page += 1
            time.sleep(0.3)
        except Exception as e:
            print(f"Error en CF página {page}: {e}")
            break
    print(f"Total Crist Fragrances: {len(all_products)} productos.")
    return all_products

def fetch_perfumes_wholesale_usa():
    print("Sincronizando Perfumes Wholesale USA...")
    all_products = []
    app_id = "699f4b5f4adb14106812b8f5"
    url = f"https://perfumeswholesaleusa.com/api/apps/{app_id}/entities/Product"
    try:
        data = get_json(url)
        items = data if isinstance(data, list) else data.get("data", [])
        for item in items:
            dist_price = float(item.get("distributor_price") or 0.0)
            ws_price = float(item.get("wholesale_price") or 0.0)
            retail_price = float(item.get("retail_price") or 0.0)
            
            # Base price is distributor_price if available, otherwise wholesale_price, otherwise retail
            base_price = dist_price if dist_price > 0 else (ws_price if ws_price > 0 else retail_price)

            images = item.get("images") or []
            image_url = images[0] if isinstance(images, list) and images else (item.get("image") or "")
            in_stock = bool(item.get("in_stock", True)) and (float(item.get("total_stock") or 1) > 0)
            
            all_products.append({
                "id": f"pw_{item.get('id')}",
                "title": (item.get("fragrance_name") or item.get("product_name") or "").strip(),
                "brand": (item.get("brand") or "Various").strip(),
                "price_usd": base_price,
                "wholesale_price": ws_price if ws_price > 0 else base_price,
                "distributor_price": dist_price if dist_price > 0 else base_price,
                "retail_price_usa": retail_price,
                "sku": item.get("product_code", ""),
                "size": item.get("size", ""),
                "gender": item.get("gender", ""),
                "stock": item.get("total_stock", 0),
                "image": image_url,
                "in_stock": in_stock,
                "store": "Perfumes Wholesale USA",
                "store_url": f"https://perfumeswholesaleusa.com/ProductDetail?id={item.get('id')}",
                "raw_type": "Fragrance"
            })
        print(f"Total Perfumes Wholesale USA: {len(all_products)} productos.")
    except Exception as e:
        print(f"Error en PW USA: {e}")
    return all_products

def sync_all(force_refresh=False):
    if not force_refresh and os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("crist_fragrances") and data.get("perfumes_wholesale_usa"):
                    print("Cargando catálogo desde caché local...")
                    return data
        except Exception as e:
            print("Error leyendo caché, sincronizando nuevamente:", e)

    try:
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    except Exception:
        pass

    cf_products = fetch_crist_fragrances()
    pw_products = fetch_perfumes_wholesale_usa()

    result = {
        "last_sync": time.strftime("%Y-%m-%d %H:%M:%S"),
        "crist_fragrances": cf_products,
        "perfumes_wholesale_usa": pw_products
    }

    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Warning guardando cache (filesystem read-only):", e)

    return result

if __name__ == "__main__":
    sync_all(force_refresh=True)
