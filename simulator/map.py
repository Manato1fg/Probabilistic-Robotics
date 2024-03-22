from typing import List

import matplotlib.pyplot as plt
from matplotlib.artist import Artist

from .interfaces import DrawableObject
from .landmark import LandMark


class Map(DrawableObject):
    def __init__(self):
        self.landmarks: List[LandMark] = []

    def append_landmark(self, landmark: LandMark) -> None:
        self.landmarks.append(landmark)

    def draw(self, ax: plt.Axes, elems: List[Artist]) -> None:
        for lm in self.landmarks:
            lm.draw(ax, elems)

    def one_step(self, time_interval: float) -> None:
        pass
