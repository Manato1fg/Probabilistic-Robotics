from typing import List

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.artist import Artist

from .interfaces import DrawableObject


class LandMark(DrawableObject):
    def __init__(self, x: float, y: float, id: int):
        self.pos = np.array([x, y]).T
        self.id = id

    def draw(self, ax: plt.Axes, elems: List[Artist]) -> None:
        c = ax.scatter(self.pos[0], self.pos[1], s=100,
                       marker="*", label=f"l_{str(id)}", color="orange")
        elems.append(c)

    def one_step(self, time_interval: float) -> None:
        pass
