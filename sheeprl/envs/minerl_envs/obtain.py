# adapted from https://github.com/minerllabs/minerl

from sheeprl.utils.imports import _IS_MINERL_0_4_4_AVAILABLE

if not _IS_MINERL_0_4_4_AVAILABLE:
    raise ModuleNotFoundError(_IS_MINERL_0_4_4_AVAILABLE)

from typing import Dict, List, Union

from minerl.herobraine.hero import handlers, mc
from minerl.herobraine.hero.handler import Handler
from minerl.herobraine.hero.mc import MS_PER_STEP

from sheeprl.envs.minerl_envs.backend import CustomSimpleEmbodimentEnvSpec

none = "none"
other = "other"


def snake_to_camel(word):
    return "".join(x.capitalize() or "_" for x in word.split("_"))


class CustomObtain(CustomSimpleEmbodimentEnvSpec):
    def __init__(
        self,
        target_item,
        dense,
        reward_schedule: List[Dict[str, Union[str, int, float]]],
        *args,
        max_episode_steps=6000,
        **kwargs,
    ):
        # 6000 for obtain iron  (5 mins)
        # 18000 for obtain diamond (15 mins)
        self.target_item = target_item
        self.dense = dense
        suffix = snake_to_camel(self.target_item)
        dense_suffix = "Dense" if self.dense else ""
        if self.dense:
            self.reward_text = "every time it obtains an item"
        else:
            self.reward_text = "only once per item the first time it obtains that item"
        self.reward_schedule = reward_schedule

        super().__init__(
            *args,
            name="CustomMineRLObtain{}{}-v0".format(suffix, dense_suffix),
            max_episode_steps=max_episode_steps,
            **kwargs,
        )

    def create_observables(self) -> List[Handler]:
        # TODO: Parameterize these observations.
        return super().create_observables() + [
            handlers.FlatInventoryObservation(
                [
                    "dirt",
                    "coal",
                    "torch",
                    "log",
                    "planks",
                    "stick",
                    "crafting_table",
                    "wooden_axe",
                    "wooden_pickaxe",
                    "stone",
                    "cobblestone",
                    "furnace",
                    "stone_axe",
                    "stone_pickaxe",
                    "iron_ore",
                    "iron_ingot",
                    "iron_axe",
                    "iron_pickaxe",
                ]
            ),
            handlers.EquippedItemObservation(items=mc.ALL_ITEMS, _default="air", _other=other),
        ]

    def create_actionables(self):
        # TODO (R): MineRL-v1 use invalid (for data)
        return super().create_actionables() + [
            handlers.PlaceBlock(
                [none, "dirt", "stone", "cobblestone", "crafting_table", "furnace", "torch"], _other=none, _default=none
            ),
            handlers.EquipAction(
                [none, "air", "wooden_axe", "wooden_pickaxe", "stone_axe", "stone_pickaxe", "iron_axe", "iron_pickaxe"],
                _other=none,
                _default=none,
            ),
            handlers.CraftAction([none, "torch", "stick", "planks", "crafting_table"], _other=none, _default=none),
            handlers.CraftNearbyAction(
                [
                    none,
                    "wooden_axe",
                    "wooden_pickaxe",
                    "stone_axe",
                    "stone_pickaxe",
                    "iron_axe",
                    "iron_pickaxe",
                    "furnace",
                ],
                _other=none,
                _default=none,
            ),
            handlers.SmeltItemNearby([none, "iron_ingot", "coal"], _other=none, _default=none),
            # As apart of pervious todo
            # this should be handlers.SmeltItem([none, 'iron_ingot', 'coal', other]),
            # but this is not supported by mineRL-v0
        ]

    def create_rewardables(self) -> List[Handler]:
        reward_handler = handlers.RewardForCollectingItems if self.dense else handlers.RewardForCollectingItemsOnce

        return [reward_handler(self.reward_schedule if self.reward_schedule else {self.target_item: 1})]

    def create_agent_start(self) -> List[Handler]:
        return super().create_agent_start()

    def create_agent_handlers(self) -> List[Handler]:
        return [handlers.AgentQuitFromPossessingItem([dict(type="diamond", amount=1)])]

    def create_server_world_generators(self) -> List[Handler]:
        return [handlers.DefaultWorldGenerator(force_reset=True)]

    def create_server_quit_producers(self) -> List[Handler]:
        return [
            handlers.ServerQuitFromTimeUp(time_limit_ms=self.max_episode_steps * MS_PER_STEP),
            handlers.ServerQuitWhenAnyAgentFinishes(),
        ]

    def create_server_decorators(self) -> List[Handler]:
        return []

    def create_server_initial_conditions(self) -> List[Handler]:
        return [
            handlers.TimeInitialCondition(
                start_time=6000,
                allow_passage_of_time=True,
            ),
            handlers.SpawningInitialCondition(allow_spawning=True),
        ]

    def is_from_folder(self, folder: str):
        return folder == "o_{}".format(self.target_item)

    def get_docstring(self):
        return ""

    def determine_success_from_rewards(self, rewards: list) -> bool:
        # TODO: Convert this to finish handlers.
        rewards = set(rewards)
        allow_missing_ratio = 0.1
        max_missing = round(len(self.reward_schedule) * allow_missing_ratio)

        # Get a list of the rewards from the reward_schedule.
        reward_values = [s["reward"] for s in self.reward_schedule]

        return len(rewards.intersection(reward_values)) >= len(reward_values) - max_missing


class CustomObtainDiamond(CustomObtain):
    def __init__(self, dense, *args, **kwargs):
        super(CustomObtainDiamond, self).__init__(
            *args,
            target_item="diamond",
            dense=dense,
            reward_schedule=[
                dict(type="log", amount=1, reward=1),
                dict(type="planks", amount=1, reward=2),
                dict(type="stick", amount=1, reward=4),
                dict(type="crafting_table", amount=1, reward=4),
                dict(type="wooden_pickaxe", amount=1, reward=8),
                dict(type="cobblestone", amount=1, reward=16),
                dict(type="furnace", amount=1, reward=32),
                dict(type="stone_pickaxe", amount=1, reward=32),
                dict(type="iron_ore", amount=1, reward=64),
                dict(type="iron_ingot", amount=1, reward=128),
                dict(type="iron_pickaxe", amount=1, reward=256),
                dict(type="diamond", amount=1, reward=1024),
            ],
            max_episode_steps=18000,
            **kwargs,
        )

    def is_from_folder(self, folder: str) -> bool:
        return folder == "o_dia"

    def get_docstring(self):
        return (
            """
.. image:: ../assets/odia1.mp4.gif
  :scale: 100 %
  :alt:

.. image:: ../assets/odia2.mp4.gif
  :scale: 100 %
  :alt:

.. image:: ../assets/odia3.mp4.gif
  :scale: 100 %
  :alt:

.. image:: ../assets/odia4.mp4.gif
  :scale: 100 %
  :alt:

In this environment the agent is required to obtain a diamond.
The agent begins in a random starting location on a random survival map without any items,
matching the normal starting conditions for human players in Minecraft.
The agent is given access to a selected summary of its inventory and GUI free
crafting, smelting, and inventory management actions.


During an episode **the agent is rewarded """
            + self.reward_text
            + """**
in the requisite item hierarchy to obtaining a diamond. The rewards for each
item are given here::

    <Item reward="1" type="log" />
    <Item reward="2" type="planks" />
    <Item reward="4" type="stick" />
    <Item reward="4" type="crafting_table" />
    <Item reward="8" type="wooden_pickaxe" />
    <Item reward="16" type="cobblestone" />
    <Item reward="32" type="furnace" />
    <Item reward="32" type="stone_pickaxe" />
    <Item reward="64" type="iron_ore" />
    <Item reward="128" type="iron_ingot" />
    <Item reward="256" type="iron_pickaxe" />
    <Item reward="1024" type="diamond" />

\n"""
        )


class CustomObtainIronPickaxe(CustomObtain):
    def __init__(self, dense, *args, **kwargs):
        super(CustomObtainIronPickaxe, self).__init__(
            *args,
            target_item="iron_pickaxe",
            dense=dense,
            reward_schedule=[
                dict(type="log", amount=1, reward=1),
                dict(type="planks", amount=1, reward=2),
                dict(type="stick", amount=1, reward=4),
                dict(type="crafting_table", amount=1, reward=4),
                dict(type="wooden_pickaxe", amount=1, reward=8),
                dict(type="cobblestone", amount=1, reward=16),
                dict(type="furnace", amount=1, reward=32),
                dict(type="stone_pickaxe", amount=1, reward=32),
                dict(type="iron_ore", amount=1, reward=64),
                dict(type="iron_ingot", amount=1, reward=128),
                dict(type="iron_pickaxe", amount=1, reward=256),
            ],
            **kwargs,
        )

    def create_agent_handlers(self):
        return [handlers.AgentQuitFromCraftingItem([dict(type="iron_pickaxe", amount=1)])]

    def is_from_folder(self, folder: str) -> bool:
        return folder == "o_iron"

    def get_docstring(self):
        return (
            """
.. image:: ../assets/orion1.mp4.gif
  :scale: 100 %
  :alt:

.. image:: ../assets/orion2.mp4.gif
  :scale: 100 %
  :alt:

.. image:: ../assets/orion3.mp4.gif
  :scale: 100 %
  :alt:

.. image:: ../assets/orion4.mp4.gif
  :scale: 100 %
  :alt:
In this environment the agent is required to obtain an iron pickaxe.
The agent begins in a random starting location, on a random survival map, without any items,
matching the normal starting conditions for human players in Minecraft.
The agent is given access to a selected view of its inventory and GUI free
crafting, smelting, and inventory management actions.


During an episode **the agent is rewarded """
            + self.reward_text
            + """**
in the requisite item hierarchy for obtaining an iron pickaxe. The reward for each
item is given here::
    <Item amount="1" reward="1" type="log" />
    <Item amount="1" reward="2" type="planks" />
    <Item amount="1" reward="4" type="stick" />
    <Item amount="1" reward="4" type="crafting_table" />
    <Item amount="1" reward="8" type="wooden_pickaxe" />
    <Item amount="1" reward="16" type="cobblestone" />
    <Item amount="1" reward="32" type="furnace" />
    <Item amount="1" reward="32" type="stone_pickaxe" />
    <Item amount="1" reward="64" type="iron_ore" />
    <Item amount="1" reward="128" type="iron_ingot" />
    <Item amount="1" reward="256" type="iron_pickaxe" />

\n"""
        )
