from pygame import Rect;
import pygame;
from keybindings import Keybinding;

from main_controller import MainController;

WINDOW_TITLE = "Turing Machine Editor";

OPTIONS_WINDOW_RECT = Rect((0, 0), (1000, 100))
MACHINE_WINDOW_RECT = Rect((0, 100), (1000, 500));
TAPE_WINDOW_RECT = Rect((0, 600), (1000, 100));
CONTROLS_WINDOW_RECT = Rect((0, 700), (1000, 100));

BG_COLOR = (255, 255, 255);

KEYBINDINGS = Keybinding(
    delete_bind = pygame.K_d
);

FRAMERATE = 20;

MINIMUM_STATE_SEPARATION_MULTIPLIER = 3;

# How long (in seconds) to wait between stepping between states when running the machine
MACHINE_RUN_CHANGE_DELAY = 1;

def main():

    controller = MainController(
        window_title = WINDOW_TITLE,
        options_window_rect = OPTIONS_WINDOW_RECT,
        machine_window_rect = MACHINE_WINDOW_RECT,
        tape_window_rect = TAPE_WINDOW_RECT,
        controls_window_rect = CONTROLS_WINDOW_RECT,
        bg_color = BG_COLOR,
        keybindings = KEYBINDINGS,
        framerate = FRAMERATE,
        state_minimum_separation_factor = MINIMUM_STATE_SEPARATION_MULTIPLIER,
        run_change_delay = MACHINE_RUN_CHANGE_DELAY
    );

    controller.run_main_loop();

    controller.cleanup();

if __name__ == "__main__":
    main();