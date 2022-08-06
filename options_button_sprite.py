from typing import Callable as tCallable;
from typing import Tuple as tTuple;
from pygame.sprite import Sprite;
from pygame import Vector2;
import pygame;

class OptionsButtonSprite(Sprite):

    def __init__(self,
        center_pos: Vector2,
        dims: tTuple[int, int],
        text: str,
        font: pygame.font.Font,
        button_bg_color: tTuple[int, int, int],
        text_color: tTuple[int, int, int],
        main_bg_color: tTuple[int, int, int]):

        super().__init__();

        self.center_pos = center_pos;
        self.dims = dims;
        self.text = text;
        self.font = font;
        self.button_bg_color = button_bg_color;
        self.text_color = text_color;
        self.main_bg_color = main_bg_color;

        pos = self.center_pos - (Vector2(self.dims) // 2);

        # Set up image

        self.image = pygame.Surface(self.dims);
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
            self.image,
            color = self.button_bg_color,
            rect = (
                0,
                0,
                self.dims[0],
                self.dims[1]
            ),
            border_radius = 3
        );

        # Write text onto rect

        text_surface = self.font.render(
            self.text,
            True,
            self.text_color,
            None
        );
        
        self.image.blit(
            source = text_surface,
            dest = (
                (self.image.get_width() // 2) - (text_surface.get_width() // 2),
                (self.image.get_height() // 2) - (text_surface.get_height() // 2),
            )
        );
