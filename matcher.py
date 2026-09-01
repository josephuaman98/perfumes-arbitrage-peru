import re
import unicodedata
from difflib import SequenceMatcher
from collections import defaultdict

def normalize_text(text: str) -> str:
    if not text:
        return ""
    text = text.lower()
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
    text = re.sub(r'\(tester\)', '', text)
    text = re.sub(r'&amp;', '&', text)
    
    # Wholesale catalog common typos & spacing
    text = re.sub(r'\baamber\b', 'amber', text)
    text = re.sub(r'\bintese\b', 'intense', text)
    text = re.sub(r'\b9\s*pm\b', '9pm', text)
    text = re.sub(r'\b9\s*am\b', '9am', text)
    text = re.sub(r'\bmandarinsky\b', 'mandarin sky', text)
    
    # Brand alias normalization
    text = re.sub(r'\bpaco rabanne\b', 'rabanne', text)
    text = re.sub(r'\bdolce & gabbana\b', 'd&g', text)
    text = re.sub(r'\byves saint laurent\b', 'ysl', text)
    text = re.sub(r'\bjean paul gaultier\b', 'jpg', text)

    # Strip store noise
    text = re.sub(r'\b(?:crist fragances|crist fragrances|wholesale|various)\b', ' ', text)
    # Strip fragrance concentrations, volumes and delivery formats with decimals (e.g. 3.4oz, 3.4 oz, 100ml, 100 ml, 2.02 oz, 6.8 oz)
    text = re.sub(r'\b\d+(?:\.\d+)?\s*(?:fl\.?\s*oz|oz|ml|piece(?:s)?|pcs|pack|paq|x\s*\d+|units)\b', ' ', text)
    text = re.sub(r'\b(?:eau de parfum|eau de toilette|extrait de parfum|edp|edt|cologne|body spray|hair perfume|perfume mist|deodorant|perfume spray|spray|vial|sample|tester)\b', ' ', text)
    text = re.sub(r'\b(?:for women and men|for women|for men|for her|for him|pour femme|pour homme|ladies|men|women|dama|caballero|hombre|mujer|unisex)\b', ' ', text)
    # Replace non-alphanumeric with space
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    # Strip any remaining standalone numbers (except 9pm, 9am, 212, 540)
    text = re.sub(r'\b(?!(?:212|540|1|9pm|9am)\b)\d+\b', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def similarity_score(title1: str, title2: str) -> float:
    n1 = normalize_text(title1)
    n2 = normalize_text(title2)
    
    if not n1 or not n2:
        return 0.0
    if n1 == n2:
        return 1.0
    
    tokens1 = set(n1.split())
    tokens2 = set(n2.split())
    
    if not tokens1 or not tokens2:
        return 0.0

    if tokens1 == tokens2:
        return 1.0

    intersection = tokens1.intersection(tokens2)
    if not intersection:
        return 0.0
    
    union = tokens1.union(tokens2)
    jaccard = len(intersection) / len(union)
    
    # If one title is a subset of the other (e.g. "odyssey mandarin sky" in "armaf odyssey mandarin sky")
    if tokens1.issubset(tokens2) or tokens2.issubset(tokens1):
        subset_ratio = len(intersection) / max(len(tokens1), len(tokens2))
        return 0.75 + 0.25 * subset_ratio

    seq_ratio = SequenceMatcher(None, n1, n2).ratio()
    return max(jaccard, seq_ratio * (len(intersection) / min(len(tokens1), len(tokens2))))

def match_catalogs(cf_products: list, pw_products: list, threshold: float = 0.65):
    """
    Global highest-score-first catalog matcher using inverted index.
    Generates candidate pairs and pairs the highest scores first (1.00 -> 0.95 -> 0.90...).
    Guarantees exact matches like Yara Candy and Odyssey Mandarin Sky pair 100% correctly.
    """
    pw_index = defaultdict(set)
    for idx, pw in enumerate(pw_products):
        norm = normalize_text(f"{pw.get('brand','')} {pw.get('title','')}")
        for token in norm.split():
            if len(token) >= 3:
                pw_index[token].add(idx)

    # 1. Collect all candidate pairs with similarity score
    candidate_pairs = []
    for cf_idx, cf in enumerate(cf_products):
        cf_title = cf.get("title", "")
        cf_brand = cf.get("brand", "")
        cf_norm_full = normalize_text(f"{cf_brand} {cf_title}")
        cf_norm_title = normalize_text(cf_title)
        cf_tokens = [t for t in cf_norm_full.split() if len(t) >= 3]

        candidates = set()
        for t in cf_tokens:
            if t in pw_index:
                candidates.update(pw_index[t])

        for pw_idx in candidates:
            pw = pw_products[pw_idx]
            pw_title = pw.get("title", "")
            pw_brand = pw.get("brand", "")
            pw_norm_full = normalize_text(f"{pw_brand} {pw_title}")
            pw_norm_title = normalize_text(pw_title)

            # Exact title or full normalized match = perfect 1.00
            if cf_norm_title == pw_norm_title or cf_norm_full == pw_norm_full or cf_norm_title == pw_norm_full or cf_norm_full == pw_norm_title:
                score = 1.0
                token_diff = 0
            else:
                score_title = similarity_score(cf_norm_title, pw_norm_title)
                score_full = similarity_score(cf_norm_full, pw_norm_full)
                score = max(score_title, score_full)
                token_diff = abs(len(cf_norm_title.split()) - len(pw_norm_title.split()))
            
            if score >= threshold:
                candidate_pairs.append((score, -token_diff, cf_idx, pw_idx))

    # 2. Sort candidate pairs by score DESCENDING, then least word difference
    candidate_pairs.sort(key=lambda x: (x[0], x[1]), reverse=True)

    # 3. Greedily pair from highest score down
    matched = []
    used_cf_indices = set()
    used_pw_indices = set()

    for score, _, cf_idx, pw_idx in candidate_pairs:
        if cf_idx in used_cf_indices or pw_idx in used_pw_indices:
            continue
        
        cf = cf_products[cf_idx]
        pw = pw_products[pw_idx]
        
        used_cf_indices.add(cf_idx)
        used_pw_indices.add(pw_idx)

        matched.append({
            "match_score": round(score, 2),
            "name": cf.get("title", ""),
            "brand": cf.get("brand") or pw.get("brand"),
            "image": cf.get("image") or pw.get("image"),
            "crist_fragrances": cf,
            "perfumes_wholesale_usa": pw
        })

    matched_cf_ids = {m["crist_fragrances"]["id"] for m in matched}
    matched_pw_ids = {m["perfumes_wholesale_usa"]["id"] for m in matched}
    unmatched_cf = [p for p in cf_products if p["id"] not in matched_cf_ids]
    unmatched_pw = [p for p in pw_products if p["id"] not in matched_pw_ids]

    return {
        "matched": sorted(matched, key=lambda x: x["match_score"], reverse=True),
        "unmatched_cf": unmatched_cf,
        "unmatched_pw": unmatched_pw
    }
