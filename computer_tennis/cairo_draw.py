import numpy as np

try:
    import cairo
except ImportError:
    raise Exception(
        "pycairo library not found, but required for the 'cairo' backend, please install pycairo before using this backend.  Note that pycairo does not provide binary wheels so it will require system packages to install.  See https://pycairo.readthedocs.io/en/latest/getting_started.html for more information"
    )

from computer_tennis.types import Color


class Surface:
    """
    https://cairographics.org/tutorial/
    https://www.cairographics.org/documentation/pycairo/2/reference/context.html
    """

    def __init__(
        self, pixel_width, pixel_height, view_width, view_height, origin_at_center=True
    ):
        self.data = np.ones((pixel_height, pixel_width, 4), dtype=np.uint8) * 255
        cairo_surface = cairo.ImageSurface.create_for_data(
            self.data, cairo.Format.RGB24, pixel_width, pixel_height
        )
        self.c = cairo.Context(cairo_surface)
        if origin_at_center:
            self.c.translate(pixel_width // 2, pixel_height // 2)
            self.c.scale(pixel_width / view_width, -pixel_height / view_height)
        else:
            self.c.scale(pixel_width / view_width, pixel_height / view_height)
        # don't antialias to match opengl backend
        self.c.set_antialias(cairo.ANTIALIAS_NONE)
        # make line widths somewhere around 1 pixel
        px, _ = self.c.device_to_user_distance(1, 1)
        self.c.set_line_width(abs(px))

    def reset(self, color=Color(1, 1, 1)):
        self.c.set_source_rgb(color.r, color.g, color.b)
        self.c.paint()

    def get_image(self):
        return self.data[:, :, 2::-1].copy()

    def draw_polygon(self, vertices, color):
        for p in vertices:
            self.c.line_to(p.x, p.y)
        self.c.close_path()
        self.c.set_source_rgba(color.r, color.g, color.b, 1.0)
        self.c.fill()
