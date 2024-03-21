from dataclasses import dataclass
from typing import List, Union

import matplotlib.pyplot as plt
import numpy as np

from .robot import Pose


@dataclass
class Observation:
    distance: float
    direction: float

    def __getitem__(self, i: int) -> float:
        if i == 0:
            return self.distance
        elif i == 1:
            return self.direction
        else:
            raise IndexError


class IdealCamera:
    def __init__(self, env_map,
                 distance_range=(0.5, 6.0),
                 direction_range=(-np.pi / 3, np.pi / 3)):
        self.map = env_map

        self.distance_range = distance_range
        self.direction_range = direction_range

    def data(self, cam_pose: "Pose") -> List[Observation]:
        observed = []
        for lm in self.map.landmarks:
            z = self.observation_function(cam_pose, lm.pos)
            if self.visible(z):
                observed.append(z)

        self.lastdata = observed
        return observed

    def visible(self, obs: Observation) -> bool:
        if obs is None:
            return False
        phi = obs.direction
        if phi < self.direction_range[0] or self.direction_range[1] < phi:
            return False
        return True

    def draw(self, ax: plt.Axes, elems: List[plt.Artist], cam_pose: "Pose") -> None:
        for lm in self.lastdata:
            x, y, theta = cam_pose
            distance, direction = lm[0], lm[1]
            lx = x + distance * np.cos(direction + theta)
            ly = y + distance * np.sin(direction + theta)
            elems += ax.plot([x, lx], [y, ly], color="pink")  # 観測線

    def observation_function(self, cam_pose: "Pose", obj_pos: np.ndarray) -> Union[Observation, None]:
        diff = obj_pos - cam_pose[0:2]
        phi = np.arctan2(diff[1], diff[0]) - cam_pose[2]
        while phi >= np.pi:
            phi -= 2 * np.pi
        while phi < -np.pi:
            phi += 2 * np.pi
        if (phi < self.direction_range[0] or self.direction_range[1] < phi):
            return None

        distance = np.hypot(*diff)
        if (distance < self.distance_range[0] or self.distance_range[1] < distance):
            return None

        return Observation(distance, phi)
