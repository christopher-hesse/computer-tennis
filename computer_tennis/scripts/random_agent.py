from gym3 import types_np, ViewerWrapper
from computer_tennis import TennisEnv

env = TennisEnv(num=2, num_players=2)
env = ViewerWrapper(env, tps=60)
step = 0
while True:
    ac = types_np.sample(env.ac_space, bshape=(env.num,))
    env.act(ac)
    rew, obs, first = env.observe()
    print(f"step {step} reward {rew} first {first}")
    if step > 0 and first[0]:
        break
    step += 1
