import torch
import math

from LanderSteeringModel import LanderSteeringModel


class LanderSteeringModelGenetic(LanderSteeringModel):
    def __init__(self, device, target_catch_pin_position):
        super(LanderSteeringModelGenetic, self).__init__(device, target_catch_pin_position)

        self.fc1 = torch.nn.Linear(10, 64)
        self.fc2 = torch.nn.Linear(64, 64)
        self.fc3 = torch.nn.Linear(64, 64)
        self.fc4 = torch.nn.Linear(64, 20)
        self.fc5 = torch.nn.Linear(20, 7)


    def forward(self, telemetry):
        x = self.telemetry_to_input(telemetry)

        x = torch.nn.functional.leaky_relu(self.fc1(x))
        x = torch.nn.functional.leaky_relu(self.fc2(x))
        x = torch.nn.functional.leaky_relu(self.fc3(x))
        x = torch.nn.functional.leaky_relu(self.fc4(x))
        x = self.fc5(x)

        y = torch.sigmoid(x)
        y = y.cpu().detach()

        return LanderSteeringModel.output_to_steering_input(y)
    
