import glob
import os
import struct
import subprocess
import sys
import zlib

ROOT = os.path.dirname(os.path.abspath(__file__))
SDK = "/tmp/rufp/android-sdk"
ECJ = os.path.join(SDK, "ecj.jar")
STORE = os.path.join(ROOT, "kbju.keystore")
KS_PASS = "kbju12345"
APK_OUT = os.path.join(ROOT, "kbju-app.apk")


def find_tool(name):
    for dirpath, dirnames, filenames in os.walk(SDK):
        if name in filenames and os.path.join("lib", name) not in dirpath:
            path = os.path.join(dirpath, name)
            if name in ("aapt", "aapt2", "zipalign", "apksigner", "d8"):
                return path
    raise SystemExit(f"не найден инструмент: {name}")


def find_android_jar():
    hits = glob.glob(os.path.join(SDK, "*", "android.jar"))
    if not hits:
        raise SystemExit("android.jar не найден")
    return max(hits, key=os.path.getsize)


def gen_icon(path, size=192):
    bg = (47, 125, 246)
    fg = (255, 255, 255)
    radius = 36
    cx, cy, r_in, r_out = 116, 96, 54, 66

    def rounded(x, y):
        dx = min(x, size - 1 - x)
        dy = min(y, size - 1 - y)
        if dx >= radius or dy >= radius:
            return True
        ex, ey = radius - dx, radius - dy
        return ex * ex + ey * ey <= radius * radius

    def in_ring(x, y):
        d2 = (x - cx) ** 2 + (y - cy) ** 2
        return r_in * r_in <= d2 <= r_out * r_out

    def in_fork(x, y):
        if 40 <= y <= 132:
            for tx in (44, 56, 68):
                if tx <= x < tx + 7:
                    return True
        if 44 <= x < 75 and 132 <= y <= 148:
            return True
        return False

    raw = bytearray()
    for y in range(size):
        raw.append(0)
        for x in range(size):
            if not rounded(x, y):
                raw += bytes((0, 0, 0, 0))
            elif in_ring(x, y) or in_fork(x, y):
                raw += bytes((*fg, 255))
            else:
                raw += bytes((*bg, 255))
    png_sig = b"\x89PNG\r\n\x1a\n"

    def chunk(tag, data):
        c = tag + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    with open(path, "wb") as f:
        f.write(png_sig)
        f.write(chunk(b"IHDR", ihdr))
        f.write(chunk(b"IDAT", zlib.compress(bytes(raw), 9)))
        f.write(chunk(b"IEND", b""))


def run(cmd, **kw):
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True, **kw)


def main():
    aapt = find_tool("aapt")
    d8 = find_tool("d8")
    zipalign = find_tool("zipalign")
    apksigner = find_tool("apksigner")
    android_jar = find_android_jar()

    os.makedirs(os.path.join(ROOT, "assets"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "res", "drawable"), exist_ok=True)
    icon_path = os.path.join(ROOT, "res", "drawable", "ic_app.png")
    if os.path.exists(icon_path):
        print("иконка уже есть, использую:", icon_path, flush=True)
    else:
        gen_icon(icon_path)
        print("иконка сгенерирована:", icon_path, flush=True)

    src_html = os.path.join(os.path.dirname(ROOT), "calorie_app.html")
    with open(src_html, encoding="utf-8") as f:
        html = f.read()
    with open(os.path.join(ROOT, "assets", "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print("assets/index.html обновлён:", len(html.encode("utf-8")) // 1024, "КБ", flush=True)

    build = os.path.join(ROOT, "build")
    subprocess.run(["rm", "-rf", build], check=True)
    classes = os.path.join(build, "classes")
    dexdir = os.path.join(build, "dex")
    os.makedirs(classes)
    os.makedirs(dexdir)

    sources = glob.glob(os.path.join(ROOT, "src", "**", "*.java"), recursive=True)
    run(["java", "-jar", ECJ, "-source", "8", "-target", "8", "-nowarn",
         "-bootclasspath", android_jar, "-d", classes] + sources)
    class_files = glob.glob(os.path.join(classes, "**", "*.class"), recursive=True)
    run([d8, "--release", "--lib", android_jar, "--output", dexdir] + class_files)

    unsigned = os.path.join(build, "app.unsigned.apk")
    run([aapt, "package", "-f", "-M", os.path.join(ROOT, "AndroidManifest.xml"),
         "-S", os.path.join(ROOT, "res"), "-A", os.path.join(ROOT, "assets"),
         "-I", android_jar, "-F", unsigned])
    run([aapt, "add", unsigned, "classes.dex"], cwd=dexdir)

    aligned = os.path.join(build, "app.aligned.apk")
    run([zipalign, "-f", "4", unsigned, aligned])

    if not os.path.exists(STORE):
        run(["keytool", "-genkeypair", "-keystore", STORE, "-alias", "kbju",
             "-keyalg", "RSA", "-keysize", "2048", "-validity", "10950",
             "-storepass", KS_PASS, "-keypass", KS_PASS,
             "-dname", "CN=KBJU Offline"])
    run([apksigner, "sign", "--ks", STORE, "--ks-pass", "pass:" + KS_PASS,
         "--key-pass", "pass:" + KS_PASS, "--out", APK_OUT, aligned])
    run([apksigner, "verify", "--print-certs", APK_OUT])
    run([aapt, "dump", "badging", APK_OUT])
    print("готово:", APK_OUT, f"({os.path.getsize(APK_OUT) // 1024} КБ)", flush=True)


if __name__ == "__main__":
    sys.exit(main())
