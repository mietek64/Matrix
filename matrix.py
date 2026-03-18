#!/usr/bin/env python3
"""
matrix  —  Matrix waterfall terminal animation

  matrix          show this help screen
  matrix -s       start animation
  matrix -c       config editor
  matrix -p       preset browser
  matrix -s -f x.json   start with custom config
  Q / Ctrl-C  →  quit
"""

import argparse
import json
import math
import os
import random
import sys
import time
import threading

from rich.console import Console
from rich.live import Live
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns
from rich.align import Align
from rich.style import Style
from rich.rule import Rule
from rich import box

try:
    import pyfiglet
    HAS_FIGLET = True
except ImportError:
    HAS_FIGLET = False

__version__ = "1.1.0"

# ─────────────────────────────────────────────────────────────────────────────
#  Paths
# ─────────────────────────────────────────────────────────────────────────────

if sys.platform == "win32":
    _CFG_HOME = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "matrix")
else:
    _CFG_HOME = os.path.expanduser("~/.config/matrix")

DEFAULT_CONFIG_PATH = os.path.join(_CFG_HOME, "config.json")
CUSTOM_PRESETS_PATH = os.path.join(_CFG_HOME, "presets.json")

# ─────────────────────────────────────────────────────────────────────────────
#  Character sets
# ─────────────────────────────────────────────────────────────────────────────

CHAR_SETS = {
    # Half-width katakana — exactly 1 terminal column wide each
    "katakana": [chr(c) for c in range(0xFF66, 0xFF9E)],
    "latin":    list("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"),
    "numbers":  list("0123456789"),
    "binary":   list("01"),
    "symbols":  list("!@#$%^&*()_+-=[]{}|;:,.<>?/~`"),
    "hex":      list("0123456789ABCDEF"),
    "mixed":    [chr(c) for c in range(0xFF66, 0xFF9E)] + list("0123456789ABCDEFabcdef"),
}

FIGLET_FONTS = {
    "small":  ["mini",     "small",   "smscript", "smshadow", "smslant", "term"],
    "medium": ["standard", "script",  "shadow",   "slant",    "digital", "lean"],
    "large":  ["big",      "banner",  "block",    "doom",     "larry3d", "univers"],
}

# ─────────────────────────────────────────────────────────────────────────────
#  Default config
# ─────────────────────────────────────────────────────────────────────────────

DEFAULT_CONFIG: dict = {
    # characters
    "chars":             "katakana",
    "custom_chars":      "",
    # colors
    "color":             "#00cc44",
    "head_color":        "bright_white",
    # animation
    "speed":             0.05,
    "density":           0.04,
    "trail_length":      20,
    "head_bright":       True,
    # effects
    "glitch":            True,
    "glitch_chance":     0.02,
    "sparkle":           False,
    "sparkle_chance":    0.04,
    "fade_edges":        False,
    "wave":              False,
    "wave_speed":        1.0,
    "rain_tilt":         0,
    "color_cycle":       False,
    "color_cycle_speed": 0.5,
    # title
    "title":             "",
    "title_position":    "top-center",
    "title_color":       "",
    "title_bg":          "",
    "title_style":       "text",
    "ascii_font":        "standard",
    "ascii_size":        "medium",
    # ui
    "exit_hint":         True,
}

# ─────────────────────────────────────────────────────────────────────────────
#  Built-in presets
# ─────────────────────────────────────────────────────────────────────────────

BUILTIN_PRESETS: list[dict] = [
    {
        "id": "classic", "name": "Classic Matrix",
        "desc": "The original — green katakana cascading through darkness",
        "tags": ["chill", "iconic"],
        "config": {
            "chars": "katakana", "color": "#00cc44", "head_color": "bright_white",
            "speed": 0.05, "density": 0.04, "trail_length": 20,
            "glitch": True, "glitch_chance": 0.02,
        },
    },
    {
        "id": "cyber_blue", "name": "Cyber Blue",
        "desc": "Cool cyan hex rain — feels like hacking a server",
        "tags": ["cool", "cyber"],
        "config": {
            "chars": "hex", "color": "#00ccff", "head_color": "bright_white",
            "speed": 0.04, "density": 0.05, "trail_length": 25,
            "glitch": True, "glitch_chance": 0.03,
            "sparkle": True, "sparkle_chance": 0.05,
        },
    },
    {
        "id": "blood_rain", "name": "Blood Rain",
        "desc": "Slow crimson latin script dripping down the void",
        "tags": ["dark", "slow"],
        "config": {
            "chars": "latin", "color": "#cc0022", "head_color": "#ff4455",
            "speed": 0.09, "density": 0.025, "trail_length": 30,
            "glitch": True, "glitch_chance": 0.015, "fade_edges": True,
        },
    },
    {
        "id": "binary_storm", "name": "Binary Storm",
        "desc": "Blinding white binary at maximum density and speed",
        "tags": ["fast", "intense"],
        "config": {
            "chars": "binary", "color": "bright_white", "head_color": "bright_white",
            "speed": 0.02, "density": 0.12, "trail_length": 12,
            "glitch": True, "glitch_chance": 0.06,
            "sparkle": True, "sparkle_chance": 0.08,
        },
    },
    {
        "id": "ghost_wave", "name": "Ghost Wave",
        "desc": "Dim white katakana with vignette and a slow rolling wave",
        "tags": ["ambient", "slow"],
        "config": {
            "chars": "katakana", "color": "#aaaaaa", "head_color": "white",
            "speed": 0.07, "density": 0.035, "trail_length": 18,
            "glitch": False, "wave": True, "wave_speed": 0.8, "fade_edges": True,
        },
    },
    {
        "id": "neon_glitch", "name": "Neon Glitch",
        "desc": "Magenta mixed charset cycling hue — maximum chaos",
        "tags": ["wild", "colorful"],
        "config": {
            "chars": "mixed", "color": "#cc00ff", "head_color": "bright_white",
            "speed": 0.04, "density": 0.06, "trail_length": 22,
            "glitch": True, "glitch_chance": 0.07,
            "sparkle": True, "sparkle_chance": 0.06,
            "color_cycle": True, "color_cycle_speed": 1.5,
        },
    },
    {
        "id": "tilt_cascade", "name": "Tilt Cascade",
        "desc": "Diagonal green rain tilting right — like wind-blown code",
        "tags": ["unique", "tilted"],
        "config": {
            "chars": "katakana", "color": "#00dd55", "head_color": "bright_white",
            "speed": 0.05, "density": 0.045, "trail_length": 20,
            "rain_tilt": 3, "glitch": True, "glitch_chance": 0.02,
        },
    },
    {
        "id": "deep_space", "name": "Deep Space",
        "desc": "Sparse dark-green rain with a slow wave — meditative",
        "tags": ["chill", "sparse"],
        "config": {
            "chars": "katakana", "color": "#005522", "head_color": "#00ff88",
            "speed": 0.08, "density": 0.018, "trail_length": 28,
            "glitch": False, "wave": True, "wave_speed": 0.4,
            "sparkle": True, "sparkle_chance": 0.02, "fade_edges": True,
        },
    },
    {
        "id": "golden_code", "name": "Golden Code",
        "desc": "Warm amber hex streams with cycling hue drift",
        "tags": ["colorful", "warm"],
        "config": {
            "chars": "hex", "color": "#cc8800", "head_color": "bright_yellow",
            "speed": 0.05, "density": 0.05, "trail_length": 22,
            "glitch": True, "glitch_chance": 0.02,
            "color_cycle": True, "color_cycle_speed": 0.3,
        },
    },
]

# ─────────────────────────────────────────────────────────────────────────────
#  Config editor schema
# ─────────────────────────────────────────────────────────────────────────────

SCHEMA = [
    {"section": "CHARACTERS"},
    {"key": "chars",             "label": "Character Set",    "type": "choice",
     "choices": list(CHAR_SETS.keys()) + ["custom"],
     "hint": "katakana  latin  numbers  binary  symbols  hex  mixed  custom"},
    {"key": "custom_chars",      "label": "Custom Chars",     "type": "string",
     "hint": "any string  (only used when chars = custom)"},

    {"section": "COLORS"},
    {"key": "color",             "label": "Stream Color",     "type": "color",
     "hint": "name / #rrggbb / rgb(r,g,b)  e.g.  cyan  #ff0080"},
    {"key": "head_color",        "label": "Head Char Color",  "type": "color",
     "hint": "color of the leading character  e.g.  bright_white"},

    {"section": "ANIMATION"},
    {"key": "speed",             "label": "Frame Speed",      "type": "float", "min": 0.01, "max": 0.50,
     "hint": "seconds per frame  ·  lower = faster  (0.01 – 0.50)"},
    {"key": "density",           "label": "Stream Density",   "type": "float", "min": 0.0,  "max": 0.30,
     "hint": "spawn probability per column per tick  (0 = off  0.30 = dense)"},
    {"key": "trail_length",      "label": "Trail Length",     "type": "int",   "min": 3,    "max": 80,
     "hint": "characters per falling stream  (3 – 80)"},
    {"key": "head_bright",       "label": "Bright Head Char", "type": "bool",
     "hint": "render leading character in head_color"},

    {"section": "EFFECTS"},
    {"key": "glitch",            "label": "Glitch",           "type": "bool",
     "hint": "random ambient stray characters across the screen"},
    {"key": "glitch_chance",     "label": "Glitch Intensity", "type": "float", "min": 0.001, "max": 0.20,
     "hint": "0.001 = subtle   0.05 = noisy   0.20 = chaos"},
    {"key": "sparkle",           "label": "Sparkle",          "type": "bool",
     "hint": "random stream cells briefly flash bright"},
    {"key": "sparkle_chance",    "label": "Sparkle Chance",   "type": "float", "min": 0.001, "max": 0.30,
     "hint": "fraction of stream cells that sparkle per frame"},
    {"key": "fade_edges",        "label": "Fade Edges",       "type": "bool",
     "hint": "vignette — streams near screen edges rendered dimmer"},
    {"key": "wave",              "label": "Wave Effect",       "type": "bool",
     "hint": "sinusoidal density ripple sweeping across columns"},
    {"key": "wave_speed",        "label": "Wave Speed",        "type": "float", "min": 0.1, "max": 10.0,
     "hint": "0.1 = slow  10.0 = fast"},
    {"key": "rain_tilt",         "label": "Rain Tilt",         "type": "int",   "min": -5,  "max": 5,
     "hint": "diagonal slant  negative=left  0=straight  positive=right"},
    {"key": "color_cycle",       "label": "Color Cycle",       "type": "bool",
     "hint": "slowly cycle stream hue over time"},
    {"key": "color_cycle_speed", "label": "Cycle Speed",       "type": "float", "min": 0.05, "max": 5.0,
     "hint": "hue rotation speed  (0.05 = glacial  5.0 = rapid)"},

    {"section": "TITLE"},
    {"key": "title",             "label": "Banner Text",       "type": "string_clearable",
     "hint": "text shown on screen  ·  leave blank to clear"},
    {"key": "title_position",    "label": "Position",          "type": "choice",
     "choices": ["top-left", "top-center", "top-right", "center-center"],
     "hint": "top-left  top-center  top-right  center-center"},
    {"key": "title_style",       "label": "Style",             "type": "choice",
     "choices": ["text", "ascii"],
     "hint": "text = simple label   ascii = figlet art  (needs pyfiglet)"},
    {"key": "ascii_font",        "label": "ASCII Font",        "type": "string",
     "hint": "figlet font  e.g.  standard  big  slant  doom  larry3d"},
    {"key": "ascii_size",        "label": "ASCII Size",        "type": "choice",
     "choices": ["small", "medium", "large"],
     "hint": "small = mini   medium = standard/slant   large = big/doom"},
    {"key": "title_color",       "label": "Title Color",       "type": "color_clearable",
     "hint": "blank = use stream color  e.g.  bright_yellow  #ffcc00"},
    {"key": "title_bg",          "label": "Title Background",  "type": "color_clearable",
     "hint": "blank = black  e.g.  #001100"},

    {"section": "UI"},
    {"key": "exit_hint",         "label": "Show Exit Hint",    "type": "bool",
     "hint": "display  Q quit  in bottom-right corner"},
]

FIELDS = [f for f in SCHEMA if "key" in f]


# ═════════════════════════════════════════════════════════════════════════════
#  Config I/O
# ═════════════════════════════════════════════════════════════════════════════

def load_config_file(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        try:
            raw = json.load(f)
            return {k: v for k, v in raw.items() if not k.startswith("_")}
        except json.JSONDecodeError as e:
            Console().print(f"[red]✗ JSON error in '{path}': {e}[/]")
            return {}

def save_config_file(cfg: dict, path: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)

def build_config(path: str) -> dict:
    return {**DEFAULT_CONFIG, **load_config_file(path)}

def is_valid_color(v: str) -> bool:
    if not v:
        return False
    try:
        Style(color=v)
        return True
    except Exception:
        return False

def safe_color(v: str, fallback: str) -> str:
    return v if is_valid_color(str(v or "")) else fallback


# ═════════════════════════════════════════════════════════════════════════════
#  Custom presets I/O
# ═════════════════════════════════════════════════════════════════════════════

def load_custom_presets() -> list[dict]:
    if not os.path.exists(CUSTOM_PRESETS_PATH):
        return []
    with open(CUSTOM_PRESETS_PATH, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            return data if isinstance(data, list) else []
        except Exception:
            return []

def save_custom_presets(presets: list[dict]) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(CUSTOM_PRESETS_PATH)), exist_ok=True)
    with open(CUSTOM_PRESETS_PATH, "w", encoding="utf-8") as f:
        json.dump(presets, f, indent=2, ensure_ascii=False)


# ═════════════════════════════════════════════════════════════════════════════
#  Color cycling
# ═════════════════════════════════════════════════════════════════════════════

def _hex_to_rgb(h: str):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4)) if len(h) == 6 else None

def _hue_rotate(base_rgb, degrees: float) -> str:
    r, g, b   = (x / 255.0 for x in base_rgb)
    cos_a     = math.cos(math.radians(degrees))
    sin_a     = math.sin(math.radians(degrees))
    sq3, one3 = math.sqrt(1 / 3), (1 - cos_a) / 3
    m = [
        [cos_a + one3,       one3 - sin_a * sq3, one3 + sin_a * sq3],
        [one3 + sin_a * sq3, cos_a + one3,       one3 - sin_a * sq3],
        [one3 - sin_a * sq3, one3 + sin_a * sq3, cos_a + one3      ],
    ]
    nr = max(0.0, min(1.0, r * m[0][0] + g * m[0][1] + b * m[0][2]))
    ng = max(0.0, min(1.0, r * m[1][0] + g * m[1][1] + b * m[1][2]))
    nb = max(0.0, min(1.0, r * m[2][0] + g * m[2][1] + b * m[2][2]))
    return f"#{int(nr*255):02x}{int(ng*255):02x}{int(nb*255):02x}"


# ═════════════════════════════════════════════════════════════════════════════
#  Stream
# ═════════════════════════════════════════════════════════════════════════════

class Stream:
    def __init__(self, col: int, rows: int, trail: int, charset: list, tilt: int = 0):
        self.col     = col
        self.rows    = rows
        self.trail   = max(3, trail)
        self.charset = charset
        self.tilt    = tilt
        self.head    = random.randint(-self.trail, 0)
        self.step    = random.choice([1, 1, 1, 2])
        self.chars   = [random.choice(charset) for _ in range(self.trail)]
        self.alive   = True

    def tick(self):
        self.head += self.step
        self.chars[random.randrange(len(self.chars))] = random.choice(self.charset)
        if self.head - self.trail > self.rows:
            self.alive = False

    def cells(self):
        n = len(self.chars)
        for i, ch in enumerate(self.chars):
            row = self.head - (n - 1 - i)
            if 0 <= row < self.rows:
                col = self.col + int(row * self.tilt * 0.25)
                if i == n - 1:           key = "head"
                elif i >= n - 4:         key = "bright"
                elif i >= int(n * 0.55): key = "mid"
                else:                    key = "dim"
                yield row, col, ch, key


# ═════════════════════════════════════════════════════════════════════════════
#  Keyboard listener
# ═════════════════════════════════════════════════════════════════════════════

def keyboard_listener(stop_event: threading.Event) -> None:
    try:
        if sys.platform == "win32":
            import msvcrt
            while not stop_event.is_set():
                if msvcrt.kbhit():
                    ch = msvcrt.getch()
                    if ch in (b"q", b"Q", b"\x1b", b"\x03"):
                        stop_event.set(); break
                time.sleep(0.02)
        else:
            import tty, termios
            fd  = sys.stdin.fileno()
            old = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                while not stop_event.is_set():
                    ch = os.read(fd, 1)
                    if ch in (b"q", b"Q", b"\x1b", b"\x03"):
                        stop_event.set(); break
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old)
    except Exception:
        pass


# ═════════════════════════════════════════════════════════════════════════════
#  Style palette
# ═════════════════════════════════════════════════════════════════════════════

def build_styles(cfg: dict, cycled_color: str = "") -> dict:
    sc  = safe_color(cycled_color or cfg.get("color",      ""), "#00cc44")
    hc  = safe_color(cfg.get("head_color",  ""),                "bright_white")
    tc  = safe_color(cfg.get("title_color", ""),                sc)
    tbg = safe_color(cfg.get("title_bg",    ""),                "black")
    return {
        "head":    Style(color=hc, bold=True),
        "bright":  Style(color=sc, bold=True),
        "mid":     Style(color=sc),
        "dim":     Style(color=sc, dim=True),
        "edge":    Style(color=sc, dim=True),
        "sparkle": Style(color=hc, bold=True),
        "glitch":  Style(color=sc, dim=True),
        "title":   Style(color=tc, bgcolor=tbg, bold=True),
        "hint":    Style(color=sc, dim=True),
    }

def get_charset(cfg: dict) -> list:
    name = cfg.get("chars", "katakana")
    if name == "custom":
        c = cfg.get("custom_chars", "")
        return list(c) if c else CHAR_SETS["katakana"]
    return CHAR_SETS.get(name, CHAR_SETS["katakana"])


# ═════════════════════════════════════════════════════════════════════════════
#  ASCII title renderer
# ═════════════════════════════════════════════════════════════════════════════

def render_ascii_title(text: str, cfg: dict) -> list[str]:
    if not HAS_FIGLET or not text:
        return [text] if text else []
    font = str(cfg.get("ascii_font", "standard")).strip()
    try:
        pyfiglet.Figlet(font=font)
    except Exception:
        group = FIGLET_FONTS.get(cfg.get("ascii_size", "medium"), FIGLET_FONTS["medium"])
        font  = group[0]
    try:
        return pyfiglet.Figlet(font=font).renderText(text).rstrip("\n").split("\n")
    except Exception:
        return [text]


# ═════════════════════════════════════════════════════════════════════════════
#  Frame builder  —  stable 2D grid
# ═════════════════════════════════════════════════════════════════════════════

def build_frame(
    streams:     list,
    rows:        int,
    cols:        int,
    cfg:         dict,
    charset:     list,
    styles:      dict,
    tick:        int,
    ascii_cache: list | None,
) -> Text:
    grid: list[list] = [[None] * cols for _ in range(rows)]

    fade    = cfg.get("fade_edges", False)
    edge_w  = max(2, int(cols * 0.08))
    sparkle = cfg.get("sparkle", False)
    spark_p = float(cfg.get("sparkle_chance", 0.04))

    for s in streams:
        for row, col, ch, key in s.cells():
            if 0 <= col < cols and 0 <= row < rows:
                if fade:
                    dist = min(col, cols - 1 - col)
                    if dist < edge_w:
                        key = "dim" if dist > edge_w // 2 else "edge"
                if sparkle and key != "head" and random.random() < spark_p:
                    key = "sparkle"
                grid[row][col] = (ch, key)

    if cfg.get("glitch", True):
        n = max(1, int(cols * rows * float(cfg.get("glitch_chance", 0.02)) * 0.025))
        for _ in range(n):
            gr = random.randint(0, max(0, rows - 2))
            gc = random.randint(0, cols - 1)
            if grid[gr][gc] is None:
                grid[gr][gc] = (random.choice(charset), "glitch")

    raw_title = str(cfg.get("title", "")).strip()
    if raw_title:
        tstyle = cfg.get("title_style", "text")
        if tstyle == "ascii" and HAS_FIGLET:
            art_lines = ascii_cache if ascii_cache is not None else render_ascii_title(raw_title, cfg)
        else:
            art_lines = [f" {raw_title} "]

        art_lines = [l.rstrip() for l in art_lines]
        art_w     = max((len(l) for l in art_lines), default=0)
        art_lines = [l.ljust(art_w) for l in art_lines]
        art_h     = len(art_lines)

        pos = cfg.get("title_position", "top-center")
        if pos == "top-left":
            sr, sc_ = 0, 1
        elif pos == "top-right":
            sr, sc_ = 0, max(0, cols - art_w - 1)
        elif pos == "center-center":
            sr  = max(0, (rows - art_h) // 2)
            sc_ = max(0, (cols - art_w) // 2)
        else:
            sr, sc_ = 0, max(0, (cols - art_w) // 2)

        for li, line in enumerate(art_lines):
            r = sr + li
            if r >= rows:
                break
            for ci, ch in enumerate(line):
                c = sc_ + ci
                if 0 <= c < cols:
                    if ch != " ":
                        grid[r][c] = (ch, "title")
                    elif tstyle == "ascii":
                        grid[r][c] = (" ", "title")

    if cfg.get("exit_hint", True):
        hint  = " Q quit "
        h_row = rows - 1
        h_col = cols - len(hint)
        if h_col >= 0:
            for i, ch in enumerate(hint):
                grid[h_row][h_col + i] = (ch, "hint")

    frame = Text(no_wrap=True, overflow="crop")
    for r in range(rows):
        for c in range(cols):
            cell = grid[r][c]
            if cell:
                ch, key = cell
                frame.append(ch, style=styles.get(key, Style()))
            else:
                frame.append(" ")
        if r < rows - 1:
            frame.append("\n")
    return frame


# ═════════════════════════════════════════════════════════════════════════════
#  Animation runner
# ═════════════════════════════════════════════════════════════════════════════

def run_animation(cfg: dict) -> None:
    console    = Console(highlight=False)
    stop_event = threading.Event()
    kbd = threading.Thread(target=keyboard_listener, args=(stop_event,), daemon=True)
    kbd.start()

    charset   = get_charset(cfg)
    speed     = float(cfg.get("speed",             0.05))
    density   = float(cfg.get("density",            0.04))
    trail     = int(  cfg.get("trail_length",       20))
    tilt      = int(  cfg.get("rain_tilt",          0))
    wave      = bool( cfg.get("wave",               False))
    wave_spd  = float(cfg.get("wave_speed",         1.0))
    cycle     = bool( cfg.get("color_cycle",        False))
    cycle_spd = float(cfg.get("color_cycle_speed",  0.5))

    ascii_cache: list | None = None
    if cfg.get("title_style") == "ascii" and cfg.get("title") and HAS_FIGLET:
        ascii_cache = render_ascii_title(str(cfg.get("title", "")), cfg)

    base_color = safe_color(cfg.get("color", ""), "#00cc44")
    base_rgb   = _hex_to_rgb(base_color) if base_color.startswith("#") else None
    hue_offset = 0.0

    streams:   list  = []
    last_size: tuple = (0, 0)
    styles = build_styles(cfg)
    tick   = 0

    try:
        with Live("", console=console, screen=True,
                  auto_refresh=False, vertical_overflow="crop") as live:
            while not stop_event.is_set():
                cols = live.console.width
                rows = live.console.height

                if cols <= 0 or rows <= 0:
                    time.sleep(0.05); continue

                if (cols, rows) != last_size:
                    streams.clear()
                    styles    = build_styles(cfg)
                    last_size = (cols, rows)

                if cycle and base_rgb:
                    hue_offset = (hue_offset + cycle_spd) % 360
                    styles = build_styles(cfg, _hue_rotate(base_rgb, hue_offset))

                for c in range(cols):
                    col_density = density
                    if wave:
                        phase = (c / max(cols, 1)) * 2 * math.pi - tick * wave_spd * 0.08
                        col_density = density * (0.4 + 0.9 * (0.5 + 0.5 * math.sin(phase)))
                    if random.random() < col_density:
                        streams.append(Stream(c, rows, trail, charset, tilt))

                for s in streams:
                    s.tick()
                streams = [s for s in streams if s.alive]

                live.update(build_frame(streams, rows, cols, cfg, charset, styles, tick, ascii_cache))
                live.refresh()
                tick += 1
                time.sleep(speed)

    except KeyboardInterrupt:
        pass
    finally:
        stop_event.set()
        kbd.join(timeout=0.5)


# ═════════════════════════════════════════════════════════════════════════════
#  No-args splash screen
# ═════════════════════════════════════════════════════════════════════════════

def _mini_rain(width: int = 36, height: int = 8) -> Text:
    """Generate a static mini rain preview using unicode block chars."""
    charset = CHAR_SETS["katakana"]
    GRN     = "#00cc44"
    DIM_C   = "#005522"
    HEAD_C  = "bright_white"

    random.seed(42)   # deterministic so it looks the same every time
    grid: list[list] = [[None] * width for _ in range(height)]

    # Plant a fixed set of streams so the preview is always consistent
    for col in range(0, width, random.randint(2, 4)):
        trail_len = random.randint(3, height)
        head_row  = random.randint(1, height - 1)
        for offset in range(trail_len):
            row = head_row - offset
            if 0 <= row < height and col < width:
                ch = random.choice(charset)
                if offset == 0:
                    grid[row][col] = (ch, "head")
                elif offset < 3:
                    grid[row][col] = (ch, "bright")
                elif offset < trail_len * 0.6:
                    grid[row][col] = (ch, "mid")
                else:
                    grid[row][col] = (ch, "dim")

    random.seed()  # restore randomness

    frame = Text(no_wrap=True)
    for r in range(height):
        for c in range(width):
            cell = grid[r][c]
            if cell:
                ch, key = cell
                if key == "head":
                    frame.append(ch, style=Style(color=HEAD_C, bold=True))
                elif key == "bright":
                    frame.append(ch, style=Style(color=GRN, bold=True))
                elif key == "mid":
                    frame.append(ch, style=Style(color=GRN))
                else:
                    frame.append(ch, style=Style(color=DIM_C))
            else:
                frame.append(" ")
        if r < height - 1:
            frame.append("\n")
    return frame


def show_splash() -> None:
    """Displayed when matrix is run with no arguments."""
    console = Console()
    G  = "#00cc44"
    DG = "#005522"
    W  = "bright_white"

    console.print()

    # ── ASCII title ───────────────────────────────────────────────────────────
    if HAS_FIGLET:
        try:
            art_lines = pyfiglet.Figlet(font="doom").renderText("MATRIX").rstrip("\n").split("\n")
        except Exception:
            art_lines = ["  M A T R I X"]
    else:
        art_lines = ["  M A T R I X  —  terminal waterfall"]

    title_text = Text(justify="center")
    for line in art_lines:
        title_text.append(line + "\n", style=Style(color=G, bold=True))

    console.print(Align.center(title_text))
    console.print(Align.center(
        Text(f"v{__version__}  ·  terminal rain  ·  made by mietek64", style=Style(color=DG, dim=True))
    ))
    console.print()

    # ── Two-column layout: commands left, preview right ───────────────────────
    cmd_table = Table(
        box=box.SIMPLE, show_header=False, padding=(0, 2),
        border_style=Style(color=DG),
    )
    cmd_table.add_column("cmd",  style=Style(color=G,  bold=True), min_width=18)
    cmd_table.add_column("desc", style=Style(color=W, dim=True))

    commands = [
        ("matrix -s",          "start the animation"),
        ("matrix -c",          "open config editor"),
        ("matrix -p",          "browse & run presets"),
        ("matrix -s -f x.json","start with custom config file"),
        ("",                   ""),
        ("config file",        DEFAULT_CONFIG_PATH),
        ("presets file",       CUSTOM_PRESETS_PATH),
    ]
    for cmd, desc in commands:
        if cmd == "":
            cmd_table.add_row("", "")
        else:
            cmd_table.add_row(cmd, desc)

    preview_panel = Panel(
        _mini_rain(36, 9),
        border_style=DG,
        padding=(0, 1),
        subtitle=Text("preview", style=Style(color=DG, dim=True)),
    )

    console.print(Columns([
        Panel(cmd_table, border_style=DG, title=Text("commands", style=Style(color=G, dim=True)),
              title_align="left", padding=(0, 1)),
        preview_panel,
    ], equal=False, expand=True))

    # ── Tips ──────────────────────────────────────────────────────────────────
    tips = [
        "Run  matrix -c  to change color, speed, charset and more.",
        "Try presets first — run  matrix -p  to pick one.",
        "Save any preset as your default with  s  inside the preset browser.",
        "Set  title  in config for a custom banner on the rain screen.",
        f"Config lives at  {DEFAULT_CONFIG_PATH}",
        "Use  matrix -s -f mytheme.json  to run a separate theme file.",
    ]
    tip = random.choice(tips)
    console.print()
    console.print(Rule(style=DG))
    tip_line = Text(justify="center")
    tip_line.append("tip  ", style=Style(color=G, bold=True))
    tip_line.append(tip,     style=Style(color=W, dim=True))
    console.print(tip_line)
    console.print()


# ═════════════════════════════════════════════════════════════════════════════
#  Config editor helpers
# ═════════════════════════════════════════════════════════════════════════════

def _fmt_value(val, field: dict) -> Text:
    ftype = field.get("type", "string")
    t = Text()
    if ftype == "bool":
        t.append("✓  on" if val else "✗  off",
                 style=Style(color="green" if val else "bright_red", bold=bool(val)))
    elif ftype in ("color", "color_clearable"):
        v = str(val or "")
        if v and is_valid_color(v):
            t.append("██ ", style=Style(color=v, bold=True))
            t.append(v,    style=Style(bold=True))
        elif not v:
            t.append("(auto)", style=Style(dim=True))
        else:
            t.append(v, style=Style(color="red"))
    elif val is None or val == "":
        t.append("(none)", style=Style(dim=True))
    else:
        t.append(str(val))
    return t

def _edit_field(console: Console, cfg: dict, field: dict):
    ftype     = field["type"]
    clearable = ftype.endswith("_clearable")
    base_type = ftype.replace("_clearable", "")
    current   = cfg.get(field["key"])

    console.print()
    inner = Text()
    inner.append(f"{field['label']}\n\n",              style=Style(bold=True))
    inner.append("current  ",                           style=Style(dim=True))
    inner.append_text(_fmt_value(current, field))
    inner.append(f"\noptions  {field.get('hint','')}", style=Style(dim=True))
    inner.append(
        "\n\n  blank = clear   x = cancel" if clearable
        else "\n\n  blank = keep current   x = cancel",
        style=Style(dim=True),
    )
    console.print(Panel(inner, border_style="dim", padding=(0, 2)))

    try:
        raw = input("  › ").strip()
    except (EOFError, KeyboardInterrupt):
        return None

    if raw.lower() == "x":
        return None
    if raw == "":
        return "" if clearable else None

    if base_type == "bool":
        if raw.lower() in ("true",  "1", "yes", "y", "on"):  return True
        if raw.lower() in ("false", "0", "no",  "n", "off"): return False
        console.print("[red]  ✗  Enter true or false[/]"); time.sleep(1.2); return None
    if base_type == "float":
        try:    v = float(raw)
        except ValueError:
            console.print("[red]  ✗  Must be a number[/]"); time.sleep(1.2); return None
        lo, hi = field.get("min", -1e9), field.get("max", 1e9)
        if not lo <= v <= hi:
            console.print(f"[red]  ✗  Must be {lo}–{hi}[/]"); time.sleep(1.2); return None
        return v
    if base_type == "int":
        try:    v = int(raw)
        except ValueError:
            console.print("[red]  ✗  Must be a whole number[/]"); time.sleep(1.2); return None
        lo, hi = field.get("min", -99999), field.get("max", 99999)
        if not lo <= v <= hi:
            console.print(f"[red]  ✗  Must be {lo}–{hi}[/]"); time.sleep(1.2); return None
        return v
    if base_type == "choice":
        choices = field.get("choices", [])
        if raw in choices: return raw
        console.print(f"[red]  ✗  Choose: {', '.join(repr(c) for c in choices)}[/]")
        time.sleep(1.4); return None
    if base_type == "color":
        if is_valid_color(raw): return raw
        console.print("[red]  ✗  Invalid color  e.g.  green  #00ff80  rgb(0,255,128)[/]")
        time.sleep(1.4); return None
    return raw


# ═════════════════════════════════════════════════════════════════════════════
#  Config editor TUI
# ═════════════════════════════════════════════════════════════════════════════

def _draw_config_editor(console: Console, cfg: dict, path: str, modified: bool) -> None:
    console.clear()
    sc = safe_color(cfg.get("color", ""), "#00cc44")

    hdr = Text(justify="center")
    hdr.append("▓▒░  ",         style=Style(color=sc, dim=True))
    hdr.append("MATRIX CONFIG", style=Style(color=sc, bold=True))
    hdr.append("  ░▒▓",         style=Style(color=sc, dim=True))
    sub = Text(justify="center")
    sub.append(path, style=Style(dim=True))
    if modified:
        sub.append("  ●  unsaved", style=Style(color="yellow", bold=True))

    console.print(Panel(hdr, subtitle=sub, border_style=sc, box=box.DOUBLE_EDGE, padding=(0, 2)))

    table = Table(
        show_header=True, header_style=Style(color=sc, bold=True),
        border_style=Style(color=sc, dim=True), box=box.SIMPLE_HEAVY,
        padding=(0, 2), show_edge=True, min_width=78,
    )
    table.add_column(" # ", justify="right", style=Style(dim=True), width=4)
    table.add_column("Setting",               style=Style(bold=True), min_width=18)
    table.add_column("Value",                                          min_width=20)
    table.add_column("Options / Range",        style=Style(dim=True), min_width=36)

    n = 1
    for entry in SCHEMA:
        if "section" in entry:
            s = Text()
            s.append(f"  {entry['section']}", style=Style(color=sc, bold=True, dim=True))
            table.add_row("", s, Text(), Text(), style=Style(dim=True))
        else:
            table.add_row(str(n), entry["label"],
                          _fmt_value(cfg.get(entry["key"]), entry), entry.get("hint", ""))
            n += 1

    console.print(table)
    footer = Text()
    for key_label, key_col, desc in [
        ("number", sc,           " → edit      "),
        ("s",      "green",      " → save      "),
        ("r",      "yellow",     " → reset all      "),
        ("q",      "bright_red", " → quit"),
    ]:
        footer.append(f"  {key_label}", style=Style(color=key_col, bold=True))
        footer.append(desc,             style=Style(dim=True))
    console.print(footer)
    console.print()

def run_config_editor(cfg_path: str) -> None:
    console  = Console()
    cfg      = build_config(cfg_path)
    modified = False

    while True:
        _draw_config_editor(console, cfg, cfg_path, modified)
        try:
            choice = input("  › ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            break
        if choice == "q":
            if modified:
                try:
                    if input("  Save before quitting? [y/N]  › ").strip().lower() == "y":
                        save_config_file(cfg, cfg_path)
                        console.print(f"\n  [bold green]✓  Saved → {cfg_path}[/]\n")
                        time.sleep(0.8)
                except (EOFError, KeyboardInterrupt):
                    pass
            break
        elif choice == "s":
            save_config_file(cfg, cfg_path)
            console.print(f"\n  [bold green]✓  Saved → {cfg_path}[/]\n")
            modified = False; time.sleep(0.8)
        elif choice == "r":
            try:
                if input("  Reset ALL to defaults? [y/N]  › ").strip().lower() == "y":
                    cfg = dict(DEFAULT_CONFIG); modified = True
            except (EOFError, KeyboardInterrupt):
                pass
        else:
            try:
                idx = int(choice) - 1
            except ValueError:
                continue
            if 0 <= idx < len(FIELDS):
                new_val = _edit_field(console, cfg, FIELDS[idx])
                if new_val is not None or new_val == "":
                    cfg[FIELDS[idx]["key"]] = new_val if new_val is not None else ""
                    modified = True


# ═════════════════════════════════════════════════════════════════════════════
#  Preset browser TUI
# ═════════════════════════════════════════════════════════════════════════════

def _all_presets() -> list[dict]:
    return (
        [{**p, "_source": "builtin"} for p in BUILTIN_PRESETS] +
        [{**p, "_source": "custom"}  for p in load_custom_presets()]
    )

def _draw_preset_browser(console: Console, presets: list[dict], sc: str) -> None:
    console.clear()
    hdr = Text(justify="center")
    hdr.append("▓▒░  ",          style=Style(color=sc, dim=True))
    hdr.append("MATRIX PRESETS", style=Style(color=sc, bold=True))
    hdr.append("  ░▒▓",          style=Style(color=sc, dim=True))
    console.print(Panel(hdr, border_style=sc, box=box.DOUBLE_EDGE, padding=(0, 2)))

    table = Table(
        show_header=True, header_style=Style(color=sc, bold=True),
        border_style=Style(color=sc, dim=True), box=box.SIMPLE_HEAVY,
        padding=(0, 2), show_edge=True, min_width=70,
    )
    table.add_column(" # ", justify="right", style=Style(dim=True), width=4)
    table.add_column("Name",         style=Style(bold=True), min_width=20)
    table.add_column("Description",                           min_width=36)
    table.add_column("Source",       style=Style(dim=True),  width=8)

    for i, p in enumerate(presets, 1):
        src = Text()
        if p.get("_source") == "builtin":
            src.append("built-in", style=Style(color=sc, dim=True))
        else:
            src.append("custom",   style=Style(color="yellow"))
        table.add_row(str(i), p.get("name", "?"), p.get("desc", ""), src)

    console.print(table)
    footer = Text()
    footer.append("  number",  style=Style(color=sc,          bold=True))
    footer.append(" → select      ", style=Style(dim=True))
    footer.append("n",          style=Style(color="green",     bold=True))
    footer.append(" → save current config as preset      ", style=Style(dim=True))
    footer.append("q",          style=Style(color="bright_red", bold=True))
    footer.append(" → back",   style=Style(dim=True))
    console.print(footer); console.print()

def _preset_action(console: Console, preset: dict, cfg_path: str, sc: str) -> None:
    console.print()
    console.print(Panel(
        f"[bold]{preset.get('name','?')}[/]\n[dim]{preset.get('desc','')}[/]",
        border_style=sc, padding=(0, 2),
    ))
    console.print()
    console.print(f"  [bold {sc}]r[/]  [dim]run now (without saving)[/]")
    console.print(f"  [bold green]s[/]  [dim]save to config and run[/]")
    if preset.get("_source") == "custom":
        console.print(f"  [bold red]d[/]  [dim]delete this preset[/]")
    console.print(f"  [bold bright_red]x[/]  [dim]cancel[/]")
    console.print()
    try:
        choice = input("  › ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return
    if choice == "x":
        return
    if choice in ("r", "s"):
        merged = {**DEFAULT_CONFIG, **preset.get("config", {})}
        if choice == "s":
            save_config_file(merged, cfg_path)
            console.print(f"\n  [bold green]✓  Saved → {cfg_path}[/]\n")
            time.sleep(0.6)
        run_animation(merged)
    elif choice == "d" and preset.get("_source") == "custom":
        customs = [p for p in load_custom_presets() if p.get("id") != preset.get("id")]
        save_custom_presets(customs)
        console.print(f"\n  [bold red]✗  Deleted '{preset.get('name')}'[/]\n")
        time.sleep(0.8)

def _save_as_preset(console: Console, cfg: dict, sc: str) -> None:
    console.print()
    console.print(Panel("[bold]Save current config as a preset[/]",
                        border_style=sc, padding=(0, 2)))
    try:
        name = input("  Preset name  › ").strip()
        if not name:
            console.print("  [dim]Cancelled.[/]"); time.sleep(0.8); return
        desc = input("  Short description  › ").strip()
    except (EOFError, KeyboardInterrupt):
        return
    pid    = name.lower().replace(" ", "_")[:32]
    clean  = {k: v for k, v in cfg.items() if not k.startswith("_")}
    customs = [p for p in load_custom_presets() if p.get("id") != pid]
    customs.append({"id": pid, "name": name, "desc": desc, "tags": ["custom"], "config": clean})
    save_custom_presets(customs)
    console.print(f"\n  [bold green]✓  Saved preset '{name}'[/]\n")
    time.sleep(1.0)

def run_preset_browser(cfg_path: str) -> None:
    console = Console()
    cfg     = build_config(cfg_path)
    sc      = safe_color(cfg.get("color", ""), "#00cc44")

    while True:
        presets = _all_presets()
        _draw_preset_browser(console, presets, sc)
        try:
            choice = input("  › ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            break
        if choice == "q":
            break
        elif choice == "n":
            _save_as_preset(console, cfg, sc)
        else:
            try:
                idx = int(choice) - 1
            except ValueError:
                continue
            if 0 <= idx < len(presets):
                _preset_action(console, presets[idx], cfg_path, sc)


# ═════════════════════════════════════════════════════════════════════════════
#  Self-installer  (matrix --install)
# ═════════════════════════════════════════════════════════════════════════════

def run_install() -> None:
    """Copy this .exe to C:\\tools\\ and add it to the user PATH automatically."""
    console = Console()
    G  = "#00cc44"

    console.print()
    console.print(f"  [bold {G}]░▒▓  MATRIX INSTALLER  ▓▒░[/]")
    console.print()

    if sys.platform != "win32":
        console.print("  [yellow]--install is for Windows only.[/]")
        console.print("  [dim]On Linux/macOS: move this binary to /usr/local/bin/[/]")
        console.print()
        return

    import shutil
    import winreg

    # Works both as a frozen .exe and as a plain .py script
    src         = sys.executable if getattr(sys, "frozen", False) else os.path.abspath(__file__)
    install_dir = r"C:\tools"
    dest        = os.path.join(install_dir, "matrix.exe")

    # ── Create C:\tools\ ──────────────────────────────────────────────────────
    try:
        os.makedirs(install_dir, exist_ok=True)
        console.print(f"  [bold green][+][/] Install folder ready: {install_dir}")
    except Exception as e:
        console.print(f"  [red][x] Could not create {install_dir}: {e}[/]"); return

    # ── Copy the .exe ─────────────────────────────────────────────────────────
    try:
        shutil.copy2(src, dest)
        console.print(f"  [bold green][+][/] Copied matrix.exe → {dest}")
    except Exception as e:
        console.print(f"  [red][x] Could not copy file: {e}[/]"); return

    # ── Add C:\tools to user PATH via registry ────────────────────────────────
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, r"Environment",
            0, winreg.KEY_READ | winreg.KEY_WRITE
        )
        try:
            current_path, _ = winreg.QueryValueEx(key, "PATH")
        except FileNotFoundError:
            current_path = ""

        parts = [p for p in current_path.split(";") if p]
        if install_dir.lower() not in [p.lower() for p in parts]:
            parts.append(install_dir)
            winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, ";".join(parts))
            console.print(f"  [bold green][+][/] Added {install_dir} to user PATH")
        else:
            console.print(f"  [bold green][+][/] {install_dir} already in PATH")
        winreg.CloseKey(key)

        # Tell Windows to refresh PATH in open windows
        import ctypes
        ctypes.windll.user32.SendMessageTimeoutW(
            0xFFFF, 0x001A, 0, "Environment", 2, 5000, None
        )
    except Exception as e:
        console.print(f"  [red][x] Could not update PATH: {e}[/]")
        console.print(f"  [dim]    Add {install_dir} to PATH manually via sysdm.cpl[/]")

    # ── Done ──────────────────────────────────────────────────────────────────
    console.print()
    console.print(f"  [bold {G}]Done![/] [dim]Open a new terminal and run:[/]")
    console.print(f"    [bold {G}]matrix[/]      [dim]show help[/]")
    console.print(f"    [bold {G}]matrix -s[/]   [dim]start animation[/]")
    console.print(f"    [bold {G}]matrix -c[/]   [dim]config editor[/]")
    console.print(f"    [bold {G}]matrix -p[/]   [dim]preset browser[/]")
    console.print()
    input("  Press Enter to close...")


# ═════════════════════════════════════════════════════════════════════════════
#  CLI entry point
# ═════════════════════════════════════════════════════════════════════════════

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="matrix",
        add_help=False,
        description="Matrix waterfall terminal animation",
    )
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("-s", "--start",   action="store_true", help="Start animation")
    mode.add_argument("-c", "--config",  action="store_true", help="Open config editor")
    mode.add_argument("-p", "--presets", action="store_true", help="Browse presets")
    mode.add_argument("-h", "--help",    action="store_true", help="Show help")
    mode.add_argument("--install",       action="store_true",
                      help="Copy to C:\\tools\\ and add to PATH  (Windows)")
    p.add_argument("-f", "--file", default=DEFAULT_CONFIG_PATH, metavar="PATH",
                   help=f"Config file  (default: {DEFAULT_CONFIG_PATH})")
    return p.parse_args()

def main() -> None:
    args = parse_args()
    if args.start:
        run_animation(build_config(args.file))
    elif args.config:
        run_config_editor(args.file)
    elif args.presets:
        run_preset_browser(args.file)
    elif args.install:
        run_install()
    else:
        show_splash()

if __name__ == "__main__":
    main()

#congrats, you reached the end of the code :)
