import pytest
from gym3 import types_np

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
        for _ in range(10):
            ac = types_np.sample(env.ac_space, bshape=(env.num,))
            env.act(ac)


@pytest.mark.parametrize("make_env", TEST_ENVS)
@pytest.mark.parametrize("surface_type", SURFACE_TYPES)
def test_speed(benchmark, make_env, surface_type):
    """
    Test the speed of different environments
    """
    env = make_env(surface_type=surface_type)
    ac = types_np.zeros(env.ac_space, bshape=(env.num,))

    def loop():
        for _ in range(1000):
            env.act(ac)

    benchmark(loop)
