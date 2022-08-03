from typing import List as tList;
from typing import Tuple as tTuple;
from struct import pack, unpack;

INT32_FMT = "i";
INT32_SIZE = 4;

SYMBOL_MAX_LENGTH = 4; # Maximum number of chars a symbol can be

class State:

    def __init__(self,
        n: int,
        pos: tTuple[int, int]):

        self.n = n;
        self.pos = pos;

class Transition:

    def __init__(self,
        start: int,
        end: int,
        read_symbol: str,
        write_symbol: str,
        head_move: str):

        self.start = start;
        self.end = end;
        self.read_symbol = read_symbol;
        self.write_symbol = write_symbol;
        self.head_move = head_move;

    def is_between(self,
        a: int | State,
        b: int | State):

        """Checks if the transition connects two states in either direction"""

        if type(a) == State:
            a = a.n;

        if type(b) == State:
            b = b.n;

        return (((self.start == a) and (self.end == b))
            or ((self.start == b) and (self.end == a)));

    def to_string(self):

        read_symbol_string = self.read_symbol if self.read_symbol != "" else "_";
        write_symbol_string = self.write_symbol if self.write_symbol != "" else "_";

        s = f"{str(self.start)},{read_symbol_string} -> {str(self.end)},{write_symbol_string},{str(self.head_move)}";

        return s;

    def applies_to(self,
        start_state: int,
        read_symbol: str):

        """Returns whether the transition applies to being in state start_state and reading symbol read_symbol"""

        return (self.start == start_state) and (self.read_symbol == read_symbol);

    def output_to_tuple(self):
        return (self.end, self.write_symbol, self.head_move);

class Machine:

    def __init__(self):
        
        self.states = [];
        self.transitions = [];

    def get_next_available_state_number(self) -> int:

        """Gets the next available number for a state in this machine"""

        i = 0;

        while True:

            if all(map(lambda s: s.n != i, self.states)):
                return i;

            i += 1;

    def add_state(self,
        pos: tTuple[int, int]) -> State:

        s = State(self.get_next_available_state_number(), pos);

        self.states.append(s);

        return s;

    def try_add_transition(self,
        start: int,
        end: int,
        read_symbol: str,
        write_symbol: str,
        head_move: int) -> bool:

        t = Transition(
            start = start,
            end = end,
            read_symbol = read_symbol,
            write_symbol = write_symbol,
            head_move = head_move
        );

        if not self.check_transition_would_be_unique(t):
            return False;
        
        self.transitions.append(t);

        return True;

    def check_transition_would_be_unique(self,
        new_t: Transition
        ) -> bool:

        combs = [];

        for t in self.transitions:

            c = (t.start, t.end, t.read_symbol);

            if c in combs:
                return False;

            else:
                combs.append(c);

        return True;

    def get_state_by_number(self,
        n: int) -> State | None:
        
        try:
            return next(filter(lambda s: s.n == n, self.states));
        except StopIteration:
            return None;

    def get_transitions_between(self,
        a: int | State,
        b: int | State) -> tList[Transition]:
        return list(filter(lambda t: t.is_between(a, b), self.transitions));

    def safe_remove_state(self,
        n: int) -> None:

        state = self.get_state_by_number(n);

        if state == None:
            raise Exception("No state exists with provided number");

        else:

            # Remove state

            self.states.remove(state);

            # Remove transitions involving state

            new_transitions_list = [];

            for t in self.transitions:

                if (t.start != n) and (t.end != n):
                    new_transitions_list.append(t);

            self.transitions = new_transitions_list;

    def determine_output(self,
        start_state: int,
        read_symbol: str
        ) -> tTuple[int, str, int] | None:

        """Determines what the machine would do when in the specified state and reading the specified symbol. Returns (next_state, write_symbol, head_move) or None if no transitions are found."""

        for t in self.transitions:

            if t.applies_to(start_state, read_symbol):
                return t.output_to_tuple();

        return None;
