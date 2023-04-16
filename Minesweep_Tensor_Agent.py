import tkinter as tk
import numpy as np
import tensorflow as tf
from Minesweep_Tensor_Env import MinesweeperEnv
from Minesweep_Tensor_GUI import MinesweeperGUI
from tf_agents.agents.dqn import dqn_agent
from tf_agents.drivers import dynamic_step_driver
from tf_agents.environments import tf_py_environment
from tf_agents.eval import metric_utils
from tf_agents.metrics import tf_metrics
from tf_agents.networks import q_network
from tf_agents.replay_buffers import tf_uniform_replay_buffer
from tf_agents.trajectories import trajectory
from tf_agents.utils import common
from tf_agents.environments import gym_wrapper
print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))

# Hyperparameters
num_iterations = 500
initial_collect_steps = 100
collect_steps_per_iteration = 10
replay_buffer_max_length = 10
batch_size = 64
learning_rate = 1e-3
log_interval = 200
num_eval_episodes = 120
eval_interval = 100
num_test_episodes = 1000
# Create Minesweeper environment and its corresponding TensorFlow environment
env = MinesweeperEnv(15, 15, 30)
print("Original environment reset:", env.reset())

train_env = tf_py_environment.TFPyEnvironment(env)
eval_env = tf_py_environment.TFPyEnvironment(env)

# Create Q-Network and DQN agent
fc_layer_params = (100, 50)
q_net = q_network.QNetwork(train_env.observation_spec(
), train_env.action_spec(), fc_layer_params=fc_layer_params)
optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)
train_step_counter = tf.Variable(0)
agent = dqn_agent.DqnAgent(train_env.time_step_spec(),
                           train_env.action_spec(),
                           q_network=q_net,
                           optimizer=optimizer,
                           td_errors_loss_fn=common.element_wise_squared_loss,
                           train_step_counter=train_step_counter)
agent.initialize()

# Replay buffer and data collection
replay_buffer = tf_uniform_replay_buffer.TFUniformReplayBuffer(
    data_spec=agent.collect_data_spec,
    batch_size=train_env.batch_size,
    max_length=replay_buffer_max_length)
collect_driver = dynamic_step_driver.DynamicStepDriver(
    train_env,
    agent.collect_policy,
    observers=[replay_buffer.add_batch],
    num_steps=collect_steps_per_iteration)

# Training
initial_time_step = train_env.current_time_step()
initial_policy_state = agent.collect_policy.get_initial_state(
    train_env.batch_size)
max_iterations = collect_steps_per_iteration


def test_agent(eval_env, agent, num_episodes, render=True):
    total_reward = 0



    for episode in range(num_episodes):
        time_step = eval_env.reset()
        policy_state = agent.policy.get_initial_state(eval_env.batch_size)
        episode_reward = 0

        if render:
            gui = MinesweeperGUI(eval_env.pyenv.envs[0])
            gui.update()

        while not time_step.is_last():
            action_step = agent.policy.action(time_step, policy_state)
            action = action_step.action.numpy()[0]

            if render:
                gui.update(action)
                root.update()

            time_step = eval_env.step(action_step.action)
            episode_reward += time_step.reward.numpy().sum()

        total_reward += episode_reward

    return total_reward / num_episodes


# Initial data collection
print("Initial data collection")
for _ in range(int(collect_steps_per_iteration)):
    initial_time_step = train_env.current_time_step()
    initial_policy_state = agent.collect_policy.get_initial_state(
        train_env.batch_size)
    max_iterations = collect_steps_per_iteration
    collect_driver.run(time_step=initial_time_step,
                       policy_state=initial_policy_state, maximum_iterations=max_iterations)
    print(
        f"Action: {collect_driver.policy.action(initial_time_step).action.numpy()}")
# Initialize root and gui variables
root = None
gui = None

if True:  # Set to True if you want to render the GUI during training
    root = tk.Tk()
    root.title("Testing Window")

    gui = MinesweeperGUI(train_env.pyenv.envs[0])


def train(agent, replay_buffer, batch_size, root=None, gui=None, render=True):
    iterator = iter(replay_buffer.as_dataset(
        num_parallel_calls=3, sample_batch_size=batch_size, num_steps=2).take(1))
    experience, _ = next(iterator)
    print("Experience:", experience)

    if render:
        if root is None and gui is None:
            root = tk.Tk()
            root.title("Testing Windoasdasdasdasdw")

            gui = MinesweeperGUI(train_env.pyenv.envs[0])
        gui.update()
        root.update()

    # Train the agent
    train_loss = agent.train(experience)

    # Return the loss_info object
    return train_loss


# Main loop
print("Main loop")
for iteration in range(num_iterations):
    print(f"Iteration: {iteration}")
    initial_time_step = train_env.current_time_step()
    initial_policy_state = agent.collect_policy.get_initial_state(
        train_env.batch_size)
    max_iterations = collect_steps_per_iteration
    collect_driver.run(time_step=initial_time_step,
                       policy_state=initial_policy_state, maximum_iterations=max_iterations)
    experience, _ = next(iter(replay_buffer.as_dataset(
        num_parallel_calls=3, sample_batch_size=batch_size, num_steps=2).take(1)))

    print("Experience shape:", {k: v.shape if hasattr(
        v, 'shape') else str(v) for k, v in experience._asdict().items()})

    train_loss = train(agent, replay_buffer, batch_size,
                       root=root, gui=gui).loss

    step = agent.train_step_counter.numpy()

    if step % log_interval == 0:
        print('step = {0}: loss = {1}'.format(step, train_loss))

    if step % eval_interval == 0:
        avg_return = tf_metrics.compute_avg_return(
            eval_env, agent.policy, num_episodes=num_eval_episodes)
        print('step = {0}: Average Return = {1}'.format(step, avg_return))

# Testing the agent
avg_test_reward = test_agent(eval_env, agent, num_test_episodes)
print(f'Average reward over {num_test_episodes} episodes: {avg_test_reward}')
