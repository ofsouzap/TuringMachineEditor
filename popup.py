from typing import Tuple as tTuple;
import tkinter as tk;
import re;

from machine import SYMBOL_MAX_LENGTH;

SYMBOL_PATTERN = r"^[A-z0-9]{0," + str(SYMBOL_MAX_LENGTH) + r"}$";
INT_PATTERN = r"^-?[0-9]*$";

def verify_symbol(s: str):
    x = re.match(SYMBOL_PATTERN, s) != None;
    return x;

def str_is_int(s: str):
    x = re.match(INT_PATTERN, s) != None;
    return x;

def run_transition_form() -> tTuple[str, str, int] | None:

    # Set up window

    window = tk.Tk();

    window.title("New Transition");
    window.geometry("256x128");

    # Create enter callback

    def enter_callback() -> None:
        window.quit();

    # Create entry variables

    read_sym_var = tk.StringVar();
    write_sym_var = tk.StringVar();
    head_move_var = tk.IntVar(value = 1);

    # Create widgets

    lbl_read_sym = tk.Label(window, text = "Read Symbol");
    lbl_write_sym = tk.Label(window, text = "Write Symbol");
    lbl_head_move = tk.Label(window, text = "Head Move Amount");
    #TODO - fix validations not working
    ety_read_sym = tk.Entry(window, textvariable = read_sym_var, validate = "key", validatecommand = (window.register(verify_symbol), "%P"));
    ety_write_sym = tk.Entry(window, textvariable = write_sym_var, validate = "key", validatecommand = (window.register(verify_symbol), "%P"));
    ety_head_move = tk.Entry(window, textvariable = head_move_var, validate = "key", validatecommand = (window.register(str_is_int), "%P"));

    btn_submit = tk.Button(window, text = "Enter", command = enter_callback);

    # Bind return key to enter button callback

    window.bind("<Return>", lambda evt: enter_callback());

    # Place widgets in window

    lbl_read_sym.grid(row = 0, column = 0);
    ety_read_sym.grid(row = 0, column = 1);

    lbl_write_sym.grid(row = 1, column = 0);
    ety_write_sym.grid(row = 1, column = 1);

    lbl_head_move.grid(row = 2, column = 0);
    ety_head_move.grid(row = 2, column = 1);

    btn_submit.grid(row = 3, column = 1);

    # Run window until it closes

    ety_read_sym.focus_set();
    window.mainloop();

    # Check if window was closed by trying to read variable

    try:
        ety_read_sym.get();
    except tk.TclError:
        return None;

    # Default head move value

    if ety_head_move.get() == "":
        # If head move entry is blank, default to value of 0
        ety_head_move.insert(0, "0");

    elif ety_head_move.get() == "-":
        # If head move entry is negative sign, default to value of -1 ("-" is already written so isn't included in insertion)
        ety_head_move.insert(0, "1");

    # Close window and return values

    output = (read_sym_var.get(), write_sym_var.get(), head_move_var.get());

    window.destroy();
    
    return output;

if __name__ == "__main__":

    # This should only run when debugging

    print(run_transition_form());
