import pygame
import pymunk
import Renderer


class RectangularObject(Renderer.Drawable):
    def __init__(self, width, height, position, anchor_point=(0.5, 0.5), color=(255, 255, 255), body_type=None):
        super().__init__(position, anchor_point)
        self.width = width
        self.height = height
        self.color = color
        self.body_type = body_type
        self.body = None
        self.shape = None

        if self.body_type is None:
            return
        
        self.body = pymunk.Body(body_type=self.body_type)
        self.body.position = self.position
        self.shape = pymunk.Poly.create_box(self.body, (self.width, self.height))

    def render(self, scale):
        super().render(scale)
        if self.rendered:
            return
        
        if self.surface is None:
            self.surface = pygame.Surface((self.width * scale, self.height * scale), pygame.SRCALPHA)

        self.surface.fill(self.color)
        self.rendered = True

    def get_position(self):
        return self.body.position if self.body is not None else self.position

    def add_to_space(self, space):

        
        space.add(self.body, self.shape)

    def __str__(self):
        return f"RectangularObject(width={self.width}, height={self.height}, position={self.position}, anchor_point={self.anchor_point})"