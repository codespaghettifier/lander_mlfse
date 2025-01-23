import pymunk
import pygame
import json

from Renderer import Renderer
from Simulation import Simulation


def load_settings():
    with open("settings.json") as file:
        settings = json.load(file)
    return settings


def read_keyboard_steering_input():
    steering_input = {
        "engine1": False,
        "engine2": False,
        "engine3": False,
        "engine4": False,
        "engine5": False,
        "rcsLeft": False,
        "rcsRight": False
    }

    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE]:
        steering_input["engine1"] = True
        steering_input["engine2"] = True
        steering_input["engine3"] = True
        steering_input["engine4"] = True
        steering_input["engine5"] = True
    if keys[pygame.K_1]:
        steering_input["engine1"] = True
    if keys[pygame.K_2]:
        steering_input["engine2"] = True
    if keys[pygame.K_3]:
        steering_input["engine3"] = True
    if keys[pygame.K_4]:
        steering_input["engine4"] = True
    if keys[pygame.K_5]:
        steering_input["engine5"] = True
    if keys[pygame.K_RIGHT]:
        steering_input["rcsLeft"] = True
    if keys[pygame.K_LEFT]:
        steering_input["rcsRight"] = True

    return steering_input


def main():
    settings = load_settings()

    pygame.init()
    screen_size = (settings["windowSize"]["width"], settings["windowSize"]["height"])
    screen = pygame.display.set_mode(screen_size)
    clock = pygame.time.Clock()
    
    lander_initial_position = (50, 50)
    simulation = Simulation(settings, lander_initial_position)

    # renderer_scale = 1
    # renderer_scale = 2
    renderer_scale = 10
    renderer = Renderer(screen, (screen_size[0] / (2 * renderer_scale) - 20, screen_size[1] / (2 * renderer_scale) - 20), renderer_scale)
    # renderer = Renderer(screen, (screen_size[0] / (2 * renderer_scale) - 150, screen_size[1] / (2 * renderer_scale) - 50), renderer_scale)


    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        steering_input = read_keyboard_steering_input()
        simulation.set_steering_input(steering_input)

        result, telemetry = simulation.step(1 / settings["fps"])
        if result is not None:
            print(result)
            print(telemetry)
            # running = False

        # Draw
        screen.fill((0, 0, 0))
        simulation.draw(renderer)

        # Print real fps to console
        # print(f"FPS: {clock.get_fps()}")

        pygame.display.flip()
        clock.tick(settings["fps"])


if __name__ == "__main__":
    main()