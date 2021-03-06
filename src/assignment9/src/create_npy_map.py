import numpy as np
import os
from matplotlib import pyplot as plt

def read_points(map_file, offset_x=0.0, offset_y=0.0):
    """
    Reads a file with the map data in the RNDF Format
    :return: generator of x, y position tuples
    """
    resolution =0.01
    Width=3.85
    Length=5.67
    ar = np.zeros((240,320))
    # detect waypoints x.y.z and store latitude / longitude as x / y
    with open(map_file) as m_file:
        for line in m_file:
            x, y = line.split('\t')[1:3]
            #ar[float(x) + offset_x, float(y) + offset_y]=1
            ar[int(float(y)/Width*ar.shape[0]) , int(float(x)/Length*ar.shape[1])]=1
    #ndimage.binary_dilation(ar)
    ar = ndimage.binary_dilation(ar, iterations=1).astype(ar.dtype)
    np.save("map.npy",ar)
 
#read_points("new_map.txt","r")
map_mat = np.load("map.npy")
plt.imshow(map_mat)
plt.show()
