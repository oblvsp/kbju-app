import argparse
import json
from pathlib import Path

import build_app


def main():
    parser = argparse.ArgumentParser(description="Собирает релиз для интернет-обновления")
    parser.add_argument("--build", type=int, required=True, help="номер сборки (больше текущей у пользователей)")
    parser.add_argument("--version", default=None, help="человекочитаемая версия, по умолчанию из build_app.py")
    parser.add_argument("--base", required=True, help="базовый URL, например https://host/kbju или http://192.168.1.5:8000")
    parser.add_argument("--notes", default="", help="описание изменений")
    args = parser.parse_args()

    dist = Path(__file__).resolve().parent / "dist"
    dist.mkdir(parents=True, exist_ok=True)
    html_path = dist / "kbju-index.html"
    build_app.main(build=args.build, version=args.version or build_app.APP_VERSION, out=html_path)

    base = args.base.rstrip("/")
    manifest = {
        "version": args.version or build_app.APP_VERSION,
        "build": args.build,
        "notes": args.notes,
        "url": base + "/kbju-index.html",
    }
    (dist / "update.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    size = html_path.stat().st_size // 1024
    print(f"готово: {dist}/update.json и {html_path} ({size} КБ)")
    print(f"адрес обновления для приложения: {base}/update.json")


if __name__ == "__main__":
    main()
