import pymunk

from RectangularObject import RectangularObject
from Renderer import DrawableGroup


class TerrainElement(RectangularObject):
    TERRAIN_ELEMENT_COLISION_TYPE = 1
    ARM_COLISION_TYPE = 2

    def __init__(self, settings, color, body_type, colision_type=TERRAIN_ELEMENT_COLISION_TYPE):
        width = settings["xMax"] - settings["xMin"]
        height = settings["yMax"] - settings["yMin"]
        position = (settings["xMin"] + settings["xMax"]) / 2, (settings["yMin"] + settings["yMax"]) / 2
        super().__init__(width, height, position, anchor_point=(0.5, 0.5), color=color, body_type=body_type)

        if self.shape is None:
            return
        
        self.shape.collision_type = colision_type


class Water(TerrainElement):
    def __init__(self, settings):
        color = (32, 64, 255)
        super().__init__(settings, color=color, body_type=pymunk.Body.STATIC)


class Ground(TerrainElement):
    def __init__(self, settings):
        color = (32, 32, 32)
        super().__init__(settings, color=color, body_type=pymunk.Body.STATIC)


class Grass(TerrainElement):
    def __init__(self, settings):
        color = (64, 192, 64)
        super().__init__(settings, color=color, body_type=pymunk.Body.STATIC)


class TowerBase(TerrainElement):
    def __init__(self, settings):
        color = (96, 96, 96)
        super().__init__(settings, color=color, body_type=pymunk.Body.STATIC)


class Tower(DrawableGroup):
    def __init__(self, settings):
        super().__init__()

        self.tower_body = TerrainElement(settings, color=(128, 128, 128), body_type=pymunk.Body.STATIC)
        self.arm = TerrainElement(settings["towerArm"], color=(64, 64, 64), body_type=pymunk.Body.STATIC, colision_type=TerrainElement.ARM_COLISION_TYPE)

    def render(self, scale):
        self.rendered = self.rendered and self.tower_body.rendered
        self.rendered = self.rendered and self.arm.rendered
        if self.rendered:
            return

        self.tower_body.render(scale)
        self.arm.render(scale)

        self.rendered = True

    def get_drawables(self):
        return [self.tower_body, self.arm]

    def add_to_space(self, space):
        self.tower_body.add_to_space(space)
        self.arm.add_to_space(space)


class Terrain(DrawableGroup):
    def __init__(self, settings):
        # Drawables
        self.water = Water(settings["water"])
        self.ground = Ground(settings["ground"])
        self.grass = Grass(settings["grass"])
        self.tower_base = TowerBase(settings["towerBase"])

        # DrawableGroups
        self.tower = Tower(settings["tower"])

    def render(self, scale):
        self.rendered = self.rendered and self.water.rendered
        self.rendered = self.rendered and self.ground.rendered
        self.rendered = self.rendered and self.grass.rendered
        self.rendered = self.rendered and self.tower_base.rendered
        self.rendered = self.rendered and self.tower.rendered
        if self.rendered:
            return

        self.water.render(scale)
        self.ground.render(scale)
        self.grass.render(scale)
        self.tower_base.render(scale)
        self.tower.render(scale)

        self.rendered = True

    def get_drawables(self):
        return [self.water, self.ground, self.grass, self.tower_base] + self.tower.get_drawables()

    def add_to_space(self, space):
        self.water.add_to_space(space)
        self.ground.add_to_space(space)
        self.grass.add_to_space(space)
        self.tower_base.add_to_space(space)
        self.tower.add_to_space(space)