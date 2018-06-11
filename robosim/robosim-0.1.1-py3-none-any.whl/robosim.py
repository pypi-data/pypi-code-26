from robosim.elements.map import Map
from robosim.elements.obstacle import Obstacle
from robosim.elements.robot import Robot
from robosim.game.engine import Engine
from robosim.game.engine_event import EngineEvent

# App information
VERSION = 0.1
ROBOSIM_TITLE = "RoboSim v.{} by Lukasz Zmudzinski | zmudzinski.me".format(VERSION)

class RoboSim:
    def __init__(self, map, multipath=True):
        self.map = map
        self.path = []        
        self.robots = []        
        self.default_size = 30  # Keeps the default drawing size
        self.obstacles = self.__create_obstacles()
        self.start = False
        self.multipath = multipath

    def __create_obstacles(self):
        """Creates obstacle objects from map data"""
        result = []
        generated_map = self.map.generate_map()
        for row in range(0, self.map.dimensions[0]):
            for column in range(0, self.map.dimensions[1]):
                if generated_map[row][column] == 1:
                    result.append(Obstacle(
                        position=(self.default_size * row, self.default_size * column),
                        size = (self.default_size, self.default_size)
                    ))
        return result

    def __check_for_user_input(self):
        """Checks for user input and returns False, when closing the app."""
        for event in Engine.get_events():
                engine_event, value = Engine.get_robosim_event(event)
                if engine_event == EngineEvent.START:
                    self.start = True
                if engine_event == EngineEvent.QUIT:
                    return False
                if engine_event == EngineEvent.LEFT_CLICK:
                    self.path.append(value)
                if engine_event == EngineEvent.RIGHT_CLICK:
                    if len(self.path) > 0:
                        # Create a new robot! Beep-Boop!
                        robot = Robot(value)
                        robot.path = self.path[:]
                        if self.multipath:
                            self.path = []
                        self.robots.append(robot)
        return True

    def add_obstacle(self, obstacle):
        """Adds an obstacle."""
        self.obstacles.append(obstacle)

    def update_robots(self):
        for robot in self.robots:
            robot.update_position()

    def run(self, title=ROBOSIM_TITLE, size_mult=20):
        """Runs the simulation."""        
        window_size = [self.map.dimensions[0] * self.default_size, self.map.dimensions[1] * self.default_size]
        screen, clock = Engine.start(window_size, title)    
        pygame_running = True

        # Let's run this thing!
        while pygame_running:
            # Check for user input.
            pygame_running = self.__check_for_user_input()

            # Update robot positions
            if self.start:
                self.update_robots()

            # Draw stuff on the map
            Engine.draw(screen, self.obstacles, self.robots, self.path)
            # Set framerate and update the screen.
            Engine.update_display(clock, 60)
        Engine.stop()
