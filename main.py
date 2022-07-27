from typing import List as tList;
from typing import Tuple as tTuple;
from math import sqrt;
from time import time as now;
import pygame;

import popup;
from machine import Machine;

from machine_window import MachineWindow;
from machine_window import STATE_WIDTH;

from tape import Tape, TAPE_DEFAULT_SYMBOL;

from tape_window import TapeWindow;

from controls_window import ControlsWindow;

WINDOW_DIMS = (1000, 700);
WINDOW_TITLE = "Turing Machine Editor";

BG_COLOR = (255, 255, 255);

MACHINE_WINDOW_HEIGHT = 500;
TAPE_WINDOW_HEIGHT = 100;
CONTROLS_WINDOW_HEIGHT = 100;

assert MACHINE_WINDOW_HEIGHT + TAPE_WINDOW_HEIGHT + CONTROLS_WINDOW_HEIGHT == WINDOW_DIMS[1];

MINIMUM_STATE_SEPARATION_MULTIPLIER = 3;

MACHINE_RUN_CHANGE_DELAY = 1; # How long (in seconds) to wait between stepping between states when running the machine

CLICK_MODE_CREATE = 0x00;
CLICK_MODE_TRANSITION = 0x01;
CLICK_MODE_DELETE = 0x02;

RUN_MODE_STOPPED = 0x00;
RUN_MODE_PLAYING = 0x01;
RUN_MODE_PAUSED = 0x02;

def main():

    # Set up pygame

    pygame.init();
    pygame.font.init();

    main_window = pygame.display.set_mode(
        size = WINDOW_DIMS
    );

    pygame.display.set_caption(WINDOW_TITLE);

    # Set up fonts

    state_font = pygame.font.SysFont("Courier New", 24);
    transition_font = pygame.font.SysFont("Courier New", 12);
    tape_symbol_font = pygame.font.SysFont("Courier New", 20);

    # Set up clock
    clock = pygame.time.Clock();

    # Set up machine, tape and windows

    machine = Machine();

    machine_window = MachineWindow(
        size = (WINDOW_DIMS[0], MACHINE_WINDOW_HEIGHT),
        machine = machine,
        bg_color = BG_COLOR,
        state_font = state_font,
        transition_font = transition_font
    );

    tape = Tape(TAPE_DEFAULT_SYMBOL);

    tape_window = TapeWindow(
        size = (WINDOW_DIMS[0], TAPE_WINDOW_HEIGHT),
        tape = tape,
        bg_color = BG_COLOR,
        font = tape_symbol_font
    );

    controls_window = ControlsWindow(
        size = (WINDOW_DIMS[0], CONTROLS_WINDOW_HEIGHT),
        bg_color = BG_COLOR
    );
    
    # Set up machine click mode

    machine_click_mode = CLICK_MODE_CREATE;

    transition_create_start = None;

    # Set up machine running

    machine_run_mode = RUN_MODE_STOPPED;
    machine_run_curr_state = 0;
    machine_run_next_move_time = 0;

    #TODO - remove from here once done testing
    tape.set(0, "a");
    tape.set(1, "b");
    tape.set(2, "a");
    tape.set(3, "b");
    tape_window.refresh();
    #TODO - remove to here once done testing

    # Main loop

    running = True;

    while running:

        # Clock tick

        clock.tick(20);

        # Handle events

        for evt in pygame.event.get():
            
            if evt.type == pygame.QUIT:
                running = False;

            elif evt.type == pygame.MOUSEBUTTONDOWN:

                mouse_pos = pygame.mouse.get_pos();

                if 0 <= mouse_pos[1] <= MACHINE_WINDOW_HEIGHT:

                    # If mouse is in machine window

                    if machine_run_mode == RUN_MODE_STOPPED: # Can only edit machine whilst it is stopped

                        if machine_click_mode == CLICK_MODE_CREATE:

                            state = machine_window.get_state_in_pos(mouse_pos);

                            if state == None:

                                # Check new position isn't too close to existing state

                                too_close = False;

                                for s in machine.states:

                                    dist = sqrt((s.pos[0] - mouse_pos[0])**2 + (s.pos[1] - mouse_pos[1])**2);

                                    if dist <= (STATE_WIDTH * MINIMUM_STATE_SEPARATION_MULTIPLIER):
                                        too_close = True;
                                        break;

                                if not too_close:

                                    state = machine.add_state(mouse_pos);
                                    machine_window.create_state_sprite(state);

                                    machine_window.set_status_text(f"Created state {state.n}.");

                                else:

                                    machine_window.set_status_text("Can't create state here.");

                            else:

                                machine_click_mode = CLICK_MODE_TRANSITION;
                                transition_create_start = state;

                                machine_window.set_status_text(f"Creating transition from {state.n}...");

                        elif machine_click_mode == CLICK_MODE_DELETE:

                            state = machine_window.get_state_in_pos(mouse_pos);

                            if state != None:

                                machine.safe_remove_state(state.n);

                                machine_window.set_status_text(f"Deleted state {state.n}");

                        elif machine_click_mode == CLICK_MODE_TRANSITION:

                            if transition_create_start == None:
                                raise Exception("No start has been set when trying to create a transition.");

                            end_state = machine_window.get_state_in_pos(mouse_pos);

                            if end_state == None:

                                machine_window.set_status_text(f"Cancelled creating transition for {state.n}.");

                            else:

                                out = popup.run_transition_form();

                                if out == None:

                                    machine_window.set_status_text(f"Didn't create transition for {state.n}.");

                                else:

                                    read_symbol, write_symbol, head_move = out;

                                    success = machine.try_add_transition(
                                        start = transition_create_start.n,
                                        end = end_state.n,
                                        read_symbol = read_symbol,
                                        write_symbol = write_symbol,
                                        head_move = head_move
                                    );

                                    if success:

                                        machine_window.refresh();

                                        machine_window.set_status_text(f"Created transition from {transition_create_start.n} to {end_state.n}.");

                                    else:

                                        machine_window.set_status_text("Couldn't create the attempted transition.");

                            transition_create_start = None;
                            machine_click_mode = CLICK_MODE_CREATE;

                elif (MACHINE_WINDOW_HEIGHT + TAPE_WINDOW_HEIGHT) <= mouse_pos[1] <= (MACHINE_WINDOW_HEIGHT + TAPE_WINDOW_HEIGHT + CONTROLS_WINDOW_HEIGHT):

                    controls_window_mouse_pos = (
                        mouse_pos[0],
                        mouse_pos[1] - (MACHINE_WINDOW_HEIGHT + TAPE_WINDOW_HEIGHT)
                    );

                    # If mouse is in controls window

                    if controls_window.pos_in_play_button(controls_window_mouse_pos):

                        if machine_run_mode == RUN_MODE_STOPPED:

                            # Don't try run without any states
                            if len(machine.states) != 0:

                                machine_run_mode = RUN_MODE_PLAYING;

                                # Store intial state of tape for returning to when stopping
                                tape.store_initial_state();

                                # Start at state 0
                                machine_run_curr_state = 0;
                                machine_window.set_curr_state(machine_run_curr_state);

                                # Prepare to change state
                                machine_run_next_move_time = now() + MACHINE_RUN_CHANGE_DELAY;
                        
                        elif machine_run_mode == RUN_MODE_PAUSED:

                            machine_run_mode = RUN_MODE_PLAYING;

                            # Prepare to change state (restart change timer)
                            machine_run_next_move_time = now() + MACHINE_RUN_CHANGE_DELAY;

                    elif controls_window.pos_in_pause_button(controls_window_mouse_pos):

                        if machine_run_mode == RUN_MODE_PLAYING:

                            machine_run_mode = RUN_MODE_PAUSED;

                    elif controls_window.pos_in_stop_button(controls_window_mouse_pos):

                        if (machine_run_mode == RUN_MODE_PLAYING) or (machine_run_mode == RUN_MODE_PAUSED):

                            machine_run_mode = RUN_MODE_STOPPED;

                            # Set current state to initial state
                            machine_run_curr_state = 0;
                            machine_window.set_curr_state(machine_run_curr_state);

                            # Load tape's initial state
                            tape.load_initial_state();
                            tape.head_to(0);

                    # Refresh windows
                    machine_window.update_state_sprites();
                    tape_window.refresh();

            elif evt.type == pygame.KEYDOWN:

                if evt.key == pygame.K_d:

                    if machine_click_mode == CLICK_MODE_CREATE:

                        machine_click_mode = CLICK_MODE_DELETE;

                        machine_window.set_status_text("Switched to delete mode.");

                    elif machine_click_mode == CLICK_MODE_DELETE:

                        machine_click_mode = CLICK_MODE_CREATE;

                        machine_window.set_status_text("Switched to create mode.");

        # Handle playing machine

        if machine_run_mode == RUN_MODE_PLAYING:

            if now() >= machine_run_next_move_time:

                # Determine next stage for machine and tape

                out = machine.determine_output(machine_run_curr_state, tape.get_at_head());

                if out == None:

                    # If no transitions found, pause machine

                    machine_run_mode = RUN_MODE_PAUSED;

                else:

                    # Extract output parts
                    next_state, write_symbol, head_move = out;

                    # Set new state
                    machine_run_curr_state = next_state;
                    machine_window.set_curr_state(machine_run_curr_state);

                    # Write symbol to tape
                    tape.set_at_head(write_symbol);

                    # Move tape head
                    tape.head_forward(head_move);

                    # Set next move time
                    machine_run_next_move_time = now() + MACHINE_RUN_CHANGE_DELAY;

                # Refresh tape and machine

                machine_window.update_state_sprites();
                tape_window.refresh();

        # Clear screen

        main_window.fill(BG_COLOR);

        # Blit windows

        main_window.blit(
            source = machine_window,
            dest = (0, 0)
        );

        main_window.blit(
            source = tape_window,
            dest = (0, MACHINE_WINDOW_HEIGHT)
        );

        main_window.blit(
            source = controls_window,
            dest = (0, MACHINE_WINDOW_HEIGHT + TAPE_WINDOW_HEIGHT)
        );

        # Flip display

        pygame.display.flip();

    pygame.font.quit();
    pygame.quit();

if __name__ == "__main__":
    main();