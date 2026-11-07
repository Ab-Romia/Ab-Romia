"""Turn tools/portrait.jpg into tools/portrait.txt: a grid of tones, 0 to 9,
with a space wherever the background was. draw.py prints it as dots.

The cut-out is GrabCut with a few hints, because the photo was taken against
a bright sky and a pyramid: the hat's patch and the face are marked as the
subject, the sky and the stones beside the shoulder as background. Tones are
contrast-normalised locally, so the eyes and the smile survive the shade of
the hat's brim.

    python3 tools/portrait.py        (needs opencv-python and numpy)
"""

from pathlib import Path

import cv2
import numpy as np

TOOLS = Path(__file__).resolve().parent
COLS = 72


def subject(img: np.ndarray) -> np.ndarray:
    h, w = img.shape[:2]
    mask = np.full((h, w), cv2.GC_BGD, np.uint8)
    mask[100:990, 20:850] = cv2.GC_PR_FGD
    mask[175:280, 490:660] = cv2.GC_FGD   # the hat's patch
    mask[290:370, 380:540] = cv2.GC_FGD   # the hat band beside it
    mask[420:900, 300:660] = cv2.GC_FGD   # the face
    mask[740:990, 780:880] = cv2.GC_BGD   # stones beside the shoulder
    mask[100:200, 680:880] = cv2.GC_BGD   # sky above the brim
    cv2.grabCut(img, mask, None, np.zeros((1, 65)), np.zeros((1, 65)), 8, cv2.GC_INIT_WITH_MASK)
    fg = np.isin(mask, (cv2.GC_FGD, cv2.GC_PR_FGD)).astype(np.uint8)
    b, r = img[:, :, 0].astype(int), img[:, :, 2].astype(int)
    fg[(b > r + 10) & (b > 150)] = 0  # any sky left
    _, label, stats, _ = cv2.connectedComponentsWithStats(fg)
    fg = (label == 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
    outline, _ = cv2.findContours(fg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    fg = cv2.drawContours(np.zeros_like(fg), outline, -1, 1, -1)
    fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, np.ones((31, 31), np.uint8))
    return cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((15, 15), np.uint8))


def tones(img: np.ndarray, fg: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(float) / 255
    lo, hi = np.percentile(gray[fg.astype(bool)], [3, 97])
    overall = np.clip((gray - lo) / (hi - lo), 0, 1)
    mean = cv2.GaussianBlur(gray, (0, 0), 30)
    spread = np.sqrt(cv2.GaussianBlur((gray - mean) ** 2, (0, 0), 30) + 1e-4)
    local = 1 / (1 + np.exp(-1.3 * (gray - mean) / spread))
    return 0.75 * local + 0.25 * overall


def main() -> None:
    img = cv2.imread(str(TOOLS / "portrait.jpg"))
    fg = subject(img)
    ys, xs = np.nonzero(fg)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    rows = round((y1 - y0) / (x1 - x0) * COLS)
    size = (COLS, rows)
    tone = cv2.resize(tones(img, fg)[y0:y1, x0:x1], size, interpolation=cv2.INTER_AREA)
    keep = cv2.resize(fg[y0:y1, x0:x1].astype(float), size, interpolation=cv2.INTER_AREA) >= 0.5
    lines = ["".join(str(min(9, int(tone[y, x] * 10))) if keep[y, x] else " " for x in range(COLS)).rstrip()
             for y in range(rows)]
    (TOOLS / "portrait.txt").write_text("\n".join(lines) + "\n")
    print(f"tools/portrait.txt  {COLS} x {rows}")


if __name__ == "__main__":
    main()
