from typing import List as tList;
from typing import Tuple as tTuple;
from pygame.sprite import Sprite;
import pygame;
from machine import Machine, Transition, State;

class TransitionsSprite(Sprite):

    """A sprite that will draw a line from one state to another and describe all the transitions between the two states"""

    def __init__(self,
        machine: Machine,
        start: State,
        end: State,
        color: tTuple[int, int, int],
        text_color: tTuple[int, int, int],
        bg_color: tTuple[int, int, int],
        line_width: int,
        font: pygame.font.Font):

        super().__init__();

        self.machine = machine;
        self.transitions = self.machine.get_transitions_between(start, end);

        # Check if any transitions exist between the two states

        if len(self.transitions) == 0:
            raise Exception("No transitions exist between the provided states");

        # Calculate positions

        start_pos_global = start.pos;
        end_pos_global = end.pos;

        origin = ( # The point that will be the top-left position
            min(start_pos_global[0], end_pos_global[0]),
            min(start_pos_global[1], end_pos_global[1])
        );

        width = abs(start_pos_global[0] - end_pos_global[0]);
        height = abs(start_pos_global[1] - end_pos_global[1]);

        start_pos_local = (
            start_pos_global[0] - origin[0],
            start_pos_global[1] - origin[1]
        );

        end_pos_local = (
            end_pos_global[0] - origin[0],
            end_pos_global[1] - origin[1]
        );

        # Set up surface

        self.image = pygame.Surface(size = (width, height)); # Creates the initial surface to draw the sprite on

        self.image.fill(color = bg_color); # Fills the surface with the background color
        self.image.set_colorkey(bg_color); # Sets what color pixels count as transparent pixels

        # Draw arrow to surface
        
        pygame.draw.line(
            surface = self.image,
            color = color,
            start_pos = start_pos_local,
            end_pos = end_pos_local,
            width = line_width
        );

        # Write details along line

        details_transitions_texts = [t.to_string() for t in self.transitions];
        details_transitions_texts_sizes = list(map(lambda s: font.size(s), details_transitions_texts));

        details_texts_surface_width = max([size[0] for size in details_transitions_texts_sizes]);
        details_texts_surface_height = sum([size[1] for size in details_transitions_texts_sizes]);

        details_text_surface = pygame.Surface((details_texts_surface_width, details_texts_surface_height));
        details_text_surface.fill(bg_color);

        h_incrementer = 0;

        for i in range(len(details_transitions_texts)):

            t = details_transitions_texts[i];

            text = font.render(
                t,
                True,
                text_color,
                bg_color
            );

            text_pos = (
                (details_text_surface.get_width() // 2) - (text.get_width() // 2),
                h_incrementer
            );

            h_incrementer += details_transitions_texts_sizes[i][1];

            details_text_surface.blit(
                source = text,
                dest = text_pos
            );

        self.image.blit(
            source = details_text_surface,
            dest = (
                (width // 2) - (details_texts_surface_width // 2),
                (height // 2) - (details_texts_surface_height // 2),
            )
        );

        #TODO - create text(s), render it/them, blit it/them onto surface in correct position(s)

        # Set up rect

        self.rect = self.image.get_rect();
        self.rect.x = origin[0];
        self.rect.y = origin[1];
