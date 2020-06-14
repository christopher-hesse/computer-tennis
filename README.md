# Computer Tennis

A gym reinforcement learning environment using the [`gym3`](https://github.com/openai/gym3) API.  This is mostly a clone of the Atari Pong (Video Olympics) game, though the actual movement code isn't that close to the original.  Both single player and 2 player modes are supported.

<img src="https://raw.githubusercontent.com/christopher-hesse/computer-tennis/master/docs/env.gif">

This environment has pixel observations which can be rendered with either OpenGL (which should work almost anywhere) or Cairo (if you have the python `pycairo` package installed).  In both cases, the rendering is done off screen so there is no popup window.  The Cairo version is probably faster, but harder to get working due to `pycairo` not having binary wheels.

The pixel observations are not square, like in the Atari game, so you have to scale to a 4:3 ratio to get the correct appearance.

In addition, X-server-less OpenGL rendering is available on Linux.  To choose the EGL device, pass `egl_device_index` to the environment constructor.

## Installation

```
git clone https://github.com/christopher-hesse/computer-tennis.git
pip install -e computer-tennis
```

## Quick Start

Use the keyboard to play against the AI opponent:

```
python -m computer_tennis.interactive
```

Create the `gym3` environment in code:

```
from computer_tennis import TennisEnv
env = TennisEnv(num=2)
```

To select different rendering backends, you can pass `surface_type="opengl"` or `surface_type="cairo"` to the constructor.

Create a `gym` environment from the `gym3` one:

```
from gym3 import ToGymEnv
from computer_tennis import TennisEnv
env = TennisEnv(num=1)
gym_env = ToGymEnv(env)
```
