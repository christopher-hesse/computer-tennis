from computer_tennis import opengl_draw


def build_surface(surface_type, **kwargs):
    if surface_type == "opengl":
        return opengl_draw.Surface(**kwargs)
    elif surface_type == "cairo":
        # late import in case pycairo is not installed
        from computer_tennis import cairo_draw

        return cairo_draw.Surface(**kwargs)
    else:
        raise Exception("invalid surface type")
