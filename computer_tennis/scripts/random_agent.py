from gym3 import types_np, ViewerWrapper
# from gym3 import VideoRecorderWrapper
from computer_tennis import TennisEnv

env = TennisEnv(num=1, num_players=1)
env = ViewerWrapper(env, tps=60, width=1024, height=768)
# env = VideoRecorderWrapper(env, directory=".", fps=60)
step = 0
while True:
    ac = types_np.sample(env.ac_space, bshape=(env.num,))
    env.act(ac)
    rew, obs, first = env.observe()
    print(f"step {step} reward {rew} first {first}")
    if step > 0 and first[0]:
        break
    step += 1
