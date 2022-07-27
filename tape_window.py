from typing import List as tList;
from typing import Tuple as tTuple;
from pygame import Surface;
import pygame;

from tape import Tape;

SYMBOLS_SHOWN_EACH_SIDE = 4; # Number of symbols shown on either side of current symbol

SYMBOL_CELL_WIDTH = 80;
SYMBOL_CELL_BORDER = 10; # Pixels of space on sides cell to leave

SYMBOL_COLOR = (0, 0, 0);
CELL_INDEX_COLOR = (0, 0, 50);
CELL_COLOR_A = (150, 150, 150);
CELL_COLOR_B = (100, 100, 100);

HEAD_CELL_ICON_COLOR = (0, 0, 0);
HEAD_CELL_ICON_HALFWIDTH = 15;
HEAD_CELL_ICON_HEIGHT = 15;

class TapeWindow(Surface):

    def __init__(self,
        size: tTuple[int, int],
        tape: Tape,
        bg_color: tTuple[int, int, int],
        font: pygame.font.Font):

        super().__init__(
            size = size
        );

        self.cell_width = SYMBOL_CELL_WIDTH;
        self.cell_height = self.get_height() - (2 * SYMBOL_CELL_BORDER);
        
        self.tape = tape;

        self.bg_color = bg_color;

        self.font = font;

        self.value_sprites = pygame.sprite.Group();
        self.tape_sprites = pygame.sprite.Group();

        self.refresh();

    def refresh(self):

        # Fill with background color

        self.fill(self.bg_color);

        # Clear existing sprites

        self.value_sprites.empty();
        self.tape_sprites.empty();

        # Add new sprites

        for i in range(-SYMBOLS_SHOWN_EACH_SIDE, SYMBOLS_SHOWN_EACH_SIDE + 1):

            cell_index = self.tape.head + i;

            # Find positions in cell

            cell_center_pos = (
                (self.get_width() // 2) + ((self.cell_width + SYMBOL_CELL_BORDER) * i),
                (self.get_height() // 2)
            );

            cell_bottom_left_pos = (
                cell_center_pos[0] - (self.cell_width // 2),
                cell_center_pos[1] + (self.cell_height // 2)
            );

            cell_top_middle_pos = (
                cell_center_pos[0],
                cell_center_pos[1] - (self.cell_height // 2)
            );

            # Determine cell color

            if cell_index % 2 == 0:
                cell_color = CELL_COLOR_A;
            else:
                cell_color = CELL_COLOR_B;

            # Draw cell rectamgle

            pygame.draw.rect(
                surface = self,
                color = cell_color,
                rect = (
                    cell_center_pos[0] - (self.cell_width // 2),
                    cell_center_pos[1] - (self.cell_height // 2),
                    self.cell_width,
                    self.cell_height
                )
            );

            # Draw head marker if head cell

            if i == 0:

                pygame.draw.polygon(
                    surface = self,
                    color = HEAD_CELL_ICON_COLOR,
                    points = (
                        (cell_top_middle_pos[0] - HEAD_CELL_ICON_HALFWIDTH, cell_top_middle_pos[1]),
                        (cell_top_middle_pos[0] + HEAD_CELL_ICON_HALFWIDTH, cell_top_middle_pos[1]),
                        (cell_top_middle_pos[0], cell_top_middle_pos[1] + HEAD_CELL_ICON_HEIGHT),
                    )
                )

            # Draw cell symbol

            symbol_text = self.font.render(
                str(self.tape.get(cell_index)),
                True,
                SYMBOL_COLOR,
                None
            );

            self.blit(
                source = symbol_text,
                dest = (
                    cell_center_pos[0] - (symbol_text.get_width() // 2),
                    cell_center_pos[1] - (symbol_text.get_height() // 2)
                )
            );

            # Draw cell index

            index_text = self.font.render(
                str(cell_index),
                True,
                CELL_INDEX_COLOR,
                None
            );

            self.blit(
                source = index_text,
                dest = (
                    cell_bottom_left_pos[0],
                    cell_bottom_left_pos[1] - index_text.get_height()
                )
            )

        # Render sprites

        self.tape_sprites.draw(self);
        self.value_sprites.draw(self);

    def scroll_amount(self, n: int) -> None:
        self.scroll_to(self.index + n);

    def scroll_to(self, i: int) -> None:
        
        self.index = i;
        self.refresh();
