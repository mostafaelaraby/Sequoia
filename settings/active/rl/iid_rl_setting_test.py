from dataclasses import dataclass
from typing import ClassVar, Dict

from common.config import Config
from conftest import DummyEnvironment
from methods import RandomBaselineMethod
from utils import take

from .iid_rl_setting import RLSetting

# TODO: Write some tests to make sure that the actions actually get sent back
# to the loaders for each of 'train' 'val' and 'test'. 


def test_basic():
    setting = RLSetting(observe_state_directly=True, dataset="cartpole")
    batch_size: int = 10
    setting.configure(config=Config(), batch_size=batch_size)
    setting.prepare_data()
    setting.setup()
    train_loader = setting.train_dataloader()
    check_interaction_with_env(
        train_loader,
        obs_shape=(batch_size, 4),
        action=None,
        reward_shape=(batch_size,),
    )

    val_loader = setting.val_dataloader()
    check_interaction_with_env(
        val_loader,
        obs_shape=(batch_size, 4),
        action=None,
        reward_shape=(batch_size,),
    )

    test_loader = setting.test_dataloader()
    check_interaction_with_env(
        test_loader,
        obs_shape=(batch_size, 4),
        action=None,
        reward_shape=(batch_size,),
    )
