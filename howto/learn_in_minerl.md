## Install MineRL environment
First you need to install the JDK 1.8, on Debian based systems you can run the following:

```bash
sudo add-apt-repository ppa:openjdk-r/ppa
sudo apt-get update
sudo apt-get install openjdk-8-jdk
```

> **Note**
>
> If you work on another OS, you can follow the instructions [here](https://minerl.readthedocs.io/en/v0.4.4/tutorials/index.html) to install JDK 1.8.

Now, you can install the MineRL environment:

```bash
pip install -e .[minerl]
```

## MineRL environments
We have modified the MineRL environments to have a custom action and observation space. We provide three different tasks:
1. Navigate: you need to set the `env_id` argument to `"minerl_custom_navigate"`.
2. Obtain Iron Pickaxe: you need to set the `env_id` argument to `"minerl_custom_obtain_iron_pickaxe"`.
3. Obtain Diamond: you need to set the `env_id` argument to `"minerl_custom_obtain_diamond"`.

> **Note**
> In all these environments, it is possible to have or not a dense reward, you can set the type of the reward by setting the `minerl_dense` argument to `True` if you want a dense reward, to `False` otherwise.
>
> In the Navigate task, it is also possible to choose wheter or not to train the agent on an extreme environment (for more info, check [here](https://minerl.readthedocs.io/en/v0.4.4/environments/index.html#minerlnavigateextreme-v0)). To choose wheter or not to train the agent on an extreme environment, you need to set the `minerl_extreme` argument to `True` or `False`.
>
> In addition, in all the environments, it is possible to set the break speed multiplier through the `mine_break_speed` argument.

### Observation Space
We have slightly modified the observation space, by adding the *life stats* (life, food and oxygen) and reshaping those already present (based on the idea proposed by Hafner in [DreamerV3](https://arxiv.org/abs/2301.04104)):
- We represent the inventory with a vector with one entry for each item of the game which gives the quantity of the corresponding item in the inventory.
- A max inventory vector with one entry for each item which contains the maximum number of items obtained by the agent so far in the episode.
- The RGB first-person camera image.
- A vector of three elements representing the life, the food and the oxygen levels of the agent.
- A one-hot vector indicating the equipped item, only for the *obtain* tasks.
- A scalar indicating the compass angle to the goal location, only for the *navigate* tasks.

### Action Space
We decided to convert the multi-discrete action space into a discrete action space. Moreover, we restrict the look up/down actions between `min_pitch` and `max_pitch` degrees.
In addition, we added the forward action when the agent selects one of the follwing actions: `jump`, `sprint`, and `sneak`.
Finally we added sticky action for the `jump` and `attack` actions. You can set the values of the `sticky_jump` and `sticky_attack` parameters through the `mine_sticky_jump` and `mine_sticky_attack` arguments, respectively. The sticky actions, if set, force the agent to repeat the selected actions for a certain number of steps.

> **Note**
> Since the MineRL environments have a multi-discrete action space, the sticky actions can be easily implemented. The agent will perform the selected action and the sticky actions simultaneously.
>
> The action repeat in the Minecraft environments is set to 1, indedd, It makes no sense to force the agent to repeat an action such as crafting (it may not have enough material for the second action).

## Headless machines

If you work on a headless machine, you need to software renderer. We recommend to adopt one of the following solutions:
1. Install the `xvfb` software with the `sudo apt install xvfb` command and prefix the train command with `xvfb-run`. For instance, to train DreamerV2 on the navigate task on an headless machine, you need to run the following command: `xvfb-run lightning run model --devices=1 sheeprl.py dreamer_v2 --env_id=minerl_custom_navigate --cnn_keys rgb`.
2. Exploit the [PyVirtualDisplay](https://github.com/ponty/PyVirtualDisplay) package.