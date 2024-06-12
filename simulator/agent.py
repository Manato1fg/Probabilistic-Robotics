from typing import List, Tuple

import matplotlib.pyplot as plt

from .camera import Observation


class Agent:
    def __init__(self, nu, w):
        self.nu = nu
        self.w = w

    def decision(
        self,
        observation: List["Observation"] = None
    ) -> Tuple[float, float]:
        # TODO: Implement here
        return self.nu, self.w

    def draw(self, ax: plt.Axes, elems: List[plt.Artist]) -> None:
        pass
