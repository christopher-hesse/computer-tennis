import platform

import moderngl
import numpy as np
from computer_tennis.types import Color


def get_scale_matrix(scale_x, scale_y):
    return np.array(
        [[scale_x, 0, 0, 0], [0, scale_y, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
        dtype=np.float32,
    )


def get_translate_matrix(translate_x, translate_y):
    return np.array(
        [[1, 0, 0, translate_x], [0, 1, 0, translate_y], [0, 0, 1, 0], [0, 0, 0, 1]],
        dtype=np.float32,
    )


class Surface:
    CIRCLE_SEGMENTS = 16

    def __init__(
        self, pixel_width, pixel_height, view_width, view_height, origin_at_center=True
    ):
        context_kwargs = {"standalone": True}
        # we have to set the argument in this weird way because there doesn't appear to be
        # a way to tell create_context to use the default backend
        if platform.system() == "Linux":
            context_kwargs["backend"] = "egl"
        self.ctx = moderngl.create_context(**context_kwargs)

        with self.ctx:
            self.fbo = self.ctx.simple_framebuffer((pixel_width, pixel_height), 4)
            self.fbo.use()
            self.prog = self.ctx.program(
                vertex_shader="""
                #version 330
                uniform mat4 proj;
                in vec2 in_vert;
                in vec4 in_color;
                out vec4 color;
                void main() {
                    gl_Position = vec4(in_vert, 0.0, 1.0) * proj;
                    color = in_color;
                }
                """,
                fragment_shader="""
                #version 330
                in vec4 color;
                out vec4 fragColor;
                void main() {
                    fragColor = color;
                }
            """,
            )
            # convert from normalized device coordinates
            proj = np.eye(4, dtype=np.float32)
            if origin_at_center:
                proj = proj.dot(
                    get_scale_matrix(scale_x=2 / view_width, scale_y=-2 / view_height)
                )
                proj = proj.dot(get_translate_matrix(translate_x=0, translate_y=0))
            else:
                proj = proj.dot(
                    get_scale_matrix(scale_x=2 / view_width, scale_y=2 / view_height)
                )
                proj = proj.dot(
                    get_translate_matrix(
                        translate_x=-view_width / 2, translate_y=-view_height / 2
                    )
                )
            self.prog["proj"].write(proj)
            self.ctx.enable(moderngl.BLEND)
            self.ctx.blend_func = self.ctx.SRC_ALPHA, self.ctx.ONE_MINUS_SRC_ALPHA

    def reset(self, color=Color(1, 1, 1)):
        with self.ctx:
            self.ctx.clear(red=color.r, green=color.g, blue=color.b, alpha=1.0)

    def get_image(self):
        with self.ctx:
            data = self.fbo.read(components=3)
            return (
                np.frombuffer(data, dtype=np.uint8)
                .reshape((self.fbo.size[1], self.fbo.size[0], 3))
                .copy()
            )

    def _draw_vertices(self, vertices, color, kind, alpha=1.0):
        with self.ctx:
            data = []
            for v in vertices:
                data.extend([v.x, v.y, color.r, color.g, color.b, alpha])
            vbo = self.ctx.buffer(np.array(data, dtype=np.float32))
            vao = self.ctx.simple_vertex_array(self.prog, vbo, "in_vert", "in_color")
            vao.render(kind)

    def draw_polygon(self, vertices, color):
        # vertex inputs are a series of points, convert to a series of triangles
        triangle_fan = []
        for i in range(1, len(vertices) - 1):
            triangle_fan.extend([vertices[0], vertices[i], vertices[i + 1]])
        self._draw_vertices(vertices=triangle_fan, color=color, kind=moderngl.TRIANGLES)
