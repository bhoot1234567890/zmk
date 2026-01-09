#!/usr/bin/env python3
"""Simple visualizer for ZMK `.keymap` files.

Usage: python visualize_keymap.py path/to/tkl_nrf52832.keymap [--outfile out.png]

This script parses the `bindings = < ... >;` block and draws a top-down keyboard layout using matplotlib.
It attempts to give wider widths to obvious large keys (SPACE, TAB, RET, BSPC, SHIFT, CTRL, ALT, GUI).
"""

import re
import argparse
import matplotlib.pyplot as plt
import matplotlib.patches as patches


LABEL_MAP = {
    'N1': '1', 'N2': '2', 'N3': '3', 'N4': '4', 'N5': '5', 'N6': '6', 'N7': '7', 'N8': '8', 'N9': '9', 'N0': '0',
    'GRAVE': '`', 'MINUS': '-', 'EQUAL': '=', 'BSPC': 'Bksp', 'RET': 'Enter', 'TAB': 'Tab', 'CAPS': 'Caps',
    'LSFT': 'Shift', 'RSFT': 'Shift', 'LCTRL': 'Ctrl', 'RCTRL': 'Ctrl', 'LALT': 'Alt', 'RALT': 'Alt',
    'LGUI': 'Win', 'RGUI': 'Win', 'K_APP': 'Menu', 'COMMA': ',', 'DOT': '.', 'SLASH': '/', 'BSLH': '\\',
    'KP_0': 'KP0', 'KP_DOT': '.', 'KP_EQUAL': '=', 'INS': 'Ins', 'END': 'End', 'PAGE_DOWN': 'PgDn',
    'SPACE': 'Space', 'LEFT': '◀', 'RIGHT': '▶', 'UP': '▲', 'DOWN': '▼', 'DEL': 'Del', 'F1': 'F1', 'F2': 'F2'
}

# Keys that should be rendered wider (units)
WIDTH_MAP = {
    'Space': 6,
    'Tab': 2,
    'Enter': 2,
    'Bksp': 2,
    'Shift': 2.5,
    'Ctrl': 2,
    'Alt': 2,
    'Win': 2,
    'Menu': 1.5
}


def human_label(raw):
    # raw is like 'ESC', 'N1', 'KP_0', 'trans'
    if raw.lower() == 'trans':
        return ''
    if raw.startswith('KP_'):
        return raw.replace('KP_', 'KP')
    if raw in LABEL_MAP:
        return LABEL_MAP[raw]
    # simple heuristics
    m = re.match(r'N(\d)', raw)
    if m:
        return m.group(1)
    return raw.title().replace('_', ' ')


def key_width(label):
    return WIDTH_MAP.get(label, 1)


def parse_keymap(path):
    with open(path, 'r') as f:
        text = f.read()

    m = re.search(r'bindings\s*=\s*<([\s\S]*?)>\s*;', text)
    if not m:
        raise ValueError('No bindings block found in keymap file')

    block = m.group(1)
    lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
    rows = []
    for ln in lines:
        # find tokens like '&kp ESC' or '&trans'
        tokens = re.findall(r'&\S+(?:\s+\S+)?', ln)
        row = []
        for t in tokens:
            t = t.strip().strip(';')
            if ' ' in t:
                parts = t.split(None, 1)
                raw = parts[1]
            else:
                raw = t[1:]
            row.append(raw)
        if row:
            rows.append(row)
    return rows


def layout_and_draw(rows, outfile=None, show=True):
    # Compute widths per key
    human_rows = [[human_label(k) for k in row] for row in rows]
    widths_rows = [[key_width(h) for h in hr] for hr in human_rows]

    row_widths = [sum(w) for w in widths_rows]
    maxw = max(row_widths)

    # drawing params
    unit = 1.0
    h = 1.0

    fig_w = maxw * unit * 0.6 + 2
    fig_h = len(rows) * (h + 0.2) * 0.6 + 2
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))

    y = len(rows)  # top row y
    for row, hrs, wds in zip(rows, human_rows, widths_rows):
        total = sum(wds)
        x = (maxw - total) / 2.0  # center row
        for raw_label, label, wd in zip(row, hrs, wds):
            rect = patches.Rectangle((x, y - h), wd * unit, h, linewidth=1, edgecolor='black', facecolor='#f5f5f5')
            ax.add_patch(rect)
            ax.text(x + (wd * unit) / 2, y - h / 2, label or raw_label, ha='center', va='center', fontsize=10)
            x += wd
        y -= (h + 0.2)

    ax.set_xlim(0, maxw + 0.5)
    ax.set_ylim(0, len(rows) + 1)
    ax.set_aspect('equal')
    ax.axis('off')

    if outfile:
        plt.savefig(outfile, bbox_inches='tight', dpi=200)
        print(f'Saved visualization to {outfile}')
    if show:
        plt.show()


def main():
    p = argparse.ArgumentParser(description='Visualize a ZMK .keymap file')
    p.add_argument('keymap', help='Path to .keymap file')
    p.add_argument('--outfile', '-o', help='Output image file (png)')
    p.add_argument('--no-show', dest='show', action='store_false', help='Do not open a GUI window')
    args = p.parse_args()

    rows = parse_keymap(args.keymap)
    layout_and_draw(rows, outfile=args.outfile, show=args.show)


if __name__ == '__main__':
    main()
