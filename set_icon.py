import sys
from PIL import Image

SIZE = 192
OUT = "android-app/res/drawable/ic_app.png"


def main():
    if len(sys.argv) < 2:
        raise SystemExit("использование: python3 set_icon.py <путь к картинке>")
    src = Image.open(sys.argv[1]).convert("RGBA")
    w, h = src.size

    px = src.load()
    min_x, min_y, max_x, max_y = w, h, 0, 0
    step = max(1, min(w, h) // 200)
    for y in range(0, h, step):
        for x in range(0, w, step):
            r, g, b, a = px[x, y]
            if a > 24 and not (r > 242 and g > 242 and b > 242):
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)
    if max_x <= min_x or max_y <= min_y:
        min_x, min_y, max_x, max_y = 0, 0, w - 1, h - 1

    cx = (min_x + max_x) / 2
    cy = (min_y + max_y) / 2
    side = min(max_x - min_x, max_y - min_y)
    half = side / 2
    box = (int(cx - half), int(cy - half), int(cx + half), int(cy + half))
    box = (max(0, box[0]), max(0, box[1]), min(w, box[2]), min(h, box[3]))
    img = src.crop(box).resize((SIZE * 4, SIZE * 4), Image.LANCZOS)

    mask = Image.new("L", (SIZE * 4, SIZE * 4), 0)
    from PIL import ImageDraw
    d = ImageDraw.Draw(mask)
    d.ellipse((0, 0, SIZE * 4 - 1, SIZE * 4 - 1), fill=255)
    img.putalpha(mask)

    img = img.resize((SIZE, SIZE), Image.LANCZOS)
    img.save(OUT)
    print(f"иконка готова: {OUT} ({SIZE}x{SIZE}, круглые углы, из {sys.argv[1]})")


if __name__ == "__main__":
    main()
