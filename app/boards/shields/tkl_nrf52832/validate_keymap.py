#!/usr/bin/env python3
"""Validate a ZMK .keymap file against zmk_keycodes.csv

Usage: python validate_keymap.py path/to/keymap keycodes.csv
"""
import csv
import re
import sys


def load_keycodes(csvpath):
    names = set()
    with open(csvpath, newline='') as f:
        rd = csv.DictReader(f)
        for r in rd:
            key = r['Keycode'].strip()
            if key:
                names.add(key.upper())
            # ShortNames can be comma-separated
            sns = r['ShortNames'].split(',') if r.get('ShortNames') else []
            for s in sns:
                s = s.strip()
                if s:
                    names.add(s.upper())
    # also allow common aliases
    names.update(['TRANS'])
    return names


def parse_keymap(path):
    with open(path) as f:
        text = f.read()
    m = re.search(r'bindings\s*=\s*<([\s\S]*?)>\s*;', text)
    if not m:
        raise SystemExit('No bindings block found')
    block = m.group(1)

    # Split on whitespace and semicolons, keeping tokens like '&kp', 'ESC', '&trans', 'TAB' etc.
    parts = re.findall(r'&[^\s;>]+|[^\s;>;]+', block)
    # Now interpret sequences: if a part starts with '&kp' (modifier/behavior) and the next part is not starting with '&',
    # combine them as a single key (e.g., '&kp' + 'ESC' -> 'ESC'). If a part starts with '&trans' or a single-word behavior, treat as 'TRANS'.
    keys = []
    i = 0
    while i < len(parts):
        p = parts[i].strip()
        if not p:
            i += 1
            continue
        if p.startswith('&kp'):
            # try to get next symbol as key
            if i + 1 < len(parts):
                nxt = parts[i+1].strip()
                # if next is like '&something', that's unexpected; treat as empty and move on
                if nxt and not nxt.startswith('&'):
                    keys.append(nxt.upper())
                    i += 2
                    continue
                else:
                    # fallback: treat '&kp' alone as unknown token
                    keys.append('&KP')
                    i += 1
                    continue
        if p.startswith('&'):
            # a single-token behavior like &trans
            keys.append(p[1:].upper())
            i += 1
            continue
        # otherwise it's a bare key like 'ESC'
        keys.append(p.upper())
        i += 1

    return keys


def main():
    if len(sys.argv) < 3:
        print('Usage: validate_keymap.py path/to.keymap path/to/zmk_keycodes.csv')
        raise SystemExit(1)
    keymap = sys.argv[1]
    csvf = sys.argv[2]

    names = load_keycodes(csvf)
    keys = parse_keymap(keymap)
    unk = sorted(set(k for k in keys if k not in names))
    if not unk:
        print('All keycodes look valid!')
        return
    print('Unknown key tokens:')
    for u in unk:
        print(' -', u)

if __name__ == '__main__':
    main()
