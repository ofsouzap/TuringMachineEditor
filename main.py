from typing import List as tList;
from typing import Tuple as tTuple;
from math import sqrt;
import pygame;

import popup;
from machine import Machine;

from machine_window import MachineWindow;
from machine_window import STATE_WIDTH;

BG_COLOR = (255, 255, 255);

WINDOW_DIMS = (1024, 576);
WINDOW_TITLE = "Turing Machine Editor";

MACHINE_WINDOW_HEIGHT = 536;
TAPE_WINDOW_HEIGHT = 40;

assert MACHINE_WINDOW_HEIGHT + TAPE_WINDOW_HEIGHT == WINDOW_DIMS[1];

MINIMUM_STATE_SEPARATION_FACTOR = 3;

CLICK_MODE_CREATE = 0x00;
CLICK_MODE_TRANSITION = 0x01;
CLICK_MODE_DELETE = 0x02;

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

    # Set up clock
    clock = pygame.time.Clock();

    # Set up machine and machine window

    machine = Machine();

    machine_window = MachineWindow(
        size = (WINDOW_DIMS[0], MACHINE_WINDOW_HEIGHT),
        machine = machine,
        bg_color = BG_COLOR,
        state_font = state_font,
        transition_font = transition_font
    );

    # Set up click mode

    click_mode = CLICK_MODE_CREATE;

    transition_create_start = None;

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

                if click_mode == CLICK_MODE_CREATE:

                    state = machine_window.get_state_in_pos(mouse_pos);

                    if state == None:

                        # Check new position isn't too close to existing state

                        too_close = False;

                        for s in machine.states:

                            dist = sqrt((s.pos[0] - mouse_pos[0])**2 + (s.pos[1] - mouse_pos[1])**2);

                            if dist <= (STATE_WIDTH * MINIMUM_STATE_SEPARATION_FACTOR):
                                too_close = True;
                                break;

                        if not too_close:

                            state = machine.add_state(mouse_pos);
                            machine_window.create_state_sprite(state);

                            machine_window.set_status_text(f"Created state {state.n}.");

                        else:

                            machine_window.set_status_text("Can't create state here.");

                    else:

                        click_mode = CLICK_MODE_TRANSITION;
                        transition_create_start = state;

                        machine_window.set_status_text(f"Creating transition from {state.n}...");

                elif click_mode == CLICK_MODE_DELETE:

                    state = machine_window.get_state_in_pos(mouse_pos);

                    if state != None:

                        machine.safe_remove_state(state.n);

                        machine_window.set_status_text(f"Deleted state {state.n}");

                elif click_mode == CLICK_MODE_TRANSITION:

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

                            machine.add_transition(
                                start = transition_create_start.n,
                                end = end_state.n,
                                read_symbol = read_symbol,
                                write_symbol = write_symbol,
                                head_move = head_move
                            );

                            machine_window.refresh();

                            machine_window.set_status_text(f"Created transition from {transition_create_start.n} to {end_state.n}.");

                    transition_create_start = None;
                    click_mode = CLICK_MODE_CREATE;

            elif evt.type == pygame.KEYDOWN:

                if evt.key == pygame.K_d:

                    if click_mode == CLICK_MODE_CREATE:

                        click_mode = CLICK_MODE_DELETE;

                        machine_window.set_status_text("Switched to delete mode.");

                    elif click_mode == CLICK_MODE_DELETE:

                        click_mode = CLICK_MODE_CREATE;

                        machine_window.set_status_text("Switched to create mode.");

        # Clear screen

        main_window.fill(BG_COLOR);

        # Blit windows

        main_window.blit(
            source = machine_window,
            dest = (0, 0)
        );

        # Flip display

        pygame.display.flip();

    pygame.font.quit();
    pygame.quit();

if __name__ == "__main__":
    main();