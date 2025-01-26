import pymunk
import pygame
import json

from RectangularObject import RectangularObject
from Renderer import Renderer
from Terrain import Terrain, TerrainElement
from Lander import Lander, LanderCatchPin

class Simulation:
    def __init__(self, settings, lander_initial_position, iterations_per_step, lander_initial_angle=0):
        self.result = None
        self.seering_input = None
        self.iterations_per_step = iterations_per_step

        self.lander_initial_angle = lander_initial_angle

        self.space = pymunk.Space()
        self.space.gravity = 0, -9.81

        self.terrain = Terrain(settings["terrain"])
        self.terrain.add_to_space(self.space)

        self.lander = Lander(settings["lander"], lander_initial_position)
        self.lander.add_to_space(self.space)
        self.lander.body.angle = self.lander_initial_angle

        self.handler_collision_lander_terrain = self.space.add_collision_handler(Lander.LANDER_COLISION_TYPE, TerrainElement.TERRAIN_ELEMENT_COLISION_TYPE)
        self.handler_collision_catch_pin_arm = self.space.add_collision_handler(LanderCatchPin.CATCH_PIN_COLISION_TYPE, TerrainElement.ARM_COLISION_TYPE)
        self.handler_collision_lander_catch_pin_arm = self.space.add_collision_handler(Lander.LANDER_COLISION_TYPE, LanderCatchPin.CATCH_PIN_COLISION_TYPE)
        self.handler_collision_lander_arm = self.space.add_collision_handler(Lander.LANDER_COLISION_TYPE, TerrainElement.ARM_COLISION_TYPE)
        self.handler_collision_lander_terrain.begin = self._handle_collision_lander_terrain
        self.handler_collision_lander_arm.begin = self._handle_collision_ignore
        self.handler_collision_lander_catch_pin_arm.begin = self._handle_collision_ignore
        self.handler_collision_catch_pin_arm.begin = self._handle_collision_catch_pin_arm

    def step(self, delta_time):
        for _ in range(self.iterations_per_step):
            self.space.step(delta_time / self.iterations_per_step)
        return self.result, self.lander.get_telemetry()

    def set_steering_input(self, steering_input):
        self.lander.update_steering(steering_input)

    def draw(self, renderer):
        renderer.draw(self.lander)
        renderer.draw_group(self.terrain)

    def reset(self):
        self.result = None
        self.lander.reset()
        self.lander.body.angle = self.lander_initial_angle

    def _handle_collision_lander_terrain(self, arbiter, space, data):
        self.result = "Collision with terrain"
        return True
    
    def _handle_collision_ignore(self, arbiter, space, data):
        return False
    
    def _handle_collision_catch_pin_arm(self, arbiter, space, data):
        self.result = "Collision with arm"
        return True

