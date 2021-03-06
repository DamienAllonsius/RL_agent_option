from agent.q import QArray
import numpy as np
from abc import ABCMeta, abstractmethod


class OptionAbstract(object):
    """
    Abstract option class that barely only needs update, reset and act functions
    """
    __metaclass__ = ABCMeta

    def __init__(self, number_actions, play=False):
        self.initial_state = None
        self.current_state = None
        self.terminal_state = None
        self.play = play
        self.number_actions = number_actions
        self.lives = None

    def check_end_option(self, new_state):
        return new_state != self.initial_state

    @abstractmethod
    def update_option(self, reward, new_position, new_state, action):
        raise NotImplementedError()

    @abstractmethod
    def act(self):
        raise NotImplementedError()

    def reset(self,
              initial_state,  # blurred image
              current_state,  # high resolution image
              terminal_state):  # blurred image

        self.initial_state = initial_state
        self.current_state = current_state
        self.terminal_state = terminal_state
        self.lives = None


class Option(OptionAbstract):
    """
        This class is doing Q learning, where Q is a matrix
        (we know the number of states and actions)
    """
    def __init__(self, number_actions,
                 play,
                 experiment_data):
        """
        here grid_size_option is the size of the zone
        state are always of high resolution
        except if stated otherwise in the variable name
        """
        super().__init__(number_actions, play)
        self.experiment_data = experiment_data
        self.q = None

    def __repr__(self):
        return "".join(["Option(", str(self.initial_state), ",", str(self.terminal_state), ")"])

    def __str__(self):
        return "option from " + str(self.initial_state) + " to " + str(self.terminal_state)

    def reset(self,
              initial_state,  # blurred image
              current_state,   # high resolution image
              terminal_state):  # blurred image

        if self.q is None:
            self.q = QArray(current_state, self.number_actions)

        super().reset(initial_state, current_state, terminal_state)
        self.q.add_state(current_state)

    def update_option(self, reward, new_state, action, remaining_lives):
        if self.lives is None:
            self.lives = remaining_lives

        end_option = self.check_end_option(new_state["blurred_state"])

        if self.play:
            return end_option

        else:
            # Update and compute the rewards
            total_reward = self.compute_total_reward(reward,
                                                     end_option,
                                                     new_state["blurred_state"],
                                                     action,
                                                     remaining_lives)

            # Update the states/actions of Q function
            # and compute the corresponding value
            self.q.add_state(new_state["state"])
            self.q.update_q_value(self.current_state,
                                  action,
                                  total_reward,
                                  new_state["state"],
                                  end_option,
                                  self.experiment_data["LEARNING_RATE"])

            # Update the lives and the state
            self.lives = remaining_lives
            self.current_state = new_state["state"]
            return end_option

    def compute_total_reward(self, reward, end_option, new_state_blurred, action, remaining_lives):
        total_reward = reward + self.experiment_data["PENALTY_OPTION_ACTION"] * (action != 0)
        if end_option:
            if new_state_blurred == self.terminal_state:
                total_reward += self.experiment_data["REWARD_END_OPTION"]
                print("option terminated correctly")

            else:
                total_reward += self.experiment_data["PENALTY_END_OPTION"]
                print("missed")

        if self.lives > remaining_lives:
            total_reward += self.experiment_data["PENALTY_LOST_LIFE_FOR_OPTIONS"]

        return total_reward

    def act(self):
        if self.play:
            best_action = self.q.find_best_action(self.current_state)

        else:
            if np.random.rand() < self.experiment_data["PROBABILITY_EXPLORE_IN_OPTION"]:
                best_action = self.q.get_random_action(self.current_state)

            else:
                best_action = self.q.find_best_action(self.current_state)

        return best_action


class OptionExplore(OptionAbstract):
    """
    This is a special option to explore. No q_function is needed here.
    """
    def __init__(self, number_actions, experiment_data):
        super().__init__(number_actions, play=False)
        self.experiment_data = experiment_data

    def __str__(self):
        return "explore option from " + str(self.initial_state)

    def act(self):
        # here we do a stupid thing: go random, until it finds a new zone
        return np.random.randint(self.number_actions)

    def update_option(self, reward, new_state, action, remaining_lives):
        if self.lives is None:
            self.lives = remaining_lives

        self.lives = remaining_lives
        return self.check_end_option(new_state["blurred_state"])

    def check_end_option(self, new_state):
        return new_state != self.initial_state
