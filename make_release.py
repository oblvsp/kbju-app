import argparse
import json
import os
import shutil

import build_app


def main():
    parser = argparse.ArgumentParser(description="Собирает релиз для интернет-обновления")
    parser.add_argument("--build", type=int, required=True, help="номер сборки (больше текущей у пользователей)")
    parser.add_argument("--version", default=None, help="человекочитаемая версия, по умолчанию из build_app.py")
    parser.add_argument("--base", required=True, help="базовый URL, например https://host/kbju или http://192.168.1.5:8000")
    parser.add_argument("--notes", default="", help="описание изменений")
    args = parser.parse_args()

    build_app.main(build=args.build, version=args.version or build_app.APP_VERSION)

    dist = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist")
    os.makedirs(dist, exist_ok=True)
    shutil.copy2(os.path.join(os.path.dirname(os.path.abspath(__file__)), "calorie_app.html"),
                 os.path.join(dist, "kbju-index.html"))

    base = args.base.rstrip("/")
    manifest = {
        "version": args.version or build_app.APP_VERSION,
        "build": args.build,
        "notes": args.notes,
        "url": base + "/kbju-index.html",
    }
    with open(os.path.join(dist, "update.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    size = os.path.getsize(os.path.join(dist, "kbju-index.html")) // 1024
    print(f"готово: {dist}/update.json и {dist}/kbju-index.html ({size} КБ)")
    print(f"адрес обновления для приложения: {base}/update.json")


if __name__ == "__main__":
    main()
