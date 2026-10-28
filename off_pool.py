import csv
import difflib
import json
import math
import os
import re
import sys
import time

import requests

UA = {"User-Agent": "products-gap-fill/1.0 (personal offline dataset)"}
CSV_PATH = "products.csv"
POOL_PATH = "/tmp/rufp/off_pool.json"
API = "https://ru.openfoodfacts.org/api/v2/search"
CATEGORIES = [
    "en:fishes",
    "en:seafood",
    "en:fresh-fish-products",
    "en:frozen-fish-products",
    "en:fish-fillets",
    "en:marinated-fish-products",
    "en:fish-products",
]
STOP = {
    "свежая", "свежий", "свежее", "вареная", "варёная", "вареный", "варёный",
    "жареная", "жареный", "копченая", "копчёная", "копчено", "запеченная",
    "сырокопченая", "сырая", "сырой", "мороженая", "свежемороженая", "морская",
    "отварная", "отварной", "припущенный", "припущенная", "на", "в", "из", "и",
    "гриле", "пару", "масле", "собственном", "соку", "растительном", "б",
    "горячего", "холодного", "копчения", "рубленые", "соленая", "соленый",
    "слабосоленая", "слабосолёная", "жирная", "жирный",
}
MEAT_CATEGORIES = [
    "en:meats",
    "en:pork",
    "en:poultry-meat-products",
    "en:cooked-meat-products",
]

session = requests.Session()
session.headers.update(UA)
HOSTS = ["https://ru.openfoodfacts.org", "https://world.openfoodfacts.org"]


def api_get(params, tries=8, pause=15):
    for attempt in range(tries):
        host = HOSTS[attempt % len(HOSTS)]
        try:
            resp = session.get(host + "/api/v2/search", params=params, timeout=45)
            if resp.status_code == 200:
                return resp.json()
            print(f"    {host.split('//')[1]}: HTTP {resp.status_code} (попытка {attempt + 1}), ждём {pause} c", flush=True)
        except requests.RequestException as e:
            print(f"    {host.split('//')[1]}: {type(e).__name__} (попытка {attempt + 1})", flush=True)
        time.sleep(pause)
    return None


def build_pool(initial=None, categories=CATEGORIES):
    pool = dict(initial or {})
    if pool:
        print(f"существующий пул: {len(pool)} товаров", flush=True)
    for cat in categories:
        print(f"== {cat} ==", flush=True)
        data = api_get({"categories_tags": cat, "page_size": "1", "fields": "code"})
        if data is None:
            print("  категория недоступна, пропускаем", flush=True)
            continue
        count = data.get("count", 0)
        print(f"  всего: {count}", flush=True)
        pages = min(math.ceil(count / 100), 50)
        for page in range(1, pages + 1):
            data = api_get({
                "categories_tags": cat,
                "page_size": "100",
                "page": str(page),
                "fields": "code,product_name,product_name_ru,brands,nutriments",
            })
            if data is None:
                print(f"  страница {page} недоступна, прерываем категорию", flush=True)
                break
            products = data.get("products", [])
            if not products:
                break
            for p in products:
                code = p.get("code")
                if not code or code in pool:
                    continue
                nutr = p.get("nutriments") or {}
                car = nutr.get("carbohydrates_100g")
                prot = nutr.get("proteins_100g")
                name = p.get("product_name") or p.get("product_name_ru") or ""
                if car is None or not name:
                    continue
                pool[code] = {
                    "name": name,
                    "brands": p.get("brands") or "",
                    "carbs": car,
                    "prot": prot,
                }
            print(f"  страница {page}/{pages}, в пуле {len(pool)}", flush=True)
            time.sleep(3.5)
    return pool


def load_pool():
    if os.path.exists(POOL_PATH):
        with open(POOL_PATH, encoding="utf-8") as f:
            return json.load(f)
    return None


def tokens(name):
    s = re.sub(r"[^\wа-яё ]+", " ", name.lower())
    return [t for t in s.split() if t not in STOP]


def to_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def match(pool, row):
    name = row["name"]
    name_lower = name.lower()
    toks = tokens(name)
    if not toks:
        return None
    key = toks[0]
    cat_prot = to_float(row["protein"])
    best = None
    best_proxy = None
    for entry in pool.values():
        pname = entry["name"].lower()
        if key not in pname:
            continue
        ratio = difflib.SequenceMatcher(None, name_lower, pname).ratio()
        car = to_float(entry["carbs"])
        if car is None:
            continue
        off_prot = to_float(entry["prot"])
        ok_prot = cat_prot is None or off_prot is None or (
            off_prot > 0 and abs(off_prot - cat_prot) / max(cat_prot, 1.0) <= 0.45
        )
        if ok_prot:
            if best is None or ratio > best[0]:
                best = (ratio, entry, car)
        elif ratio >= 0.6:
            if best_proxy is None or ratio > best_proxy[0]:
                best_proxy = (ratio, entry, car)
    if best is not None and best[0] >= 0.5:
        return best + (False,)
    if best_proxy is not None:
        return best_proxy + (True,)
    return None


def main():
    pool = load_pool() or {}
    pool = build_pool(pool, CATEGORIES)
    if "--meat" in sys.argv:
        pool = build_pool(pool, MEAT_CATEGORIES)
    with open(POOL_PATH, "w", encoding="utf-8") as f:
        json.dump(pool, f, ensure_ascii=False)
    print(f"пул сохранён: {len(pool)} товаров", flush=True)
    with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        fieldnames = reader.fieldnames
        rows = list(reader)

    gap_idx = [i for i, r in enumerate(rows) if r["carbs"] in ("", "None")]
    print(f"строк без carbs: {len(gap_idx)}", flush=True)

    filled = 0
    unmatched = []
    proxies = []
    if os.path.exists("/tmp/rufp/off_filled.txt"):
        os.remove("/tmp/rufp/off_filled.txt")
    for n, i in enumerate(gap_idx, 1):
        row = rows[i]
        m = match(pool, row)
        if m is None:
            unmatched.append((row["name"], "нет совпадения в пуле OFF"))
        else:
            ratio, entry, car, proxy = m
            row["carbs"] = f"{car:.1f}"
            filled += 1
            with open("/tmp/rufp/off_filled.txt", "a", encoding="utf-8") as f:
                tag = " [замещено аналогом вида]" if proxy else ""
                f.write(f"{row['name']}\t{entry['name']}\t{entry['brands']}\tratio={ratio:.2f}\tcarbs={car:.1f}{tag}\n")
            if proxy:
                proxies.append(row["name"])
        if n % 25 == 0 or n == len(gap_idx):
            print(f"  ...{n}/{len(gap_idx)} обработано, заполнено: {filled}", flush=True)

    with open(CSV_PATH, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)

    print(f"итого заполнено из пула OFF: {filled}, не найдено: {len(unmatched)}", flush=True)
    with open("/tmp/rufp/off_unmatched.txt", "w", encoding="utf-8") as f:
        for name, reason in unmatched:
            f.write(f"{name}\t{reason}\n")
    with open("/tmp/rufp/off_proxy.txt", "w", encoding="utf-8") as f:
        for name in proxies:
            f.write(name + "\n")


if __name__ == "__main__":
    main()
