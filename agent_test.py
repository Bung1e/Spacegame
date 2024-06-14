import torch
import random
import numpy as np
from collections import deque
from test import GalacticShooterAI, Direction
from model_test import Linear_QNet, QTrainer
from helper import plot

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class Agent:
    def __init__(self):
        self.n_games = 0
        self.epsilon = 0
        self.gamma = 0.9
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = Linear_QNet(8, 256, 4)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def get_state(self, game):
        player = game.player

        state = [
            player.rect.x,
            player.rect.y,
            player.speed_x,
            len(game.aliens),
            game.aliens.sprites()[0].rect.x if len(game.aliens) > 0 else 0,
            game.aliens.sprites()[0].rect.y if len(game.aliens) > 0 else 0,
            game.score,
            game.lives,
        ]
        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        self.epsilon = 80 - self.n_games
        final_move = [0, 0, 0, 0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 3)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move

def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = GalacticShooterAI()
    while True:
        state_old = agent.get_state(game)
        final_move = agent.get_action(state_old)
        

        print(f"Action taken (final_move): {final_move}")

        action = Direction.DO_NOTHING
        if final_move[0] == 1:
            action = Direction.LEFT
        elif final_move[1] == 1:
            action = Direction.RIGHT
        elif final_move[2] == 1:
            action = Direction.SHOOT
        elif final_move[3] == 1:
            action = Direction.DO_NOTHING

        print(f"Move action (Direction): {action}")

        reward, done, score = game.play_step(action)
        state_new = agent.get_state(game)

        agent.train_short_memory(state_old, final_move, reward, state_new, done)
        agent.remember(state_old, final_move, reward, state_new, done)

        if done:
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()

            if score > record:
                record = score
                agent.model.save()

            print('Game', agent.n_games, 'Score', score, 'Record:', record)

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)

if __name__ == '__main__':
    train()
