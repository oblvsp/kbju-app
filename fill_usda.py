import csv
import os
import re

CSV_PATH = "products.csv"
SR_DIR = "/tmp/rufp/FoodData_Central_sr_legacy_food_csv_2018-04"
PROT_ID = "1003"
CARB_ID = "1005"

M = {
    "Индейка вареная": (["^Turkey, whole, meat only, cooked, roasted$", "^Turkey, all classes, light meat, cooked, roasted$"], True),
    "Корейка": (["^Pork, fresh, loin, whole, separable lean and fat, raw$"], False),
    "Корейка копчено-запеченная": (["^Pork, fresh, loin, whole, separable lean and fat, cooked, roasted$", "^Pork, cured, ham, whole, separable lean and fat, unheated$"], True),
    "Корейка свиная б/к (карбонад)": (["^Pork, fresh, loin, whole, separable lean and fat, cooked, roasted$", "^Pork, cured, ham, whole, separable lean only, roasted$"], True),
    "Корейка сырокопченая": (["^Pork, cured, ham, whole, separable lean and fat, unheated$", "^Pork, fresh, loin, whole, separable lean and fat, raw$"], True),
    "Котлеты из свинины рубленые": (["^Pork, fresh, ground, raw$"], True),
    "Котлеты из свинины сырые": (["^Pork, fresh, ground, raw$"], True),
    "Омуль свежий": (["^Fish, whitefish, mixed species, raw$"], True),
    "Осётр отварной": (["^Fish, sturgeon, mixed species, cooked, dry heat$", "^Fish, sturgeon, mixed species, raw$"], True),
    "Пангасиус": (["^Fish, catfish, channel, farmed, raw$"], True),
    "Путассу": (["^Fish, whiting, mixed species, raw$"], True),
    "Сазан азовский": (["^Fish, carp, raw$"], False),
    "Сазан каспийский": (["^Fish, carp, raw$"], False),
    "Сайра бланшированная в масле": (["^Fish, mackerel, jack, canned, drained solids$", "^Fish, sardine, Atlantic, canned in oil, drained solids with bone$"], True),
    "Сайра свежая": (["^Fish, herring, Atlantic, raw$", "^Fish, herring, Pacific, raw$"], True),
    "Салака копчёная": (["^Fish, herring, Atlantic, kippered$"], True),
    "Сардина в масле": (["^Fish, sardine, Atlantic, canned in oil, drained solids with bone$"], False),
    "Сардина отварная": (["^Fish, sardine, Atlantic, canned in oil, drained solids with bone$", "^Fish, herring, Atlantic, raw$"], True),
    "Сардина свежая": (["^Fish, herring, Atlantic, raw$", "^Fish, herring, Pacific, raw$"], True),
    "Севрюга свежая": (["^Fish, sturgeon, mixed species, raw$"], True),
    "Сельдь в растительном масле": (["^Fish, herring, Atlantic, raw$", "^Fish, herring, Atlantic, pickled$"], True),
    "Сельдь горячего копчения": (["^Fish, herring, Atlantic, kippered$"], False),
    "Сельдь свежая": (["^Fish, herring, Atlantic, raw$"], False),
    "Сёмга на гриле": (["^Fish, salmon, Atlantic, wild, cooked, dry heat$", "^Fish, salmon, Atlantic, farmed, cooked, dry heat$"], False),
    "Сёмга на пару": (["^Fish, salmon, coho, wild, cooked, moist heat$", "^Fish, salmon, Atlantic, wild, cooked, dry heat$"], True),
    "Сёмга отварная": (["^Fish, salmon, coho, wild, cooked, moist heat$", "^Fish, salmon, Atlantic, wild, cooked, dry heat$"], True),
    "Сёмга Русское море слабосоленая филе-кусок": (["^Fish, salmon, chinook, smoked$", "^Fish, salmon, Atlantic, farmed, raw$"], True),
    "Сёмга свежая": (["^Fish, salmon, Atlantic, wild, raw$", "^Fish, salmon, Atlantic, farmed, raw$"], False),
    "Сибас": (["^Fish, bass, striped, raw$", "^Fish, bass, fresh.?water, mixed species, raw$"], True),
    "Сиг": (["^Fish, whitefish, mixed species, raw$", "^Fish, cisco, raw$"], False),
    "Скумбрия в масле": (["^Fish, mackerel, jack, canned, drained solids$"], True),
    "Скумбрия на пару": (["^Fish, mackerel, Atlantic, cooked, dry heat$", "^Fish, mackerel, Pacific and jack, mixed species, cooked, dry heat$"], True),
    "Скумбрия отварная": (["^Fish, mackerel, Atlantic, cooked, dry heat$", "^Fish, mackerel, Pacific and jack, mixed species, cooked, dry heat$"], True),
    "Сом отварной": (["^Fish, catfish, channel, farmed, cooked, dry heat$"], True),
    "Сом припущенный": (["^Fish, catfish, channel, farmed, cooked, dry heat$"], True),
    "Сом свежий": (["^Fish, catfish, channel, farmed, raw$"], False),
    "Ставрида в масле": (["^Fish, mackerel, jack, canned, drained solids$"], True),
    "Ставрида отварная": (["^Fish, mackerel, Pacific and jack, mixed species, cooked, dry heat$"], True),
    "Ставрида припущенная": (["^Fish, mackerel, Pacific and jack, mixed species, cooked, dry heat$"], True),
    "Ставрида свежая": (["^Fish, mackerel, Pacific and jack, mixed species, raw$"], False),
    "Ставрида холодного копчения": (["^Fish, mackerel, jack, canned, drained solids$", "^Fish, mackerel, Pacific and jack, mixed species, raw$"], True),
    "Стерлядь свежая": (["^Fish, sturgeon, mixed species, raw$"], True),
    "Судак отварной": (["^Fish, pike, walleye, cooked, dry heat$"], True),
    "Судак припущенный": (["^Fish, pike, walleye, cooked, dry heat$"], True),
    "Судак свежий": (["^Fish, pike, walleye, raw$"], False),
    "Талисман": (["^Fish, flatfish \\(flounder and sole species\\), raw$", "^Fish, flatfish.*raw$"], True),
    "Терпуг": (["^Fish, ling, raw$", "^Fish, pollock, Alaska, raw$"], True),
    "Терпуг зубатый": (["^Fish, ling, raw$", "^Fish, pollock, Alaska, raw$"], True),
    "Тиляпия жареная": (["^Fish, tilapia, cooked, dry heat$", "^Fish, tilapia, raw$"], False),
    "Трепанг варёный": (["^Sea cucumber, yane \\(Alaska Native\\)$"], True),
    "Трепанг жареный": (["^Sea cucumber, yane \\(Alaska Native\\)$"], True),
    "Треска горячего копчения": (["^Fish, haddock, smoked$", "^Fish, cod, Atlantic, dried and salted$"], True),
    "Треска жареная": (["^Fish, cod, Atlantic, cooked, dry heat$"], False),
    "Треска копченая": (["^Fish, haddock, smoked$", "^Fish, cod, Atlantic, dried and salted$"], True),
    "Треска отварная": (["^Fish, cod, Pacific, cooked$", "^Fish, cod, Atlantic, cooked, dry heat$"], True),
    "Треска свежая": (["^Fish, cod, Atlantic, raw$"], False),
    "Треска соленая": (["^Fish, cod, Atlantic, dried and salted$"], True),
    "Тунец 5 морей в собственном соку": (["^Fish, tuna, light, canned in water, drained solids"], False),
    "Тунец в растительном масле": (["^Fish, tuna, light, canned in oil, drained solids$"], False),
    "Угорь копчёный": (["^Fish, eel, mixed species, cooked, dry heat$", "^Fish, eel, mixed species, raw$"], True),
    "Угорь морской свежий": (["^Fish, eel, mixed species, raw$"], False),
    "Угорь свежий": (["^Fish, eel, mixed species, raw$"], False),
    "Устрицы отварные": (["^Mollusks, oyster, eastern, wild, cooked, moist heat$", "^Mollusks, oyster, Pacific, cooked, moist heat$"], True),
    "Форель в масле Делси": (["^Fish, trout, rainbow, farmed, raw$"], True),
    "Форель морская свежая": (["^Fish, trout, rainbow, farmed, raw$", "^Fish, trout, rainbow, wild, raw$"], False),
    "Форель отварная": (["^Fish, trout, mixed species, cooked, dry heat$", "^Fish, trout, rainbow, farmed, cooked, dry heat$"], True),
    "Форель слабосолёная": (["^Fish, trout, rainbow, farmed, raw$"], True),
    "Форель слабосолёная жирная": (["^Fish, trout, rainbow, farmed, raw$"], True),
    "Хамса соленая": (["^Fish, anchovy, european, raw$"], True),
    "Щука отварная": (["^Fish, pike, northern, cooked, dry heat$"], True),
    "Щука припущенная": (["^Fish, pike, northern, cooked, dry heat$"], True),
    "Щука свежая": (["^Fish, pike, northern, raw$"], False),
    "Язык морской": (["^Fish, flatfish \\(flounder and sole species\\), raw$"], False),
    "Язь свежий": (["^Fish, carp, raw$", "^Fish, whitefish, mixed species, raw$"], True),
}
OVERWRITE = {"Путассу"}


def main():
    with open(os.path.join(SR_DIR, "food.csv"), encoding="utf-8", newline="") as f:
        foods = list(csv.DictReader(f))

    candidates = {name: [] for name in M}
    for row in foods:
        desc = row["description"]
        for name, (patterns, _) in M.items():
            for pri, pat in enumerate(patterns):
                if re.search(pat, desc, re.I):
                    candidates[name].append((pri, int(row["fdc_id"]), desc))
                    break

    needed = {fdc for lst in candidates.values() for _, fdc, _ in lst}
    nutrients = {}
    with open(os.path.join(SR_DIR, "food_nutrient.csv"), encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            fdc = int(row["fdc_id"])
            if fdc in needed and row["nutrient_id"] in (PROT_ID, CARB_ID):
                nutrients.setdefault(fdc, {})[row["nutrient_id"]] = row["amount"]

    with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        fieldnames = reader.fieldnames
        rows = list(reader)

    if os.path.exists("/tmp/rufp/usda_filled.txt"):
        os.remove("/tmp/rufp/usda_filled.txt")
    unresolved = []
    filled = 0
    for row in rows:
        name = row["name"]
        if name not in M:
            continue
        if row["carbs"] not in ("", "None") and name not in OVERWRITE:
            continue
        lst = candidates[name]
        if not lst:
            unresolved.append((name, "нет совпадения в SR Legacy"))
            continue
        try:
            cat_prot = float(row["protein"]) if row["protein"] not in ("", "None") else None
        except ValueError:
            cat_prot = None

        def sort_key(c):
            pri, fdc, _ = c
            usda_prot = nutrients.get(fdc, {}).get(PROT_ID)
            diff = 0.0
            if cat_prot is not None and usda_prot is not None:
                diff = abs(float(usda_prot) - cat_prot)
            return (pri, diff)

        lst.sort(key=sort_key)
        pri, fdc, desc = lst[0]
        car = nutrients.get(fdc, {}).get(CARB_ID)
        if car is None:
            unresolved.append((name, f"нет углеводов у {desc!r}"))
            continue
        row["carbs"] = f"{float(car):.1f}"
        filled += 1
        _, proxy = M[name]
        with open("/tmp/rufp/usda_filled.txt", "a", encoding="utf-8") as f:
            tag = " [proxy-замещение]" if proxy else ""
            f.write(f"{name}\t{desc}\tcarbs={float(car):.1f}{tag}\n")

    with open(CSV_PATH, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)

    print(f"заполнено из USDA: {filled}, не разрешено: {len(unresolved)}", flush=True)
    with open("/tmp/rufp/usda_unresolved.txt", "w", encoding="utf-8") as f:
        for name, reason in unresolved:
            f.write(f"{name}\t{reason}\n")


if __name__ == "__main__":
    main()
