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

from scipy.stats import expon, norm, uniform

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


class Robot(IdealRobot):

    def __init__(
        self,
        pose: "Pose",
        agent: "Agent" = None,
        sensor: "IdealCamera" = None,
        color: str = "red",
        r: float = 0.2,
        noise_per_meter: float = 5,
        noise_std: float = math.pi / 60,
        bias_rate_stds: Tuple[float, float] = (0.1, 0.1),
        expected_stuck_time: float = 1e100,  # スタックする時間の期待値
        expected_escape_time: float = 1e-100,  # スタックから抜け出す時間の期待値
        expected_kidnap_time: float = 1e100,  # 誘拐される時間の期待値
        kidnap_range_x: Tuple[float, float] = (-5.0, 5.0),
        kidnap_range_y: Tuple[float, float] = (-5.0, 5.0)
    ):
        super().__init__(pose, agent, sensor, color, r)
        self.noise_pdf = expon(
            scale=1.0 / (1e-100 + noise_per_meter))  # 小石は指数分布に従う
        self.distance_until_noise = self.noise_pdf.rvs()  # ドローする
        self.theta_noise = norm(scale=noise_std)  # 角度は正規分布に従う
        self.bias_rate_nu = norm.rvs(
            loc=1.0, scale=bias_rate_stds[0])  # 平均loc, 標準偏差scaleの正規分布
        self.bias_rate_omega = norm.rvs(
            loc=1.0, scale=bias_rate_stds[1])
        self.stuck_pdf = expon(scale=expected_stuck_time)
        self.time_until_stuck = self.stuck_pdf.rvs()
        self.escape_pdf = expon(scale=expected_escape_time)
        self.time_until_escape = self.escape_pdf.rvs()
        self.is_stucking = False  # スタックしているかどうか
        self.kidnap_pdf = expon(scale=expected_kidnap_time)
        self.time_until_kidnap = self.kidnap_pdf.rvs()
        # 誘拐される範囲を一葉分布からサンプリング
        self.kidnap_dist = uniform(loc=(kidnap_range_x[0], kidnap_range_y[0]), scale=(
            kidnap_range_x[1] - kidnap_range_x[0], kidnap_range_y[1] - kidnap_range_y[0]))

    def kidnap(self, pose: "Pose", time_interval: float) -> "Pose":
        self.time_until_kidnap -= time_interval
        if self.time_until_kidnap <= 0.0:
            self.time_until_kidnap += self.kidnap_pdf.rvs()
            return Pose(*self.kidnap_dist.rvs(), pose.theta)
        else:
            return pose

    def stuck(self, nu: float, omega: float, time_interval: float) -> Tuple[float, float]:
        if self.is_stucking:
            self.time_until_escape -= time_interval
            if self.time_until_escape <= 0.0:
                self.time_until_escape += self.escape_pdf.rvs()
                self.is_stucking = False
        else:
            self.time_until_stuck -= time_interval
            if self.time_until_stuck <= 0.0:
                self.time_until_stuck += self.stuck_pdf.rvs()
                self.is_stucking = True

        return nu * (not self.is_stucking), omega * (not self.is_stucking)

    def bias(self, nu: float, omega: float) -> Tuple[float, float]:
        return nu * self.bias_rate_nu, omega * self.bias_rate_omega

    def noise(self, pose: "Pose", nu: float, omega: float, time_interval: float) -> "Pose":
        self.distance_until_noise -= abs(nu) * time_interval + \
            self.r * omega * time_interval  # 車輪の分も考慮
        if self.distance_until_noise <= 0.0:
            self.distance_until_noise += self.noise_pdf.rvs()
            pose.theta += self.theta_noise.rvs()
        return pose

    def one_step(self, time_interval: float) -> None:
        if self.agent is not None:
            obs = self.sensor.data(self.pose) if self.sensor else None
            nu, omega = self.agent.decision(obs)
            nu, omega = self.bias(nu, omega)
            nu, omega = self.stuck(nu, omega, time_interval)
            self.pose = self.state_transition(
                nu, omega, time_interval, self.pose)
            self.pose = self.noise(self.pose, nu, omega, time_interval)
            self.pose = self.kidnap(self.pose, time_interval)

        self.tragectory.append(self.pose)
