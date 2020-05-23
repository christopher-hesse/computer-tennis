import numpy as np
from computer_tennis.env import TennisEnv

from computer_tennis.interactive_base import Interactive


class TennisEnvInteractive(Interactive):
    def __init__(self):
        env = TennisEnv()
        self._action_space = env.action_space
        self._buttons = env.buttons
        super().__init__(env=env, sync=False)

    def get_image(self, obs, env):
        return obs[:, :, :3]

    def keys_to_act(self, pressed_keys):
        act = np.zeros(shape=(self._action_space.n,), dtype=np.bool)
        key_to_button = {"UP": "UP", "DOWN": "DOWN"}
        for key, button in key_to_button.items():
            if key in pressed_keys:
                act[self._buttons.index(button)] = True
                break
        return act


def main():
    ia = TennisEnvInteractive()
    ia.run()


if __name__ == "__main__":
    main()
