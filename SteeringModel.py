import torch
import json
import math
import threading
import multiprocessing
import queue


class LanderSteeringModel(torch.nn.Module):
    def __init__(self, device):
        super(LanderSteeringModel, self).__init__()
        self.device = device

        self.fc1 = torch.nn.Linear(8, 64)
        # self.fc2 = torch.nn.Linear(64, 64)
        # self.fc3 = torch.nn.Linear(64, 64)
        self.fc4 = torch.nn.Linear(64, 20)
        self.fc5 = torch.nn.Linear(20, 7)


    def forward(self, telemetry):
        # x = [
        #     telemetry['position'][0],
        #     telemetry['position'][1],
        #     telemetry['angle'],
        #     telemetry['catch_pin_position'][0],
        #     telemetry['catch_pin_position'][1],
        #     telemetry['velocity'][0],
        #     telemetry['velocity'][1],
        #     telemetry['angular_velocity'],
        #     telemetry['mass'],
        #     telemetry['dry_mass'],
        #     telemetry['propellant_mass'],
        #     telemetry['propellant_capacity'],
        #     telemetry['moment']
        # ]
        # x = torch.tensor(x, dtype=torch.float32).to(self.device)

        x = [
            math.sqrt(abs(telemetry['position'][0])) * math.copysign(1, telemetry['position'][0]),
            math.sqrt(abs(telemetry['position'][1])) * math.copysign(1, telemetry['position'][1]),
            telemetry['angle'],
            math.sqrt(abs(telemetry['velocity'][0])) * math.copysign(1, telemetry['velocity'][0]),
            math.sqrt(abs(telemetry['velocity'][1])) * math.copysign(1, telemetry['velocity'][1]),
            telemetry['velocity'][0],
            telemetry['velocity'][1],
            telemetry['angular_velocity'],
            # telemetry['mass'],
            # telemetry['dry_mass'],
            # telemetry['propellant_mass'] / telemetry['propellant_capacity']
            # telemetry['moment']
        ]
        x = torch.tensor(x, dtype=torch.float32).to(self.device)

        x = torch.nn.functional.leaky_relu(self.fc1(x))
        # x = torch.nn.functional.leaky_relu(self.fc2(x))
        # x = torch.nn.functional.leaky_relu(self.fc3(x))
        x = torch.nn.functional.leaky_relu(self.fc4(x))
        x = self.fc5(x)

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
    
