from typing import List as tList;
from typing import Tuple as tTuple;
from pygame import Surface, Vector2;
import pygame;

from machine import Machine, State, Transition;

from state_sprite import StateSprite;
from transitions_sprite import TransitionsSprite;

STATE_COLOR = (0, 0, 0);
CURR_STATE_COLOR = (0, 100, 200);
STATE_TEXT_COLOR = (255, 0, 0);
STATE_WIDTH = 40;

TRANSITION_COLOR = (255, 0, 255);
TRANSITION_TEXT_COLOR = (255, 0, 0);
TRANSITION_LINE_WIDTH = 5;
TRANSITION_LOOP_HEIGHT = 50;

STATUS_TEXT_COLOR = (0, 0, 255);
STATUS_TEXT_POS = (5, 5);

class MachineWindow(Surface):

    def __init__(self,
        size: tTuple[int, int],
        machine: Machine,
        bg_color: tTuple[int, int, int],
        state_font: pygame.font.Font,
        transition_font: pygame.font.Font):

        super().__init__(
            size = size
        );
        
        self.machine = machine;

        self.curr_state = 0;

        self.bg_color = bg_color;
        self.state_font = state_font;
        self.transition_font = transition_font;

        self.state_sprites = pygame.sprite.Group();
        self.transition_sprites = pygame.sprite.Group();

        self.status_text = "";

        self.set_status_text("");
        self.refresh();

    def refresh(self) -> None:

        """Clears all machine sprites on the surface and re-draws them, looking at the state of the machine"""

        # Fill with background color

        self.fill(self.bg_color);

        # Clear existing sprites

        self.state_sprites.empty();
        self.transition_sprites.empty();

        # Add new sprites

        for i in range(len(self.machine.states)):

            s1 = self.machine.states[i];

            self.create_state_sprite(s1);

            for j in range(i, len(self.machine.states)):

                s2 = self.machine.states[j];

                self.create_transitions_sprite(s1, s2);

        # Initially update state sprites (for setting current state)

        self.update_state_sprites();

        # Draw sprites

        self.redraw_sprites();

        # Render status text

        text_surface = self.state_font.render(
            self.status_text,
            False,
            STATUS_TEXT_COLOR,
            None
        );

        self.blit(
            source = text_surface,
            dest = STATUS_TEXT_POS
        );

    def set_machine(self, m: Machine) -> None:
        self.machine = m;

    def redraw_sprites(self) -> None:

        # Render sprites

        self.transition_sprites.draw(self);
        self.state_sprites.draw(self);

    def update_state_sprites(self) -> None:

        self.state_sprites.update(curr_state = self.curr_state);

        self.redraw_sprites();

    def create_state_sprite(self,
        state: State
        ) -> None:

        s = StateSprite(
            state = state,
            state_color = STATE_COLOR,
            curr_state_color = CURR_STATE_COLOR,
            text_color = STATE_TEXT_COLOR,
            bg_color = self.bg_color,
            width = STATE_WIDTH,
            font = self.state_font
        );

        self.state_sprites.add(s);

    def create_transitions_sprite(self,
        s1: State,
        s2: State
        ) -> None:

        if len(self.machine.get_transitions_between(s1, s2)) == 0:
            return;

        s = TransitionsSprite(
            machine = self.machine,
            parent_dims = self.get_size(),
            start = s1,
            end = s2,
            color = TRANSITION_COLOR,
            text_color = TRANSITION_TEXT_COLOR,
            bg_color = self.bg_color,
            line_width = TRANSITION_LINE_WIDTH,
            loop_transition_height = TRANSITION_LOOP_HEIGHT,
            font = self.transition_font
        );

        self.transition_sprites.add(s);

    def get_state_in_pos(self,
        pos: Vector2
        ) -> State | None:

        for s in self.state_sprites:

            if s.check_pos_in_sprite(pos):
                return s.state;

        return None;

    def set_status_text(self,
        text: str | None) -> None:

        if text == None:
            text = "";

        self.status_text = text;

        self.refresh();

    def set_curr_state(self,
        n: int) -> None:

        self.curr_state = n;
        self.update_state_sprites();
