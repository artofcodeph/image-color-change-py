"""cc.py — small utility to replace a color region in an image.

This module is organized in small, testable functions:
- parse_hex_color
- compute_mask
- apply_target_color
- change_color_in_image (orchestrator)
- CLI entrypoint via main()
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
from typing import Optional, Tuple

from PIL import Image
import numpy as np


ColorRGB = Tuple[int, int, int]


def parse_hex_color(s: str) -> ColorRGB:
    """Parse a hex color like '#A5CF53' or 'A5CF53' or 'fff' into an (R, G, B) tuple."""
    if s.startswith('#'):
        s = s[1:]
    if len(s) == 3:
        s = ''.join(ch * 2 for ch in s)
    if not re.fullmatch(r'[0-9a-fA-F]{6}', s):
        raise argparse.ArgumentTypeError(
            f"Invalid hex color: '{s}'. Use formats like '#A5CF53' or 'A5CF53' or 'fff'."
        )
    r = int(s[0:2], 16)
    g = int(s[2:4], 16)
    b = int(s[4:6], 16)
    return (r, g, b)


def _ensure_exists(path: Path) -> None:
    if not path.is_file():
        raise SystemExit(f"Input file not found: {path}")


def load_image_as_array(path: Path) -> np.ndarray:
    """Load an image and return an RGBA NumPy array."""
    img = Image.open(path).convert("RGBA")
    return np.array(img)


def save_array_as_image(arr: np.ndarray, path: Path) -> None:
    Image.fromarray(arr).save(path)


def compute_mask(arr: np.ndarray, from_color: Optional[ColorRGB], tolerance: int = 60) -> np.ndarray:
    """Return a boolean mask selecting pixels to replace.

    If `from_color` is provided, select pixels within Euclidean RGB distance <= tolerance.
    Otherwise fallback to the original heuristic (red-ish area).
    """
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]

    if from_color is not None:
        fr, fg, fb = from_color
        # promote to signed to avoid uint8 wraparound on subtraction
        rr = r.astype(np.int16)
        gg = g.astype(np.int16)
        bb = b.astype(np.int16)
        dist2 = (rr - fr) ** 2 + (gg - fg) ** 2 + (bb - fb) ** 2
        return dist2 <= (tolerance ** 2)

    # original heuristic: tuned for typical red area
    return (r > 150) & (g < 100) & (b < 100)


def apply_target_color(arr: np.ndarray, mask: np.ndarray, to_color: ColorRGB) -> np.ndarray:
    """Return a copy of `arr` with masked pixels replaced with `to_color`.

    Operates on the first three channels (RGB) and preserves alpha.
    """
    out = arr.copy()
    out[mask, 0:3] = to_color
    return out


@dataclass
class ChangeResult:
    output_path: Path
    replaced_from: Optional[ColorRGB]
    replaced_to: ColorRGB
    tolerance: int


def change_color_in_image(input_path: Path, output_path: Path, to_color: ColorRGB,
                          from_color: Optional[ColorRGB] = None, tolerance: int = 60) -> ChangeResult:
    _ensure_exists(input_path)

    arr = load_image_as_array(input_path)
    mask = compute_mask(arr, from_color, tolerance=tolerance)
    out = apply_target_color(arr, mask, to_color)
    save_array_as_image(out, output_path)

    return ChangeResult(output_path, from_color, to_color, tolerance)


def format_color_hex(c: ColorRGB) -> str:
    return f"#{c[0]:02X}{c[1]:02X}{c[2]:02X}"


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Change a specific red area in an image to a new color')

    # Positional arguments with defaults
    parser.add_argument('input', nargs='?', default='input.webp', help='Input filename (default: input.webp)')
    parser.add_argument('output', nargs='?', default='output.png', help='Output filename (default: output.png)')

    # Backwards-compatible optional flags use distinct dest names to avoid colliding with positional names
    parser.add_argument('-i', '--input-file', dest='input_file', help='Input filename (alias for positional input)')
    parser.add_argument('-o', '--output-file', dest='output_file', help='Output filename (alias for positional output)')

    parser.add_argument('--to-color', '--color', dest='to_color', default='#A5CF53', type=parse_hex_color,
                        help="Replacement (target) color in hex (e.g. '#A5CF53' or 'A5CF53' or 'fff'). Default: #A5CF53 (alias: --color)")

    parser.add_argument('-f', '--from-color', dest='from_color', type=parse_hex_color,
                        help="Original/source color to replace (hex). If omitted, uses the default red-mask heuristic.")
    parser.add_argument('-t', '--tolerance', dest='tolerance', type=int, default=60,
                        help="Color distance tolerance (0-441). Only used when --from-color is provided. Default: 60")

    args = parser.parse_args(argv)

    # Map flag aliases into positional attributes if provided
    if getattr(args, 'input_file', None):
        args.input = args.input_file
    if getattr(args, 'output_file', None):
        args.output = args.output_file

    return args


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)

    if args.tolerance < 0:
        raise SystemExit("--tolerance must be non-negative")

    input_path = Path(args.input)
    output_path = Path(args.output)

    result = change_color_in_image(input_path, output_path, args.to_color, args.from_color, args.tolerance)

    if result.replaced_from is not None:
        print(f"Saved result to {result.output_path} (replaced {format_color_hex(result.replaced_from)} with {format_color_hex(result.replaced_to)}, tolerance={result.tolerance})")
    else:
        print(f"Saved result to {result.output_path} (color: {format_color_hex(result.replaced_to)})")

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
