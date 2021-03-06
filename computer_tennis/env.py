import collections
import random
import math

import gym3
import numpy as np

from computer_tennis.types import Color, Vec2
from computer_tennis.util import build_surface


Rect = collections.namedtuple("Rect", "x, y, w, h")

SCREEN_WIDTH = 160
SCREEN_HEIGHT = 210
MAX_SCORE = 20

DIGITS = {
    0: [Rect(0, 0, 12, 4), Rect(0, 16, 12, 4), Rect(0, 0, 4, 20), Rect(8, 0, 4, 20)],
    1: [Rect(4, 0, 4, 20)],
    2: [
        Rect(0, 0, 12, 4),
        Rect(0, 8, 12, 4),
        Rect(0, 16, 12, 4),
        Rect(8, 0, 4, 12),
        Rect(0, 8, 4, 12),
    ],
    3: [Rect(0, 0, 12, 4), Rect(0, 16, 12, 4), Rect(8, 0, 4, 20), Rect(4, 8, 8, 4)],
    4: [Rect(0, 0, 4, 12), Rect(8, 0, 4, 20), Rect(0, 8, 12, 4)],
    5: [
        Rect(0, 0, 12, 4),
        Rect(0, 8, 12, 4),
        Rect(0, 16, 12, 4),
        Rect(0, 0, 4, 12),
        Rect(8, 8, 4, 12),
    ],
    6: [Rect(0, 0, 4, 20), Rect(0, 8, 12, 4), Rect(0, 16, 12, 4), Rect(8, 8, 4, 12)],
    7: [Rect(0, 0, 12, 4), Rect(8, 0, 4, 20)],
    8: [
        Rect(0, 0, 12, 4),
        Rect(0, 8, 12, 4),
        Rect(0, 16, 12, 4),
        Rect(0, 0, 4, 20),
        Rect(8, 0, 4, 20),
    ],
    9: [Rect(0, 0, 12, 4), Rect(0, 0, 4, 12), Rect(8, 0, 4, 20), Rect(0, 8, 12, 4)],
}


def _clamp(v, low, high):
    if v < low:
        return low
    elif v > high:
        return high
    else:
        return v


def TennisEnv(num=1, surface_type="opengl", num_players=1, egl_device_index=None):
    assert num % num_players == 0
    num = num // num_players
    envs = []
    for _ in range(num):
        envs.append(
            SingleTennisEnv(
                surface_type=surface_type,
                num_players=num_players,
                egl_device_index=egl_device_index,
            )
        )
    return gym3.ConcatEnv(envs)


class SingleTennisEnv(gym3.Env):
    def __init__(self, surface_type, num_players, egl_device_index):
        # same buttons as retro atari
        self.buttons = [
            "BUTTON",
            None,
            "SELECT",
            "RESET",
            "UP",
            "DOWN",
            "LEFT",
            "RIGHT",
        ]
        ob_space = gym3.types.TensorType(
            eltype=gym3.types.Discrete(256, dtype_name="uint8"),
            shape=(SCREEN_HEIGHT, SCREEN_WIDTH, 3),
        )
        ac_space = gym3.types.TensorType(
            eltype=gym3.types.Discrete(2, dtype_name="uint8"),
            shape=(len(self.buttons),),
        )
        super().__init__(ob_space=ob_space, ac_space=ac_space, num=num_players)

        self._render_window = None
        self._viewer = None

        self._ball_pos = None
        self._last_obs = None

        surface_kwargs = {}
        if surface_type == "opengl":
            surface_kwargs["egl_device_index"] = egl_device_index

        self._surface = build_surface(
            surface_type,
            pixel_width=SCREEN_WIDTH,
            pixel_height=SCREEN_HEIGHT,
            view_width=SCREEN_WIDTH,
            view_height=SCREEN_HEIGHT,
            origin_at_center=False,
            **surface_kwargs,
        )

        self._white_color = Color(236 / 255, 236 / 255, 236 / 255)
        # self._bg_color = Color(144 / 255, 72 / 255, 17 / 255)
        # self._p1_color = Color(92 / 255, 186 / 255, 92 / 255)
        # self._p2_color = Color(213 / 255, 130 / 255, 74 / 255)
        self._bg_color = Color(114 / 255, 106 / 255, 149 / 255)
        self._p1_color = Color(246 / 255, 167 / 255, 193 / 255)
        self._p2_color = Color(151 / 255, 242 / 255, 243 / 255)

        self._ball_rect = Rect(0, 0, 2, 4)
        self._paddle_rect = Rect(0, 0, 4, 16)
        self._bottom_bar_rect = Rect(0, SCREEN_HEIGHT - 16, SCREEN_WIDTH, 16)
        self._top_bar_rect = Rect(0, 24, SCREEN_WIDTH, 10)

        self._ball_pos = None
        self._ball_vel = None

        self._p1_pos = None
        self._p1_vel = None
        self._p2_pos = None
        self._p2_vel = None

        self._p1_accel = 1
        if num_players == 2:
            self._p2_accel = 1
        else:
            # make computer a bit slower so it's easier to score
            self._p2_accel = 0.8

        self._reset_state(2, full_reset=True)

        self._p1_score = 0
        self._p2_score = 0

        self._last_obs = (0.0, self._render(), True)

    def _rect_to_vertices(self, rect):
        return [
            Vec2(rect.x, rect.y),
            Vec2(rect.x + rect.w, rect.y),
            Vec2(rect.x + rect.w, rect.y + rect.h),
            Vec2(rect.x, rect.y + rect.h),
        ]

    def _reset_state(self, serve_to_player, full_reset):
        self._ball_pos = Vec2(
            78, random.randrange(115 - SCREEN_HEIGHT // 4, 115 + SCREEN_HEIGHT // 4)
        )

        if serve_to_player == 1:
            if self._p1_pos.y > 100:
                start_angle = 0
                end_angle = 45
            else:
                start_angle = 315
                end_angle = 360
        elif serve_to_player == 2:
            start_angle = 135
            end_angle = 225
        else:
            raise Exception("invalid player")

        ball_angle = random.uniform(
            start_angle / 180 * math.pi, end_angle / 180 * math.pi
        )
        ball_dir = Vec2(math.cos(ball_angle), math.sin(ball_angle))
        self._ball_vel = ball_dir * random.uniform(0.5, 2.0)

        if full_reset:
            self._p1_pos = Vec2(140, 168 + random.uniform(-10, 10))
            self._p1_vel = Vec2(0, 0)

        self._p2_pos = Vec2(16, 115 + random.uniform(-10, 10))
        self._p2_vel = Vec2(0, 0)

    def _lines_overlap(self, a1, a2, b1, b2):
        assert a1 <= a2 and b1 <= b2
        return a1 <= b2 and b1 <= a2

    def _rects_overlap(self, a, b):
        return self._lines_overlap(
            a.x, a.x + a.w, b.x, b.x + b.w
        ) and self._lines_overlap(a.y, a.y + a.h, b.y, b.y + b.h)

    def _move_rect(self, p, r):
        return Rect(p.x + r.x, p.y + r.y, r.w, r.h)

    def _draw_digit(self, digit, pos, color):
        for rect in DIGITS[digit]:
            vertices = [v + pos for v in self._rect_to_vertices(rect)]
            self._surface.draw_polygon(vertices, color)

    def _render(self):
        self._surface.reset(color=self._bg_color)

        self._draw_digit(self._p1_score % 10, Vec2(116, 1), self._p1_color)
        if self._p1_score >= 10:
            self._draw_digit(
                int(self._p1_score / 10) % 10, Vec2(100, 1), self._p1_color
            )

        self._draw_digit(self._p2_score % 10, Vec2(36, 1), self._p2_color)
        if self._p2_score >= 10:
            self._draw_digit(int(self._p2_score / 10) % 10, Vec2(20, 1), self._p2_color)

        vertices = [v + self._ball_pos for v in self._rect_to_vertices(self._ball_rect)]
        self._surface.draw_polygon(vertices, self._white_color)

        vertices = [v + self._p1_pos for v in self._rect_to_vertices(self._paddle_rect)]
        self._surface.draw_polygon(vertices, self._p1_color)

        vertices = [v + self._p2_pos for v in self._rect_to_vertices(self._paddle_rect)]
        self._surface.draw_polygon(vertices, self._p2_color)

        self._surface.draw_polygon(
            self._rect_to_vertices(self._bottom_bar_rect), self._white_color
        )
        self._surface.draw_polygon(
            self._rect_to_vertices(self._top_bar_rect), self._white_color
        )

        img = self._surface.get_image()
        return img

    def observe(self):
        rew, img, first = self._last_obs
        if self.num == 2:
            return (
                np.array([rew, -rew], dtype=np.float32),
                np.stack([img, img], axis=0),
                np.array([first, first], dtype=np.bool),
            )
        else:
            return (
                np.array([rew], dtype=np.float32),
                np.expand_dims(img, axis=0),
                np.array([first], dtype=np.bool),
            )

    def act(self, ac):
        action = ac[0]
        if action[4] and action[5]:
            pass
        elif action[4]:
            # up
            self._p1_vel += Vec2(0, -self._p1_accel)
        elif action[5]:
            # down
            self._p1_vel += Vec2(0, self._p1_accel)

        if self.num == 2:
            p2_action = ac[1]
            if p2_action[4] and p2_action[5]:
                pass
            elif p2_action[4]:
                # up
                self._p2_vel += Vec2(0, -self._p2_accel)
            elif p2_action[5]:
                # down
                self._p2_vel += Vec2(0, self._p2_accel)
        else:
            # AI
            paddle_mid_y = self._p2_pos.y + self._paddle_rect.h / 2
            ball_mid_y = self._ball_pos.y + self._ball_rect.h / 2
            diff_mid_y = paddle_mid_y - ball_mid_y
            if abs(diff_mid_y) < 2:
                # dead zone
                pass
            elif paddle_mid_y > ball_mid_y:
                self._p2_vel += Vec2(0, -self._p2_accel)
            else:
                self._p2_vel += Vec2(0, self._p2_accel)

        self._p1_vel.y *= 0.8
        self._p2_vel.y *= 0.8
        self._p1_vel.y = _clamp(self._p1_vel.y, -2, 2)
        self._p2_vel.y = _clamp(self._p2_vel.y, -2, 2)

        self._ball_pos += self._ball_vel
        self._p1_pos += self._p1_vel
        self._p2_pos += self._p2_vel

        self._p1_pos.y = _clamp(self._p1_pos.y, 24, SCREEN_HEIGHT)
        self._p2_pos.y = _clamp(self._p2_pos.y, 24, SCREEN_HEIGHT)

        objects = [
            (1, self._p1_pos, self._paddle_rect),
            (2, self._p2_pos, self._paddle_rect),
            (0, Vec2(0, 0), self._bottom_bar_rect),
            (0, Vec2(0, 0), self._top_bar_rect),
        ]

        for (player, pos, rect) in objects:
            if self._rects_overlap(
                self._move_rect(self._ball_pos, self._ball_rect),
                self._move_rect(pos, rect),
            ):
                if player == 0:
                    # bars are at the top and bottom, so just invert y velocity
                    self._ball_vel.y = -self._ball_vel.y
                else:
                    # depending on where we collide with the paddle, send the ball back out
                    diff_y = (
                        pos.y
                        + self._paddle_rect.h / 2
                        - (self._ball_pos.y + self._ball_rect.h / 2)
                    )
                    dist_y = abs(diff_y)
                    v_x = 1
                    if dist_y <= 2:
                        v_y = 0
                    elif dist_y <= 4:
                        v_y = 1
                    else:
                        v_y = 2
                    if diff_y > 0:
                        # send upward
                        v_y = -v_y
                    if player == 1:
                        # reverse x velocity
                        v_x = -v_x
                    self._ball_vel = Vec2(v_x, v_y)

        if self._ball_pos.x < 0 or self._ball_pos.x > 160:
            self._ball_vel.x = -self._ball_vel.x

        rew = 0.0
        first = False
        if self._ball_pos.x < 0:
            self._p1_score += 1
            rew = 1.0
            if self._p1_score >= MAX_SCORE:
                first = True
            self._reset_state(serve_to_player=2, full_reset=first)
        elif self._ball_pos.x > SCREEN_WIDTH:
            self._p2_score += 1
            rew = -1.0
            if self._p2_score >= MAX_SCORE:
                first = True
            self._reset_state(serve_to_player=1, full_reset=first)

        self._last_obs = (rew, self._render(), first)

    def get_info(self):
        return [{} for _ in range(self.num)]

    def keys_to_act(self, keys_list):
        result = []
        for keys in keys_list:
            act = np.zeros(shape=self.ac_space.shape, dtype=np.uint8)
            key_to_button = {"UP": "UP", "DOWN": "DOWN"}
            for key, button in key_to_button.items():
                if key in keys:
                    act[self.buttons.index(button)] = 1
                    break
            result.append(np.expand_dims(act, axis=0))
        return result
