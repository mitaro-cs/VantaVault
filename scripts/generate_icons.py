from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
GENERATED_DIR = ROOT / "assets" / "generated"
ICONSET_DIR = GENERATED_DIR / "VantaVault.iconset"
PNG_ICON = GENERATED_DIR / "vantavault-1024.png"
ICO_ICON = GENERATED_DIR / "vantavault.ico"
ICNS_ICON = GENERATED_DIR / "vantavault.icns"


def font_candidates() -> list[Path]:
    candidates = [
        Path("/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf"),
        Path("/System/Library/Fonts/Supplemental/Georgia Bold.ttf"),
        Path("/System/Library/Fonts/Supplemental/Times New Roman.ttf"),
        Path("C:/Windows/Fonts/georgiab.ttf"),
        Path("C:/Windows/Fonts/timesbd.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"),
    ]
    return [path for path in candidates if path.exists()]


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = font_candidates()
    for path in candidates:
        try:
            return ImageFont.truetype(str(path), size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def draw_monogram(size: int = 1024) -> Image.Image:
    image = Image.new("RGBA", (size, size), "#080808")
    draw = ImageDraw.Draw(image)

    for y in range(size):
        alpha = int(28 * (y / size))
        draw.line((0, y, size, y), fill=(255, 255, 255, alpha))

    draw.ellipse(
        (size * 0.11, size * 0.11, size * 0.89, size * 0.89),
        outline=(255, 255, 255, 18),
        width=2,
    )
    draw.ellipse(
        (size * 0.18, size * 0.18, size * 0.82, size * 0.82),
        outline=(194, 177, 151, 12),
        width=2,
    )

    main_font = load_font(int(size * 0.62))
    sub_font = load_font(int(size * 0.16))

    draw.text(
        (size * 0.31, size * 0.16),
        "V",
        font=main_font,
        fill="#f6f2ea",
    )
    draw.text(
        (size * 0.58, size * 0.57),
        "Vw",
        font=sub_font,
        fill="#f6f2ea",
    )
    return image


def build_png_and_ico() -> None:
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    image = draw_monogram()
    image.save(PNG_ICON)
    image.save(
        ICO_ICON,
        format="ICO",
        sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)],
    )


def build_icns() -> None:
    if sys.platform != "darwin":
        return
    if ICONSET_DIR.exists():
        for child in ICONSET_DIR.iterdir():
            child.unlink()
    else:
        ICONSET_DIR.mkdir(parents=True, exist_ok=True)

    icon_sizes = [
        16,
        32,
        64,
        128,
        256,
        512,
        1024,
    ]
    source = Image.open(PNG_ICON)
    for size in icon_sizes:
        resized = source.resize((size, size), Image.LANCZOS)
        filename = ICONSET_DIR / f"icon_{size}x{size}.png"
        resized.save(filename)
        if size != 1024:
            retina = source.resize((size * 2, size * 2), Image.LANCZOS)
            retina.save(ICONSET_DIR / f"icon_{size}x{size}@2x.png")

    subprocess.run(["iconutil", "-c", "icns", str(ICONSET_DIR), "-o", str(ICNS_ICON)], check=True)


def main() -> None:
    build_png_and_ico()
    build_icns()
    print(f"Generated assets in {GENERATED_DIR}")


if __name__ == "__main__":
    main()
