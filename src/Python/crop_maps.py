

# --- SETTINGS (edit these) ----------------------------------------------------
# Folder with input PNGs
INPUT_DIR = r"C:/Users/JG/Desktop/_maps_onestop_v02"     # e.g., r"/mnt/data"
# C:\Users\JG\Desktop\_maps_onestop_v02

# Where to save cropped PNGs (creates the folder if missing)
OUTPUT_DIR = r"C:/Users/JG/Desktop/_maps_onestop_v02_crop"  # e.g., r"/mnt/data/cropped"
# C:\Users\JG\Desktop\_maps_onestop_v02_crop

# Crop amounts for each side. Use pixels (e.g., 120) or percentages (e.g., "5%").
CROP_TOP = 600      # amount to remove from the top
CROP_BOTTOM = 600    # amount to remove from the bottom
CROP_RIGHT = 500    # amount to remove from the right
# -----------------------------------------------------------------------------


from pathlib import Path
from PIL import Image

_MIN_W, _MIN_H = 1, 1  # never output 0x0

def _parse_crop(value, size_px: int) -> int:
    """Accept pixel ints (e.g., 120) or percentages as strings (e.g., '5%')."""
    if isinstance(value, str) and value.strip().endswith("%"):
        pct = float(value.strip()[:-1])
        return int(round(size_px * (pct / 100.0)))
    return int(value)

def _clamp(v: int, lo: int, hi: int) -> int:
    return max(lo, min(v, hi))

def crop_folder(input_dir: str, output_dir: str, top, bottom, right) -> list[str]:
    """
    Crop TOP, BOTTOM, RIGHT from every PNG in input_dir; return output paths.
    Hard-clamps requests so the result is always at least 1×1 px.
    """
    in_dir = Path(input_dir)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    outputs: list[str] = []
    for path in sorted(in_dir.glob("*.png")):
        with Image.open(path) as im:
            w, h = im.size

            # Parse user requests (pixels or percentages)
            req_top = _parse_crop(top, h)
            req_bottom = _parse_crop(bottom, h)
            req_right = _parse_crop(right, w)

            # Clamp each side so a 1-pixel image is still possible
            top_px   = _clamp(req_top,   0, max(0, h - _MIN_H))
            right_px = _clamp(req_right, 0, max(0, w - _MIN_W))
            # After fixing top, limit bottom so height remains >= 1
            max_bottom = max(0, h - top_px - _MIN_H)
            bottom_px  = _clamp(req_bottom, 0, max_bottom)

            # Compute final crop box (left, upper, right, lower)
            left = 0
            upper = top_px
            new_right = w - right_px
            lower = h - bottom_px

            # Final safety (shouldn’t trigger now)
            if new_right - left < _MIN_W or lower - upper < _MIN_H:
                # Auto-relax bottom/top if a rounding made it 0
                lower = max(upper + _MIN_H, lower)
                new_right = max(left + _MIN_W, new_right)

            # Optional: convert to RGBA to avoid rare save issues with palette PNGs
            out = im.convert("RGBA").crop((left, upper, new_right, lower))

            out_path = out_dir / path.name
            out.save(out_path)

            # Helpful log so you see the *effective* crops used
            eff_w, eff_h = out.size
            print(
                f"{path.name}: size {w}x{h} -> {eff_w}x{eff_h}  "
                f"(top={top_px}, bottom={bottom_px}, right={right_px})"
            )
            outputs.append(str(out_path))

    return outputs


if __name__ == "__main__":
    # Change the settings above, then run this file from VS Code.
    paths = crop_folder(INPUT_DIR, OUTPUT_DIR, CROP_TOP, CROP_BOTTOM, CROP_RIGHT)
    print(f"Cropped {len(paths)} PNG(s). Saved to: {OUTPUT_DIR}")
    for p in paths:
        print(p)
