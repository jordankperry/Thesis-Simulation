from collections import deque
import random
from typing import Tuple
import torch

import model

LR = 0.002
GAMMA = 0.7

sampleSize = 1000

# BRAIN WILL NEED TO BE SEPARTED INTO TWO PREDATOR BRAIN VS PREY BRAIN

class Brain:
    def __init__(self) -> None:
        self.moves = 0
        self.epsilon = 1        # randomness
        self.memory = deque(maxlen=20000)
        self.model = model.Linear_QNet(24,256)
        self.trainer = model.QTrainer(self.model, LR, GAMMA)

    def remember(self, flatState: Tuple, appVelocities: list[float], reward: float, nextFlatState: Tuple):
        self.memory.append((flatState, tuple(appVelocities), reward, nextFlatState))

    def trainLongMemory(self):
        if len(self.memory) > 20000:
            sample = random.sample(self.memory, sampleSize)
        else:
            sample = self.memory
        
        states, appVelocities, rewards, nextStates = zip(*sample)
        self.trainer.train(states, appVelocities, rewards, nextStates)

    def trainMemory(self, flatState: Tuple, appVelocities: list[float], reward: float, nextFlatState: Tuple):
        self.trainer.train(flatState, tuple(appVelocities), reward, nextFlatState)

    def getAppliedVelocities(self, state: Tuple, flatState: Tuple, x: float, y: float) -> list[float, float]:
        self.epsilon = (150 - self.moves) / 120
        appliedForce = [0, 0]

        if random.random() > self.epsilon:
            # should theoretically make it completely random movements to help understand how it works
            appliedForce[0] = (random.random() - 0.5) * 20
            appliedForce[1] = (random.random() - 0.5) * 20

            # If "random" movement, apply force directly toward primary targets 
            # appliedForce[0] += (state[0][0][0].x - x)                                   / 25 if state[0][0][0].x > 0 else 0
            # # appliedForce[0] += (state[0][1][0].x - x) * state[0][1][1] / state[0][0][1] / 50 if state[0][1][0].x > 0 else 0
            # # appliedForce[0] += (state[0][2][0].x - x) * state[0][2][1] / state[0][0][1] / 45 if state[0][2][0].x > 0 else 0
            # appliedForce[1] += (state[0][0][0].y - y)                                   / 25 if state[0][0][0].y > 0 else 0
            # # appliedForce[1] += (state[0][1][0].y - y) * state[0][1][1] / state[0][0][1] / 35 if state[0][1][0].y > 0 else 0
            # # appliedForce[1] += (state[0][2][0].y - y) * state[0][2][1] / state[0][0][1] / 45 if state[0][2][0].y > 0 else 0
            # Apply force away from threats
            # appliedForce[0] -= (state[1][0][0].x - x)                                   / 35 if state[1][0][0].x > 0 else 0
            # appliedForce[0] -= (state[1][1][0].x - x) * state[1][1][1] / state[1][0][1] / 45 if state[1][1][0].x > 0 else 0
            # appliedForce[0] -= (state[1][2][0].x - x) * state[1][2][1] / state[1][0][1] / 55 if state[1][2][0].x > 0 else 0
            # appliedForce[1] -= (state[1][0][0].y - y)                                   / 35 if state[1][0][0].y > 0 else 0
            # appliedForce[1] -= (state[1][1][0].y - y) * state[1][1][1] / state[1][0][1] / 45 if state[1][1][0].y > 0 else 0
            # appliedForce[1] -= (state[1][2][0].y - y) * state[1][2][1] / state[1][0][1] / 55 if state[1][2][0].y > 0 else 0
        else:
            torchState = torch.tensor(flatState, dtype=torch.float)
            appliedForce[0] = self.model(torchState)[0].item()
            appliedForce[0] = self.model(torchState)[1].item()

            ## MAY NEED TO CLAMP??? OR SOMETHING
            # definitely nEED TO ADJUST Q CALCULATION
            #MAYBE TRY CREATURES WITH ONLY 1 OR 0 AGGRESSIVENESS AND ENSURE NO EATING IS ALLOWED OF SAME AGGRESSIVESS (complete prey/predator)
            # also maybe try getting rid of reward 

        return appliedForce

    def move(self):
        self.moves += 1
        print(self.moves)