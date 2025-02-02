from laspy.file import File
import numpy as np
from scipy import spatial
from scipy.spatial import *
import time
import sys
import math

class Point_Class():
    def __init__(self, index, x, y, z):
        self.index = index
        self.x = x
        self.y = y
        self.z = z
        # print(self.index, self.x, self.y, self.z)

class Grid_cell():
    def __init__(self):
        self.vegetation_flag = False
        self.mid_x = None
        self.mid_y = None
        self.point_array = []
        self.max_z = -float("INF")
        self.min_z = float("INF")
        self.delta_z = 0
    
    # def __init__(self, mid_x, mid_y):
    #     self.mid_x = mid_x
    #     self.mid_y = mid_y
    #     self.point_array = []
    
    def set_mid_x(self, mid_x):
        self.mid_x = mid_x

    def set_mid_y(self, mid_y):
        self.mid_y = mid_y
    
    def get_mid_x(self):
        return self.mid_x

    def get_mid_y(self):
        return self.mid_y

    # add points to kdTree
    def add_point(self, point):
        self.point_array.append(point)
        #########################################
        # ADD THIS IN?
        # if point.z > self.max_z:
        #     self.max_z = point.z
        # if point.z < self.min_z:
        #     self.min_z = point.z

        # self.delta_z = abs(self.max_z - self.min_z)
        # self.find_vegetation(100)

    def calculate_average(self):
        pass

    def find_vegetation(self, height):
        ##########################################
        # find max and min z of the cell
        # should I put this in the add_point function?
        self.min_z = float("INF")
        self.max_z = -float("INF")
        for point in self.point_array:
            if point.z < self.min_z:
                self.min_z = point.z
            if point.z > self.max_z:
                self.max_z = point.z
        print("delta z ", abs(self.max_z - self.min_z))
        if abs(self.max_z - self.min_z) > height:
            print("vegetation found")
            self.vegetation_flag = True




class Grid():
    def __init__(self, las_file, cell_size):
        #do we want to call this here?
        #will probably want to clean up once we get everything written
        self.las_file = las_file
        self.cell_size = cell_size
        
        print(self.las_file)
        self.base_file = File(self.las_file, mode = "rw")

        self.file_name = las_file.split('.')[0]
        print(self.file_name)
        self.grid = self.make_grid_by_cell(self.cell_size)
        # self.make_kd_tree()
        
    def make_grid_by_cell(self, size_of_cells):
        
        # Find out what the point format looks like.
        # print("point format")
        # pointformat = self.base_file.point_format
        # for spec in pointformat:
        #     print(spec.name)

        # # #Like XML or etree objects instead?
        # # a_mess_of_xml = pointformat.xml()
        # # an_etree_object = pointformat.etree()

        # # #It looks like we have color data in this file, so we can grab:
        # # blue = inFile.blue
        # print("\nheader format")
        # #Lets take a look at the header also.
        # headerformat = self.base_file.header.header_format
        # for spec in headerformat:
        #     print(spec.name)

        # print(self.base_file.header.max)
        # print(self.base_file.header.min)
        
        #################################################
        #pull in the base x array and base y array -- max. deltas, and then assigning points to grid cells
        #### USE LOWER CASE x, y, z on self.base_file
        base_x = self.base_file.x
        max_x = np.max(base_x)
        min_x = np.min(base_x)

        print("max x ", max_x)
        if round(max_x,2) != round(self.base_file.header.max[0], 2):
            print("x max coordinate mismatch", max_x, self.base_file.header.max[0])
        print("min x ", min_x)
        if round(min_x,2) != round(self.base_file.header.min[0], 2):
            print("x min coordinate mismatch")

        base_y = self.base_file.y
        max_y = np.max(base_y)
        min_y = np.min(base_y)

        print("max y ", max_y)
        if round(max_y,2) != round(self.base_file.header.max[1], 2):
            print("y max coordinate mismatch")
        print("min y ", min_y)
        if round(min_y,2) != round(self.base_file.header.min[1], 2):
            print("y min coordinate mismatch")

        base_z = self.base_file.z
        max_z = np.max(base_z)
        min_z = np.min(base_z)

        print("max z ", max_z)
        if round(max_z,2) != round(self.base_file.header.max[2], 2):
            print("y max coordinate mismatch")
        print("min z ", min_z)
        if round(min_z,2) != round(self.base_file.header.min[2], 2):
            print("y min coordinate mismatch")

        
        ################################################
        # calculate x and y length of scan to be used in determing grid spots
        delta_x = abs(max_x - min_x)
        delta_y = abs(max_y - min_y)
        area = float(delta_x)*float(delta_y)

        print("delta x", delta_x)
        print("delta y", delta_y) 
        print("area", area)

        #################################################
        # number of cells for gridding = delta / size_of_cell
        # cieling used so that we dont cut off the end of the grid/scan
        print("Size of cells ", size_of_cells, " by ", size_of_cells)

        number_of_cells_x = math.ceil(delta_x/size_of_cells)
        print("# x cells", number_of_cells_x)

        number_of_cells_y = math.ceil(delta_y/size_of_cells)
        print("# y cells", number_of_cells_y)


        #################################################
        # make grid
        self.grid = [[Grid_cell() for i in range(number_of_cells_y)] for j in range(number_of_cells_x)]
        print("Grid complete")

        #################################################
        # add points to grid cells
        for i in range(len(self.base_file.points)):
            if (i % 1000000) == 0:
                print(i, " of ", len(self.base_file.points), " points added to grid")


            grid_x = math.floor((base_x[i]-min_x)/size_of_cells)
            grid_y = math.floor((base_y[i]-min_y)/size_of_cells)
            try:
                point = Point_Class(i, base_x[i], base_y[i], base_z[i])
                self.grid[grid_x][grid_y].add_point(point)
                # print("point added to grid cell", grid_x, grid_y)
            except:
                print("exception adding point to grid cell", grid_x, grid_y, i)

        print("All points added to grid cells.")

        max_points = 0
        total = 0
        for i in range(len(self.grid)):
            for j in range(len(self.grid[0])):
                # print("# points ", len(self.grid[i][j].point_array))
                total += len(self.grid[i][j].point_array)
                if len(self.grid[i][j].point_array) > max_points:
                    max_points = len(self.grid[i][j].point_array)
                    max_i = i
                    max_j = j

        print('max number of points ', max_points)
        print("Total points in grid cells", total)

        self.grid[max_i][max_j].find_vegetation(10)
       
 
        
        """
        # x_pointer = min_x + grid_x_size/2
        # print("x pointer", x_pointer)
        # y_pointer = min_y + grid_y_size/2
        # print("y pointer", y_pointer)
        # mid_x = x_pointer
        # self.grid_cells = []
        # for i in range(int(number_of_cells)):
        #     mid_y = y_pointer
        #     for j in range(int(number_of_cells)):
        #         self.grid_cells.append(Grid_cell(mid_x, mid_y))
        #         # print("grid cell ", len(self.grid_cells), " ", self.grid_cells[-1].mid_x)
        #         # print("grid cell ", len(self.grid_cells), " ", self.grid_cells[-1].mid_y)
        #         mid_y += grid_y_size
        #     mid_x += grid_x_size

        
        # self.grid_cells = np.asarray(self.grid_cells)

        # mid_x_vec = np.vectorize(Grid_cell.get_mid_x, otypes=[object])
        # mid_y_vec = np.vectorize(Grid_cell.get_mid_y, otypes=[object])
        
        # mid_x_array = mid_x_vec(self.grid_cells)
        # mid_y_array = mid_y_vec(self.grid_cells)

        # mid_x_array = np.vstack(mid_x_array)
        # mid_y_array = np.vstack(mid_y_array)
        # self.mid_xy_array = [mid_x_array, mid_y_array]
        

        # print(self.mid_xy_array)
        """


    # def make_kd_tree(self):
    #     self.grid_cell_tree = spatial.cKDTree(self.mid_x_array)


        
###################################################
# # Ubuntu
# grid = Grid("../../las_data/points_clean.las", 500)

###################################################
# # Windows
# grid = Grid("../../../Documents/YC_LiftDeck_10Dec19.las", 100)
grid = Grid("../../../Documents/LiftDeck2.las", 1)



    # def make_grid(grid_size):
    #     pass

    # if __name__ == "__main__":
    #     grid = Grid(sys.argv[1], 0, 4)
        


