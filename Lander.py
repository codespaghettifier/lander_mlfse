import pymunk
import pygame
import math

from Renderer import DrawableGroup, Renderer
from RectangularObject import RectangularObject


class Thruster:
    def __init__(self, settings):
        self.x = settings["x"]
        self.y = settings["y"]
        self.is_on = False
        self.lander_body = None

    def draw(self, surface, scale):
        width = self.width * scale
        height = self.height * scale
        x = 0.5 * surface.get_width() + self.x * scale - 0.5 * width
        y = surface.get_height() - height - self.y * scale
        color = (0, 255, 0) if self.is_on else (0, 69, 255)
        pygame.draw.rect(surface, color, (x, y, width, height))

    def set_lander_body(self, body):
        self.lander_body = body

    def updateSteering(self, is_on):
        self.is_on = is_on


class LanderEngine(Thruster):
    def __init__(self, commonSettings, settings):
        super().__init__(settings)
        self.thrust = commonSettings["engineThrust"]    # kN
        self.isp = commonSettings["engineIsp"]  # s
        self.width = 1
        self.height = 2

    def updateSteering(self, is_on):
        super().updateSteering(is_on)

        if self.is_on:
            self.lander_body.apply_force_at_local_point((0, self.thrust * 10), (self.x, self.y))


class RcsThruster(Thruster):
    def __init__(self, commonSettings, settings):
        super().__init__(settings)
        self.thrust = commonSettings["rcsThrusterThrust"]   # kN
        self.isp = commonSettings["rcsThrusterIsp"] # s
        self.width = 2
        self.height = 1

    def updateSteering(self, is_on):
        super().updateSteering(is_on)

        if self.is_on:
            force = self.thrust * 10 * (1 if self.x < 0 else -1)
            self.lander_body.apply_force_at_local_point((force, 0), (self.x, self.y))


class LanderCatchPin:
    CATCH_PIN_COLISION_TYPE = 3

    def __init__(self, settings, lander_position):
        self.x = settings["x"]
        self.y = settings["y"]
        self.radius = settings["radius"]
        self.lander_body = None

        self.body = pymunk.Body(body_type=pymunk.Body.DYNAMIC)
        self.body.mass = 1
        self.body.moment = pymunk.moment_for_circle(self.body.mass, 0, self.radius)
        self.body.position = (lander_position[0] + settings["x"], lander_position[1] + settings["y"])
        self.shape = pymunk.Circle(self.body, self.radius)
        self.shape.collision_type = LanderCatchPin.CATCH_PIN_COLISION_TYPE

    def draw(self, surface, scale):
        radius = self.radius * scale
        x = 0.5 * surface.get_width() + self.x * scale
        y = surface.get_height() - self.y * scale
        color = (0, 64, 255)
        pygame.draw.circle(surface, color, (int(x), int(y)), int(radius))

    def set_lander_body(self, body):
        self.lander_body = body

    def add_to_space(self, space):
        space.add(self.body, self.shape)

    def reset(self):
        self.body.position = self.lander_body.position[0] + self.x, self.lander_body.position[1] + self.y
        self.body.velocity = 0, 0
        self.body.angle = 0
        self.body.angular_velocity = 0


class Lander(RectangularObject):
    LANDER_COLISION_TYPE = 4

    def __init__(self, settings, initial_position):
        self.initial_position = initial_position
        self.width = settings["width"]  # m
        self.height = settings["height"]    # m
        self.dryMass = settings["dryMass"]  # t
        self.propellantCapacity = settings["propellantCapacity"]  # t
        self.propellantMass = settings["propellantMass"]    # t
        self.engineFlameLength = settings["engineFlameLength"]  # m
        self.rcsThrusterFlameLength = settings["rcsThrusterFlameLength"]    # m

        super().__init__(self.width, self.height, self.initial_position, anchor_point=(0.5, 0.5), color=(128, 128, 128), body_type=pymunk.Body.DYNAMIC)
    
        moment_dry = pymunk.moment_for_box(self.dryMass, (self.width, self.height))
        moment_propellant = pymunk.moment_for_box(self.propellantMass, (self.width, self.propellantMass / self.propellantCapacity * self.height))
        self.body.moment = moment_dry + moment_propellant
        self.body.mass = self.dryMass + self.propellantMass
        self.body.position = self.initial_position[0], self.initial_position[1] + self.height / 2

        self.catch_pin = LanderCatchPin(settings["catchPin"], initial_position)
        self.engines = []
        for engine in settings["engines"]:
            self.engines.append(LanderEngine(settings, engine))
        self.rcsThrusters = []
        for thruster in settings["rcsThrusters"]:
            self.rcsThrusters.append(RcsThruster(settings, thruster))

        self.shape.collision_type = Lander.LANDER_COLISION_TYPE
        catch_pin_y = settings["catchPin"]["y"]
        anchor_offset = (0, catch_pin_y - self.height / 2)
        self.catch_pin_joint = pymunk.PinJoint(self.body, self.catch_pin.body, anchor_offset, (0, 0))

        self.hull_surface = None
        self.hull_surface_rendered = False

    def render(self, scale):
        self.render_hull_surface(scale)

        self.surface = pygame.Surface((self.width * scale, self.height * scale), pygame.SRCALPHA)
        self.surface.blit(self.hull_surface, (0, 0))

        angle = math.degrees(self.body.angle)
        self.surface = pygame.transform.rotate(self.hull_surface, angle)

    def render_hull_surface(self, scale):
        if self.hull_surface_rendered:
            return

        if self.hull_surface is None:
            self.hull_surface = pygame.Surface((self.width * scale, self.height * scale), pygame.SRCALPHA)

        self.render_hull(scale)
        self.render_catch_pin(scale)
        self.render_engines(scale)
        self.render_rcs_thrusters(scale)

    def render_hull(self, scale):
        # Hull
        self.hull_surface.fill(self.color)

        # Propellant
        width = self.width * scale
        height = self.propellantMass / self.propellantCapacity * self.height * scale
        x = 0
        y = self.height * scale - height 
        pygame.draw.rect(self.hull_surface, (0, 192, 255), (x, y, width, height))

    def render_catch_pin(self, scale):
        self.catch_pin.draw(self.hull_surface, scale)

    def render_engines(self, scale):
        for engine in self.engines:
            engine.draw(self.hull_surface, scale)

    def render_rcs_thrusters(self, scale):
        for thruster in self.rcsThrusters:
            thruster.draw(self.hull_surface, scale)

    def add_to_space(self, space):
        space.add(self.body, self.shape)

        self.catch_pin.set_lander_body(self.body)
        self.catch_pin.add_to_space(space)
        space.add(self.catch_pin_joint)

        for engine in self.engines:
            engine.set_lander_body(self.body)

        for thruster in self.rcsThrusters:
            thruster.set_lander_body(self.body)

    def update_steering(self, steeringInput):
        self.hull_surface_rendered = False
        for engine, is_on in zip(self.engines, ["engine1", "engine2", "engine3", "engine4", "engine5"]):
            engine.updateSteering(steeringInput[is_on])

        self.rcsThrusters[0].updateSteering(steeringInput["rcsLeft"])
        self.rcsThrusters[2].updateSteering(steeringInput["rcsLeft"])
        self.rcsThrusters[4].updateSteering(steeringInput["rcsLeft"])

        self.rcsThrusters[1].updateSteering(steeringInput["rcsRight"])
        self.rcsThrusters[3].updateSteering(steeringInput["rcsRight"])
        self.rcsThrusters[5].updateSteering(steeringInput["rcsRight"])

    def reset(self):
        self.hull_surface_rendered = False
        self.body.position = self.initial_position[0], self.initial_position[1] + self.height / 2
        self.body.velocity = 0, 0
        self.body.angle = 0
        self.body.angular_velocity = 0

        self.catch_pin.reset()

    def get_telemetry(self):
        return {
            "position": self.body.position,
            "angle": self.body.angle,
            "catch_pin_position": self.catch_pin.body.position,
            "velocity": self.body.velocity,
            "angular_velocity": self.body.angular_velocity,
            "mass": self.body.mass,
            "dry_mass": self.dryMass,
            "propellant_mass": self.propellantMass,
            "propellant_capacity": self.propellantCapacity,
            "moment": self.body.moment
        }
