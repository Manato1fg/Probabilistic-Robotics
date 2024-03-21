from typing import List

import matplotlib
from matplotlib import animation as ani
from matplotlib import pyplot as plt

from .interfaces import DrawableObject

matplotlib.use('TkAgg')


class World:
    def __init__(self, time_span: int = 60, time_interval: float = 0.1):
        self.objects = []
        self.time_span = time_span
        self.time_interval = time_interval

    def append(self, obj):
        self.objects.append(obj)

    def draw(self):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_aspect('equal')
        ax.set_xlim(-5, 5)
        ax.set_ylim(-5, 5)
        ax.set_xlabel('X', fontdict={'size': 15})
        ax.set_ylabel('Y', fontdict={'size': 15})

        elems = []

        self.ani = ani.FuncAnimation(
            fig,
            self.one_step,
            fargs=(elems, ax),
            frames=int(self.time_span / self.time_interval) + 1,
            interval=int(self.time_interval * 1000),
            repeat=False
        )
        plt.show()

        for obj in self.objects:
            obj.draw(ax, [])

    def one_step(self, i: int, elems: List[DrawableObject], ax: plt.Axes):
        while elems:
            elems.pop().remove()
        time_str = "t = %.2f[s]" % (self.time_interval * i)
        elems.append(ax.text(-4.4, 4.5, time_str, fontsize=10))
        for obj in self.objects:
            obj.draw(ax, elems)
            obj.one_step(self.time_interval)
