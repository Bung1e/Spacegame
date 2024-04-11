import torch
import random 
import numpy as np 
from test import GalacticShooterAI, Direction, Alien, Bullet, Player
from collections import deque

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class Agent:
    def __init__(self):
        self.n_games = 0
        self.epsilon = 0
        self.gamma = 0

    def get_state(self, game):
        pass

    def remember(self, state, action, reward, next_state, done):
        pass

    def train_long_memory(self):
        pass

    def train_short_memory(self):
        pass
    
    def get_action(self, state):
        pass

def train():
    all_scores = []
    all_penalties = []
    epochs, penalties, reward, = 0, 0, 0
    done = False
    while True:
        pass

if __name__ == '__main__':
    train()