from dataclasses import dataclass
from typing import List

from matplotlib import pyplot as plt


@dataclass
class Pose:
    x: float
    y: float
    theta: float


class DrawableObject:
    def draw(self, ax: plt.Axes, elems: List[plt.Artist]) -> None:
        raise NotImplementedError

    def one_step(self, time_interval: float):
        raise NotImplementedError
