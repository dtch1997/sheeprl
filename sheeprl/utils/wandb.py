import argparse
import wandb
import time
from dataclasses import dataclass
from typing import Iterable

@dataclass
class WandBArgs:
    track: bool = False
    wandb_project_name: str = "svf_gymnasium"
    wandb_entity: str = "dtch1997"
    wandb_group: str = "default"
    wandb_tags: Iterable[str] = tuple()


def init_wandb(args, run_name, config) -> "wandb.Run":
    return wandb.init(
        name=run_name,
        project=args.wandb_project_name,
        entity=args.wandb_entity,
        group=args.wandb_group,
        config=config,
        tags=args.wandb_tags,
        sync_tensorboard=True        
    )