import torch
import math

from LanderSteeringModel import LanderSteeringModel


class LanderSteeringModelActor(LanderSteeringModel):
    def __init__(self, device, target_catch_pin_position):
        super(LanderSteeringModelActor, self).__init__(device, target_catch_pin_position)

        self.fc1 = torch.nn.Linear(10, 128)
        self.fc2 = torch.nn.Linear(128, 128)
        # self.fc3 = torch.nn.Linear(64, 20)
        self.fc4 = torch.nn.Linear(128, 7)


    def forward(self, telemetry):
        x = self.telemetry_to_input(telemetry)

        x = torch.nn.functional.leaky_relu(self.fc1(x))
        x = torch.nn.functional.leaky_relu(self.fc2(x))
        # x = torch.nn.functional.leaky_relu(self.fc3(x))
        x = self.fc4(x)

        y = torch.sigmoid(x)
        return y

class LanderSteeringModelCritic(LanderSteeringModel):
    def __init__(self, device, target_catch_pin_position):
        super(LanderSteeringModelCritic, self).__init__(device, target_catch_pin_position)

        self.fc1 = torch.nn.Linear(10, 128)
        self.fc2 = torch.nn.Linear(128, 128)
        # self.fc3 = torch.nn.Linear(64, 20)
        self.fc4 = torch.nn.Linear(128, 1)


    def forward(self, telemetry):
        x = self.telemetry_to_input(telemetry)

        x = torch.nn.functional.leaky_relu(self.fc1(x))
        x = torch.nn.functional.leaky_relu(self.fc2(x))
        # x = torch.nn.functional.leaky_relu(self.fc3(x))
        y = self.fc4(x)

        return y
    
