from typing import List as tList;
from typing import Tuple as tTuple;
from pygame.sprite import Sprite;
import pygame;
from machine import State;

class StateSprite(Sprite):

    def __init__(self,
        state: State,
        color: tTuple[int, int, int],
        text_color: tTuple[int, int, int],
        bg_color: tTuple[int, int, int],
        width: int,
        font: pygame.font.Font):

        super().__init__();

        self.width = width;

        self.state = state;

        n = self.state.n;
        pos = (
            self.state.pos[0] - (width // 2),
            self.state.pos[1] - (width // 2)
        );

        # Set up image surface

        self.image = pygame.Surface(size = (width, width)); # Creates the initial surface to draw the sprite on

        self.image.fill(color = bg_color); # Fills the surface with the background color
        self.image.set_colorkey(bg_color); # Sets what color pixels count as transparent pixels

        # Draw circle to surface

        pygame.draw.circle(
            surface = self.image,
            color = color,
            center = (width // 2, width // 2),
            radius = width // 2
        );

        # Write n on circle
        
        text = font.render(
            str(n),
            True,
            text_color,
            None
        );
        
        text_width = text.get_rect().width;
        text_height = text.get_rect().height;

        text_pos = (
            width // 2 - (text_width // 2),
            width // 2 - (text_height // 2)
        );

        self.image.blit(
            source = text,
            dest = text_pos
        );

        # Set up rect

        self.rect = self.image.get_rect();
        self.rect.x = pos[0];
        self.rect.y = pos[1];

    def check_pos_in_sprite(self,
        pos: tTuple[int, int]
        ) -> bool:

        """Checks whether the provided position is in the bounds of this state. Bounds are taken to be in the shape of a circle around the center"""
        
        sqr_d = ((pos[0] - self.state.pos[0])**2) + ((pos[1] - self.state.pos[1])**2);

        return sqr_d <= (self.width/2)**2;
