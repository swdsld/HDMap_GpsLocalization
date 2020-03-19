from GpsLocalization import GpsLocalization
from utils import BGenerator as Bg
import matplotlib.pyplot as plt
from tqdm import trange
import utils.Utm as utm
import numpy as np
gps = GpsLocalization()
gps.CURVE_THRESHOLD = 0.995
for k in trange(162):
    for i, pt in enumerate(gps.lane_shape[k]):
        if i % 3 == 0:
            curve = gps.get_lane_curvature(k, i)
            if curve == 'straight':
                color = 'black'
                s = 1
            elif curve == 'left':
                color = 'red'
                s = 10
            elif curve == 'right':
                color = 'blue'
                s = 10
            plt.scatter(pt[1], pt[0], s=s, c=color)
plt.show()

#
# gps = GpsLocalization()
#
# plt.figure(1)
# # gps.hdmap.plot_map(gps.SHAPE_FILE_LIST[2], gps.COLOR_LIST[2], tag=True)
# # gps.hdmap.plot_map(gps.SHAPE_FILE_LIST[1], gps.COLOR_LIST[1], tag=True)
# gps.hdmap.plot_map(gps.SHAPE_FILE_LIST[0], gps.COLOR_LIST[0], tag=False)
# # plt.pause(0.1)
# from scipy import interpolate
# f = open('map_data/route.txt')
# route = f.read()
# route = route.split(',')
# route = [int(i) for i in route]
# for i in range(0, len(route) - 1):
#     plt.plot(gps.lane_shape[route[i]][:, 1], gps.lane_shape[route[i]][:, 0], color='blue')
#     d = utm.latlon_dist(gps.lane_shape[route[i]][-1], gps.lane_shape[route[i+1]][0])
#     if d > 0.5:
#         plt.plot([gps.lane_shape[route[i]][-1, 1], gps.lane_shape[route[i+1]][0, 1]], [gps.lane_shape[route[i]][-1, 0], gps.lane_shape[route[i+1]][0, 0]], color='darkgreen')
#         # print(np.sum(gps.tangent_velocities[route[i]][-1] * gps.tangent_velocities[route[i+1]][1]))
#         if 0 < np.sum(gps.tangent_velocities[route[i]][-1] * gps.tangent_velocities[route[i+1]][1]) < 0.9:
#             plt.plot([gps.lane_shape[route[i]][-1, 1], gps.lane_shape[route[i + 1]][0, 1]],
#                      [gps.lane_shape[route[i]][-1, 0], gps.lane_shape[route[i + 1]][0, 0]], color='yellow')
#             xnew = np.linspace(gps.lane_shape[route[i]][-1, 1], gps.lane_shape[route[i + 1]][0, 1], 30)
#             t = interpolate.CubicSpline(np.array([gps.lane_shape[route[i]][-1, 1], gps.lane_shape[route[i + 1]][0, 1]]),
#                      np.array([gps.lane_shape[route[i]][-1, 0], gps.lane_shape[route[i + 1]][0, 0]]), bc_type=((2, 0.0), (2, 0.0)))
#             t = t(xnew)
#             plt.plot(xnew, t, color='black')
#
#             print(np.cross(gps.tangent_velocities[route[i]][-1], gps.tangent_velocities[route[i + 1]][1]))
# plt.show()
