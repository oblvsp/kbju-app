import csv
import re
import shutil
import time

import requests
from bs4 import BeautifulSoup

BASE = "https://calorizator.ru"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0"}
CSV_PATH = "products.csv"
BAK_PATH = "products.csv.bak"
FIELDS = ("protein", "fat", "carbs", "kcal")
KEYWORDS = {
    "kcal": ("калор", "ккал"),
    "protein": ("бел",),
    "fat": ("жир",),
    "carbs": ("углев",),
}

session = requests.Session()
session.headers.update(UA)


def fetch(url, tries=3):
    for attempt in range(tries):
        try:
            resp = session.get(url, timeout=30)
            if resp.status_code == 200:
                return resp.text
            if resp.status_code == 404:
                return None
        except requests.RequestException:
            pass
        time.sleep(1.5 * (attempt + 1))
    return None


def to_num(text):
    if not text:
        return None
    match = re.search(r"\d+(?:\.\d+)?", text.replace(",", "."))
    return float(match.group(0)) if match else None


def parse_card(html):
    soup = BeautifulSoup(html, "html.parser")
    vals = {}
    for table in soup.find_all("table"):
        trs = table.find_all("tr")
        if not trs or "Нутриент" not in trs[0].get_text(" ", strip=True):
            continue
        for tr in trs[1:]:
            cells = tr.find_all(["td", "th"])
            if len(cells) < 2:
                continue
            name = cells[0].get_text(" ", strip=True).lower()
            num = to_num(cells[1].get_text(" ", strip=True))
            if num is None:
                continue
            for field, kws in KEYWORDS.items():
                if any(k in name for k in kws):
                    vals.setdefault(field, num)
                    break
    for div in soup.select("div[class*='field-field-']"):
        label = div.select_one(".field-label-inline-first")
        if not label:
            continue
        ltext = label.get_text(" ", strip=True).lower()
        full = div.get_text(" ", strip=True)
        val_text = full.replace(label.get_text(" ", strip=True), "", 1).strip()
        num = to_num(val_text)
        if num is None:
            continue
        for field, kws in KEYWORDS.items():
            if any(k in ltext for k in kws):
                vals.setdefault(field, num)
                break
    return vals


def save(fieldnames, rows):
    with open(CSV_PATH, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)


def main():
    shutil.copy2(CSV_PATH, BAK_PATH)
    with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        fieldnames = reader.fieldnames
        rows = list(reader)

    gap_idx = [i for i, r in enumerate(rows) if any(r[k] in ("", "None") for k in FIELDS)]
    print(f"строк с пропусками: {len(gap_idx)}", flush=True)

    filled = 0
    not_found = []
    for n, i in enumerate(gap_idx, 1):
        row = rows[i]
        url = row["url"] if row["url"].startswith("http") else BASE + row["url"]
        html = fetch(url)
        if html is None:
            not_found.append((row["name"], row["url"], "нет ответа"))
        else:
            vals = parse_card(html)
            got = []
            for field in FIELDS:
                if row[field] in ("", "None") and field in vals:
                    row[field] = f"{vals[field]:.1f}"
                    got.append(field)
            if got:
                filled += 1
            else:
                not_found.append((row["name"], row["url"], "нет данных на карточке"))
        if n % 20 == 0 or n == len(gap_idx):
            save(fieldnames, rows)
            print(f"  ...{n}/{len(gap_idx)} обработано, строк заполнено: {filled}", flush=True)
        time.sleep(0.5)

    print(f"итого заполнено строк: {filled}", flush=True)
    print(f"не удалось заполнить: {len(not_found)}", flush=True)
    with open("/tmp/rufp/card_not_filled.txt", "w", encoding="utf-8") as f:
        for name, url, reason in not_found:
            f.write(f"{name}\t{url}\t{reason}\n")


if __name__ == "__main__":
    main()
