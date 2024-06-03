import os
import numpy as np
import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.results_plotter import load_results, ts2xy
from stable_baselines3.common import results_plotter
import matplotlib.pyplot as plt
import cv2
import pygame
from test import GalacticShooterAI, Direction
import random 

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

class GalacticShooterEnv(gym.Env):
    def __init__(self):
        super(GalacticShooterEnv, self).__init__()
        self.action_space = gym.spaces.Discrete(4)
        self.observation_space = gym.spaces.Box(low=0, high=255, shape=(84, 84, 1), dtype=np.uint8)
        self.game = GalacticShooterAI()
        
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        if seed is not None:
            np.random.seed(seed)
            random.seed(seed)
        self.game.reset()
        return self._get_obs(), {}

    def step(self, action):
        actions = [Direction.LEFT, Direction.RIGHT, Direction.SHOOT, Direction.DO_NOTHING]
        reward, done, score = self.game.play_step(actions[action])
        obs = self._get_obs()
        terminated = done
        truncated = False
        return obs, reward, terminated, truncated, {}

    def render(self, mode='human'):
        self.game.update_ui()

    def _get_obs(self):
        raw_pixels = pygame.surfarray.array3d(pygame.display.get_surface())
        raw_pixels = np.transpose(raw_pixels, (1, 0, 2))

        gray_pixels = cv2.cvtColor(raw_pixels, cv2.COLOR_RGB2GRAY)

        # Маскирование пуль (красный цвет в RGB)
        lower_red = np.array([100, 0, 0])
        upper_red = np.array([255, 100, 100])
        mask = cv2.inRange(raw_pixels, lower_red, upper_red)
        gray_pixels[mask > 0] = 0
        gray_pixels = cv2.resize(gray_pixels, (84, 84), interpolation=cv2.INTER_AREA)

        obs = np.expand_dims(gray_pixels, axis=-1)
        return obs

class SaveOnBestTrainingRewardCallback(BaseCallback):
    def __init__(self, check_freq: int, log_dir: str, verbose=1):
        super(SaveOnBestTrainingRewardCallback, self).__init__(verbose)
        self.check_freq = check_freq
        self.log_dir = log_dir
        self.save_path = os.path.join(log_dir, 'best_model')
        self.best_mean_reward = -np.inf

    def _init_callback(self) -> None:
        if self.save_path is not None:
            os.makedirs(self.save_path, exist_ok=True)

    def _on_step(self) -> bool:
        if self.n_calls % self.check_freq == 0:
            x, y = ts2xy(load_results(self.log_dir), 'timesteps')
            if len(x) > 0:
                mean_reward = np.mean(y[-50:])
                if self.verbose > 0:
                    print(f"Num timesteps: {self.num_timesteps}")
                    print(f"Best mean reward: {self.best_mean_reward:.2f} - Last mean reward per episode: {mean_reward:.2f}")

                if mean_reward > self.best_mean_reward:
                    self.best_mean_reward = mean_reward
                    if self.verbose > 0:
                        print(f"Saving new best model to {self.save_path}")
                    self.model.save(self.save_path)
        return True

log_dir = "tmp/"
os.makedirs(log_dir, exist_ok=True)

# Create and wrap the environment
env = GalacticShooterEnv()
env = Monitor(env, log_dir)

# Instantiate the agent with adjusted hyperparameters
model = PPO('CnnPolicy', env, verbose=1, n_steps=2048, learning_rate=0.0003)

# Callback to save the best model
callback = SaveOnBestTrainingRewardCallback(check_freq=1000, log_dir=log_dir)

# Train the agent with increased training steps
model.learn(total_timesteps=2000000, callback=callback)

# Plot the results
results_plotter.plot_results([log_dir], 2000000, results_plotter.X_TIMESTEPS, "PPO GalacticShooter")
plt.show()

# Save the final model
model.save("GalacticShooterModel")