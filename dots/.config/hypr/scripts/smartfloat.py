#!/usr/bin/env python3
"""
smartfloat.py - Smart Float Manager for Hyprland

Usage:
  smartfloat.py list
  smartfloat.py info <address_hex_or_without_0x>
  smartfloat.py apply <address_hex_or_without_0x> <preset>

Example:
  smartfloat.py apply 56339236ac40 wallet
  smartfloat.py apply 0x56339236ac40 wallet

Config file: ~/.config/hypr/smartfloat.conf
Preset format:
[rightfloat]
width=25%
height=90%
x=95%-width
y=5%
snap=true
anchor=center
"""

from __future__ import annotations
import subprocess, json, re, os, sys, time, ast, math
from typing import Optional, Dict

HOME = os.environ.get("HOME", "~")
LOGFILE = os.path.join(os.environ.get("XDG_CACHE_HOME", os.path.join(HOME, ".cache")), "hypr", "smartfloat.log")
CFGFILE = os.path.join(os.environ.get("XDG_CONFIG_HOME", os.path.join(HOME, ".config")), "hypr", "smartfloat.conf")
os.makedirs(os.path.dirname(LOGFILE), exist_ok=True)

def log(*parts):
    s = " ".join(str(p) for p in parts)
    with open(LOGFILE, "a") as f:
        f.write(f"[{time.strftime('%F %T')}] {s}\n")

def run_cmd(args, capture=True):
    try:
        if capture:
            out = subprocess.check_output(args, stderr=subprocess.DEVNULL, text=True)
            return out
        else:
            subprocess.Popen(args)
            return ""
    except subprocess.CalledProcessError as e:
        log("Command failed:", args, "->", e)
        return ""

def hyprctl_json(kind: str):
    """Call hyprctl -j <kind> (clients/monitors) and parse JSON."""
    out = run_cmd(["hyprctl", "-j", kind])
    if not out:
        return []
    try:
        return json.loads(out)
    except Exception as e:
        log("JSON parse failed for hyprctl -j", kind, ":", e)
        return []

def get_client(address_full: str):
    clients = hyprctl_json("clients")
    for c in clients:
        if c.get("address") == address_full:
            return c
    return None

def get_monitor_by_id(mid):
    mons = hyprctl_json("monitors")
    for m in mons:
        if m.get("id") == mid or str(m.get("id")) == str(mid):
            return m
    return None

# ---------- Safe arithmetic evaluator ----------
# Accepts strings with numbers, operators + - * / and parentheses.
# No names, no function calls, etc.
ALLOWED_NODES = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Num, ast.Constant,
                 ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.USub, ast.UAdd, ast.Mod, ast.FloorDiv, ast.LShift, ast.RShift)

def safe_eval(expr: str) -> Optional[float]:
    try:
        node = ast.parse(expr, mode='eval')
    except Exception as e:
        log("safe_eval parse error:", expr, e)
        return None

    # Walk nodes to ensure only allowed
    for n in ast.walk(node):
        if not isinstance(n, ALLOWED_NODES):
            # allow parentheses by virtue of AST structure; they don't exist as nodes
            return None

    try:
        value = eval(compile(node, "<safe>", "eval"), {"__builtins__": {}}, {})
        return float(value)
    except Exception as e:
        log("safe_eval eval error:", expr, e)
        return None

# ---------- Expression to pixel computation ----------
def compute_px(expr: str, axis: str, mon_dim: int, win_dim: int) -> Optional[int]:
    """
    expr examples:
      "50%" -> 50% of mon_dim
      "95%-width" -> (95% of mon_dim) - win_dim
      "right-5%" -> (mon_dim - win_dim) - 5%*mon_dim
      "120" -> raw px
      "width" -> win_dim
    axis: "x" or "y" (affects interpretation of percentages if used specially)
    """
    if expr is None or expr == "":
        return None

    expr = expr.strip()

    # convenience: "width" or "height"
    if expr == "width":
        return int(win_dim)
    if expr == "height":
        return int(win_dim if axis == "x" else win_dim)  # caller should pass appropriate win_dim

    # right-5% and bottom-5% shortcuts
    m = re.fullmatch(r"right-([0-9]+(?:\.[0-9]+)?)%", expr)
    if m and axis == "x":
        pct = float(m.group(1))
        pct_px = pct / 100.0 * mon_dim
        val = (mon_dim - win_dim) - pct_px
        return int(round(val))

    m = re.fullmatch(r"bottom-([0-9]+(?:\.[0-9]+)?)%", expr)
    if m and axis == "y":
        pct = float(m.group(1))
        pct_px = pct / 100.0 * mon_dim
        val = (mon_dim - win_dim) - pct_px
        return int(round(val))

    # If expr is a plain percentage like "95%"
    m = re.fullmatch(r"([0-9]+(?:\.[0-9]+)?)%", expr)
    if m:
        pct = float(m.group(1))
        return int(round(pct / 100.0 * mon_dim))

    # If plain integer px
    m = re.fullmatch(r"([0-9]+)", expr)
    if m:
        return int(m.group(1))

    # Generic expression: replace percentages with (N/100*mon_dim), replace 'width'/'height'
    tmp = expr
    # replace occurrences of NN% with (NN/100*mon_dim)
    def pct_repl(match):
        num = match.group(1)
        return f"({num}/100*{mon_dim})"
    tmp = re.sub(r'([0-9]+(?:\.[0-9]+)?)%', pct_repl, tmp)

    # replace width/height with numbers
    tmp = re.sub(r'\bwidth\b', str(win_dim), tmp)
    tmp = re.sub(r'\bheight\b', str(win_dim), tmp)

    # allow minus sign without space, e.g. "95%-width" becomes "(95/100*mon_dim)-win_dim"
    # safe_eval checks AST nodes so only arithmetic remains
    val = safe_eval(tmp)
    if val is None:
        log("compute_px: failed safe eval for expr", expr, "-> transformed:", tmp)
        return None
    return int(round(val))

# ---------- Config loader ----------
def load_presets_from_cfg(path: str) -> Dict[str, Dict[str,str]]:
    presets = {}
    if not os.path.isfile(path):
        return presets
    cur = None
    with open(path, "r") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            m = re.match(r'^\[(.+)\]$', line)
            if m:
                cur = m.group(1).strip()
                presets[cur] = {}
                continue
            m = re.match(r'^([a-zA-Z0-9_]+)\s*=\s*(.+)$', line)
            if m and cur:
                k = m.group(1).strip().lower()
                v = m.group(2).strip()
                presets[cur][k] = v
    return presets

# built-in presets (fallback)
BUILTIN_PRESETS = {
    "big": {"width":"70%", "height":"70%", "anchor":"center", "snap":"true"},
    "bottomleft": {"x":"5%", "y":"80%", "snap":"true"},
    "center": {"anchor":"center"}
}

def list_presets(cfg_presets):
    names = set()
    names.update(BUILTIN_PRESETS.keys())
    names.update(cfg_presets.keys())
    for n in sorted(names):
        print(n)

# ---------- Hyprctl dispatcher helpers ----------
def hypr_dispatch(cmd_parts: list):
    # cmd_parts: list of args after "hyprctl dispatch", e.g. ["setfloating", "address:0x..."]
    args = ["hyprctl", "dispatch"] + cmd_parts
    # For commands where we pass a comma-separated argument e.g. resizewindowpixel exact 100 200,"address:0x..."
    # We will call via subprocess.run to avoid shell parsing issues
    try:
        subprocess.run(args, stderr=subprocess.DEVNULL)
    except Exception as e:
        log("hypr_dispatch failed:", args, e)

def hypr_exec_list(args_list):
    # convenience for commands that are simple lists of args (rarely used)
    try:
        subprocess.run(["hyprctl"] + args_list, stderr=subprocess.DEVNULL)
    except Exception as e:
        log("hypr_exec_list failed", args_list, e)

# ---------- Main apply flow ----------
def apply_preset(address_in: str, preset_name: str, cfg_presets):
    # normalize address to start with 0x
    addr = address_in.lower()
    if not addr.startswith("0x"):
        addr = "0x" + addr

    log(f"smartfloat apply: addr={addr} preset={preset_name}")

    client = get_client(addr)
    if not client:
        log("Client not found for address", addr)
        return

    mon_id = client.get("monitor")
    mon = get_monitor_by_id(mon_id)
    if not mon:
        log("Monitor not found for id", mon_id)
        return

    mon_x = int(mon.get("x", 0))
    mon_y = int(mon.get("y", 0))
    mon_w = int(mon.get("width", 0))
    mon_h = int(mon.get("height", 0))

    # Merge preset: cfg overrides builtin
    preset = {}
    if preset_name in BUILTIN_PRESETS:
        preset.update(BUILTIN_PRESETS[preset_name])
    if preset_name in cfg_presets:
        preset.update(cfg_presets[preset_name])

    log("Using preset:", preset)

    # Ensure floating
    hypr_dispatch(["setfloating", f"address:{addr}"])
    # small sleep to let Hyprland update
    time.sleep(0.04)

    # Resize if width/height provided
    W_px = None
    H_px = None
    if "width" in preset:
        W_px = compute_px(preset["width"], "x", mon_w, client.get("size", [0,0])[0])
    if "height" in preset:
        H_px = compute_px(preset["height"], "y", mon_h, client.get("size", [0,0])[1])

    # If only one axis provided, use current window size for the other
    # Refresh client info first
    client = get_client(addr)
    if not client:
        log("Client disappeared after floating")
        return
    cur_w = int(client.get("size", [0,0])[0])
    cur_h = int(client.get("size", [0,0])[1])
    if W_px is None:
        W_px = cur_w
    if H_px is None:
        H_px = cur_h

    if W_px is not None and H_px is not None:
        log(f"Resizing to {W_px}x{H_px}px")
        # hyprctl expects arguments like: resizewindowpixel exact <W> <H>,"address:0x..."
        # We'll call hyprctl dispatch with a single string after converting
        # Build the argument string as hyprctl expects it (without shell)
        # Because hyprctl 'dispatch' passes words, we'll pass the comma-delimited final arg as one item
        arglist = ["resizewindowpixel", "exact", str(W_px), f"{H_px},address:{addr}"]
        hypr_dispatch(arglist)
        time.sleep(0.03)
    else:
        log("No resize requested")

    # Refresh client geometry after resize
    client = get_client(addr)
    if not client:
        log("Client vanished after resize")
        return
    win_w = int(client.get("size", [0,0])[0])
    win_h = int(client.get("size", [0,0])[1])

    # Determine move
    final_x = None
    final_y = None

    if "x" in preset:
        px = compute_px(preset["x"], "x", mon_w, win_w)
        if px is not None:
            final_x = mon_x + int(px)
    elif preset.get("anchor") in ("left","right","center"):
        if preset["anchor"] == "left":
            final_x = mon_x
        elif preset["anchor"] == "right":
            final_x = mon_x + mon_w - win_w
        elif preset["anchor"] == "center":
            final_x = mon_x + (mon_w // 2) - (win_w // 2)

    if "y" in preset:
        py = compute_px(preset["y"], "y", mon_h, win_h)
        if py is not None:
            final_y = mon_y + int(py)
    elif preset.get("anchor") in ("top","bottom","center"):
        if preset["anchor"] == "top":
            final_y = mon_y
        elif preset["anchor"] == "bottom":
            final_y = mon_y + mon_h - win_h
        elif preset["anchor"] == "center":
            final_y = mon_y + (mon_h // 2) - (win_h // 2)

    if final_x is None and final_y is None:
        log("No move requested")
    else:
        # fallback to current coordinates if one axis empty
        cur_x = int(client.get("at", [0,0])[0])
        cur_y = int(client.get("at", [0,0])[1])
        if final_x is None:
            final_x = cur_x
        if final_y is None:
            final_y = cur_y
        log(f"Moving to X={final_x} Y={final_y}")
        arglist = ["movewindowpixel", "exact", str(final_x), f"{final_y},address:{addr}"]
        hypr_dispatch(arglist)
        time.sleep(0.02)

    # Snapping/clamping if requested
    snap = preset.get("snap", "").lower() == "true"
    if snap:
        client = get_client(addr)
        if not client:
            log("Client vanished before snap")
            return
        cx = int(client.get("at", [0,0])[0])
        cy = int(client.get("at", [0,0])[1])
        cw = int(client.get("size", [0,0])[0])
        ch = int(client.get("size", [0,0])[1])
        nx = max(mon_x, min(cx, mon_x + mon_w - cw))
        ny = max(mon_y, min(cy, mon_y + mon_h - ch))
        if nx != cx or ny != cy:
            log(f"Snapping to NX={nx} NY={ny}")
            hypr_dispatch(["movewindowpixel","exact", str(nx), f"{ny},address:{addr}"])
    log("smartfloat apply done for", addr, "preset", preset_name)

# ---------- CLI ----------
def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]
    cfg_presets = load_presets_from_cfg(CFGFILE)
    if cmd == "list":
        list_presets(cfg_presets)
    elif cmd == "info":
        if len(sys.argv) < 3:
            print("info requires address")
            sys.exit(1)
        addr = sys.argv[2]
        if not addr.startswith("0x"):
            addr = "0x" + addr
        client = get_client(addr)
        print(json.dumps(client, indent=2))
    elif cmd == "apply":
        if len(sys.argv) < 4:
            print("apply requires address and preset")
            sys.exit(1)
        addr = sys.argv[2]
        preset = sys.argv[3]
        # allow calling with or without 0x
        if not addr.startswith("0x"):
            addr = addr
        apply_preset(addr, preset, cfg_presets)
    else:
        print("Unknown command", cmd)
        sys.exit(1)

if __name__ == "__main__":
    main()

