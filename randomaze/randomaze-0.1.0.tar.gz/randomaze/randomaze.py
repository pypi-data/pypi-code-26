class Maze():

    
    def __init__(self, len_x, len_y):

        import numpy as np

        self.len_x = len_x
        self.len_y = len_y        
        self.maze = np.zeros([self.len_x * self.len_y])

        self.player_x_coordinate = None
        self.player_y_coordinate = None
        self.goal_x_coordinate = None
        self.goal_y_coordinate = None
        self.pit_x_coordinate = None
        self.pit_y_coordinate = None

        #1: Player
        #2: Goal
        #3: Pit
        for i in range(1,4):
            self._place(i)

    
    def _place(self, item, m = None, n = None, is_replace = False):
        
        import numpy as np

        self.placement_confict = 1

        if ((m==None) & (n==None)):
            m, n = np.random.randint(0,self.len_x), np.random.randint(0,self.len_y)

        ind = self.twoD_to_oneD_loc(m, n) - 1

        while (self.placement_confict): 

            if (is_replace):
                self.maze[ind]=item
                self.placement_confict = 0
                   
            elif self.maze[ind]==0:
                self.maze[ind]=item
                self.placement_confict = 0

            m, n = np.random.randint(0,self.len_x), np.random.randint(0,self.len_y)
            ind = self.twoD_to_oneD_loc(m, n) - 1


    def print_maze(self):

        print(self.maze.reshape(self.len_y, self.len_x))


    def return_1D_maze(self):

        return self.maze


    def twoD_to_oneD_loc(self, m, n):
        """
        Returns 1D array index given X and Y coordinates for a 2-D format. All columns of a row must be filled first.
        """

        return (n-1)*self.len_x+m


    def oneD_to_twoD_loc(self, l):
        """
        Returns X and Y coordinates for a 2-D format. All columns of a row are filled first.
        """

        if (int(l%self.len_x) == 0):
            m = self.len_x
        else:
            m = int(l%self.len_x)

        if (int(l/self.len_x) == l/self.len_x):
            n = int(l/self.len_x)
        else:
            n = int(l/self.len_x)+1

        return m, n


    def find_loc(self, item):

        import numpy as np

        oneD_loc = np.argwhere(self.maze == item) + 1

        return self.oneD_to_twoD_loc(oneD_loc)



    def move(self, actions = None, take_random_action = False):
        """
        Actions:
        0: Left
        1: Right
        2: Up
        3: Down
        """

        import numpy as np

        action_impact = [[-1,0],[1,0],[0,-1],[0,1]]
        action_text = ['Left', 'Right', 'Up', 'Down']

        if(actions != None):
            max_action = np.argmax(actions)

        if(take_random_action):
            max_action = np.random.randint(0,4)

        print("Action: ", action_text[max_action])

        self.player_x_coordinate, self.player_y_coordinate = self.find_loc(1)
        self.goal_x_coordinate, self.goal_y_coordinate = self.find_loc(2)
        self.pit_x_coordinate, self.pit_y_coordinate = self.find_loc(3)

        self.player_new_x_coordinate, self.player_new_y_coordinate = np.add(np.array([self.player_x_coordinate, self.player_y_coordinate]),np.array(action_impact[max_action]))
        print("Old:", self.player_x_coordinate, self.player_y_coordinate)

        if ((self.player_new_x_coordinate > self.len_x) | (self.player_new_x_coordinate < 1) | (self.player_new_y_coordinate > self.len_y) | (self.player_new_y_coordinate < 1)):
            self.player_new_x_coordinate, self.player_new_y_coordinate = self.player_x_coordinate, self.player_y_coordinate
            # return "You Hit the Wall!"

        elif ((self.player_new_x_coordinate == self.goal_x_coordinate) & (self.player_new_y_coordinate == self.goal_y_coordinate)):
            return "Won!"

        elif ((self.player_new_x_coordinate == self.pit_x_coordinate) & (self.player_new_y_coordinate == self.pit_y_coordinate)):          
            return "Lost!"

        else:
            self._place(0, self.player_x_coordinate, self.player_y_coordinate, is_replace = True)
            self._place(1, self.player_new_x_coordinate, self.player_new_y_coordinate)

        print("New:", self.player_new_x_coordinate, self.player_new_y_coordinate)

