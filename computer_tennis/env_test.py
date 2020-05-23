import pytest
import platform
import numpy as np

from computer_tennis.env import TennisEnv

TEST_ENVS = [TennisEnv]
SURFACE_TYPES = ["opengl", "cairo"]


@pytest.mark.parametrize("make_env", TEST_ENVS)
@pytest.mark.parametrize("surface_type", SURFACE_TYPES)
def test_works(make_env, surface_type):
    """
    Make sure the environment works at all and that we can instantiate multiple copies
    """
    envs = []
    for _ in range(3):
        env = make_env(surface_type=surface_type)
        envs.append(env)
        env.reset()
        for _ in range(10):
            env.step(env.action_space.sample())

    for env in envs:
        env.close()


@pytest.mark.parametrize("make_env", TEST_ENVS)
@pytest.mark.parametrize("surface_type", SURFACE_TYPES)
def test_speed(benchmark, make_env, surface_type):
    """
    Test the speed of different environments
    """
    env = make_env(surface_type=surface_type)
    act = np.zeros(env.action_space.shape, dtype=env.action_space.dtype)
    env.reset()

    def loop():
        for _ in range(1000):
            _, _, done, _ = env.step(act)
            if done:
                env.reset()

    benchmark(loop)
    env.close()
