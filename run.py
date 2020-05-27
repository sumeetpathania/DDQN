import argparse
import datetime
import gym
import numpy as np
import itertools
import torch
from tensorboardX import SummaryWriter
import mujoco_py

from dqn import DQN
from utils.loggin import Logger
from utils.traj import eval_policy

parser = argparse.ArgumentParser(description='Parc')
parser.add_argument('--env', default="HalfCheetah-v2",
                    help='Mujoco Gym environment (default: HalfCheetah-v2)')
parser.add_argument('--eval', type=bool, default=True,
                    help='Evaluates a policy a policy every 10 episode (default: True)')
parser.add_argument('--gamma', type=float, default=0.99, metavar='G',
                    help='discount factor for reward (default: 0.99)')
parser.add_argument('--tau', type=float, default=0.005, metavar='G',
                    help='target smoothing coefficient(τ) (default: 0.005)')
parser.add_argument('--lr', type=float, default=0.0003, metavar='G',
                    help='learning rate (default: 0.0003)')
parser.add_argument("--eps_min", type=float, default=0.01, metavar='G',
                    help='minimun epsilon')
parser.add_argument("--eps_decays", type=float, default=10000, metavar='G',
                    help='number of steps to decay episilon to eps_min')
parser.add_argument('--seed', type=int, default=10, metavar='N',
                    help='random seed (default: 10)')
parser.add_argument('--num_steps', type=int, default=100000, metavar='N',
                    help='maximum number of steps (default: 100000)')
parser.add_argument('--start_steps', type=int, default=500, metavar='N',
                    help='Steps sampling random actions (default: 200)')
parser.add_argument('--hidden_size', type=int, default=256, metavar='N',
                    help='network size (net_size) for Actor and Model (default: 256)')
parser.add_argument('--batch_size', type=int, default=128, metavar='N',
                    help='batch size (default: 128)')
parser.add_argument('--buffer_size', type=int, default=1000000, metavar='N',
                    help='size of replay buffer (default: 10000000)')
parser.add_argument('--update_freq', type=int, default=4, metavar='N',
                    help='number of simulations steps per update (default: 1)')
parser.add_argument('--dir', default="runs",
                    help='loggin directory to create folder containing tensorboard and loggin files')
parser.add_argument('--cuda', action="store_true",
                    help='run on CUDA (default: False)')
args = parser.parse_args()

env = gym.make(args.env)

env.seed(args.seed)
np.random.seed(args.seed)
torch.manual_seed(args.seed)
torch.cuda.manual_seed(args.seed)
torch.backends.cudnn.deterministic=True

agent = DQN(env.observation_space.shape[0], env.action_space.n, env.action_space, args)
LOG_DIR = '{}/{}_DQN_{}'.format(args.dir, datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"), args.env)
writer = SummaryWriter(logdir=LOG_DIR)

total_numsteps = 0
for i_episode in itertools.count(1):

    episode_reward = 0
    episode_steps = 0
    done = False
    state = env.reset()

    while not done:
        if total_numsteps < args.start_steps:
            action = env.action_space.sample()  # Sample random action
        else:
            action = agent.act(state)  # Sample action from policy

        next_state, reward, done, _ = env.step(action) # Step
        episode_steps += 1
        total_numsteps += 1
        episode_reward += reward
        # Ignore the "done" signal if it comes from hitting the time horizon.
        # (https://github.com/openai/spinningup/blob/master/spinup/algos/sac/sac.py)
        mask = 1 if episode_steps == env._max_episode_steps else float(not done)

        agent.step(state, action, reward, next_state, mask)
        if total_numsteps >= args.start_steps and total_numsteps % args.update_freq == 0:
            q_loss = agent.update()
            writer.add_scalar('loss/q', q_loss, total_numsteps)

        state = next_state

    if total_numsteps > args.num_steps:
        break

    writer.add_scalar('reward/train_per_stp', episode_reward, total_numsteps)
    print("Episode: {}, total numsteps: {}, episode steps: {}, reward: {}".format(i_episode, total_numsteps, episode_steps, round(episode_reward, 2)))

    # ---------- Evaluation loop every 10 episodes ---------- #
    if i_episode % 10 == 0 and args.eval == True:
        test_episodes = 5
        avg_reward = eval_policy(env, agent, args.gamma, test_episodes)
        print("Test Episodes: {}, Avg. Reward: {}".format(test_episodes, round(avg_reward, 2)))

env.close()
writer.close()
