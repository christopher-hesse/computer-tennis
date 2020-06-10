from computer_tennis.env import TennisEnv

from gym3 import Interactive


def main():
    env = TennisEnv()
    ia = Interactive(env, tps=60)
    ia.run()


if __name__ == "__main__":
    main()
