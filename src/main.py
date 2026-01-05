from manim import *
import numpy as np
import math

class S(Scene):
    k = 0.5
    lambda_1 = 1 + k
    lambda_2 = 1 - k

    A = np.array([[1, k], [k, 1]])
    D = np.array([[lambda_1, 0], [0, lambda_2]])
    P = np.array([[1, -1], [1, 1]])

    def write_tex(self, axis, t, color):
        text = MathTex(t, color=color)
        
        text \
            .next_to(axis, RIGHT) \
            .shift(RIGHT * 5) \
            .scale(2.0)

        return text

    def create_axis(self):
        ax = Axes(
            x_range=[-10, 11, 1],
            y_range=[-10, 11, 1],
            tips=True,
            axis_config={
                "include_numbers": True,
                "color": BLACK,
                "decimal_number_config": {
                    "color": BLACK,
                    "num_decimal_places": 0
                }
            },
            x_length=20,
            y_length=20
        )

        y_label = MathTex("y", color=BLACK)
        y_label.next_to(ax.y_axis.get_top(), RIGHT, buff=0.75)

        labels = ax.get_axis_labels(
            x_label=MathTex("x", color=BLACK)
        )

        return VGroup(ax, y_label, labels)
         

    def create_grid(self, axis, color, n=5):
        dots_map = {
            (x, y): Dot(point=axis.c2p(x, y), radius=0.075, color=color)
            for y in range(-n, n + 1)
            for x in range(-n, n + 1) if y != 0 or x != 0
        }

        dots = VGroup(*dots_map.values())

        def c2p(x, y):
            return dots_map[(x, y)].get_center()

        rect = always_redraw(
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

        return VGroup(rect, dots)

    def transform(self, M, x, y):
            v = np.array([[x], [y]])                
            return (M @ v).flatten()
    
    def shear_gird(self, axis, M, grid):
        return [
            dot.animate.move_to(
                axis.c2p(*self.transform(M, *axis.p2c(dot.get_center())[:2]))
            )
            for dot in grid
        ]
    
    def make_vector_arrow(self, ax, x, y, text, color=BLUE):
        arrow = Arrow(color=color, stroke_width=20, start=ax.get_origin(), end=ax.c2p(x, y), buff=0).set_z_index(1)
        label = MathTex(text,  color=color).next_to(arrow.get_end(), RIGHT + UP/2, buff=0.25).set_z_index(1)

        return VGroup(arrow, label)

    def construct(self):
        axis_group = self.create_axis()
        ax = axis_group[0]

        axis_origin = ax.get_origin()

        self.add(axis_group)

        # write text
        A_text = self \
            .write_tex(ax, r"v \mapsto Av = \begin{pmatrix} 1 & k \\ k & 1 \end{pmatrix} v", GREEN) \
            .to_edge(UP)

        self.add(A_text)

        # draw eigen-lines
        line1 = ax.plot(lambda x: x, color=RED, stroke_opacity=0.75)
        line2 = ax.plot(lambda x: -x, color=RED, stroke_opacity=0.75)
        line_label = ax.get_graph_label(
            line1,
            label=MathTex("|x| = |y|"),
            x_val=6,
            direction=UR,
            buff=0.25,
        )

        line_group = VGroup(line1, line2, line_label)

        self.add(line_group)

        # standard ordered basis arrows

        coords = always_redraw(
              lambda: VGroup(
                *self.make_vector_arrow(ax, 1, 0, r"e_1 = (1, 0)", PURE_BLUE),
                *self.make_vector_arrow(ax, 0, 1, r"e_2 = (0, 1)", PURE_RED)
              )
        )

        self.add(coords)

        A_rect, A_grid = self.create_grid(ax, GREEN)
        D_rect, D_grid = self.create_grid(ax, RED)

        # animate dots/background rectangle
        self.add(A_rect, A_grid, D_rect, D_grid)

        self.play(
            *self.shear_gird(ax, self.A, A_grid),
            run_time=3
        )
        P_inverse_text = self \
            .write_tex(ax, r"v \mapsto P^{-1} v", RED) \
            .next_to(A_text, DOWN) \
            .shift(DOWN * 2)

        def rotate_coord_system(*, reverse=False):
            return (axis_group
                .animate
                .rotate(-PI/4 if reverse else PI/4, about_point=axis_origin)
                .scale(1/math.sqrt(2) if reverse else math.sqrt(2), about_point=axis_origin))
        
        # eigen coordinates
        self.play(
            rotate_coord_system(),
            FadeOut(line_group),
            FadeIn(P_inverse_text),
            run_time=3
        )

        D_text = self \
            .write_tex(ax, r"P^{-1} v \mapsto D\!\left(P^{-1} v\right)", RED) \
            .next_to(P_inverse_text, DOWN) \
            .shift(DOWN * 2)

        self.play(
            *self.shear_gird(ax, self.D, D_grid),
            FadeIn(D_text),
            run_time=3
        )

        P_text = self \
            .write_tex(ax, r"D\!\left(P^{-1} v\right) \mapsto P\,D\!\left(P^{-1} v\right) = A v", RED) \
            .next_to(D_text, DOWN) \
            .shift(DOWN * 2)
        
        self.play(
            rotate_coord_system(reverse=True),
            FadeIn(P_text),
            run_time=2
        )

        self.wait()
