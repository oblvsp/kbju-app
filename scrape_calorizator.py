import csv
import time

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://calorizator.ru/product/all"
FIRST_PAGE = 0
LAST_PAGE = 86
OUTPUT_FILE = "products.csv"
REQUEST_TIMEOUT = 30
DELAY_BETWEEN_REQUESTS = 0.5
MAX_RETRIES = 5

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
    ),
    "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
}


def fetch_page(session: requests.Session, page: int) -> str:
    params = {"page": page} if page > 0 else None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = session.get(
                BASE_URL, params=params, timeout=REQUEST_TIMEOUT, headers=HEADERS
            )
            response.raise_for_status()
            return response.text
        except requests.RequestException as exc:
            wait = DELAY_BETWEEN_REQUESTS * attempt * 2
            print(
                f"  [стр. {page}] ошибка: {exc}; "
                f"повтор {attempt}/{MAX_RETRIES} через {wait:.1f}с"
            )
            time.sleep(wait)
    raise RuntimeError(f"Не удалось получить страницу {page} после {MAX_RETRIES} попыток")


def parse_page(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    table = soup.select_one("table.views-table")
    if table is None:
        return []
    rows = []
    tbody = table.find("tbody")
    if tbody is None:
        return []
    for tr in tbody.find_all("tr"):
        title_cell = tr.select_one("td.views-field-title a")
        if title_cell is None:
            continue
        name = title_cell.get_text(strip=True)
        url = "https://calorizator.ru" + title_cell.get("href", "")
        numbers = []
        for field in (
            "field-protein-value",
            "field-fat-value",
            "field-carbohydrate-value",
            "field-kcal-value",
        ):
            cell = tr.select_one(f"td.views-field-{field}")
            text = cell.get_text(strip=True).replace(",", ".") if cell else ""
            try:
                numbers.append(float(text))
            except ValueError:
                numbers.append(None)
        rows.append(
            {
                "name": name,
                "url": url,
                "protein": numbers[0],
                "fat": numbers[1],
                "carbs": numbers[2],
                "kcal": numbers[3],
            }
        )
    return rows


def main() -> None:
    session = requests.Session()
    all_rows: list[dict] = []
    empty_pages: list[int] = []

    for page in range(FIRST_PAGE, LAST_PAGE + 1):
        html = fetch_page(session, page)
        rows = parse_page(html)
        if not rows:
            empty_pages.append(page)
        all_rows.extend(rows)
        print(f"стр. {page:>2}: +{len(rows)} (всего {len(all_rows)})")
        time.sleep(DELAY_BETWEEN_REQUESTS)

    fieldnames = ["name", "url", "protein", "fat", "carbs", "kcal"]
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"\nГотово: {len(all_rows)} продуктов -> {OUTPUT_FILE}")
    if empty_pages:
        print(f"Пустые страницы (нет данных): {empty_pages}")


if __name__ == "__main__":
    main()
