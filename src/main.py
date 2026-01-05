from manim import *
from manim.scene.scene import Scene

import numpy as np
from numpy.typing import NDArray

import math

class Coordinate_System:
    def __init__(self, axes: Axes, *rest: VGroup):
        self.axes = axes
        self.mobjects = VGroup(self.axes, *rest)
        self.origin = self.axes.get_origin()

class Grid:
    def __init__(self, background: Mobject, dots: VGroup):
        self.background = background
        self.dots = dots
        self.mobjects = VGroup(background, dots)

class Plot:
    def __init__(self, plot: VGroup, label):
        self.plot = plot
        self.label = label
        self.mobjects = VGroup(plot, label)


class Transformation:
    k = 0.5
    lambda_1 = 1 + k
    lambda_2 = 1 - k

    A = np.array([[1, k], [k, 1]])
    A_inverse = np.linalg.inv(A)
    D = np.array([[lambda_1, 0], [0, lambda_2]])
    P = np.array([[1, -1], [1, 1]])

    def __init__(self):
        self.__axes: Axes | None = None

        self.coordinate_system: Coordinate_System | None = None
        self.grid: Grid | None = None
        self.plot: Plot | None = None

    def create_coordinate_system(self, size: int, color=BLACK):
        self.__axes = Axes(
            x_range=[-size, size + 1, 1],
            y_range=[-size, size + 1, 1],
            tips=True,
            axis_config={
                "include_numbers": True,
                "color": color,
                "decimal_number_config": {
                    "color": color,
                    "num_decimal_places": 0
                }
            },
            x_length=size * 2,
            y_length=size * 2
        )

        y_label = MathTex("y", color=color)
        y_label.next_to(self.__axes.y_axis.get_top(), RIGHT, buff=0.75)

        x_label = self.__axes.get_axis_labels(
            x_label=MathTex("x", color=color)
        )

        self.coordinate_system = Coordinate_System(
            self.__axes,
            VGroup(
                x_label,
                y_label
            )
        )

    def create_plot(self):
        line1 = self.__axes.plot(lambda x: x, color=RED, stroke_opacity=0.75)
        line2 = self.__axes.plot(lambda x: -x, color=RED, stroke_opacity=0.75)
        label = self.__axes.get_graph_label(
            line1,
            label=MathTex("|x| = |y|", color=RED),
            x_val=6,
            direction=UR,
            buff=0.25,
        )

        self.plot = Plot(VGroup(line1, line2), label)
    
    def create_grid(self, color: ManimColor, n=5):
        dots_map = {
            (x, y): Dot(point=self.__axes.c2p(x, y), radius=0.075, color=color)
            for y in range(-n, n + 1)
            for x in range(-n, n + 1) if y != 0 or x != 0
        }

        dots = VGroup(*dots_map.values())

        def c2p(x, y):
            return dots_map[(x, y)].get_center()

        background = always_redraw(
            lambda: Polygon(
            *[
                c2p(n, n),
                c2p(-n, n),
                c2p(-n, -n),
                c2p(n, -n)
            ],
                color=color,
                fill_color=color,
                fill_opacity=0.1,
                stroke_width=0
            ).move_to(dots.get_center())
        )

        self.grid = Grid(background, dots)
    
    def transform(self, M: NDArray, x: float, y: float):
            v = np.array([[x], [y]])

            return (M @ v).flatten()
    
    def transform_grid(self, M: NDArray):
        return [
            dot.animate.move_to(
                self.__axes.c2p(*self.transform(M, *self.__axes.p2c(dot.get_center())[:2]))
            )
            for dot in self.grid.dots
        ]

class S(Scene):
    def rotate_coordinate_system(self, coordinate_system: Coordinate_System, angle: float):
        return coordinate_system.axes \
            .animate \
            .rotate(angle, about_point=coordinate_system.origin) \
            .scale(1*(math.cos(angle)) ** (1 if angle < 0 else -1), about_point=coordinate_system.origin)

    def construct(self):
        transformation = Transformation()

        transformation.create_coordinate_system(10)
        transformation.create_grid(PURPLE, 5)
        transformation.create_plot()

        self.add(
            transformation.grid.mobjects,
            transformation.coordinate_system.mobjects,
            transformation.plot.mobjects
        )

        self.play(*transformation.transform_grid(Transformation.A), run_time=3)
        self.play(*transformation.transform_grid(Transformation.A_inverse), run_time=3)

        self.play(
            self.rotate_coordinate_system(transformation.coordinate_system, PI/4),
            FadeOut(transformation.plot.mobjects),
            run_time=3
        )

        self.play(*transformation.transform_grid(Transformation.D), run_time=3)

        self.play(
            self.rotate_coordinate_system(transformation.coordinate_system, -PI/4),
            run_time=3
        )
        
        self.wait()
