from typing import Callable as tCallable;
from typing import Tuple as tTuple;
from pygame.sprite import Sprite;
from pygame.math import Vector2;
import pygame;

class ControlButtonSprite(Sprite):

    def __init__(self,
        center_pos: Vector2,
        width: int,
        draw_icon_call: tCallable[[pygame.Surface, tTuple[int, int, int], Vector2, int], None],
        icon_padding: int,
        button_bg_color: tTuple[int, int, int],
        shaded_button_bg_color: tTuple[int, int, int],
        icon_color: tTuple[int, int, int],
        main_bg_color: tTuple[int, int, int]):

        super().__init__();

        self.draw_icon_call = draw_icon_call;
        self.center_pos = center_pos;
        self.width = width;
        self.icon_padding = icon_padding;
        self.button_bg_color = button_bg_color;
        self.shaded_button_bg_color = shaded_button_bg_color;
        self.icon_color = icon_color;
        self.main_bg_color = main_bg_color;

        self.shaded = False;

        pos = self.center_pos - Vector2(self.width // 2);

        # Set up image

        self.image = pygame.Surface((self.width, self.width));
        self.image.set_colorkey(self.main_bg_color);

        # Set up rect

        self.rect = self.image.get_rect();
        self.rect.x = pos[0];
        self.rect.y = pos[1];

    def update(self):

        super().update();

        # Clear

        self.image.fill(self.main_bg_color);

        # Draw rounded button background

        pygame.draw.rect(
            surface = self.image,
            color = self.button_bg_color if not self.shaded else self.shaded_button_bg_color,
            rect = (
                0,
                0,
                self.width,
                self.width
            ),
            border_radius = 3
        );

        # Draw icon using callable set

        self.draw_icon_call(
            self.image,
            self.icon_color,
            Vector2(
                self.image.get_width() // 2,
                self.image.get_height() // 2
            ),
            self.width - (2 * self.icon_padding)
        );

    def set_shaded_state(self,
        state: bool) -> None:
        self.shaded = state;
