import pygame;

class Keybinding:

    def __init__(self,
        delete_bind: int = pygame.K_d):

        self.delete_bind = delete_bind;