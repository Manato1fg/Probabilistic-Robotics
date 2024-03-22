from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm, uniform

import random

if TYPE_CHECKING:
    from .map import Map
    from .robot import Pose


@dataclass
class Observation:
    distance: float
    direction: float

    id: int = -1

    def __getitem__(self, i: int) -> float:
        if i == 0:
            return self.distance
        elif i == 1:
            return self.direction
        elif i == 2:
            return self.id
        else:
            raise IndexError


class IdealCamera:
    def __init__(
        self,
        env_map: "Map",
        distance_range: Tuple[float, float] = (0.5, 6.0),
        direction_range: Tuple[float, float] = (-np.pi / 3, np.pi / 3)
    ):
        self.map = env_map

        self.distance_range = distance_range
        self.direction_range = direction_range

    def data(self, cam_pose: "Pose") -> List[Observation]:
        observed = []
        for lm in self.map.landmarks:
            z = IdealCamera.relative_polar_pos(cam_pose, lm.pos)
            obs = Observation(*z, lm.id)
            if self.visible(obs):
                observed.append(obs)

        self.lastdata = observed
        return observed

    def visible(self, obs: Observation) -> bool:
        if obs is None:
            return False
        phi = obs.direction
        while phi < -np.pi:
            phi += 2 * np.pi
        while phi > np.pi:
            phi -= 2 * np.pi
        if phi < self.direction_range[0] or self.direction_range[1] < phi:
            return False
        return True

    def draw(self, ax: plt.Axes, elems: List[plt.Artist], cam_pose: "Pose") -> None:
        for ld in self.lastdata:
            x, y, theta = cam_pose
            distance, direction = ld[0], ld[1]
            lx = x + distance * np.cos(direction + theta)
            ly = y + distance * np.sin(direction + theta)
            elems += ax.plot([x, lx], [y, ly], color="pink")  # 観測線

    @classmethod
    def relative_polar_pos(cls, cam_pose: "Pose", obj_pos: np.ndarray) -> np.ndarray:
        distance = (obj_pos[0] - cam_pose[0]) ** 2 + \
            (obj_pos[1] - cam_pose[1]) ** 2
        distance = np.sqrt(distance)
        direction = np.arctan2(
            obj_pos[1] - cam_pose[1], obj_pos[0] - cam_pose[0]) - cam_pose[2]
        return np.array([distance, direction]).T


class Camera(IdealCamera):

    def __init__(
        self,
        env_map: "Map",
        distance_range: Tuple[float, float] = (0.5, 6.0),
        direction_range: Tuple[float, float] = (-np.pi / 3, np.pi / 3),
        distance_noise_rate: float = 0.1,
        direction_noise: float = np.pi / 90,
        distance_bias_rate_stddev: float = 0.1,
        direction_bias_stddev: float = np.pi / 90,
        phantom_prob: float = 0.0,
        phantom_range_x: Tuple[float] = (-5.0, 5.0),
        phantom_range_y: Tuple[float] = (-5.0, 5.0),
        oversight_prob: float = 0.0,
        occlusion_prob: float = 0.0
    ):
        super().__init__(env_map, distance_range, direction_range)
        self.distance_noise_rate = distance_noise_rate
        self.direction_noise = direction_noise
        self.distance_bias_std = norm.rvs(
            loc=0.0, scale=distance_bias_rate_stddev)  # 恒常的なバイアス
        self.direction_bias = norm.rvs(scale=direction_bias_stddev)
        self.phantom_prob = phantom_prob
        self.phantom_dist = uniform(
            loc=(phantom_range_x[0], phantom_range_y[0]),
            scale=(phantom_range_x[1] - phantom_range_x[0],
                   phantom_range_y[1] - phantom_range_y[0])
        )
        self.oversight_prob = oversight_prob
        self.occlusion_prob = occlusion_prob

    def occlusion(self, cam_pose: "Pose", relpos: np.ndarray) -> np.ndarray:
        if random.random() < self.occlusion_prob:
            ell = relpos[0] + uniform.rvs() * \
                (self.distance_range[1] - relpos[0])
            phi = relpos[1]  # 方向はそのまま
            return np.array([ell, phi]).T
        else:
            return relpos

    def oversight(self) -> bool:
        return random.random() < self.oversight_prob

    def phantom(self, cam_pose: "Pose", relpos: np.ndarray) -> np.ndarray:
        if random.random() < self.phantom_prob:
            pos = np.array(self.phantom_dist.rvs()).T
            return IdealCamera.relative_polar_pos(cam_pose, pos)
        else:
            return relpos

    def bias(self, relpos: np.ndarray) -> np.ndarray:
        ell = relpos[0] + relpos[0] * self.distance_bias_std
        phi = relpos[1] + self.direction_bias
        return np.array([ell, phi]).T

    def noise(self, relpos: np.ndarray) -> np.ndarray:
        ell = norm.rvs(
            loc=relpos[0],
            scale=relpos[0] * self.distance_noise_rate
        )
        phi = norm.rvs(
            loc=relpos[1],
            scale=self.direction_noise
        )
        return np.array([ell, phi]).T

    def data(self, cam_pose: "Pose") -> List[Observation]:
        observed = []
        for lm in self.map.landmarks:
            z = IdealCamera.relative_polar_pos(cam_pose, lm.pos)
            z = self.phantom(cam_pose, z)
            z = self.occlusion(cam_pose, z)
            obs = Observation(*z, lm.id)
            if self.oversight():
                obs = None  # 見落としが発生
            if self.visible(obs):
                z = self.noise(z)
                z = self.bias(z)
                observed.append(Observation(*z, lm.id))

        self.lastdata = observed
        return observed
