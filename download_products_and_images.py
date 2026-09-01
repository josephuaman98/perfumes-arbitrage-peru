import os
import json
import urllib.request
import re
import concurrent.futures
import time
import csv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
IMAGES_DIR = os.path.join(BASE_DIR, "imagenes_perfumes")
CF_IMG_DIR = os.path.join(IMAGES_DIR, "crist_fragrances")
PW_IMG_DIR = os.path.join(IMAGES_DIR, "perfumes_wholesale_usa")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CF_IMG_DIR, exist_ok=True)
os.makedirs(PW_IMG_DIR, exist_ok=True)

CACHE_FILE = os.path.join(DATA_DIR, "perfumes_cache.json")

def sanitize_filename(name: str) -> str:
    # Remove invalid filesystem characters
    clean = re.sub(r'[\\/*?:"<>|]', "", name)
    clean = re.sub(r'\s+', '_', clean).strip("._")
    return clean[:80]

def download_single_image(item, target_dir, default_ext=".jpg"):
    img_url = item.get("image")
    if not img_url:
        return item, None

    # Fix relative or protocol-less URLs
    if img_url.startswith("//"):
        img_url = "https:" + img_url
    elif not img_url.startswith("http"):
        img_url = "https://" + img_url

    prod_id = item.get("id", "prod")
    title_safe = sanitize_filename(item.get("title", "perfume"))
    ext = os.path.splitext(img_url.split("?")[0])[1]
    if not ext or len(ext) > 5:
        ext = default_ext

    filename = f"{prod_id}_{title_safe}{ext}"
    local_path = os.path.join(target_dir, filename)

    if os.path.exists(local_path) and os.path.getsize(local_path) > 500:
        rel_path = os.path.relpath(local_path, BASE_DIR)
        item["local_image_path"] = rel_path
        return item, rel_path

    try:
        req = urllib.request.Request(img_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        with urllib.request.urlopen(req, timeout=12) as response, open(local_path, 'wb') as out_file:
            out_file.write(response.read())
        rel_path = os.path.relpath(local_path, BASE_DIR)
        item["local_image_path"] = rel_path
        return item, rel_path
    except Exception as e:
        item["local_image_path"] = None
        return item, None

def save_csv_and_json(data_cf, data_pw):
    # 1. Save unified JSON
    json_path = os.path.join(DATA_DIR, "catalogo_completo_con_imagenes.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            "total_crist_fragrances": len(data_cf),
            "total_perfumes_wholesale_usa": len(data_pw),
            "crist_fragrances": data_cf,
            "perfumes_wholesale_usa": data_pw
        }, f, ensure_ascii=False, indent=2)
    print(f"Catálogo JSON guardado en: {json_path}")

    # 2. Save CSV for easy Excel view
    csv_path = os.path.join(DATA_DIR, "catalogo_completo_perfumes.csv")
    all_items = data_cf + data_pw
    if all_items:
        keys = ["store", "id", "brand", "title", "price_usd", "sku", "in_stock", "image", "local_image_path", "store_url"]
        with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(all_items)
        print(f"Catálogo CSV guardado en: {csv_path}")

def run_download_pipeline(max_workers=20):
    print("==================================================")
    print(" INICIANDO DESCARGA DE PRODUCTOS E IMÁGENES")
    print("==================================================")

    if not os.path.exists(CACHE_FILE):
        from scraper import sync_all
        sync_all(force_refresh=True)

    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        cache = json.load(f)

    cf_list = cache.get("crist_fragrances", [])
    pw_list = cache.get("perfumes_wholesale_usa", [])

    print(f"\n1. Descargando imágenes de Crist Fragrances ({len(cf_list)} productos)...")
    updated_cf = []
    cf_downloaded = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(download_single_image, item, CF_IMG_DIR): item for item in cf_list}
        for future in concurrent.futures.as_completed(futures):
            item, path = future.result()
            updated_cf.append(item)
            if path:
                cf_downloaded += 1
            if len(updated_cf) % 250 == 0:
                print(f"  Progreso CF: {len(updated_cf)}/{len(cf_list)} procesados ({cf_downloaded} imágenes descargadas)...")

    print(f"-> Crist Fragrances completado: {cf_downloaded} imágenes guardadas en {CF_IMG_DIR}")

    print(f"\n2. Descargando imágenes de Perfumes Wholesale USA ({len(pw_list)} productos)...")
    updated_pw = []
    pw_downloaded = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(download_single_image, item, PW_IMG_DIR): item for item in pw_list}
        for future in concurrent.futures.as_completed(futures):
            item, path = future.result()
            updated_pw.append(item)
            if path:
                pw_downloaded += 1
            if len(updated_pw) % 50 == 0:
                print(f"  Progreso PW: {len(updated_pw)}/{len(pw_list)} procesados ({pw_downloaded} imágenes descargadas)...")

    print(f"-> Perfumes Wholesale USA completado: {pw_downloaded} imágenes guardadas en {PW_IMG_DIR}")

    # Save all updated metadata
    save_csv_and_json(updated_cf, updated_pw)

    # Also update the cache file so the web server uses the local image paths if needed
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "last_sync": time.strftime("%Y-%m-%d %H:%M:%S"),
            "crist_fragrances": updated_cf,
            "perfumes_wholesale_usa": updated_pw
        }, f, ensure_ascii=False, indent=2)

    print("\n==================================================")
    print(" ¡DESCARGA Y EXTRACCIÓN FINALIZADA CON ÉXITO!")
    print(f" Total imágenes guardadas: {cf_downloaded + pw_downloaded}")
    print(f" Carpeta de imágenes: {IMAGES_DIR}")
    print("==================================================")

if __name__ == "__main__":
    run_download_pipeline()
