from manim import *
import numpy as np

class S(Scene):
    def construct(self):
        bg_ax = Axes(
            x_range=[-10, 11, 1],
            y_range=[-10, 11, 1],
            tips=False,
            x_length=20,
            y_length=20
        )

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
        self.add(ax, labels, y_label)

        # shearing scale 
        k = ValueTracker(0.0)

        def transform(x, y):
            k_value = k.get_value()

            A = np.array([[1, k_value], [k_value, 1]])
            v = np.array([x, y])
            
            return A @ v
        
        # animate dots
        dots = always_redraw(
            lambda: VGroup(*[
                Dot(point=bg_ax.c2p(*transform(x, y)), color=BLUE, radius=0.075)
                for y in range(-5, 6)
                for x in range(-5, 6) if y != 0 or x !=0
            ])
        )

        self.add(dots)

        # Background rectangle
        corners = [[-5, 5], [5, 5], [5, -5], [-5, -5]]
        
        rect = always_redraw(
            lambda: Polygon(
                *[bg_ax.c2p(*transform(x, y)) for x, y in corners],
                color=BLUE,
                fill_color=BLUE,
                fill_opacity=0.1,
                stroke_width=0
            ).move_to(dots.get_center())
        )

        self.add(rect)

        # draw eigen-lines
        line1 = ax.plot(lambda x: x, color=RED, stroke_opacity=0.5)
        line2 = ax.plot(lambda x: -x, color=RED, stroke_opacity=0.5)
        line_label = ax.get_graph_label(
            line1,
            label=MathTex("|x| = |y|"),
            x_val=6,
            direction=UR,
            buff=0.25,
        )

        line_group = VGroup(line1, line2, line_label)

        self.add(line_group)

        # animate matrix tex
        matrix_tex = always_redraw(
            lambda: MathTex(
                f"A = \\begin{{bmatrix}} 1 & {k.get_value():.2f} \\\\ {k.get_value():.2f} & 1 \\end{{bmatrix}}",
                color=BLACK
            ).to_corner(UR, buff=1)
        )
        self.add(matrix_tex)

        # animate k
        self.play(k.animate.set_value(0.5), run_time=3)
        # self.play(k.animate.set_value(0), run_time=3)

        # self.play(ax.animate.rotate(-PI/4, about_point=bg_ax.get_origin()))
        # self.play(FadeOut(line_group))

        self.play(k.animate.set_value(0), run_time=3)
        # self.play(k.animate.set_value(0.5), run_time=3)

        self.wait()
