from typing import Callable as tCallable;
from typing import Tuple as tTuple;
from typing import List as tList;
from pygame import Surface, Vector2;
import pygame;

from options_button_sprite import OptionsButtonSprite;

BUTTON_DIMS = (120, 40);
BUTTON_SEPARATION = 10;

BUTTON_BG_COLOR = (200, 200, 200);
BUTTON_TEXT_COLOR = (0, 0, 0);

class OptionsWindow(Surface):

    def __init__(self,
        size: tTuple[int, int],
        bg_color: tTuple[int, int, int],
        font: pygame.font.Font):

        super().__init__(size);

        self.bg_color = bg_color;
        self.font = font;

        self.button_sprites = pygame.sprite.Group();

        # Save button

        self.save_button = OptionsButtonSprite(
            center_pos = self.get_nth_button_center_pos(0),
            dims = BUTTON_DIMS,
            text = "Save",
            font = self.font,
            button_bg_color = BUTTON_BG_COLOR,
            text_color = BUTTON_TEXT_COLOR,
            main_bg_color = self.bg_color
        );

        self.button_sprites.add(self.save_button);

        # Load button

        self.load_button = OptionsButtonSprite(
            center_pos = self.get_nth_button_center_pos(1),
            dims = BUTTON_DIMS,
            text = "Load",
            font = self.font,
            button_bg_color = BUTTON_BG_COLOR,
            text_color = BUTTON_TEXT_COLOR,
            main_bg_color = self.bg_color
        );

        self.button_sprites.add(self.load_button);

        # Load tape button

        self.load_tape_button = OptionsButtonSprite(
            center_pos = self.get_nth_button_center_pos(2),
            dims = BUTTON_DIMS,
            text = "Load Tape",
            font = self.font,
            button_bg_color = BUTTON_BG_COLOR,
            text_color = BUTTON_TEXT_COLOR,
            main_bg_color = self.bg_color
        );

        self.button_sprites.add(self.load_tape_button);

        # Refresh to start

        self.refresh();

    def refresh(self):

        # Clear window

        self.fill(self.bg_color);

        # Update sprites

        self.button_sprites.update();

        # Draw sprites

        self.button_sprites.draw(self);

    def get_nth_button_center_pos(self,
        n: int):
        return (
            ((BUTTON_SEPARATION // 2) + (BUTTON_DIMS[0] // 2)) + (n * (BUTTON_DIMS[0] + BUTTON_SEPARATION)),
            self.get_height() // 2
        );

    def pos_in_save_button(self,
        pos: Vector2) -> bool:
        return self.save_button.rect.collidepoint(pos);

    def pos_in_load_button(self,
        pos: Vector2) -> bool:
        return self.load_button.rect.collidepoint(pos);

    def pos_in_load_tape_button(self,
        pos: Vector2) -> bool:
        return self.load_tape_button.rect.collidepoint(pos);
