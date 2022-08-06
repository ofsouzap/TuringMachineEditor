from typing import List as tList;
from typing import Tuple as tTuple;
from struct import pack, unpack;
from pygame import Vector2;

from machine import State, Transition, Machine;

INT32_FMT = "i";
INT32_SIZE = 4;

# For tkinter.filedialog

MACHINE_FILE_EXTENSION = ".turingmach";
MACHINE_FILETYPES = [("Turing Machine", f"*{MACHINE_FILE_EXTENSION}"),
    ("All Files", "*.*")]

class MachineSerializer:

    @staticmethod
    def serialize(m: Machine) -> bytes:

        bs = bytearray();

        # Write number of states

        MachineSerializer.add_bytes_to_bytearray(bs, pack(INT32_FMT, len(m.states)));

        # Write states

        for s in m.states:

            MachineSerializer.add_bytes_to_bytearray(bs, pack(INT32_FMT, s.n));
            MachineSerializer.add_bytes_to_bytearray(bs, pack(INT32_FMT, s.pos[0]));
            MachineSerializer.add_bytes_to_bytearray(bs, pack(INT32_FMT, s.pos[1]));

        # Write number of transitions

        MachineSerializer.add_bytes_to_bytearray(bs, pack(INT32_FMT, len(m.transitions)));

        # Write transitions

        for t in m.transitions:

            MachineSerializer.add_bytes_to_bytearray(bs, pack(INT32_FMT, t.start));
            MachineSerializer.add_bytes_to_bytearray(bs, pack(INT32_FMT, t.end));
            MachineSerializer.add_bytes_to_bytearray(bs, MachineSerializer.serialize_str(t.read_symbol));
            MachineSerializer.add_bytes_to_bytearray(bs, MachineSerializer.serialize_str(t.write_symbol));
            MachineSerializer.add_bytes_to_bytearray(bs, pack(INT32_FMT, t.head_move));

        # Return bytes

        return bytes(bs);

    @staticmethod
    def deserialize(bs: bytes) -> Machine:

        m = Machine();

        i = 0;

        # Read number of states

        states_count = unpack(INT32_FMT, bs[i : i + INT32_SIZE])[0];
        i += INT32_SIZE;

        # Read states

        for _ in range(states_count):

            n, pos_x, pos_y = unpack(INT32_FMT * 3, bs[i : i + (INT32_SIZE * 3)]);
            i += INT32_SIZE * 3;

            s = State(n, Vector2(pos_x, pos_y));
            m.states.append(s);

        # Read number of transitions

        transitions_count = unpack(INT32_FMT, bs[i : i + INT32_SIZE])[0];
        i += INT32_SIZE;

        # Read transitions

        for _ in range(transitions_count):

            start, end = unpack(INT32_FMT * 2, bs[i : i + (INT32_SIZE * 2)]);
            i += INT32_SIZE * 2;

            read_symbol, i_inc = MachineSerializer.deserialize_str(bs[i:]);
            i += i_inc;

            write_symbol, i_inc = MachineSerializer.deserialize_str(bs[i:]);
            i += i_inc;

            head_move = unpack(INT32_FMT, bs[i : i + INT32_SIZE])[0];
            i += INT32_SIZE;

            t = Transition(start, end, read_symbol, write_symbol, head_move);
            m.transitions.append(t);

        # Return output

        return m;

    @staticmethod
    def serialize_str(s: str) -> bytes:

        bs = bytearray();

        MachineSerializer.add_bytes_to_bytearray(bs, pack(INT32_FMT, len(s)));

        MachineSerializer.add_bytes_to_bytearray(bs, s.encode());

        return bs;

    @staticmethod
    def deserialize_str(bs: bytes) -> tTuple[str, int]:

        i = 0;

        size = unpack(INT32_FMT, bs[i : i + INT32_SIZE])[0];
        i += INT32_SIZE;

        s = bs[i : i + size].decode();
        i += size;

        return (s, i);

    @staticmethod
    def add_bytes_to_bytearray(arr: bytearray,
        bs: bytes) -> None:

        for b in bs:
            arr.append(b);
