import pymunk
import pygame
import json
import torch

from Renderer import Renderer
from Simulation import Simulation

class LanderSteeringModel(torch.nn.Module):
    def __init__(self, device):
        super(LanderSteeringModel, self).__init__()
        self.device = device

        self.fc1 = torch.nn.Linear(13, 64)
        self.fc2 = torch.nn.Linear(64, 128)
        self.fc3 = torch.nn.Linear(128, 64)
        self.fc4 = torch.nn.Linear(64, 7)


    def forward(self, telemetry):
        x = [
            telemetry['position'][0],
            telemetry['position'][1],
            telemetry['angle'],
            telemetry['catch_pin_position'][0],
            telemetry['catch_pin_position'][1],
            telemetry['velocity'][0],
            telemetry['velocity'][1],
            telemetry['angular_velocity'],
            telemetry['mass'],
            telemetry['dry_mass'],
            telemetry['propellant_mass'],
            telemetry['propellant_capacity'],
            telemetry['moment']
        ]
        x = torch.tensor(x, dtype=torch.float32).to(self.device)

        x = torch.nn.functional.relu(self.fc1(x))
        x = torch.nn.functional.relu(self.fc2(x))
        x = torch.nn.functional.relu(self.fc3(x))
        x = self.fc4(x)

        y = torch.sigmoid(x)
        y = y.cpu().detach()

        steering_input = {
            "engine1": y[0].item(),
            "engine2": y[1].item(),
            "engine3": y[2].item(),
            "engine4": y[3].item(),
            "engine5": y[4].item(),
            "rcsLeft": y[5].item(),
            "rcsRight": y[6].item()
        }
        return steering_input

def to_binary_steering(steeering_input):
    binary_steering = {}
    for key, value in steeering_input.items():
        binary_steering[key] = value > 0.5
    return binary_steering

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
    
    lander_initial_position = settings["landerInitialPosition"]["x"], settings["landerInitialPosition"]["y"]
    simulation_iterations_per_step = settings["simulationIterationsPerStep"]
    simulation = Simulation(settings, lander_initial_position, simulation_iterations_per_step)

    # renderer_scale = 1
    # renderer_scale = 2
    renderer_scale = 5
    # renderer_scale = 10
    renderer = Renderer(screen, (screen_size[0] / (2 * renderer_scale) - 20, screen_size[1] / (2 * renderer_scale) - 20), renderer_scale)
    # renderer = Renderer(screen, (screen_size[0] / (2 * renderer_scale) - 150, screen_size[1] / (2 * renderer_scale) - 50), renderer_scale)

    # Load model
    steering_model = LanderSteeringModel("cpu")
    steering_model.load_state_dict(torch.load("model.pth"))
    steering_model.eval()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False



        result, telemetry = simulation.step(1 / settings["fps"])
        if result is not None:
            print(result)
            print(telemetry)
            simulation.reset()
            # running = False

        # steering_input = read_keyboard_steering_input()
        steering_input = to_binary_steering(steering_model(telemetry))
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