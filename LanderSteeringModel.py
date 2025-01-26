import torch
import math


class LanderSteeringModel(torch.nn.Module):
    def __init__(self, device, target_catch_pin_position):
        super(LanderSteeringModel, self).__init__()
        self.device = device
        self.target_catch_pin_position = target_catch_pin_position

    def telemetry_to_input(self, telemetry):
        distance_to_target_x = telemetry['catch_pin_position'][0] - self.target_catch_pin_position[0]
        distance_to_target_y = telemetry['catch_pin_position'][1] - self.target_catch_pin_position[1]

        input = [
            distance_to_target_x / 10,
            distance_to_target_y / 10,
            math.sqrt(abs(distance_to_target_x)) * math.copysign(1, distance_to_target_x),
            math.sqrt(abs(distance_to_target_y)) * math.copysign(1, distance_to_target_y),
            telemetry['angle'],
            telemetry['velocity'][0] / 10,
            telemetry['velocity'][1] / 10,
            math.sqrt(abs(telemetry['velocity'][0])) * math.copysign(1, telemetry['velocity'][0]),
            math.sqrt(abs(telemetry['velocity'][1])) * math.copysign(1, telemetry['velocity'][1]),
            telemetry['angular_velocity'],
            # telemetry['mass'],
            # telemetry['dry_mass'],
            # telemetry['propellant_mass'] / telemetry['propellant_capacity']
            # telemetry['moment']
        ]
        return torch.tensor(input, dtype=torch.float32).to(self.device)
    
    def output_to_steering_input(self, output):
        y = torch.sigmoid(output)
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
