import csv
import difflib
import re
import time

import requests

UA = {"User-Agent": "products-gap-fill/1.0 (personal offline dataset)"}
CSV_PATH = "products.csv"
API = "https://ru.openfoodfacts.org/cgi/search.pl"
FIELDS = ("protein", "fat", "carbs", "kcal")
STOP = {
    "свежая", "свежий", "свежее", "вареная", "варёная", "вареный", "варёный",
    "жареная", "жареный", "копченая", "копчёная", "копчено", "запеченная",
    "сырокопченая", "сырая", "сырой", "мороженая", "свежемороженая", "морская",
    "отварная", "отварной", "припущенный", "припущенная", "на", "в", "из", "и",
    "гриле", "пару", "масле", "собственном", "соку", "растительном", "б",
    "горячего", "холодного", "копчения", "рубленые", "соленая", "соленый",
    "слабосоленая", "слабосолёная", "жирная", "жирный",
}

session = requests.Session()
session.headers.update(UA)


def tokens(name):
    s = re.sub(r"[^\wа-яё ]+", " ", name.lower())
    return [t for t in s.split() if t not in STOP]


def fetch_json(params, tries=3):
    for attempt in range(tries):
        try:
            resp = session.get(API, params=params, timeout=30)
            if resp.status_code == 200:
                return resp.json()
        except (requests.RequestException, ValueError):
            pass
        time.sleep(2.0 * (attempt + 1))
    return None


def search(name):
    data = fetch_json({
        "search_terms": name,
        "search_simple": "1",
        "action": "process",
        "json": "1",
        "page_size": "20",
        "fields": "product_name,generic_name,brands,categories,nutriments",
    })
    if not data:
        return None
    my_tokens = tokens(name)
    if not my_tokens:
        return None
    key = my_tokens[0]
    return data.get("products", []), key


def best_match(products, key, name_lower, protein_txt):
    best = None
    best_risky = None
    try:
        cat_prot = float(protein_txt) if protein_txt not in ("", "None") else None
    except ValueError:
        cat_prot = None
    for p in products:
        pname = p.get("product_name") or p.get("generic_name") or ""
        if not pname:
            continue
        pl = pname.lower()
        if key not in pl:
            continue
        nutr = p.get("nutriments") or {}
        car = nutr.get("carbohydrates_100g")
        if car is None:
            continue
        try:
            car = float(car)
        except (TypeError, ValueError):
            continue
        ratio = difflib.SequenceMatcher(None, name_lower, pl).ratio()
        off_prot = nutr.get("proteins_100g")
        try:
            off_prot = float(off_prot) if off_prot is not None else None
        except (TypeError, ValueError):
            off_prot = None
        ok_prot = cat_prot is None or off_prot is None or (
            off_prot > 0 and abs(off_prot - cat_prot) / max(cat_prot, 1.0) <= 0.45
        )
        cand = (ratio, pname, car, off_prot)
        if ok_prot:
            if best is None or ratio > best[0]:
                best = cand
        elif ratio >= 0.6:
            if best_risky is None or ratio > best_risky[0]:
                best_risky = cand
    if best is not None and best[0] >= 0.5:
        return best
    return best_risky


def save(fieldnames, rows):
    with open(CSV_PATH, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)


def main():
    with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        fieldnames = reader.fieldnames
        rows = list(reader)

    gap_idx = [i for i, r in enumerate(rows) if r["carbs"] in ("", "None")]
    print(f"строк без carbs: {len(gap_idx)}", flush=True)

    filled = 0
    unmatched = []
    for n, i in enumerate(gap_idx, 1):
        row = rows[i]
        name_lower = row["name"].lower()
        result = search(row["name"])
        if result is None:
            unmatched.append((row["name"], "нет ответа OFF"))
        else:
            products, key = result
            match = best_match(products, key, name_lower, row["protein"])
            if match is None:
                unmatched.append((row["name"], "нет подходящего совпадения"))
            else:
                ratio, pname, car, _ = match
                row["carbs"] = f"{car:.1f}"
                filled += 1
                with open("/tmp/rufp/off_filled.txt", "a", encoding="utf-8") as f:
                    f.write(f"{row['name']}\t{pname}\tratio={ratio:.2f}\tcarbs={car:.1f}\n")
        if n % 20 == 0 or n == len(gap_idx):
            save(fieldnames, rows)
            print(f"  ...{n}/{len(gap_idx)} обработано, заполнено: {filled}", flush=True)
        time.sleep(0.7)

    save(fieldnames, rows)
    print(f"итого заполнено: {filled}, не найдено: {len(unmatched)}", flush=True)
    with open("/tmp/rufp/off_unmatched.txt", "w", encoding="utf-8") as f:
        for name, reason in unmatched:
            f.write(f"{name}\t{reason}\n")


if __name__ == "__main__":
    main()
