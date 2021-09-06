import gym
import numpy as np
from gym.spaces import Discrete, Dict

from .config import RecEnvConfig, UserConfig
from .user import User


class RecEnv(gym.Env):

    metadata = {"render.modes": ["human"]}

    def __init__(self, config: RecEnvConfig):
        super(RecEnv, self).__init__()
        self.config = config

        # At each step you suggest a song, so each action is a single song ID
        self.action_space = Discrete(config.song_catalog_config.size)

        # We need to provide a user ID to the recommender and the initial song
        self.observation_space = Dict(
            user=Discrete(config.user_base_size),
            song=Discrete(config.song_catalog_config.size),
        )

        self.users = self.load_users()

        self.user = None
        self.session = None

        self.reset()

    def load_users(self):
        return [
            User(UserConfig(j, self.config.song_catalog_config))
            for j in range(self.config.user_base_size)
        ]

    def step(self, recommendation: int):
        assert self.action_space.contains(recommendation), str(recommendation)
        playback_time = self.user.consume(recommendation, self.session)
        return self.session.observe(), playback_time, self.session.finished, None

    def reset(self):
        self.user = self.users[np.random.randint(self.config.user_base_size)]
        self.session = self.user.new_session()
        return self.session.observe()

    def render(self, mode="human", close=False):
        print(f"Current session: {self.session}")

    def seed(self, seed=None):
        np.random.seed(seed)
