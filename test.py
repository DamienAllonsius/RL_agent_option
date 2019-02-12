import sys, unittest
sys.path.append('gridenvs')
from gridenvs.utils import Point, Direction
from agent.q import Q
from agent.option import Option, OptionExplore
from agent.agent import AgentOption
from variables import *
"""
class OptionTest(unittest.TestCase):
    def test_eq_option_explore(self):
        opt_1 = OptionExplore(Point(0,0))
        opt_2 = OptionExplore(Point(0,0))
        self.assertEqual(opt_1, opt_2)

    def test_act_option_explore(self):
        opt_1 = OptionExplore(Point(0,0))
        action = opt_1.act()
        self.assertTrue(action in Direction.cardinal())

    def test_check_end_option_explore(self):
        opt_1 = OptionExplore(Point(0,0))
        self.assertFalse(opt_1.check_end_option(Point(0,0)))
        self.assertTrue(opt_1.check_end_option(Point(10,0)))

    def test_add_primitive_actions(self):
        option_1 = Option(position = Point(0,0), initial_state = Point(0,0), terminal_state = Point(1,1))
        option_1.add_primitive_actions(Point(0,0))
        cardinal = Direction.cardinal()
        self.assertEqual(option_1.q.q_dict, {Point(0,0) : {cardinal[0] : 0, cardinal[1] : 0, cardinal[2] : 0, cardinal[3] : 0}})

        with  self.assertRaises(Exception):
            option_1.add_primitive_actions(Point(1,1))

"""                                    
class QTests(unittest.TestCase):
    def test_add_state(self):
        q = Q(Point(0,0))
        q.add_state(Point(0,1))
        self.assertEqual(q.q_dict, {Point(0,0) : {}, Point(0,1) : {}})
        q.add_state(Point(0,0))
        self.assertEqual(q.q_dict, {Point(0,0) : {}, Point(0,1) : {}})
        
    def test_add_action_to_state(self):
        q = Q(Point(0,0))
        q.add_action_to_state(Point(0,0), Point(2,2))
        self.assertEqual(q.q_dict, {Point(0,0) : {Point(2,2) : 0}})

        with  self.assertRaises(Exception):
            q.add_action_to_state(Point(0,3), Point(0,1))
            
        q.add_action_to_state(Point(0,0), Point(4,4))
        self.assertEqual(q.q_dict, {Point(0,0) : {Point(2,2) : 0, Point(4,4) : 0}})

        q.add_action_to_state(Point(0,0), Point(4,4))
        self.assertEqual(q.q_dict, {Point(0,0) : {Point(2,2) : 0, Point(4,4) : 0}})
    
    def test_add_action_to_state_with_option(self):
        position_1 = Point(0,0)
        zone_1 = Point(0,0)
        terminal_zone_1 = Point(1,0)
        terminal_zone_2 = Point(5,5)        
        option_1 = Option(initial_state = zone_1, terminal_state = terminal_zone_1, position = position_1, grid_size_option = Point(1,1), play = False)
        option_2 = Option(initial_state = zone_1, terminal_state = terminal_zone_1, position = position_1, grid_size_option = Point(1,1), play = False)
        option_3 = Option(initial_state = zone_1, terminal_state = terminal_zone_2, position = position_1, grid_size_option = Point(1,1), play = False)
        self.assertTrue(option_1 == option_2)
        self.assertFalse(option_1 == option_3)

        q = Q(zone_1)
        q.add_state(zone_1)
        q.add_action_to_state(zone_1, option_1)
        q.add_action_to_state(zone_1, option_2)
        q.add_action_to_state(zone_1, option_3)
        self.assertEqual(q.q_dict, {zone_1 : {option_1 : 0, option_3 : 0}})
            
    def test_find_best_action(self):
        q = Q(Point(0,0))
        zone_1 = Point(0,0)
        terminal_zone_1 = Point(1,0)
        option =  OptionExplore(initial_state = zone_1)
        
        q.add_action_to_state(Point(0,0), Point(0,0))
        q.q_dict[Point(0,0)][Point(0,0)] = 2
        
        q.add_action_to_state(Point(0,0), Point(0,1))
        q.q_dict[Point(0,0)][Point(0,1)] = 4
        
        q.add_action_to_state(Point(0,0), option)
        q.q_dict[Point(0,0)][option] = 77
        
        q.add_action_to_state(Point(0,0), Point(0,3))
        q.q_dict[Point(0,0)][Point(0,3)] = 3

        q.add_state(Point(10,10))

        best_reward, best_action = q.find_best_action(Point(0,0))
        self.assertEqual(best_reward, 77)
        self.assertEqual(best_action, option)
        with self.assertRaises(Exception):
            q.find_best_action(Point(10,10))  
        with self.assertRaises(Exception):
            q.find_best_action(Point(4,4))
        
    def test_find_best_action_with_options(self):
        q = Q(Point(0,0))
        agent = AgentOption(Point(0,0),Point(0,0), grid_size_option = Point(1,1), play = False)
        q.add_action_to_state(Point(0,0), agent.explore_option)
        q.q_dict[Point(0,0)][agent.explore_option] = 2

        best_reward, best_action = q.find_best_action(Point(0,0))
        self.assertEqual(best_reward, 2)
        self.assertEqual(best_action, agent.explore_option)

        opt = Option(position = Point(0,0), initial_state = Point(0,1), terminal_state = Point(2,2), grid_size_option = Point(1,1), play = False)
        q.add_state(Point(0,1))
        q.add_action_to_state(Point(0,1), opt)
        self.assertEqual(0, q.q_dict[Point(0,1)][opt])


    def test_is_actions(self):
        q = Q(Point(0,0))
        q.add_action_to_state(Point(0,0), Point(2,2))
        q.add_state(Point(1,1))
        self.assertTrue(q.is_actions(Point(0,0)))
        self.assertFalse(q.is_actions(Point(1,1)))
    
    def test_update_q_dict(self):

        state = Point(0,0) 
        new_state = Point(0,1)
        action = Option(position = state, initial_state = state, terminal_state = new_state, grid_size_option = Point(1,1), play = False)
        reward = 12
        q = Q(state)

        q.update_q_dict(state, new_state, action, reward)
        self.assertEqual(q.q_dict, {state : {action : LEARNING_RATE * reward}, new_state : {}})

        q.add_action_to_state(new_state, new_state)
        state_action_value = 100
        q.q_dict[new_state][new_state] = state_action_value
        q.update_q_dict(state, new_state, action, reward)

        q_predict =  {state : {action : (1-LEARNING_RATE) * LEARNING_RATE * reward + LEARNING_RATE * (reward + state_action_value)}, new_state : {new_state : state_action_value}}
        self.assertEqual(q.q_dict, q_predict)
        
if __name__ == '__main__':
    unittest.main()
#    q_tests = QTests()
#    q_tests.test_add_state()
