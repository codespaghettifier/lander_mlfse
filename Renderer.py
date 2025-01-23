import pymunk
import pygame
import json
import math


class Drawable:
    def __init__(self, position, anchor_point=(0.5, 0.5)):
        self.surface = None
        self.position = position
        self.anchor_point = anchor_point
        self.last_scale = 1
        self.rendered = False
        self.surface = None

    def render(self, scale):
        if scale != self.last_scale:
            self.rendered = False
            self.surface = None
            self.last_scale = scale

    def get_position(self):
        return self.position


class DrawableGroup:
    def __init__(self):
        self.rendered = False

    def get_drawables(self):
        raise NotImplementedError


class Renderer:
    def __init__(self, surface, center, scale):
        self.surface = surface
        self.surface_width = surface.get_width()
        self.surface_height = surface.get_height()
        self.center = center
        self.scale = scale
        
    def draw(self, drawable):
        drawable.render(self.scale)

        width, height = drawable.surface.get_size()

        anchor_shift_x = width * -drawable.anchor_point[0]
        anchor_shift_y = height * -drawable.anchor_point[1]
        center_shift_x = -self.center[0] * self.scale
        center_shift_y = -self.center[1] * self.scale
        position_x = drawable.get_position()[0] * self.scale + anchor_shift_x + center_shift_x
        position_y = drawable.get_position()[1] * self.scale  + anchor_shift_y + center_shift_y

        x = position_x  + 0.5 * self.surface_width
        y = -(position_y) + 0.5 * self.surface_height - height

        # print(position_x, position_y, width, height, anchor_shift_x, anchor_shift_y, center_shift_x, center_shift_y, x, y)

        self.surface.blit(drawable.surface, (x, y))

    def draw_group(self, drawable_group):
        for drawable in drawable_group.get_drawables():
            self.draw(drawable)

    