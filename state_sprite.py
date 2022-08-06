from typing import List as tList;
from typing import Tuple as tTuple;
from pygame.sprite import Sprite;
import pygame;
from pygame import Vector2;
from machine import State;

class StateSprite(Sprite):

    def __init__(self,
        state: State,
        state_color: tTuple[int, int, int],
        curr_state_color: tTuple[int, int, int],
        text_color: tTuple[int, int, int],
        bg_color: tTuple[int, int, int],
        width: int,
        font: pygame.font.Font):

        super().__init__();

        self.width = width;

        self.state = state;
        self.is_curr = False;

        self.font = font;

        pos = self.state.pos - Vector2(width // 2);

        # Save colors

        self.state_color = state_color;
        self.curr_state_color = curr_state_color;
        self.text_color = text_color;
        self.bg_color = bg_color;

        # Set up image surface

        self.image = pygame.Surface(size = (width, width)); # Creates the initial surface to draw the sprite on

        # Set up rect

        self.rect = self.image.get_rect();
        self.rect.x = pos[0];
        self.rect.y = pos[1];

        # Draw onto surface
        
        self.redraw();

    def update(self,
        curr_state: int) -> None:

        super().update();

        self.is_curr = curr_state == self.state.n;

        self.redraw();

    def redraw(self) -> None:

        self.image.fill(color = self.bg_color); # Fills the surface with the background color
        self.image.set_colorkey(self.bg_color); # Sets what color pixels count as transparent pixels

        # Draw circle to surface

        color = (self.state_color) if (not self.is_curr) else (self.curr_state_color);

        pygame.draw.circle(
            surface = self.image,
            color = color,
            center = Vector2(self.width // 2),
            radius = self.width // 2
        );

        # Write n on circle
        
        text = self.font.render(
            str(self.state.n),
            True,
            self.text_color,
            None
        );
        
        text_width = text.get_rect().width;
        text_height = text.get_rect().height;

        text_pos = Vector2(self.width // 2);
        text_pos[0] -= text_width // 2;
        text_pos[1] -= text_height // 2;

        self.image.blit(
            source = text,
            dest = text_pos
        );

    def set_is_curr(self,
        b: bool) -> None:
        self.is_curr = b;

    def check_pos_in_sprite(self,
        pos: Vector2
        ) -> bool:

        """Checks whether the provided position is in the bounds of this state. Bounds are taken to be in the shape of a circle around the center"""
        
        disp = pos - self.state.pos;
        sqr_d = disp.magnitude_squared();

        return sqr_d <= (self.width/2)**2;
