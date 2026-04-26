from __future__ import annotations

import gymnasium as gym
import torch
import torch.nn as nn
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor


class WoodokuFeatures(BaseFeaturesExtractor):
    def __init__(self, observation_space: gym.spaces.Dict, features_dim: int = 256) -> None:
        super().__init__(observation_space, features_dim)
        self.board_net = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Flatten(),
        )
        self.pieces_net = nn.Sequential(nn.Flatten(), nn.Linear(75, 64), nn.ReLU())
        merged_dim = 64 * 9 * 9 + 64 + 3
        self.head = nn.Sequential(nn.Linear(merged_dim, features_dim), nn.ReLU())

    def forward(self, obs: dict) -> torch.Tensor:
        board = obs["board"].float().unsqueeze(1)
        pieces = obs["pieces"].float()
        active = obs["active"].float()
        b = self.board_net(board)
        p = self.pieces_net(pieces)
        return self.head(torch.cat([b, p, active], dim=1))
