# colorchange

> Simple script to replace a color (or a heuristically-detected red area) in an image with another color.

## 🔧 Requirements

- Python 3.8+
- Pillow
- NumPy

Install dependencies:

```bash
python -m pip install --upgrade pip
pip install pillow numpy
```

## ▶️ Usage

```bash
python cc.py [input] [output] [options]
```

- `input` and `output` are optional positional arguments (defaults: `input.webp`, `output.png`).
- Flags (backwards compatible): `-i / --input-file`, `-o / --output-file` (these map to the same `input` and `output` values).

### Options

- `--to-color <hex>` (alias: `--color`)
  - Replacement/target color in hex (examples: `#A5CF53`, `A5CF53`, `fff`). Default: `#A5CF53`.

- `-f, --from-color <hex>`
  - The source/original color to replace. When provided, the script replaces pixels close to this color (see `--tolerance`). If omitted, the script uses a heuristic that targets a red-ish area (the original behavior).

- `-t, --tolerance <int>`
  - Color-distance tolerance for `--from-color`. Integer ≥ 0 (default: `60`). Distance is Euclidean in RGB-space; max theoretical distance ≈ 441.

## 🔍 Examples

- Use defaults (reads `input.webp`, writes `output.png`):

```bash
python cc.py
```

- Positional files:

```bash
python cc.py my_input.webp result.png --to-color #00FF00
```

- Replace a specific source color (within tolerance):

```bash
python cc.py -i in.png -o out.png -f E02020 --to-color A5CF53 -t 50
```

- Using short flags (backwards compatible):

```bash
python cc.py -i in.png -o out.png --to-color fff
```

## Notes & Tips

- If you want more control over what gets selected, provide `--from-color` and tune `--tolerance`.
- For images with compression artifacts or gradients, a larger tolerance helps capture similar colors.
- The script operates on the RGBA image, preserving alpha.

## Contributing

Found a bug or want a feature (e.g., preview mode)? Open an issue or a PR with an example input image and desired output.

---

Made with ❤️ — `cc.py`
