from typing import List as tList;
from typing import Tuple as tTuple;

TAPE_DEFAULT_SYMBOL = "-";

class Tape:

    def __init__(self, default_v):

        self._default_v = default_v;
        self._vs = {};
        self.head = 0;
        self._initial_state = None;

    def get_at_head(self) -> str:
        return self.get(self.head);

    def set_at_head(self, v: str) -> None:
        self.set(self.head, v);

    def get(self, i: int) -> str:

        if i in self._vs.keys():
            return self._vs[i];

        else:
            return self._default_v;

    def set(self, i: int, v: str) -> None:

        self._vs[i] = v;

    def _get_non_default_bounds(self) -> tTuple[int, int]:

        start = 0;
        end = 0;

        for n in self._vs.keys():

            if (start == None) or (n < start):
                start = n;

            if (end == None) or (n > end):
                end = n;

        return (start, end);

    def read_all(self) -> tList[str]:

        out = [];
        bounds = self._get_non_default_bounds();

        for i in range(bounds[0], bounds[1] + 1, 1):
            out.append(self.get(i));

        return out;

    def head_forward(self,
        amount: int = 1) -> None:
        self.head_to(self.head + amount);

    def head_back(self,
        amount: int = 1) -> None:
        self.head_to(self.head - amount);

    def head_to(self,
        index: int) -> None:
        self.head = index;

    def store_initial_state(self) -> None:

        """Stores the current state of the tape as the initial state that can be returned to after running the machine."""

        self._initial_state = dict(self._vs);

    def load_initial_state(self) -> None:

        """Loads the stored initial state if there is one stored."""

        if self._initial_state == None:
            raise Exception("No initial state has been stored when trying to load it.");

        self._vs = dict(self._initial_state);
