import ctypes

import pyglet
from pyglet import gl


class ImageViewer:
    def __init__(self, width=1024, height=1024):
        self.width = width
        self.height = height

        self._window = pyglet.window.Window(width=width, height=height)
        self._texture_id = None
        self._texture_width = None
        self._texture_height = None

    def draw(self, img):
        if self._window.has_exit:
            return False

        self._window.switch_to()
        self._window.dispatch_events()

        if self._texture_id is None:
            gl.glEnable(gl.GL_TEXTURE_2D)
            self._texture_id = gl.GLuint(0)
            gl.glGenTextures(1, ctypes.byref(self._texture_id))
            gl.glBindTexture(gl.GL_TEXTURE_2D, self._texture_id)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP)
            gl.glTexParameteri(
                gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST
            )
            gl.glTexParameteri(
                gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST
            )
            self._texture_width = img.shape[1]
            self._texture_height = img.shape[0]
            gl.glTexImage2D(
                gl.GL_TEXTURE_2D,
                0,
                gl.GL_RGBA8,
                self._texture_width,
                self._texture_height,
                0,
                gl.GL_RGB,
                gl.GL_UNSIGNED_BYTE,
                None,
            )

        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self._texture_id)
        assert (
            len(img.shape) == 3
            and img.shape[1] == self._texture_width
            and img.shape[0] == self._texture_height
        ), "invalid image shape"
        image_bytes = img.tobytes()  # keep bytes alive for duration of subimage2d call
        video_buffer = ctypes.cast(image_bytes, ctypes.POINTER(ctypes.c_short))
        gl.glTexSubImage2D(
            gl.GL_TEXTURE_2D,
            0,
            0,
            0,
            self._texture_width,
            self._texture_height,
            gl.GL_RGB,
            gl.GL_UNSIGNED_BYTE,
            video_buffer,
        )

        x = 0
        y = 0
        w = self._window.width
        h = self._window.height

        pyglet.graphics.draw(
            4,
            pyglet.gl.GL_QUADS,
            ("v2f", [x, y, x + w, y, x + w, y + h, x, y + h]),
            ("t2f", [0, 1, 1, 1, 1, 0, 0, 0]),
        )

        self._window.flip()
        return True
