# ░▒▓ MATRIX ▓▒░

**A Matrix-style waterfall animation for your terminal.**  
Full RGB color, 9 built-in presets, TUI config editor, standalone `.exe`.

> **Disclaimer:** This is an independent personal project by [mietek64](https://github.com/mietek64).  
> It is **not affiliated with, endorsed by, or related to** *The Matrix* film franchise,  
> Warner Bros., Village Roadshow Pictures, or any associated rights holders.  
> The name refers to the classic "digital rain" terminal aesthetic, not the movie.

---

## Preview

```
 ｦ                ｦ         ｦ
 ｧ  ｦ             ｱ         ｷ
 ｨ  ｧ    ｦ        ｲ  ｦ      ｸ
 ｩ  ｨ    ｧ        ｳ  ｧ  ｦ   ｹ
    ｩ    ｨ           ｨ  ｧ
         ｩ              ｨ
```

Features: **full RGB color**, **9 built-in presets**, **wave / sparkle / tilt / glitch effects**,  
**ASCII art title banners**, color cycling — all configurable through a TUI editor or plain JSON.

---

## Install

### Windows — one download, no Python needed

1. Download **[matrix.exe](https://github.com/mietek64/Matrix/releases/latest/download/matrix.exe)** from Releases
2. Move it to a permanent folder — e.g. `C:\tools\`
3. Add that folder to your PATH *(one-time, 30 seconds)*:
   - Press `Win + R` → type `sysdm.cpl` → Enter
   - **Advanced** tab → **Environment Variables**
   - Under *User variables*, select **Path** → **Edit** → **New** → paste `C:\tools`
   - Click OK, open a **new** terminal window
4. Type `matrix` ✓

> **Antivirus note:** Windows Defender may flag PyInstaller-packaged executables.  
> This is a known false positive with PyInstaller's bootloader — the source code is fully visible above.  
> You can build it yourself from source if you prefer (see [Build from Source](#build-from-source)).

### Linux / macOS

```bash
curl -fsSL https://github.com/mietek64/Matrix/releases/latest/download/matrix-linux \
  -o matrix && chmod +x matrix && sudo mv matrix /usr/local/bin/
matrix
```

---

## Usage

```
matrix                  show help & live preview
matrix -s               start the animation
matrix -c               open config editor
matrix -p               browse & run presets
matrix -s -f theme.json start with a custom config file
```

Press **Q** or **Ctrl-C** to quit the animation.

---

## Presets

Run `matrix -p` to open the preset browser. Pick a number, press `r` to run or `s` to save as default.

| Preset | Description |
|--------|-------------|
| Classic Matrix | Green katakana cascading through darkness |
| Cyber Blue | Cyan hex rain with sparkle |
| Blood Rain | Slow crimson latin script |
| Binary Storm | Dense white binary at full speed |
| Ghost Wave | Dim katakana with vignette and rolling wave |
| Neon Glitch | Magenta cycling hue — maximum chaos |
| Tilt Cascade | Diagonal wind-blown green rain |
| Deep Space | Sparse dark-green meditative rain |
| Golden Code | Warm amber hex with slow hue drift |

Save any config as a **custom preset** with `n` inside the preset browser.

---

## Configuration

Config is created automatically at first save:
- **Windows:** `%APPDATA%\matrix\config.json`
- **Linux/macOS:** `~/.config/matrix/config.json`

Edit it with the built-in editor (`matrix -c`) or any text editor. All keys and their meaning:

| Key | Default | Description |
|-----|---------|-------------|
| `chars` | `katakana` | `katakana` `latin` `numbers` `binary` `symbols` `hex` `mixed` `custom` |
| `custom_chars` | `""` | Your own character string (only used when `chars = custom`) |
| `color` | `#00cc44` | Stream color — Rich name, `#rrggbb`, or `rgb(r,g,b)` |
| `head_color` | `bright_white` | Color of the leading character on each stream |
| `speed` | `0.05` | Seconds per frame — lower = faster (0.01–0.50) |
| `density` | `0.04` | Stream spawn probability per column per tick (0–0.30) |
| `trail_length` | `20` | Characters per falling stream (3–80) |
| `head_bright` | `true` | Render leading character in `head_color` |
| `glitch` | `true` | Random ambient stray characters |
| `glitch_chance` | `0.02` | Glitch intensity (0.001 subtle → 0.20 chaos) |
| `sparkle` | `false` | Stream cells randomly flash bright |
| `sparkle_chance` | `0.04` | Fraction of stream cells that sparkle per frame |
| `fade_edges` | `false` | Vignette — dims streams near screen edges |
| `wave` | `false` | Sinusoidal density ripple across columns |
| `wave_speed` | `1.0` | Wave travel speed (0.1–10.0) |
| `rain_tilt` | `0` | Diagonal slant (−5 left → 0 straight → 5 right) |
| `color_cycle` | `false` | Slowly rotate stream hue over time |
| `color_cycle_speed` | `0.5` | Hue rotation speed (0.05–5.0) |
| `title` | `""` | Text shown on screen (empty = hidden) |
| `title_position` | `top-center` | `top-left` `top-center` `top-right` `center-center` |
| `title_style` | `text` | `text` or `ascii` (ASCII art via pyfiglet) |
| `ascii_font` | `standard` | Figlet font name — e.g. `doom` `big` `slant` |
| `ascii_size` | `medium` | Font group fallback: `small` `medium` `large` |
| `title_color` | `""` | Title text color (empty = stream color) |
| `title_bg` | `""` | Title background (empty = black) |
| `exit_hint` | `true` | Show `Q quit` hint in bottom-right corner |

---

## Build from Source

Requires **Python 3.13**.

```powershell
# Install dependencies
py -3.13 -m pip install pyinstaller pyfiglet rich

# Build (Windows — run as one command)
py -3.13 -m PyInstaller --onefile --console --name matrix `
  --hidden-import pyfiglet --hidden-import pyfiglet.fonts --hidden-import rich `
  "--add-data=$(py -3.13 -c 'import pyfiglet,os;print(os.path.dirname(pyfiglet.__file__))');pyfiglet" `
  --exclude-module tkinter --exclude-module unittest `
  --exclude-module email --exclude-module http `
  matrix.py
```

```bash
# Linux / macOS
python3.13 -m pip install pyinstaller pyfiglet rich

python3.13 -m PyInstaller --onefile --console --name matrix \
  --hidden-import pyfiglet --hidden-import pyfiglet.fonts --hidden-import rich \
  --add-data "$(python3.13 -c 'import pyfiglet,os;print(os.path.dirname(pyfiglet.__file__))'):pyfiglet" \
  --exclude-module tkinter --exclude-module unittest \
  --exclude-module email --exclude-module http \
  matrix.py
```

Output: `dist/matrix.exe` (Windows) or `dist/matrix` (Linux/macOS).

---

## Project Structure

```
Matrix/
├── matrix.py              main script (all logic in one file)
├── config.json            default config template
├── pyproject.toml         package metadata
├── README.md
├── LICENSE
├── SECURITY.md
├── CONTRIBUTING.md
├── CHANGELOG.md
├── .gitignore
└── .github/
    ├── ISSUE_TEMPLATE/
    │   ├── bug_report.md
    │   └── feature_request.md
    └── PULL_REQUEST_TEMPLATE.md
```

---

## License

MIT — see [LICENSE](LICENSE).

---

*This project is not affiliated with The Matrix franchise. "Matrix rain" is a well-established term in the terminal/CLI community for this style of animation.*
