import argparse
import os
import re
from PIL import Image
import numpy as np


def parse_hex_color(s: str):
    """Parse a hex color like '#A5CF53' or 'A5CF53' or 'fff' into an (R, G, B) tuple."""
    if s.startswith('#'):
        s = s[1:]
    if len(s) == 3:
        s = ''.join(ch * 2 for ch in s)
    if not re.fullmatch(r'[0-9a-fA-F]{6}', s):
        raise argparse.ArgumentTypeError(f"Invalid hex color: '{s}'. Use formats like '#A5CF53' or 'A5CF53' or 'fff'.")
    r = int(s[0:2], 16)
    g = int(s[2:4], 16)
    b = int(s[4:6], 16)
    return (r, g, b)


def main():
    parser = argparse.ArgumentParser(description='Change a specific red area in an image to a new color')

    # Positional arguments with defaults, and backwards-compatible flags
    parser.add_argument('input', nargs='?', default='input.webp', help='Input filename (default: input.webp)')
    parser.add_argument('output', nargs='?', default='output.png', help='Output filename (default: output.png)')
    parser.add_argument('-i', '--input-file', dest='input', help=argparse.SUPPRESS)
    parser.add_argument('-o', '--output-file', dest='output', help=argparse.SUPPRESS)

    parser.add_argument('--to-color', '--color', dest='to_color', default='#A5CF53', type=parse_hex_color,
                        help="Replacement (target) color in hex (e.g. '#A5CF53' or 'A5CF53' or 'fff'). Default: #A5CF53 (alias: --color)")

    parser.add_argument('-f', '--from-color', dest='from_color', type=parse_hex_color,
                        help="Original/source color to replace (hex). If omitted, uses the default red-mask heuristic.")
    parser.add_argument('-t', '--tolerance', dest='tolerance', type=int, default=60,
                        help="Color distance tolerance (0-441). Only used when --from-color is provided. Default: 60")

    args = parser.parse_args()

    if args.tolerance < 0:
        raise SystemExit("--tolerance must be non-negative")

    if not os.path.isfile(args.input):
        raise SystemExit(f"Input file not found: {args.input}")

    # Load the image
    img = Image.open(args.input).convert("RGBA")
    arr = np.array(img)

    # Split channels
    r, g, b, a = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2], arr[:, :, 3]

    # Build mask: either color-distance from --from-color, or the original red heuristic
    if args.from_color is not None:
        fr, fg, fb = args.from_color
        # promote to signed to avoid uint8 wraparound on subtraction
        rr = r.astype(np.int16)
        gg = g.astype(np.int16)
        bb = b.astype(np.int16)
        dist2 = (rr - fr) ** 2 + (gg - fg) ** 2 + (bb - fb) ** 2
        mask = dist2 <= (args.tolerance ** 2)
    else:
        mask = (r > 150) & (g < 100) & (b < 100)

    # Apply new color
    color_rgb = args.to_color  # tuple (R, G, B)
    arr[mask, 0:3] = color_rgb

    # Save result
    Image.fromarray(arr).save(args.output)
    if args.from_color is not None:
        print(f"Saved result to {args.output} (replaced #{args.from_color[0]:02X}{args.from_color[1]:02X}{args.from_color[2]:02X} with #{color_rgb[0]:02X}{color_rgb[1]:02X}{color_rgb[2]:02X}, tolerance={args.tolerance})")
    else:
        print(f"Saved result to {args.output} (color: #{color_rgb[0]:02X}{color_rgb[1]:02X}{color_rgb[2]:02X})")


if __name__ == '__main__':
    main()
