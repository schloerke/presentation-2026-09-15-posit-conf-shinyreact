"""Shared syntax-highlighting for the shinyreact Keynote theme.

Keynote cannot highlight code, but it preserves colour on a rich-text paste. So
we highlight to RTF using the theme's token colours and put that on the
clipboard; Cmd-V into a code placeholder keeps the colours.

Used by the `highlight-r` and `highlight-python` executables next to this file.

Token colours are the ones DESIGN.md measured against the #141519 panel; all
clear 7:1 contrast. Comment is #9AA3B2 - the conventional #6B7280 measures
3.77:1 and disappears from the back of a room.
"""

import subprocess
import sys
from pathlib import Path

from pygments import format as pygments_format
from pygments.formatters import RtfFormatter
from pygments.lexers import get_lexer_by_name
from pygments.style import Style
from pygments.token import (Comment, Error, Keyword, Name, Number, Operator,
                            Punctuation, String, Text)

TEXT = "#f2f4f8"
CYAN = "#6fd4e8"
KEYWORD = "#c7a0ff"
STRING = "#9fe88d"
NUMBER = "#ffb86c"
COMMENT = "#9aa3b2"


class ShinyreactDark(Style):
    """Mirrors the code tokens in DESIGN.md section 4.1."""

    background_color = "#141519"
    styles = {
        Text: TEXT,
        Punctuation: TEXT,
        Operator: TEXT,
        Keyword: KEYWORD,
        Keyword.Constant: KEYWORD,
        Keyword.Declaration: KEYWORD,
        Keyword.Namespace: KEYWORD,
        Keyword.Reserved: KEYWORD,
        Name: TEXT,
        Name.Function: CYAN,
        Name.Function.Magic: CYAN,
        Name.Class: CYAN,
        Name.Decorator: CYAN,
        Name.Tag: CYAN,
        Name.Builtin: CYAN,
        Name.Builtin.Pseudo: KEYWORD,
        Name.Attribute: TEXT,
        String: STRING,
        String.Doc: COMMENT,
        String.Interpol: TEXT,
        Number: NUMBER,
        Comment: COMMENT,
        Comment.Preproc: COMMENT,
        Error: TEXT,
    }


def calls_as_functions(tokens):
    """Colour `foo(` as a function call.

    Pygments only tags a name as Name.Function where the lexer knows it is one,
    so `useShinyInput(...)` in TSX and most R calls come out as plain text. The
    design puts call sites in cyan, so promote any Name immediately followed by
    an opening paren.
    """
    toks = list(tokens)
    out = []
    for i, (ttype, value) in enumerate(toks):
        if ttype in Name and value.strip():
            j = i + 1
            while j < len(toks) and not toks[j][1].strip():
                j += 1
            if j < len(toks) and toks[j][1].lstrip().startswith("("):
                ttype = Name.Function
        out.append((ttype, value))
    return out


def read_source(path=None):
    """File if given, else stdin if piped, else the clipboard."""
    if path:
        return Path(path).read_text()
    if not sys.stdin.isatty():
        # Fall through to the clipboard when stdin is attached but empty - that
        # is any non-tty caller (CI, an editor hook) rather than a real pipe.
        piped = sys.stdin.read()
        if piped.strip():
            return piped
    return subprocess.run(["pbpaste"], capture_output=True, text=True,
                          check=True).stdout


def to_clipboard(rtf):
    # -Prefer rtf makes the clipboard carry a real RTF flavour, which is what
    # Keynote reads to keep the colours.
    subprocess.run(["pbcopy", "-Prefer", "rtf"], input=rtf.encode(), check=True)


def run(lang, argv, *, label):
    import argparse

    ap = argparse.ArgumentParser(
        prog=f"highlight-{lang}",
        description=f"Syntax-highlight {label} for the shinyreact Keynote theme. "
                    "Reads a file, stdin, or the clipboard; writes RTF to the clipboard.")
    ap.add_argument("file", nargs="?", help="source file (default: clipboard)")
    ap.add_argument("--size", type=int, default=34,
                    help="font size in spec px on the 1920x1080 canvas (default 34)")
    ap.add_argument("--stdout", action="store_true",
                    help="print RTF instead of copying")
    args = ap.parse_args(argv)

    code = read_source(args.file).rstrip("\n")
    if not code.strip():
        ap.error("no code found (clipboard empty?)")

    lexer = get_lexer_by_name(lang)
    tokens = calls_as_functions(lexer.get_tokens(code))
    # RtfFormatter wants half-points; spec px -> pt is /2, so px == half-points.
    rtf = pygments_format(tokens, RtfFormatter(
        style=ShinyreactDark, fontface="Source Code Pro", fontsize=args.size))

    if args.stdout:
        sys.stdout.write(rtf)
        return
    to_clipboard(rtf)
    print(f"copied {code.count(chr(10)) + 1} lines of {label} — paste into Keynote "
          "with Cmd-V (not Paste and Match Style)")
