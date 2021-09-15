import argparse
import cmd
from dataclasses import dataclass, asdict
import numpy as np
import pandas as pd
import scipy.stats as ss
import tqdm

import yaml

from sim.agents import Recommender, DummyRecommender, RemoteRecommender
from sim.agents.console import ConsoleRecommender
from sim.envs import RecEnv
from sim.envs.config import RecEnvConfigSchema, RecEnvConfig

DUMMY = "dummy"
REMOTE = "remote"
CONSOLE = "console"


@dataclass
class EpisodeStats:
    day: int
    episode: int
    reward: float = 0.0
    steps: int = 0


def run_episode(day: int, episode: int, env: RecEnv, recommender: Recommender):
    observation = env.reset()
    done = False
    reward = 1.0

    stats = EpisodeStats(day, episode)

    while not done:
        action = recommender.recommend(observation, reward, done)
        observation, reward, done, info = env.step(action)
        stats.reward += reward
        stats.steps += 1

    recommender.recommend(observation, reward, done)

    return stats


def run_experiment(
    day: int, env: RecEnv, episodes: int, recommender: str, config: RecEnvConfig
):
    if recommender == DUMMY:
        recommender = DummyRecommender(env.action_space)
    elif recommender == REMOTE:
        recommender = RemoteRecommender(config.remote_recommender_config)
    elif recommender == CONSOLE:
        recommender = ConsoleRecommender(config.remote_recommender_config)
    else:
        raise ValueError(f"Unknown recommender type: {recommender}")

    stats = []
    for episode_id in tqdm.trange(episodes):
        stats.append(run_episode(day, episode_id, env, recommender))
    return stats


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--episodes", help="Number of episodes in experiment", type=int, default=100,
    )
    parser.add_argument(
        "--recommender", choices=[DUMMY, REMOTE, CONSOLE], help="Recommender to use",
    )
    parser.add_argument(
        "--seed", help="Random seed for the env", type=int, default=42,
    )
    parser.add_argument(
        "--config",
        help="Path to environment config",
        type=str,
        default="config/env.yml",
    )
    args = parser.parse_args()

    config = RecEnvConfigSchema().load(yaml.full_load(open(args.config)))

    stats = []
    with RecEnv(config) as env:
        env.seed(args.seed)

        day = 1
        while True:
            stats.extend(
                run_experiment(day, env, args.episodes, args.recommender, config)
            )

            time_control = TimeControl()
            time_control.cmdloop(
                f"End of day {day}. Would you like to start a new day?"
            )
            if time_control.done:
                break
            else:
                day += 1

    result = (
        pd.DataFrame([asdict(s) for s in stats])
        .groupby("day")[["reward", "steps"]]
        .agg([np.mean, ss.sem])
    )
    print(f"## Experiment results summary\n\n{result.to_markdown()}")


class TimeControl(cmd.Cmd):
    prompt = "(y/n) "

    def __init__(self):
        super().__init__()
        self.done = False

    def do_y(self, arg):
        print("Moving to the next day!")
        return True

    def do_n(self, arg):
        print("Ending the simulation")
        self.done = True
        return True


if __name__ == "__main__":
    main()
