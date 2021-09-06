import argparse
import os
from typing import List

import pandas as pd
import tqdm as tqdm
import yaml

from sim.agents import Recommender, DummyRecommender
from sim.envs import RecEnv
from sim.envs.config import RecEnvConfigSchema, RecEnvConfig


def log_entry(run, episode, step, recommender, observation, action, reward, done):
    entry = {
        "run": run,
        "episode": episode,
        "step": step,
        "recommender": recommender,
        "action": action,
        "reward": reward,
        "done": done,
    }

    entry.update(observation)

    return entry


def run_episode(run: int, episode: int, env: RecEnv, recommender: Recommender):
    log = []

    previous_observation = env.reset()
    done = False
    reward = 0
    step = 0

    while not done:
        action = recommender.recommend(previous_observation, reward, done)
        observation, reward, done, info = env.step(action)

        log.append(
            log_entry(
                run, episode, step, str(recommender), observation, action, reward, done
            )
        )

        previous_observation = observation
        step += 1

    return log


def run_experiment(run: int, env: RecEnv, episodes: int):
    recommender = DummyRecommender(env.action_space)

    log = []

    for episode_id in range(episodes):
        log.extend(run_episode(run, episode_id, env, recommender))

    return log


def save_results(log: List, config: RecEnvConfig, output_dir: str):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    yaml.dump(
        RecEnvConfigSchema().dump(config),
        open(os.path.join(output_dir, "config.yml"), "w"),
    )

    data = pd.DataFrame(log)
    data.to_csv(os.path.join(output_dir, "data.csv"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--runs",
        help="Number of experiment runs",
        type=int,
        default=5,
    )
    parser.add_argument(
        "--episodes",
        help="Number of episodes in experiment",
        type=int,
        default=100,
    )
    parser.add_argument(
        "--seed",
        help="Random seed for the env",
        type=int,
        default=42,
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

    log = []
    with RecEnv(config) as env:
        env.seed(args.seed)

        for run in tqdm.trange(args.runs, desc="runs"):
            log.extend(run_experiment(run, env, args.episodes))

    save_results(log, config, args.output_dir)


if __name__ == "__main__":
    main()
