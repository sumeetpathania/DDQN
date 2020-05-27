from game import Player, Enemy, Cloud

import pygame
import random
import time
import numpy as np
import gym.spaces as spaces

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

class RocketEnv():
    def __init__(self):
        self.max_num_enemies = 20
        self.max_clouds = 6        
        self.enemy_timer = 1
        self.cloud_timer = 1

        self.state_size = self.max_num_enemies * 2 + 2
        high = np.array([np.inf]*self.state_size)
        self.observation_space = spaces.Box(-high, high)
        self.action_space = spaces.Discrete(5)
        self._max_episode_steps = np.inf

    def reset(self):
        '''reset the environment, called at the beginning of each episode
        :return curr_state (1d array): current state'''
        pygame.init()
        self.done = False

        # Clock for framerate
        self.clock = pygame.time.Clock()        

        # screen
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        # Create custom events for adding a new enemy and cloud
        self.ADDENEMY = pygame.USEREVENT + 1
        pygame.time.set_timer(self.ADDENEMY, self.enemy_timer)
        self.ADDCLOUD = pygame.USEREVENT + 1
        pygame.time.set_timer(self.ADDCLOUD, self.cloud_timer)

        # Create our 'player'
        self.player = Player()

        # Create groups to hold enemy sprites, cloud sprites, and all sprites
        self.enemies = pygame.sprite.Group()
        self.clouds = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)

        curr_state = self.__get_curr_state()
        return curr_state

    def step(self, action):
        '''step on action
        :param action (int): action chosen by the agent
        :return state (1d array): current state after taking action
        :return reward (float): constant reward of 1
        :return done (bool): if the episode is finished
        :return info (dict): empty dict
        '''
        if self.done:
            raise TypeError('Unable to step on action since episode is done.. Call reset() to start new episode')

        for event in pygame.event.get():
            # Should we add a new enemy?
            if event.type == self.ADDENEMY:
                # Create the new enemy, and add it to our sprite groups
                if len(self.enemies) < self.max_num_enemies:
                    new_enemy = Enemy()
                    self.enemies.add(new_enemy)
                    self.all_sprites.add(new_enemy)

            # adding a new cloud
            if event.type == self.ADDCLOUD:
                if len(self.clouds) < self.max_clouds:
                    new_cloud = Cloud()
                    self.clouds.add(new_cloud)
                    self.all_sprites.add(new_cloud)

        # Update position of rocket player with action taken
        self.player.update(action)

        # Update the position of our enemies and clouds
        self.enemies.update()
        self.clouds.update()

        # background colour
        self.screen.fill((135, 206, 235))

        # Draw all our sprites
        for entity in self.all_sprites:
            self.screen.blit(entity.surf, entity.rect)

        # Check if any enemies have collided with the player
        if pygame.sprite.spritecollideany(self.player, self.enemies):
            # If so, remove the player
            self.player.kill()
            self.done = True

        # Ensure we maintain a 30 frames pe second rate
        #self.clock.tick(1000)

        curr_state = self.__get_curr_state()
        reward = 1
        info = {}
        return curr_state, reward, self.done, info

    def render(self):
        '''display the enviroment'''
        pygame.display.flip()
        self.clock.tick(27)

    def __get_curr_state(self):
        '''get current state of the environment
        :return state (1d array): state vector stacked of rocket and enemy positions'''
        all_pos = np.zeros((self.max_num_enemies+1, 2))
        rocket_pos = self.player.get_position()
        all_pos[0] = rocket_pos
        idx = 1
        for enemy in self.enemies:
            all_pos[idx] = enemy.get_position()
            idx += 1
            if idx > self.max_num_enemies + 1:
                raise ValueError('Implementation error: too many enemies {} for env state vector'.format(idx))

        state = all_pos.flatten()
        if len(state) != self.state_size:
            raise ValueError('Implementation Error: env state vector of size {} does not match state size {}'.format(len(all_pos), self.state_size))

        return state

    def close(self):
        pygame.display.flip()
        print ('closing RocketEnv')
        time.sleep(0.5)
        pygame.quit()

if __name__ == "__main__":
    print ('test run env.py w/ random policy')
    env = RocketEnv()
    for i in range(3):
        state = env.reset()
        episode_steps = 0
        done = False
        print ("watching episode ", i + 1)
        while not done:
            action = random.choice([0, 1, 2, 3, 4])
            env.render()
            next_state, reward, done, _ = env.step(action)
            episode_steps += 1
            state = next_state
        print ('episode length: ', episode_steps)
    env.close()
