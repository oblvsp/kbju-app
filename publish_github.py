"""Build and publish the standalone HTML app and its update manifest."""

import argparse
import base64
import json
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WORK = ROOT / "github-update"
DIST = ROOT / "dist"
CONFIG = ROOT / "github.config.json"


def run(args, *, cwd=None, capture=False, env=None):
    print("+", " ".join(args), flush=True)
    result = subprocess.run(
        args,
        cwd=cwd,
        capture_output=capture,
        text=True,
        env=env,
    )
    if result.returncode:
        if capture:
            print(result.stdout, result.stderr)
        raise SystemExit("команда завершилась с ошибкой: " + " ".join(args))
    return result.stdout.strip() if capture else None


def git_environment(cfg):
    """Keep HTTPS credentials out of Git remotes, logs, and config files."""
    token = os.environ.get("GITHUB_TOKEN") or cfg.get("token")
    if not token:
        return os.environ.copy()
    env = os.environ.copy()
    auth = base64.b64encode(("x-access-token:" + token).encode()).decode()
    env.update(
        GIT_CONFIG_COUNT="1",
        GIT_CONFIG_KEY_0="http.extraheader",
        GIT_CONFIG_VALUE_0="AUTHORIZATION: basic " + auth,
    )
    return env


def save_json(path, payload):
    temporary = path.with_name(path.name + ".tmp")
    try:
        temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def prepare_checkout(repo_url, branch, env):
    if not (WORK / ".git").exists():
        if WORK.exists() and any(WORK.iterdir()):
            raise SystemExit(f"{WORK} существует, но не является checkout Git; перенесите её и повторите")
        WORK.parent.mkdir(parents=True, exist_ok=True)
        run(["git", "clone", "--branch", branch, "--single-branch", repo_url, str(WORK)], env=env)
        return

    if run(["git", "status", "--porcelain"], cwd=WORK, capture=True, env=env):
        raise SystemExit(f"В {WORK} есть незакоммиченные изменения; сохраните их или очистите checkout")
    run(["git", "remote", "set-url", "origin", repo_url], cwd=WORK, env=env)
    run(["git", "fetch", "origin", branch], cwd=WORK, env=env)
    base = subprocess.run(["git", "merge-base", "HEAD", "FETCH_HEAD"], cwd=WORK, capture_output=True, text=True, env=env)
    if base.returncode:
        # Upgrade a legacy publisher checkout created with an unrelated git init.
        run(["git", "checkout", "-B", branch, "FETCH_HEAD"], cwd=WORK, env=env)
    else:
        # Bring the checkout up to date without discarding prepared --no-push commits.
        run(["git", "merge", "--ff-only", "FETCH_HEAD"], cwd=WORK, env=env)


def published_build(fallback):
    manifest_path = WORK / "update.json"
    if not manifest_path.exists():
        return fallback
    try:
        build = int(json.loads(manifest_path.read_text(encoding="utf-8")).get("build", 0))
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Не удалось прочитать номер сборки из {manifest_path}: {exc}")
    return max(fallback, build)


def main():
    parser = argparse.ArgumentParser(description="Собирает и публикует HTML-релиз в GitHub")
    parser.add_argument("--build", type=int, default=None, help="номер сборки (по умолчанию: последняя + 1)")
    parser.add_argument("--version", default=None, help="человекочитаемая версия")
    parser.add_argument("--notes", default=None, help="описание изменений")
    parser.add_argument("--no-push", action="store_true", help="собрать и закоммитить, но не публиковать")
    args = parser.parse_args()

    if not CONFIG.exists():
        save_json(CONFIG, {"repo": "USERNAME/REPO", "notes": ""})
        raise SystemExit('Создан шаблон github.config.json — укажите "repo" в формате username/repo')
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    repo = cfg.get("repo", "")
    if not isinstance(repo, str) or len(repo.split("/")) != 2 or any(not part for part in repo.split("/")):
        raise SystemExit('В github.config.json укажите "repo" в формате username/repo')

    import build_app

    branch = cfg.get("branch", "main")
    if not isinstance(branch, str) or not branch.strip():
        raise SystemExit('В github.config.json ветка "branch" должна быть непустой строкой')
    branch = branch.strip()
    mode = cfg.get("mode") or ("https" if os.environ.get("GITHUB_TOKEN") or cfg.get("token") else "ssh")
    repo_url = f"git@github.com:{repo}.git" if mode == "ssh" else f"https://github.com/{repo}.git"
    env = git_environment(cfg)
    prepare_checkout(repo_url, branch, env)

    last_build = published_build(int(cfg.get("last_build", build_app.APP_BUILD)))
    new_build = args.build if args.build is not None else last_build + 1
    if new_build <= last_build:
        raise SystemExit(f"Номер сборки должен быть больше последней опубликованной ({last_build})")
    version = args.version or build_app.APP_VERSION
    notes = args.notes if args.notes is not None else cfg.get("notes", "")

    DIST.mkdir(parents=True, exist_ok=True)
    html_path = DIST / "kbju-index.html"
    build_app.main(build=new_build, version=version, out=html_path)
    base = f"https://raw.githubusercontent.com/{repo}/{branch}"
    manifest = {
        "version": version,
        "build": new_build,
        "notes": notes,
        "url": base + "/kbju-index.html",
    }
    save_json(DIST / "update.json", manifest)

    run(["git", "config", "user.name", cfg.get("git_name", "kbju-release-bot")], cwd=WORK, env=env)
    run(["git", "config", "user.email", cfg.get("git_email", "kbju-release@local")], cwd=WORK, env=env)

    shutil.copy2(html_path, WORK / "kbju-index.html")
    save_json(WORK / "update.json", manifest)
    run(["git", "add", "--", "kbju-index.html", "update.json"], cwd=WORK, env=env)
    commit = subprocess.run(
        ["git", "commit", "-m", f"release {version}: build {new_build}"],
        cwd=WORK,
        capture_output=True,
        text=True,
        env=env,
    )
    if commit.returncode:
        if "nothing to commit" not in (commit.stdout + commit.stderr):
            print(commit.stdout, commit.stderr)
            raise SystemExit("git commit не удался")
        raise SystemExit("Релиз совпадает с уже опубликованными файлами; номер сборки не изменён")
    print(f"commit: build {new_build}", flush=True)

    if args.no_push:
        print("push пропущен (--no-push)")
        return

    run(["git", "push", "origin", f"HEAD:{branch}"], cwd=WORK, env=env)
    local_sha = run(["git", "rev-parse", "HEAD"], cwd=WORK, capture=True, env=env)
    remote_sha = run(["git", "ls-remote", "origin", f"refs/heads/{branch}"], cwd=WORK, capture=True, env=env)
    if not remote_sha or remote_sha.split()[0] != local_sha:
        raise SystemExit("Проверка публикации не пройдена: SHA удалённой ветки не совпадает с коммитом релиза")

    cfg["last_build"] = new_build
    save_json(CONFIG, cfg)
    print(f"опубликовано: сборка {new_build} ({local_sha[:7]})")
    print("адрес обновления для приложения: " + base + "/update.json")


if __name__ == "__main__":
    main()
