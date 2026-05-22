#!/usr/bin/env python3
"""Generate Open Graph cards for the site.

Requires Pillow:
  python3 -m pip install Pillow
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
WIDTH = 1200
HEIGHT = 630

COLORS = {
    "bg": "#19191D",
    "ink": "#ECECEF",
    "soft": "#B6B6BE",
    "mute": "#85858F",
    "accent": "#8FA3C2",
    "rule": "#303137",
}

FONT = "/System/Library/Fonts/SFNS.ttf"
MONO = "/System/Library/Fonts/SFNSMono.ttf"

PAGES = [
    {
        "output": "og.png",
        "eyebrow": "writing",
        "title": "spfpt",
        "subtitle": "Notes on engineering practice, LLM finetuning research, and building with AI agents.",
        "footer": "spfpt.github.io",
    },
    {
        "output": "claude-code-101/og.png",
        "eyebrow": "essay / may 2026 / 35 min",
        "title": "Claude Code, in production",
        "subtitle": "A working guide from first prompt to agentic workflows.",
        "footer": "spfpt.github.io/claude-code-101",
    },
]


def load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(path, size=size)
    except OSError:
        return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size=size)


def sans(size: int) -> ImageFont.FreeTypeFont:
    return load_font(FONT, size)


def mono(size: int) -> ImageFont.FreeTypeFont:
    return load_font(MONO, size)


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    line = ""

    for word in words:
        test = word if not line else f"{line} {word}"
        if draw.textbbox((0, 0), test, font=font)[2] <= max_width:
            line = test
            continue
        if line:
            lines.append(line)
        line = word

    if line:
        lines.append(line)
    return lines


def draw_mark(draw: ImageDraw.ImageDraw, x: int, y: int, scale: float = 1.0) -> None:
    points = [
        (x + 0 * scale, y + 0 * scale),
        (x + 36 * scale, y + 0 * scale),
        (x + 58 * scale, y + 18 * scale),
        (x + 36 * scale, y + 36 * scale),
        (x + 14 * scale, y + 36 * scale),
        (x - 8 * scale, y + 54 * scale),
        (x + 14 * scale, y + 72 * scale),
        (x + 58 * scale, y + 72 * scale),
    ]
    draw.line(points, fill=COLORS["accent"], width=max(3, int(9 * scale)), joint="curve")


def generate_card(page: dict[str, str]) -> None:
    image = Image.new("RGB", (WIDTH, HEIGHT), COLORS["bg"])
    draw = ImageDraw.Draw(image)

    draw.line((92, 90, 1108, 90), fill=COLORS["rule"], width=1)
    draw.line((92, 540, 1108, 540), fill=COLORS["rule"], width=1)

    draw_mark(draw, 96, 120, 0.72)
    draw.text((174, 121), "spfpt", fill=COLORS["ink"], font=sans(33))
    draw.text((92, 218), page["eyebrow"].upper(), fill=COLORS["accent"], font=mono(20))

    title_font = sans(76 if len(page["title"]) < 28 else 68)
    y = 262
    for line in wrap_text(draw, page["title"], title_font, 1016):
        draw.text((92, y), line, fill=COLORS["ink"], font=title_font)
        y += 82

    y += 22
    subtitle_font = sans(30)
    for line in wrap_text(draw, page["subtitle"], subtitle_font, 960)[:2]:
        draw.text((94, y), line, fill=COLORS["soft"], font=subtitle_font)
        y += 42

    draw.text((92, 563), page["footer"], fill=COLORS["mute"], font=mono(22))

    output = ROOT / page["output"]
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, optimize=True)
    print(f"generated {output.relative_to(ROOT)}")


def main() -> None:
    for page in PAGES:
        generate_card(page)


if __name__ == "__main__":
    main()
