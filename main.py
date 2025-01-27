import pymunk
import pygame
import json
import torch
import math

from Renderer import Renderer
from Simulation import Simulation
from LanderSteeringModel import LanderSteeringModel
from SteeringModelGenetic import LanderSteeringModelGenetic
from SteeringModelActorCritic import LanderSteeringModelActor


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

settings = load_settings()
tower_arm_settings = settings["terrain"]["tower"]["towerArm"]
target_catch_pin_position_x = (tower_arm_settings["xMax"] + tower_arm_settings["xMin"]) / 2
target_catch_pin_position_y = tower_arm_settings["yMax"] + settings["lander"]["catchPin"]["radius"]
target_catch_pin_position = (target_catch_pin_position_x, target_catch_pin_position_y)
print(target_catch_pin_position)
target_angle = 0
target_velocity = (0, 0)
target_angular_velocity = 0

def loss_function_components(telemetry):
    catch_pin_position = telemetry['catch_pin_position']
    angle = telemetry['angle']
    velocity = telemetry['velocity']
    angular_velocity = telemetry['angular_velocity']

    position_loss = math.sqrt((catch_pin_position[0] - target_catch_pin_position[0])**2 + (catch_pin_position[1] - target_catch_pin_position[1])**2)
    angle_loss = abs(angle - target_angle)
    velocity_loss = math.sqrt((velocity[0] - target_velocity[0])**2 + (velocity[1] - target_velocity[1])**2)
    angular_velocity_loss = abs(angular_velocity - target_angular_velocity)

    position_loss = min(math.exp(min(position_loss, 25) / 10) - 1 + position_loss / 2, 100) + position_loss / 10
    angle_loss = min(angle_loss * 100 + math.exp(angle_loss) - 1, 100) + angle_loss * 10
    velocity_loss = min(math.exp(min(velocity_loss, 5) / 2.5) -1 + velocity_loss, 100) + velocity_loss / 10
    angular_velocity_loss = min(angular_velocity_loss * 100 + math.exp(angular_velocity_loss) - 1, 100) + angular_velocity_loss * 10
    loss = position_loss + angle_loss + velocity_loss + angular_velocity_loss
    return torch.tensor([loss, position_loss, angle_loss, velocity_loss, angular_velocity_loss])

def loss_function(telemetry):
    return loss_function_components(telemetry)[0]

def main():
    settings = load_settings()

    pygame.init()
    screen_size = (settings["windowSize"]["width"], settings["windowSize"]["height"])
    screen = pygame.display.set_mode(screen_size)
    clock = pygame.time.Clock()
    
    lander_initial_position = settings["landerInitialPosition"]["x"], settings["landerInitialPosition"]["y"]
    simulation_iterations_per_step = settings["simulationIterationsPerStep"]
    simulation = Simulation(settings, lander_initial_position, simulation_iterations_per_step, lander_initial_angle=-math.pi / 6)

    # renderer_scale = 1
    renderer_scale = 2
    # renderer_scale = 4
    # renderer_scale = 10
    renderer = Renderer(screen, (screen_size[0] / (2 * renderer_scale) - 200, screen_size[1] / (2 * renderer_scale) - 20), renderer_scale)
    # renderer = Renderer(screen, (screen_size[0] / (2 * renderer_scale) - 150, screen_size[1] / (2 * renderer_scale) - 50), renderer_scale)

    # Load model
    steering_model = LanderSteeringModelActor("cpu", target_catch_pin_position)
    # steering_model.load_state_dict(torch.load("model_100.pth"))
    steering_model.load_state_dict(torch.load("model.pth"))
    steering_model.eval()

    running = True
    frame = 0
    while running:
        frame += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        result, telemetry = simulation.step(1 / settings["fps"])
        if frame % settings["fps"] == 0:
            loss, position_loss, angle_loss, velocity_loss, angular_velocity_loss = loss_function_components(telemetry)
            loss = loss_function(telemetry)
            print(f"{loss:.2f}\t{position_loss:.2f}\t{angle_loss:.2f}\t{velocity_loss:.2f}\t{angular_velocity_loss:.2f}")

        if result is not None:
            print(result)
            print(telemetry)
            print(loss_function(telemetry))
            simulation.reset()
            # running = False

        # steering_input = read_keyboard_steering_input()
        steering_input = steering_model(telemetry)
        steering_input = LanderSteeringModel.output_to_steering_input(steering_input)
        # print(steering_input)
        steering_input = LanderSteeringModel.to_binary_steering(steering_input)
        simulation.set_steering_input(steering_input)

        # Draw
        screen.fill((0, 0, 0))
        simulation.draw(renderer)

        # Print real fps to console
        # print(f"FPS: {clock.get_fps()}")

        pygame.display.flip()
        clock.tick(settings["fps"])


if __name__ == "__main__":
    main()