from typing import List as tList;
from typing import Tuple as tTuple;
from math import sqrt;
from time import time as now;
from pygame import Rect;
from pygame.event import Event;
import pygame;
from tkinter.filedialog import asksaveasfile, askopenfile;

from keybindings import Keybinding;

from machine import Machine;
from tape import Tape, TAPE_DEFAULT_SYMBOL;
from machine_serializer import MachineSerializer, MACHINE_FILETYPES, MACHINE_FILE_EXTENSION;

from options_window import OptionsWindow;
from machine_window import MachineWindow, STATE_WIDTH;
from tape_window import TapeWindow;
from controls_window import ControlsWindow;

import popup;

# Enumerators

CLICK_MODE_CREATE = 0x00;
CLICK_MODE_TRANSITION = 0x01;
CLICK_MODE_DELETE = 0x02;

RUN_MODE_STOPPED = 0x00;
RUN_MODE_PLAYING = 0x01;
RUN_MODE_PAUSED = 0x02;

# A class wasn't created for the main window directly as the main window must be created with pygame.display.set_mode so instead a controller class for main program has been made

class MainController:

    def __init__(self,
        window_title: str,
        options_window_rect: Rect,
        machine_window_rect: Rect,
        tape_window_rect: Rect,
        controls_window_rect: Rect,
        bg_color: tTuple[int, int, int],
        keybindings: Keybinding,
        framerate: int,
        state_minimum_separation_factor: float,
        run_change_delay: float):

        # Initialise pygame if not already done

        if (not pygame.get_init()):

            self.initialised_pygame = True;
            pygame.init();

        else:
            self.initialised_pygame = False;

        # Initialise pygame.font if not already done
        
        if (not pygame.font.get_init()):

            self.initialised_pygame_font = True;
            pygame.font.init();

        else:
            self.initialised_pygame_font = False;

        # Create fonts

        self.options_font = pygame.font.SysFont("Courier New", 20);
        self.state_font = pygame.font.SysFont("Courier New", 24);
        self.transition_font = pygame.font.SysFont("Courier New", 12);
        self.tape_symbol_font = pygame.font.SysFont("Courier New", 20);

        # Store settings

        self.options_window_rect = options_window_rect;
        self.machine_window_rect = machine_window_rect;
        self.tape_window_rect = tape_window_rect;
        self.controls_window_rect = controls_window_rect;

        self.window_size = MainController.calculate_main_window_size(
            self.machine_window_rect,
            self.tape_window_rect,
            self.controls_window_rect
        );

        self.bg_color = bg_color;

        self.keybindings = keybindings;

        self.framerate = framerate;
        self.state_minimum_separation_factor = state_minimum_separation_factor;
        self.run_change_delay = run_change_delay;

        # Create window

        self.window = pygame.display.set_mode(self.window_size);
        pygame.display.set_caption(window_title);

        # Set up clock

        self.clock = pygame.time.Clock();

        # Set up machine and tape

        self.machine = Machine();
        self.tape = Tape(TAPE_DEFAULT_SYMBOL);

        # Create sub-windows

        self.options_window = OptionsWindow(
            size = self.options_window_rect.size,
            bg_color = bg_color,
            font = self.options_font
        );

        self.machine_window = MachineWindow(
            size = self.machine_window_rect.size,
            machine = self.machine,
            bg_color = bg_color,
            state_font = self.state_font,
            transition_font = self.transition_font
        );

        self.tape_window = TapeWindow(
            size = self.tape_window_rect.size,
            tape = self.tape,
            bg_color = bg_color,
            font = self.tape_symbol_font
        );

        self.controls_window = ControlsWindow(
            size = self.controls_window_rect.size,
            bg_color = bg_color
        );

        # Set up machine click mode

        self.machine_click_mode = CLICK_MODE_CREATE;
        self.transition_create_start = None;

        # Set up machine running

        self.run_mode = RUN_MODE_STOPPED;
        self.run_curr_state = 0;
        self.run_next_move_time = 0;

        # Prepare main loop

        self.running = True;

    def cleanup(self):

        if self.initialised_pygame_font:
            pygame.font.quit();

        if self.initialised_pygame:
            pygame.quit();

    @staticmethod
    def calculate_main_window_size(*window_rects: Rect) -> tTuple[int, int]:

        size = [0, 0];

        for r in window_rects:

            if r.right > size[0]:
                size[0] = r.right;

            if r.bottom > size[1]:
                size[1] = r.bottom;

        return tuple(size);

    @staticmethod
    def global_pos_to_rect_relative(pos: tTuple[int, int],
        rect: Rect) -> tTuple[int, int]:

        """Takes a position and returns that position but relative to the top-left of the provided Rect."""

        return (
            pos[0] - rect.left,
            pos[1] - rect.top
        );

    def check_can_create_state_in_pos(self,
        pos: tTuple[int, int]) -> bool:

        for s in self.machine.states:

            dist = sqrt((s.pos[0] - pos[0])**2 + (s.pos[1] - pos[1])**2);

            if dist <= (STATE_WIDTH * self.state_minimum_separation_factor):
                return False;

        return True;

    def set_machine(self, m: Machine) -> None:
        self.machine = m;
        self.machine_window.set_machine(m);
        self.machine_window.refresh();

    # Main loop

    def stop_main_loop(self) -> None:
        self.running = False;

    def run_main_loop(self) -> None:

        while self.running:

            # Clock tick
            self.clock.tick(self.framerate);

            # Handle events
            self.handle_pygame_evts();

            # Update running machine
            self.update_run_machine();

            # Clear main window
            self.window.fill(self.bg_color);

            # Blit sub-windows onto main window
            
            self.window.blit(self.options_window, self.options_window_rect.topleft);
            self.window.blit(self.machine_window, self.machine_window_rect.topleft);
            self.window.blit(self.tape_window, self.tape_window_rect.topleft);
            self.window.blit(self.controls_window, self.controls_window_rect.topleft);

            # Flip display

            pygame.display.flip();

    def update_run_machine(self) -> None:

        if self.run_mode != RUN_MODE_PLAYING:
            return; # Don't move if not meant to be running

        if now() < self.run_next_move_time:
            return; # Don't move until it is time to do so

        # Determine next stage for machine and tape
        out = self.machine.determine_output(self.run_curr_state, self.tape.get_at_head());

        if out == None:

            # If no transitions found, pause machine

            self.run_mode = RUN_MODE_PAUSED;

        else:

            # Extract output parts
            next_state, write_symbol, head_move = out;

            # Set new state
            self.run_curr_state = next_state;
            self.machine_window.set_curr_state(self.run_curr_state);

            # Write symbol to tape
            self.tape.set_at_head(write_symbol);

            # Move tape head
            self.tape.head_forward(head_move);

            # Set next move time
            self.run_next_move_time = now() + self.run_change_delay;

        # Refresh tape and machine

        self.machine_window.update_state_sprites();
        self.tape_window.refresh();

    # Checking window mouse is in

    def check_mouse_in_options_window(self,
        pos: tTuple[int, int]) -> bool:
        return self.options_window_rect.collidepoint(pos);

    def check_mouse_in_machine_window(self,
        pos: tTuple[int, int]) -> bool:
        return self.machine_window_rect.collidepoint(pos);

    def check_mouse_in_tape_window(self,
        pos: tTuple[int, int]) -> bool:
        return self.tape_window_rect.collidepoint(pos);

    def check_mouse_in_controls_window(self,
        pos: tTuple[int, int]) -> bool:
        return self.controls_window_rect.collidepoint(pos);

    # Handling pygame events

    def handle_pygame_evts(self) -> None:

        for evt in pygame.event.get():

            if evt.type == pygame.QUIT:
                self.stop_main_loop();

            elif evt.type == pygame.MOUSEBUTTONDOWN:
                self.handle_evt_mousedown();

            elif evt.type == pygame.KEYDOWN:
                self.handle_evt_keydown(evt);

    # Handle clicks

    def handle_evt_mousedown(self) -> None:

        mouse_pos = pygame.mouse.get_pos();

        # N.B. mouse position passed to click-handling methods is done relative to the window

        if self.check_mouse_in_options_window(mouse_pos):
            self.handle_options_window_click(MainController.global_pos_to_rect_relative(mouse_pos, self.options_window_rect));

        elif self.check_mouse_in_machine_window(mouse_pos):
            self.handle_machine_window_click(MainController.global_pos_to_rect_relative(mouse_pos, self.machine_window_rect));

        elif self.check_mouse_in_controls_window(mouse_pos):
            self.handle_controls_window_click(MainController.global_pos_to_rect_relative(mouse_pos, self.controls_window_rect));

    def handle_options_window_click(self,
        pos: tTuple[int, int]) -> None:

        if self.run_mode != RUN_MODE_STOPPED:
            return; # Can't use options while running machine

        if self.options_window.pos_in_save_button(pos):
            self.handle_options_window_save_button();

        elif self.options_window.pos_in_load_button(pos):
            self.handle_options_window_load_button();

    def handle_options_window_save_button(self):

        file = asksaveasfile(mode = "wb", defaultextension = MACHINE_FILE_EXTENSION, filetypes = MACHINE_FILETYPES);

        if file != None:

            bs = MachineSerializer.serialize(self.machine);

            file.write(bs);

            file.close();

            self.machine_window.set_status_text("Saved machine.");

    def handle_options_window_load_button(self):

        file = askopenfile(mode = "rb", defaultextension = MACHINE_FILE_EXTENSION, filetypes = MACHINE_FILETYPES);

        if file != None:

            self.machine = MachineSerializer.deserialize(file.read());

            file.close();

            self.set_machine(self.machine);
            self.machine_window.refresh();
            self.machine_window.set_status_text("Loaded machine.");

    def handle_machine_window_click(self,
        pos: tTuple[int, int]) -> None:

        if self.run_mode != RUN_MODE_STOPPED:
            return; # Can't edit machine while running

        if self.machine_click_mode == CLICK_MODE_CREATE:
            self.handle_machine_window_click_create(pos);

        elif self.machine_click_mode == CLICK_MODE_DELETE:
            self.handle_machine_window_click_delete(pos);

        elif self.machine_click_mode == CLICK_MODE_TRANSITION:
            self.handle_machine_window_click_transition(pos);

    def handle_machine_window_click_create(self,
        pos: tTuple[int, int]) -> None:

        clicked_state = self.machine_window.get_state_in_pos(pos);

        if clicked_state == None:

            can_create = self.check_can_create_state_in_pos(pos);

            if can_create:

                clicked_state = self.machine.add_state(pos);
                self.machine_window.create_state_sprite(clicked_state);

                self.machine_window.set_status_text(f"Created state {clicked_state.n}.");

            else:

                self.machine_window.set_status_text("Can't create state here.");

        else:

            self.machine_click_mode = CLICK_MODE_TRANSITION;
            self.transition_create_start = clicked_state;

            self.machine_window.set_status_text(f"Creating transition from {clicked_state.n}...");

    def handle_machine_window_click_delete(self,
        pos: tTuple[int, int]) -> None:
        
        clicked_state = self.machine_window.get_state_in_pos(pos);

        if clicked_state != None:

            self.machine.safe_remove_state(clicked_state.n);

            self.machine_window.set_status_text(f"Deleted state {clicked_state.n}.");

    def handle_machine_window_click_transition(self,
        pos: tTuple[int, int]) -> None:

        if self.transition_create_start == None:
            raise Exception("No start has been set when trying to create a transition.");

        end_state = self.machine_window.get_state_in_pos(pos);

        if end_state == None:

            self.machine_window.set_status_text(f"Cancelled creating transition for {self.transition_create_start.n}.");

        else:

            out = popup.run_transition_form();

            if out == None:

                self.machine_window.set_status_text(f"Didn't create transition for {self.transition_create_start.n}.");

            else:

                read_symbol, write_symbol, head_move = out;

                success = self.machine.try_add_transition(
                    start = self.transition_create_start.n,
                    end = end_state.n,
                    read_symbol = read_symbol,
                    write_symbol = write_symbol,
                    head_move = head_move
                );

                if success:

                    self.machine_window.refresh();

                    self.machine_window.set_status_text(f"Created transition from {self.transition_create_start.n} to {end_state.n}.");

                else:

                    self.machine_window.set_status_text("Couldn't create the attempted transition.");

        self.transition_create_start = None;
        self.machine_click_mode = CLICK_MODE_CREATE;

    def handle_controls_window_click(self,
        pos: tTuple[int, int]) -> None:

        if self.controls_window.pos_in_play_button(pos):
            self.handle_controls_window_play_button();

        elif self.controls_window.pos_in_pause_button(pos):
            self.handle_controls_window_pause_button();

        elif self.controls_window.pos_in_stop_button(pos):
            self.handle_controls_window_stop_button();

        # Refresh windows
        self.machine_window.update_state_sprites();
        self.tape_window.refresh();

    def handle_controls_window_play_button(self) -> None:

        if self.run_mode == RUN_MODE_STOPPED:

            # Don't try run without any states
            if len(self.machine.states) != 0:

                self.run_mode = RUN_MODE_PLAYING;

                # Store intial state of tape for returning to when stopping
                self.tape.store_initial_state();

                # Start at state 0
                self.run_curr_state = 0;
                self.machine_window.set_curr_state(self.run_curr_state);
                
                # Prepare to change state
                self.run_next_move_time = now() + self.run_change_delay;

        elif self.run_mode == RUN_MODE_PAUSED:

            self.run_mode = RUN_MODE_PLAYING;

            self.run_next_move_time = now() + self.run_change_delay;

    def handle_controls_window_pause_button(self) -> None:

        if self.run_mode == RUN_MODE_PLAYING:
            self.run_mode = RUN_MODE_PAUSED;

    def handle_controls_window_stop_button(self) -> None:

        if self.run_mode in (RUN_MODE_PLAYING, RUN_MODE_PAUSED):

            self.run_mode = RUN_MODE_STOPPED;

            # Set current run state to initial state
            self.run_curr_state = 0;
            self.machine_window.set_curr_state(0);

            # Load tape's initial state
            self.tape.load_initial_state();
            self.tape.head_to(0);

    # Handle key presses

    def handle_evt_keydown(self,
        evt: Event) -> None:

        if evt.key == self.keybindings.delete_bind:
            self.handle_delete_key_pressed();

    def handle_delete_key_pressed(self) -> None:

        if self.machine_click_mode == CLICK_MODE_CREATE:

            self.machine_click_mode = CLICK_MODE_DELETE;
            self.machine_window.set_status_text("Switched to delete mode.");

        elif self.machine_click_mode == CLICK_MODE_DELETE:

            self.machine_click_mode = CLICK_MODE_CREATE;
            self.machine_window.set_status_text("Switched to create mode.");
