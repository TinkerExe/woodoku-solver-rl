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


class WoodokuFeaturesV2(BaseFeaturesExtractor):
    """v2 extractor with explicit scalar branch and board local/global streams."""

    def __init__(self, observation_space: gym.spaces.Dict, features_dim: int = 256) -> None:
        super().__init__(observation_space, features_dim)
        self.board_local = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(64 * 9 * 9, 256),
            nn.ReLU(),
        )
        self.board_global = nn.Sequential(
            nn.Conv2d(1, 16, kernel_size=9, padding=0),
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(16, 64),
            nn.ReLU(),
        )
        self.pieces_net = nn.Sequential(nn.Flatten(), nn.Linear(75, 128), nn.ReLU())
        scalars_dim = int(observation_space["scalars"].shape[0]) if "scalars" in observation_space.spaces else 0
        self.scalars_net = nn.Sequential(nn.Linear(max(scalars_dim, 1), 64), nn.ReLU())
        merged_dim = 256 + 64 + 128 + 64 + 3
        self.head = nn.Sequential(nn.Linear(merged_dim, features_dim), nn.ReLU())
        self._scalars_dim = scalars_dim

    def forward(self, obs: dict) -> torch.Tensor:
        board = obs["board"].float().unsqueeze(1)
        pieces = obs["pieces"].float()
        active = obs["active"].float()
        b_local = self.board_local(board)
        b_global = self.board_global(board)
        p = self.pieces_net(pieces)
        if self._scalars_dim > 0 and "scalars" in obs:
            s = obs["scalars"].float()
        else:
            s = torch.zeros((board.shape[0], 1), dtype=torch.float32, device=board.device)
        s = self.scalars_net(s)
        return self.head(torch.cat([b_local, b_global, p, s, active], dim=1))
