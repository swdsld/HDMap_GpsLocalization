from GpsLocalization import GpsLocalization
from utils import BGenerator as Bg
import matplotlib.pyplot as plt
from tqdm import trange, tqdm
import utils.Utm as utm
import numpy as np
import os
import csv

gps = GpsLocalization()
gps.CURVE_THRESHOLD = 0.995
curve_data_path = './map_data/curve_data'
if os.path.isdir(curve_data_path) is False:
    os.mkdir(curve_data_path)

for k in trange(162):
    lane_file = open(curve_data_path + '/' + str(k) + '.csv', 'w')
    for i, pt in tqdm(enumerate(gps.lane_shape[k])):
        curve = gps.get_lane_curvature(k, i)
        if curve == 'straight':
            c = 2
        elif curve == 'left':
            c = 3
        elif curve == 'right':
            c = 4
        lane_file.write(str(i) + ',' + str(c) + '\n')
