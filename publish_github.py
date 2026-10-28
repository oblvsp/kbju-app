import argparse
import json
import os
import shutil
import subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(ROOT, "github-update")
CONFIG = os.path.join(ROOT, "github.config.json")


def run(cmd, cwd=None, capture=False):
    print("+", " ".join(cmd), flush=True)
    result = subprocess.run(cmd, cwd=cwd, capture_output=capture, text=True)
    if result.returncode != 0:
        if capture:
            print(result.stdout, result.stderr)
        raise SystemExit("команда завершилась с ошибкой: " + " ".join(cmd))
    return result.stdout.strip() if capture else None


def main():
    parser = argparse.ArgumentParser(description="Публикует релиз обновления в GitHub-репозиторий")
    parser.add_argument("--build", type=int, default=None, help="номер сборки (по умолчанию: последняя + 1)")
    parser.add_argument("--version", default=None, help="человекочитаемая версия")
    parser.add_argument("--notes", default=None, help="описание изменений")
    parser.add_argument("--no-push", action="store_true", help="собрать и закоммитить, но не пушить")
    args = parser.parse_args()

    if not os.path.exists(CONFIG):
        with open(CONFIG, "w", encoding="utf-8") as f:
            json.dump({"repo": "USERNAME/REPO", "notes": ""}, f, ensure_ascii=False, indent=2)
        raise SystemExit('Создан шаблон github.config.json — укажи там "repo" в формате username/repo')

    with open(CONFIG, encoding="utf-8") as f:
        cfg = json.load(f)
    repo = cfg.get("repo", "")
    if not repo or "/" not in repo or repo.startswith("USERNAME"):
        raise SystemExit('В github.config.json укажи "repo" в формате username/repo')

    import build_app

    last = int(cfg.get("last_build", build_app.APP_BUILD))
    new_build = args.build if args.build is not None else last + 1
    version = args.version or build_app.APP_VERSION
    notes = args.notes if args.notes is not None else cfg.get("notes", "")

    dist = os.path.join(ROOT, "dist")
    os.makedirs(dist, exist_ok=True)
    # Собираем свежий HTML сразу в dist (единый источник — products.csv + шаблон build_app).
    build_app.main(build=new_build, version=version, out=os.path.join(dist, "kbju-index.html"))
    base = "https://raw.githubusercontent.com/" + repo + "/main"
    manifest = {"version": version, "build": new_build, "notes": notes, "url": base + "/kbju-index.html"}
    with open(os.path.join(dist, "update.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    if not os.path.exists(os.path.join(WORK, ".git")):
        os.makedirs(WORK, exist_ok=True)
        run(["git", "init", "-b", "main"], cwd=WORK)
    run(["git", "config", "user.name", cfg.get("git_name", "kbju-release-bot")], cwd=WORK)
    run(["git", "config", "user.email", cfg.get("git_email", "kbju-release@local")], cwd=WORK)

    mode = cfg.get("mode", "ssh")
    if mode == "https" and cfg.get("token"):
        url = "https://" + cfg["token"] + "@github.com/" + repo + ".git"
    elif mode == "https":
        url = "https://github.com/" + repo + ".git"
    else:
        url = "git@github.com:" + repo + ".git"
    remotes = run(["git", "remote"], cwd=WORK, capture=True)
    if "origin" in remotes.split():
        run(["git", "remote", "set-url", "origin", url], cwd=WORK)
    else:
        run(["git", "remote", "add", "origin", url], cwd=WORK)

    shutil.copy2(os.path.join(dist, "kbju-index.html"), os.path.join(WORK, "kbju-index.html"))
    with open(os.path.join(WORK, "update.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    with open(os.path.join(WORK, "README.md"), "w", encoding="utf-8") as f:
        f.write("# Обновления калькулятора КБЖУ\n\nАдрес обновления для приложения: " + base + "/update.json\n\nСкачать APK: " + base + "/kbju-app.apk\n")

    run(["git", "add", "-A"], cwd=WORK)
    commit = subprocess.run(["git", "commit", "-m", "release " + version + ": build " + str(new_build)],
                            cwd=WORK, capture_output=True, text=True)
    if commit.returncode == 0:
        print("commit: build " + str(new_build), flush=True)
    elif "nothing to commit" in (commit.stdout + commit.stderr):
        print("изменений нет — коммит пропущен", flush=True)
    else:
        print(commit.stdout, commit.stderr)
        raise SystemExit("git commit не удался")

    if args.no_push:
        print("push пропущен (--no-push)")
        return

    run(["git", "push", "-u", "origin", "main"], cwd=WORK)
    cfg["last_build"] = new_build
    with open(CONFIG, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
    print("опубликовано: сборка " + str(new_build))
    print("адрес обновления для приложения: " + base + "/update.json")


if __name__ == "__main__":
    main()
