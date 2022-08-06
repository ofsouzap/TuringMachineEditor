from io import TextIOWrapper;
from re import match;

from tape import Tape, TAPE_DEFAULT_SYMBOL;
from machine import SYMBOL_MAX_LENGTH;

TAPE_SYMBOL_PATTERN = r"^((?P<pos>-?[0-9]+)\s*:)?\s*(?P<symbol>[A-z0-9]{1,4})$";

# For tkinter.filedialog

TAPE_FILETYPES = [("All Files", "*.*")]

def try_read_tape(f: TextIOWrapper) -> Tape | None:

    t = Tape(TAPE_DEFAULT_SYMBOL);
    _next_index = 0;

    for l in f.readlines():

        l = l.strip();

        if len(l) == 0:
            continue;

        m = match(TAPE_SYMBOL_PATTERN, l);

        if m == None:
            return None;

        pos = m.group("pos");

        if not pos:
            pos = _next_index;
        else:
            pos = int(pos);

        symbol = m.group("symbol");

        if len(symbol) > SYMBOL_MAX_LENGTH:
            return None;

        else:
            t.set(pos, symbol);
            _next_index = pos + 1;

    return t;
