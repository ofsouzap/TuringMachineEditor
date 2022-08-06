from typing import Callable as tCallable;
from typing import Tuple as tTuple;
from typing import List as tList;
from pygame import Surface, Vector2;
import pygame;

from control_button_sprite import ControlButtonSprite;

BUTTON_WIDTH = 50;
BUTTON_SEPARATION = 10;
BUTTON_ICON_PADDING = 10;

BUTTON_BG_COLOR = (200, 200, 200);
BUTTON_ICON_COLOR = (0, 0, 0);

# Icon shapes

PLAY_ICON_POINTS = [
    (0, 0),
    (1, 0.5),
    (0, 1),
];

PAUSE_ICON_POINTS_0 = [
    (0, 0),
    (0.4, 0),
    (0.4, 1),
    (0, 1)
];

PAUSE_ICON_POINTS_1 = [
    (0.6, 0),
    (1, 0),
    (1, 1),
    (0.6, 1)
];

STOP_ICON_POINTS = [
    (0, 0),
    (1, 0),
    (1, 1),
    (0, 1)
];

class ControlsWindow(Surface):

    def __init__(self,
        size: tTuple[int, int],
        bg_color: tTuple[int, int, int]):

        super().__init__(size);

        self.bg_color = bg_color;

        self.button_sprites = pygame.sprite.Group();

        center = Vector2(
            self.get_width() // 2,
            self.get_height() // 2
        );

        button_separation_displacement = Vector2(1, 0) * (BUTTON_WIDTH + BUTTON_SEPARATION);

        # Pause button

        self.pause_button = ControlButtonSprite(
            center_pos = center - button_separation_displacement,
            width = BUTTON_WIDTH,
            draw_icon_call = ControlsWindow.draw_pause_icon,
            icon_padding = BUTTON_ICON_PADDING,
            button_bg_color = BUTTON_BG_COLOR,
            icon_color = BUTTON_ICON_COLOR,
            main_bg_color = self.bg_color
        );

        self.button_sprites.add(self.pause_button);

        # Play button

        self.play_button = ControlButtonSprite(
            center_pos = center,
            width = BUTTON_WIDTH,
            draw_icon_call = ControlsWindow.draw_play_icon,
            icon_padding = BUTTON_ICON_PADDING,
            button_bg_color = BUTTON_BG_COLOR,
            icon_color = BUTTON_ICON_COLOR,
            main_bg_color = self.bg_color
        );

        self.button_sprites.add(self.play_button);

        # Stop button

        self.stop_button = ControlButtonSprite(
            center_pos = center + button_separation_displacement,
            width = BUTTON_WIDTH,
            draw_icon_call = ControlsWindow.draw_stop_icon,
            icon_padding = BUTTON_ICON_PADDING,
            button_bg_color = BUTTON_BG_COLOR,
            icon_color = BUTTON_ICON_COLOR,
            main_bg_color = self.bg_color
        );

        self.button_sprites.add(self.stop_button);

        # Refresh canvas

        self.refresh();

    def refresh(self):

        # Clear window

        self.fill(self.bg_color);

        # Update sprites

        self.button_sprites.update();

        # Draw sprites

        self.button_sprites.draw(self);

    def pos_in_play_button(self,
        pos: Vector2) -> bool:
        return self.play_button.rect.collidepoint(pos);

    def pos_in_pause_button(self,
        pos: Vector2) -> bool:
        return self.pause_button.rect.collidepoint(pos);

    def pos_in_stop_button(self,
        pos: Vector2) -> bool:
        return self.stop_button.rect.collidepoint(pos);

    @staticmethod
    def process_shape_points(orig: tList[Vector2],
        width: int,
        center: Vector2
        ) -> tList[Vector2]:
        
        half_vec = Vector2(0.5);

        points = [((p - half_vec) * width) + center for p in orig];

        return points;

    @staticmethod
    def draw_play_icon(surface: Surface,
        color: tTuple[int, int, int],
        center: Vector2,
        width: int) -> None:

        points = ControlsWindow.process_shape_points(
            orig = PLAY_ICON_POINTS,
            width = width,
            center = center
        );

        pygame.draw.polygon(
            surface = surface,
            color = color,
            points = points
        );

    @staticmethod
    def draw_pause_icon(surface: Surface,
        color: tTuple[int, int, int],
        center: Vector2,
        width: int) -> None:

        points0 = ControlsWindow.process_shape_points(
            orig = PAUSE_ICON_POINTS_0,
            width = width,
            center = center
        );

        pygame.draw.polygon(
            surface = surface,
            color = color,
            points = points0
        );

        points1 = ControlsWindow.process_shape_points(
            orig = PAUSE_ICON_POINTS_1,
            width = width,
            center = center
        );

        pygame.draw.polygon(
            surface = surface,
            color = color,
            points = points1
        );

    @staticmethod
    def draw_stop_icon(surface: Surface,
        color: tTuple[int, int, int],
        center: Vector2,
        width: int) -> None:

        points = ControlsWindow.process_shape_points(
            orig = STOP_ICON_POINTS,
            width = width,
            center = center
        );

        pygame.draw.polygon(
            surface = surface,
            color = color,
            points = points
        );
