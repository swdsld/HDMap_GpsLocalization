from utils import Utm
import shapefile as sp
import numpy as np
from matplotlib import pyplot as plt

class HDMap:
    def __init__(self):
        self.X_MIN = 302350
        self.X_MAX = 302690
        self.Y_MIN = 4123500
        self.Y_MAX = 4124690

        self.shapelist = {}

    def utm_transform(self, points):
        points[:, 0], points[:, 1] = Utm.to_latlon(points[:, 0], points[:, 1], 52, 'T')
        return points

    def read_map(self, map_dir, map_name):
        # 정밀지도
        shp_file = map_dir + '/' + map_name + ".shp"
        dbf_file = map_dir + '/' + map_name + ".dbf"
        shx_file = map_dir + '/' + map_name + ".shx"

        shp = open(shp_file, 'rb')
        dbf = open(dbf_file, 'rb')
        shx = open(shx_file, 'rb')
        shape_file = sp.Reader(shp=shp, shx=shx, dbf=dbf)

        shapes = []
        count = -1
        for shape in shape_file.shapes():
            points = np.array(shape.points)
            if np.sum((np.min(points, axis=0) > [self.X_MIN, self.Y_MIN]) & (np.max(points, axis=0) < [self.X_MAX, self.Y_MAX])) == 2:
                points = self.utm_transform(points)
                shapes.append(points)
                count += 1
            else:
                continue

        self.shapelist[map_name] = shapes

    def plot_map(self, map_name, color, tag=False):
        for count, points in enumerate(self.shapelist[map_name]):
            if points.shape[0] > 1:  # line type
                plt.plot(points[:, 1], points[:, 0], color=color)
            else:  # point type
                plt.scatter(points[:, 1], points[:, 0], color=color, s=10)

            if tag is True:
                mid = points.shape[0] // 2
                plt.annotate(str(count), xy=(points[mid, 1], points[mid, 0]))

    def save_map_csv(self, shapes, filename):
        file = open(filename + '.csv', 'w')
        for i, shape in enumerate(shapes):
            for point in shape:
                file.write(str(i) + ',' + str(point[0]) + ',' + str(point[1]) + '\n')
        file.close()