import argparse
from dataclasses import dataclass, asdict
import pandas as pd
import tqdm

import yaml

from sim.agents import Recommender, DummyRecommender, RemoteRecommender
from sim.envs import RecEnv
from sim.envs.config import RecEnvConfigSchema


@dataclass
class EpisodeStats:
    episode: int
    reward: float = 0.0
    steps: int = 0


def run_episode(episode: int, env: RecEnv, recommender: Recommender):
    previous_observation = env.reset()
    done = False
    reward = 0

    stats = EpisodeStats(episode)

    while not done:
        action = recommender.recommend(previous_observation, reward, done)
        observation, reward, done, info = env.step(action)
        previous_observation = observation
        stats.reward += reward
        stats.steps += 1

    return stats


def run_experiment(env: RecEnv, episodes: int, dummy: bool):
    if dummy:
        recommender = DummyRecommender(env.action_space)
    else:
        recommender = RemoteRecommender()

    stats = []
    for episode_id in tqdm.trange(episodes):
        stats.append(run_episode(episode_id, env, recommender))
    return stats


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--episodes", help="Number of episodes in experiment", type=int, default=100,
    )
    parser.add_argument(
        "--dummy-recommender",
        action="store_true",
        help="Run local recommender without calling the actual service",
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
    parser.add_argument("output_dir", help="A path to experiment data", type=str)
    args = parser.parse_args()

    config = RecEnvConfigSchema().load(yaml.full_load(open(args.config)))

    with RecEnv(config) as env:
        env.seed(args.seed)
        stats = run_experiment(env, args.episodes, args.dummy_recommender)

    print(
        f"## Experiment summary\n\n{pd.DataFrame([asdict(s) for s in stats]).describe().to_markdown()}"
    )


if __name__ == "__main__":
    main()
