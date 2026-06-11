"""pdf2pic: PDF pages → clipboard long images."""
import sys, time, csv, ctypes
from pathlib import Path
from datetime import datetime
from io import BytesIO

import fitz
from PIL import Image

# Win32 clipboard via ctypes (no pywin32 needed)
CF_DIB = 8
GMEM_MOVEABLE = 0x0002
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
kernel32.GlobalAlloc.restype = ctypes.c_void_p
kernel32.GlobalAlloc.argtypes = [ctypes.c_uint, ctypes.c_size_t]
kernel32.GlobalLock.restype = ctypes.c_void_p
kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
user32.SetClipboardData.argtypes = [ctypes.c_uint, ctypes.c_void_p]


def render_page(doc, idx, dpi=150):
    pix = doc[idx].get_pixmap(matrix=fitz.Matrix(dpi / 72, dpi / 72))
    return Image.frombytes("RGB", [pix.width, pix.height], pix.samples)


def vconcat(imgs):
    w = max(i.width for i in imgs)
    h = sum(i.height for i in imgs)
    out = Image.new("RGB", (w, h))
    y = 0
    for i in imgs:
        out.paste(i, (0, y))
        y += i.height
    return out


def to_clipboard(img):
    buf = BytesIO()
    img.convert("RGB").save(buf, "BMP")
    dib = buf.getvalue()[14:]  # strip BITMAPFILEHEADER (14 bytes)
    buf.close()

    h = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(dib))
    p = kernel32.GlobalLock(h)
    ctypes.memmove(p, dib, len(dib))
    kernel32.GlobalUnlock(h)

    user32.OpenClipboard(0)
    user32.EmptyClipboard()
    user32.SetClipboardData(CF_DIB, h)
    user32.CloseClipboard()


def log_index(csv_path, start, end):
    header = not csv_path.exists()
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if header:
            w.writerow(["timestamp", "start", "end", "label"])
        w.writerow([datetime.now().isoformat(timespec="seconds"), start, end, ""])


def main():
    if len(sys.argv) < 2:
        print("Usage: pdf2pic <path-to.pdf> [-i|--index]")
        sys.exit(1)

    enable_index = any(arg in {"-i", "--index"} for arg in sys.argv[2:])
    pdf = Path(sys.argv[1]).resolve()
    if not pdf.exists():
        print(f"not found: {pdf}")
        sys.exit(1)

    doc = fitz.open(str(pdf))
    n = len(doc)
    idx_csv = pdf.parent / f"{pdf.stem}.index.csv"

    print(f"[pdf2pic] {pdf.name} ({n} pages)")
    print("  format: <start>,<count> [-l<N>]  default -l2")
    print("  quit: q\n")

    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not raw or raw.lower() == "q":
            break

        # parse
        le = 3  # default long-edge
        tokens = raw.split()
        for t in tokens[1:]:
            if t.lower().startswith("-l"):
                try:
                    le = int(t[2:])
                except ValueError:
                    pass

        try:
            s, c = map(int, tokens[0].split(","))
        except ValueError:
            print("  bad format, try: 3,3 or 3,3 -l3")
            continue

        if s < 1 or s > n:
            print(f"  start must be 1..{n}")
            continue
        if c < 1:
            print("  count must be >= 1")
            continue

        end = min(s + c - 1, n)
        pages = [render_page(doc, i) for i in range(s - 1, end)]

        # chunk → concat → clipboard
        num_chunks = 0
        for i in range(0, len(pages), le):
            grp = pages[i : i + le]
            cs, ce = s + i, s + i + len(grp) - 1
            cat = vconcat(grp) if len(grp) > 1 else grp[0]

            if num_chunks > 0:
                time.sleep(0.6)  # let clipboard history register previous item

            to_clipboard(cat)
            if enable_index:
                log_index(idx_csv, cs, ce)
            label = f"{cs}-{ce}" if cs != ce else str(cs)
            print(f"  → {label}.png  (copied)")

            if cat is not grp[0]:
                cat.close()
            num_chunks += 1

        for p in pages:
            p.close()

    doc.close()
    print("[pdf2pic] bye")


if __name__ == "__main__":
    main()
