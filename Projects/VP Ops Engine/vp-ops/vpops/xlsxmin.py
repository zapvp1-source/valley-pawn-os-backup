"""
xlsxmin.py — minimal read-only .xlsx cell-grid reader, stdlib only.

BUILD_SPEC.md mandates "Python 3 stdlib only... No pip dependencies" for this
engine, so this replaces openpyxl (used by the existing, Claude-driven
store_kpis_compile.py) with a small zipfile + xml.etree reader that covers
exactly what the Bravo EOM export needs: numeric cells, shared-string cells,
and inline-string cells, addressed by 1-based (row, col) like openpyxl's
ws.cell(row, col).
"""

from __future__ import annotations
import re
import zipfile
from xml.etree import ElementTree as ET

_NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
_COL_RE = re.compile(r"^([A-Z]+)(\d+)$")


def _col_to_index(col_letters: str) -> int:
    idx = 0
    for ch in col_letters:
        idx = idx * 26 + (ord(ch) - ord("A") + 1)
    return idx


def _cell_ref_to_rc(ref: str) -> tuple[int, int]:
    m = _COL_RE.match(ref)
    if not m:
        raise ValueError(f"Unrecognized cell ref: {ref!r}")
    col_letters, row_str = m.groups()
    return int(row_str), _col_to_index(col_letters)


def _load_shared_strings(zf: zipfile.ZipFile) -> list[str]:
    try:
        raw = zf.read("xl/sharedStrings.xml")
    except KeyError:
        return []
    root = ET.fromstring(raw)
    out = []
    for si in root.findall("m:si", _NS):
        # Concatenate all <t> runs (handles rich text split across <r><t>...)
        texts = [t.text or "" for t in si.findall(".//m:t", _NS)]
        out.append("".join(texts))
    return out


def read_sheet_grid(path, sheet_index: int = 1) -> dict[tuple[int, int], object]:
    """Returns {(row, col): value} for the given worksheet (1-based, sparse).

    Values are floats for numeric cells, strings for text cells. Cells with
    no value are simply absent from the dict (matches openpyxl's None-on-
    missing behavior when read via grid.get((r, c))).
    """
    grid: dict[tuple[int, int], object] = {}
    with zipfile.ZipFile(path) as zf:
        shared = _load_shared_strings(zf)
        sheet_name = f"xl/worksheets/sheet{sheet_index}.xml"
        root = ET.fromstring(zf.read(sheet_name))
        for row_el in root.findall(".//m:sheetData/m:row", _NS):
            for c_el in row_el.findall("m:c", _NS):
                ref = c_el.get("r")
                if not ref:
                    continue
                r, c = _cell_ref_to_rc(ref)
                ctype = c_el.get("t")
                v_el = c_el.find("m:v", _NS)
                if ctype == "s":
                    if v_el is None:
                        continue
                    idx = int(v_el.text)
                    grid[(r, c)] = shared[idx] if 0 <= idx < len(shared) else ""
                elif ctype == "inlineStr":
                    is_el = c_el.find("m:is", _NS)
                    texts = [t.text or "" for t in (is_el.findall(".//m:t", _NS) if is_el is not None else [])]
                    grid[(r, c)] = "".join(texts)
                elif ctype == "str":
                    # cached formula-result string
                    grid[(r, c)] = v_el.text if v_el is not None else ""
                elif ctype == "b":
                    grid[(r, c)] = bool(int(v_el.text)) if v_el is not None else None
                else:
                    # numeric (no t attribute) or anything else with a plain <v>
                    if v_el is None or v_el.text is None:
                        continue
                    try:
                        grid[(r, c)] = float(v_el.text)
                    except ValueError:
                        grid[(r, c)] = v_el.text
    return grid


def max_row_col(grid: dict[tuple[int, int], object]) -> tuple[int, int]:
    if not grid:
        return 0, 0
    return max(r for r, _ in grid), max(c for _, c in grid)


class Worksheet:
    """Thin openpyxl-`.active`-shaped wrapper so callers ported from
    store_kpis_compile.py need minimal changes: ws.cell(r, c).value semantics
    via ws.get(r, c), plus max_row/max_column."""

    def __init__(self, grid: dict[tuple[int, int], object]):
        self._grid = grid
        self.max_row, self.max_column = max_row_col(grid)

    def get(self, row: int, col: int):
        return self._grid.get((row, col))


def load_active_sheet(path) -> Worksheet:
    return Worksheet(read_sheet_grid(path, sheet_index=1))
