import math
from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Tuple, Union

import numpy as np
from matplotlib import patches
from matplotlib import pyplot as plt
from matplotlib.artist import Artist

if TYPE_CHECKING:
    from .agent import Agent
    from .camera import IdealCamera

from .interfaces import DrawableObject


@dataclass
class Pose:
    x: float
    y: float
    theta: float

    def __add__(self, p: Union["Pose", Tuple[float, float, float], np.ndarray]):
        if isinstance(p, Pose):
            return Pose(self.x + p.x, self.y + p.y, self.theta + p.theta)
        else:
            return Pose(self.x + p[0], self.y + p[1], self.theta + p[2])

    def __getitem__(self, i: Union[int, slice]):
        if isinstance(i, slice):
            return [self.x, self.y, self.theta][i]
        elif i == 0:
            return self.x
        elif i == 1:
            return self.y
        elif i == 2:
            return self.theta
        else:
            raise IndexError

    def __print__(self):
        return f"x: {self.x}, y: {self.y}, theta: {self.theta}"


class IdealRobot(DrawableObject):
    def __init__(self, pose: "Pose", agent: "Agent" = None, sensor: "IdealCamera" = None, color: str = "red", r: float = 0.2):
        self.pose = pose
        self.color = color
        self.r = r
        self.agent = agent
        self.sensor = sensor
        self.tragectory = [pose]

    def draw(self, ax: plt.Axes, elems: List[Artist]) -> None:
        x, y, theta = self.pose
        theta = math.radians(theta)
        _x = x + self.r * math.cos(theta)
        _y = y + self.r * math.sin(theta)
        elems.extend(ax.plot([x, _x], [y, _y], color=self.color))
        c = patches.Circle(xy=(x, y), radius=self.r,
                           fill=False, color=self.color)
        elems.append(ax.add_patch(c))
        # 軌跡の描画
        elems.extend(ax.plot(
            [e[0] for e in self.tragectory], [e[1] for e in self.tragectory], linewidth=0.5, color="black"))

        if self.sensor and len(self.tragectory) > 1:
            self.sensor.draw(ax, elems, self.tragectory[-2])

        if self.agent:
            self.agent.draw(ax, elems)

    def one_step(self, time_interval: float) -> None:
        if self.agent is not None:
            obs = self.sensor.data(self.pose) if self.sensor else None
            nu, omega = self.agent.decision(obs)
            self.pose = self.state_transition(
                nu, omega, time_interval, self.pose)

        self.tragectory.append(self.pose)

    @classmethod
    def state_transition(cls, nu: float, w: float, t: float, pose: "Pose") -> "Pose":
        t0 = pose.theta
        phase = t0 + w * t
        if math.fabs(w) < 1e-10:
            return Pose(pose.x + nu * math.cos(t0) * t, pose.y + nu * math.sin(t0) * t, t0)
        else:
            return Pose(
                pose.x - nu / w * math.sin(t0) + nu / w * math.sin(phase),
                pose.y + nu / w * math.cos(t0) - nu / w * math.cos(phase),
                phase
            )
