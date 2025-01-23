import pymunk
import pygame
import json

from RectangularObject import RectangularObject
from Renderer import Renderer
from Terrain import Terrain, TerrainElement
from Lander import Lander, LanderCatchPin


def load_settings():
    with open("settings.json") as file:
        settings = json.load(file)
    return settings


def main():
    settings = load_settings()

    pygame.init()
    screen_size = (settings["windowSize"]["width"], settings["windowSize"]["height"])
    screen = pygame.display.set_mode(screen_size)
    clock = pygame.time.Clock()
    
    space = pymunk.Space()
    space.gravity = 0, -9.81
    # space.gravity = 0, -0.981

    terrain = Terrain(settings["terrain"])
    terrain.add_to_space(space)

    initial_position = (50, 50)
    lander = Lander(settings["lander"], initial_position)
    lander.add_to_space(space)

    def handle_collision_lander_terrain(arbiter, space, data):
        print("Collision with terrain")
        return True
    
    def handle_collision_no_collision(arbiter, space, data):
        return False
    
    def handle_collision_catch_pin_arm(arbiter, space, data):
        print("Collision with arm")
        return True

    handler_collision_lander_terrain = space.add_collision_handler(Lander.LANDER_COLISION_TYPE, TerrainElement.TERRAIN_ELEMENT_COLISION_TYPE)
    handler_collision_catch_pin_arm = space.add_collision_handler(LanderCatchPin.CATCH_PIN_COLISION_TYPE, TerrainElement.ARM_COLISION_TYPE)
    handler_collision_lander_catch_pin_arm = space.add_collision_handler(Lander.LANDER_COLISION_TYPE, LanderCatchPin.CATCH_PIN_COLISION_TYPE)
    handler_collision_lander_arm = space.add_collision_handler(Lander.LANDER_COLISION_TYPE, TerrainElement.ARM_COLISION_TYPE)
    handler_collision_lander_terrain.begin = handle_collision_lander_terrain
    handler_collision_lander_arm.begin = handle_collision_no_collision
    handler_collision_lander_catch_pin_arm.begin = handle_collision_no_collision
    handler_collision_catch_pin_arm.begin = handle_collision_catch_pin_arm

    # renderer_scale = 1
    # renderer_scale = 2
    renderer_scale = 10
    renderer = Renderer(screen, (screen_size[0] / (2 * renderer_scale) - 20, screen_size[1] / (2 * renderer_scale) - 20), renderer_scale)
    # renderer = Renderer(screen, (screen_size[0] / (2 * renderer_scale) - 150, screen_size[1] / (2 * renderer_scale) - 50), renderer_scale)


    running = True
    while running:
        steeringInput = {
            "engine1": False,
            "engine2": False,
            "engine3": False,
            "engine4": False,
            "engine5": False,
            "rcsLeft": False,
            "rcsRight": False
        }

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            steeringInput["engine1"] = True
            steeringInput["engine2"] = True
            steeringInput["engine3"] = True
            steeringInput["engine4"] = True
            steeringInput["engine5"] = True
        if keys[pygame.K_1]:
            steeringInput["engine1"] = True
        if keys[pygame.K_2]:
            steeringInput["engine2"] = True
        if keys[pygame.K_3]:
            steeringInput["engine3"] = True
        if keys[pygame.K_4]:
            steeringInput["engine4"] = True
        if keys[pygame.K_5]:
            steeringInput["engine5"] = True
        if keys[pygame.K_RIGHT]:
            steeringInput["rcsLeft"] = True
        if keys[pygame.K_LEFT]:
            steeringInput["rcsRight"] = True


        lander.updateSteering(steeringInput)

        # Update physics
        physics_iterations = 10
        delta_time = 1.0 / settings["fps"] / physics_iterations
        for _ in range(physics_iterations):
            space.step(delta_time)

        # Draw
        screen.fill((0, 0, 0))

        renderer.draw(lander)
        renderer.draw_group(terrain)

        # Print real fps to console
        # print(f"FPS: {clock.get_fps()}")

        pygame.display.flip()
        clock.tick(settings["fps"])


if __name__ == "__main__":
    main()