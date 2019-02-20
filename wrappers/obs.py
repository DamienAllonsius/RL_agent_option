import sys
import gym
import numpy as np
import time
import cv2
from gym.envs.classic_control import rendering
from variables import *
sys.path.append('gridenvs')
import gridenvs.examples  # load example gridworld environments
from gym.envs.classic_control import rendering

class ObservationZoneWrapper(gym.ObservationWrapper):
    """
    to be used with class ZonesEnv
    """
    def __init__(self, env, zone_size_x, zone_size_y, blurred, gray_scale = False):
        super(gym.ObservationWrapper, self).__init__(env)
        self.zone_size_x = zone_size_x
        self.zone_size_y = zone_size_y
        self.blurred = blurred
        self.gray_scale = gray_scale
        
    def render(self, size = (512, 512), mode = 'human', close = False, blurred_render = False):
        if hasattr(self.env.__class__, 'render_scaled'): # we call render_scaled function from gridenvs
            return self.env.render_scaled(size, mode, close)
         
        else: # we scale the image from other environment (like Atari)
            img = self.env.env.ale.getScreenRGB2()
            if blurred_render:
                img = self.make_downsampled_image(img)
                
            if self.gray_scale:
                img = self.make_gray_scale(img)
                
            img_resized = cv2.resize(img, size, interpolation=cv2.INTER_NEAREST)
                
            if mode == 'rgb_array':
                return img
            
            elif mode == 'human':
                from gym.envs.classic_control import rendering
                if self.env.env.viewer is None:
                    self.env.env.viewer = rendering.SimpleImageViewer()
                    
                self.env.env.viewer.imshow(img_resized)
                return self.env.env.viewer.isopen

    def make_downsampled_image(self, image):
        len_y = len(image) # with MontezumaRevenge-v4 : 160
        len_x = len(image[0]) # with MontezumaRevenge-v4 : 210
        if (len_x % self.zone_size_x == 0) and (len_y % self.zone_size_y == 0):
            downsampled_size = (len_x // self.zone_size_x , len_y // self.zone_size_y)
            img_blurred = cv2.resize(image, downsampled_size, interpolation=cv2.INTER_AREA) # vector of size "downsampled_size"
            return img_blurred
        
        else:
            raise Exception("The gridworld " + str(len_x) + "x" + str(len_y) +  " can not be fragmented into zones " + str(self.zone_size_x) + "x" + str(self.zone_size_y))
            
    def observation(self, observation):
        #instead of returning a nested array, returns a *blurred*, *nested* *tuple* : img_blurred_tuple. Returns also the hashed obersvation.
        img = observation.copy()
        if not(self.blurred or self.gray_scale):
            return observation

        else:
            if self.blurred:
                img = self.make_downsampled_image(img)

            if self.gray_scale:
                img = self.make_gray_scale(img)
            
            # transform the observation in tuple
            img_tuple = tuple(tuple(tuple(color) for color in lig) for lig in img)
            observation_tuple = tuple(tuple(tuple(color) for color in lig) for lig in observation)
            return hash(observation_tuple), hash(img_tuple)

    def make_gray_scale(self, image):
        for i in range(len(image)):
            for j in range(len(image[0])):
                rgb = image[i][j]
                gray_level = (255 * 3) // NUMBER_GRAY_COLORS
                sum_rgb = (sum(rgb) // gray_level) * gray_level
                image[i][j] = [sum_rgb] * 3
                
        return image

"""
env = ObservationZoneWrapper(gym.make(ENV_NAME),  zone_size_x = 1, zone_size_y = 1, blurred = True)
obs = env.reset()

viewer = rendering.SimpleImageViewer()
viewer.imshow(obs)

time.sleep(5)
"""