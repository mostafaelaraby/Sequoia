from typing import (Any, Callable, Generator, Iterable, List, Optional,
                    Sequence, Tuple, TypeVar, Union)

import gym
import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.multiprocessing as mp
from gym.envs.classic_control import CartPoleEnv
from torch import Tensor
from torch.utils.data import Dataset, IterableDataset

from settings.active.active_dataloader import ActiveDataLoader
from settings.base.environment import (ActionType, EnvironmentBase,
                                       ObservationType, RewardType)
from utils.logging_utils import get_logger, log_calls

from .gym_dataset import GymDataset
from .utils import ZipDataset

logger = get_logger(__file__)

T = TypeVar("T")

class GymDataLoader(ActiveDataLoader[
        Tensor,
        Tensor,
        Tensor
    ]):
    def __init__(self, env: Union[str, gym.Env],
                       observe_pixels: bool=True,
                       batch_size: int=1,
                       num_workers: int=None,
                        **kwargs):
        self.kwargs = kwargs
        self.environments: List[GymDataset] = [
            GymDataset(env, observe_pixels=observe_pixels) for _ in range(batch_size)
        ]
        self._observe_pixels = observe_pixels
        self.dataset = ZipDataset(self.environments)
        if num_workers is not None:
            assert num_workers == batch_size, f"Number of workers should be None or batch_size."
        # init the dataloader.
        super().__init__(self.dataset, batch_size=batch_size, **kwargs)

    def random_actions(self) -> List[ActionType]:
        return [env.action_space.sample() for env in self.environments]
    
    def send(self, actions: List[ActionType]) -> List[RewardType]:
        return [
            env.send(action) for env, action in zip(self.environments, actions)
        ]

    def __iter__(self):
        for batch in super().__iter__():
            assert len(batch) == self.batch_size
            # print([v.shape for v in batch[0]])
            if isinstance(batch, (Tensor, np.ndarray)):
                batch = torch.as_tensor(batch)
            elif isinstance(batch[0], tuple):
                raise NotImplementedError("Can't handle supervised dataset as an 'RL' dataset quite yet.")
            elif isinstance(batch[0], (Tensor, np.ndarray)):
                print([v.shape for v in batch])
                batch = torch.stack([torch.as_tensor(v) for v in batch])
            print(f"batch shape: {batch.shape}")
            yield batch

    @property
    def action_space(self) -> gym.Space:
        spaces = [env.action_space for env in self.environments]
        first_space = spaces[0]
        if not all(space.shape == first_space.shape for space in spaces):
            raise RuntimeError(f"Different action spaces: {spaces}")
        return first_space

    @property
    def observation_space(self) -> gym.Space:
        spaces = [env.observation_space for env in self.environments]
        first_space = spaces[0]
        if not all(space.shape == first_space.shape for space in spaces):
            raise RuntimeError(f"Different observation spaces: {spaces}")
        if self.observe_pixels:
            state = self.environments[0].state
            return gym.Space(shape=state.shape, dtype=state.dtype)        
        return first_space

    @property
    def batch_size(self) -> Optional[int]:
        return len(self.environments)
    
    @batch_size.setter
    def batch_size(self, value: int) -> None:
        if len(self.environments) != value:
            raise RuntimeError(
                f"Can't change the batch size (yet). Current batch size: "
                f"{len(self.environments)}, new: {value}"
            )

    @property
    def observe_pixels(self) -> bool:
        return self._observe_pixels
    
    @observe_pixels.setter
    def observe_pixels(self, value: bool) -> None:
        self._observe_pixels = value
        for env in self.environments:
            env.observe_pixels = value

def worker_env_init(self, worker_id: int):
    """ TODO: Experimenting with using a worker_init_fn arg to DataLoader to for
    multiple workers with active (Gym) environments.
    """
    logger.debug(f"Initializing dataloader worker {worker_id}")
    worker_info = torch.utils.data.get_worker_info()
    dataset: GymDataLoaderironment = worker_info.dataset  # the dataset copy in this worker process
    
    seed = worker_info.seed
    # Sometimes the numpy seed is too large.
    if seed > 4294967295:
        seed %= 4294967295
    logger.debug(f"Seed for worker {worker_id}: {seed}")

    seed_everything(seed)
    
    # TODO: Use this maybe to add an Environemnt in the Batched version of the Environment above?
    # assert len(dataset.envs) == worker_id
    # logger.debug(f"Creating environment copy for worker {worker_id}.")
    # dataset.envs.append(dataset.env_factory())

    # overall_start = dataset.start
    # overall_end = dataset.end
    # configure the dataset to only process the split workload
    # dataset.env_name = ['SpaceInvaders-v0', 'Pong-v0'][worker_info.id]
    # logger.debug(f" ENV: {dataset.env}")
    logger.debug('dataset: ', dataset)
