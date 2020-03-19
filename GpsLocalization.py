from utils import Utm, HDMap as map
import numpy as np
import csv
import os

class GpsLocalization:
    def __init__(self):
        self.SHAPE_FILE_DIR = './map_shapes'
        self.LANE_DATA_DIR = './map_data/lane_num2.csv'
        self.CURVE_DATA_DIR = './map_data/curve_data'

        self.SHAPE_FILE_LIST = ['A1_LANE', 'A2_STOP', 'A3_LINK', 'B1_SIGNAL_POINT']
        self.COLOR_LIST = ['red', 'darkgreen', 'blue', 'green']
        self.ON_LANE_THRESHOLD = 2
        self.STOP_LANE_PAIR_THRESHOLD = 0.3
        self.CURVE_THRESHOLD = 0.995

        self.hdmap = self.load_map_shape()
        self.gps_iter = self.gps_iterator()
        self.lane_shape = self.hdmap.shapelist['A3_LINK']
        self.stop_shape = self.hdmap.shapelist['A2_STOP']
        self.stop_lane_pair_list = self.stop_lane_pair(self.lane_shape, self.stop_shape)
        self.lane_num = self.load_lane_num()

        self.tangent_velocities = self.get_tangent_velocities()

        self.curve_data = self.load_curve_data()

    def load_map_shape(self):
        mymap = map.HDMap()
        for name, color in zip(self.SHAPE_FILE_LIST, self.COLOR_LIST):
            mymap.read_map(self.SHAPE_FILE_DIR, name)
        return mymap

    def load_lane_num(self):
        with open(self.LANE_DATA_DIR, 'r', encoding='utf-8-sig') as f:
            return np.array(list(csv.reader(f)), dtype=np.int32)

    def load_curve_data(self):
        curve_data = {}
        for curve_file in os.listdir(self.CURVE_DATA_DIR):
            with open(self.CURVE_DATA_DIR + '/' + curve_file) as f:
                curve_data[int(curve_file.split('.')[0])] = np.array(list(csv.reader(f)), dtype=np.int32)
        return curve_data

    def save_curve_data(self):
        for curve_file in os.listdir(self.CURVE_DATA_DIR):
            with open(self.CURVE_DATA_DIR + '/' + curve_file, 'w', newline='\n', encoding='utf-8') as f:
                csv.writer(f).writerows(self.curve_data[int(curve_file.split('.')[0])].tolist())

    @staticmethod
    def gps_iterator():  # gps iterator --> gps stream 부분, 수정필요
        gps_data = open('gps_data/INTEGRATED.txt')
        return gps_data.readlines()

    @staticmethod
    def parse_gps(point):  # gps parsing --> 수정 필요
        point = point.split(',')
        lat = Utm.min2deg(float(point[2]) / 100)
        long = Utm.min2deg(float(point[4]) / 100)
        return lat, long

    def stop_lane_pair(self, lane_shape, stop_shape):
        stop_lane_pair = []
        for i, stop in enumerate(stop_shape):
            for stop_point in stop:
                dist = []
                for lane in lane_shape:
                    dist.append(np.min(Utm.latlon_dist(lane, stop_point)))
                shortest_lane = np.argmin(dist)
                if np.min(dist) < self.STOP_LANE_PAIR_THRESHOLD:
                    if [i, shortest_lane] not in stop_lane_pair:
                        stop_lane_pair.append([i, shortest_lane])
        stop_lane_pair = np.array(stop_lane_pair)
        return stop_lane_pair

    def get_lane_number(self, lane_id):
        _, lane_group, lane_num, total_lane_num = self.lane_num[lane_id]
        lane_group = self.lane_num[np.where(self.lane_num[:, 1] == lane_group)[0]]

        right_lane_num = None
        left_lane_num = None
        if lane_num < total_lane_num:
            right_lane = np.where(lane_group[:, 2] == lane_num + 1)[0]
            if len(right_lane) > 0:
                right_lane_num = lane_group[right_lane, 0][0]
        if lane_num > 1:
            left_lane = np.where(lane_group[:, 2] == lane_num - 1)[0]
            if len(left_lane) > 0:
                left_lane_num = lane_group[left_lane, 0][0]

        return lane_num, total_lane_num, left_lane_num, right_lane_num

    @staticmethod
    def lane_tangent_velocity(l):
        dx_dt = np.gradient(l[:, 0])
        dy_dt = np.gradient(l[:, 1])
        velocity = np.array([[dx_dt[i], dy_dt[i]] for i in range(dx_dt.size)])
        ds_dt = np.sqrt(dx_dt * dx_dt + dy_dt * dy_dt)
        tangent = np.array([1 / (ds_dt + 1e-25)] * 2).transpose() * velocity

        return tangent

    def get_tangent_velocities(self):
        t = []
        for l in self.lane_shape:
            t.append(self.lane_tangent_velocity(l))
        return t

    def get_lane_curvature(self, lane_id, lane_point):
        interval = len(self.lane_shape[lane_id]) // 15 + 1
        curvature = 'straight'
        if len(self.lane_shape[lane_id]) > interval:
            t = self.tangent_velocities[lane_id]
            t = t[::interval, :]

            tp = t[:-1]
            tn = t[1:]
            cos = np.sum(tp * tn, axis=1)
            sin = np.cross(tp, tn, axis=1)
            lane_point_ = lane_point//interval
            lane_point_ = lane_point_ if lane_point_ < len(tp) else len(tp) - 1
            # print(cos[lane_point_])
            if 0 < cos[lane_point_] < self.CURVE_THRESHOLD:
                lr = np.sign(sin[lane_point_])
                curvature = 'right' if lr > 0 else 'left'

        return curvature

    def lane_localization(self):
        out_of_lane = True
        ahead_stop = None

        for point in self.gps_iter:  # gps iterator
            lat, long = self.parse_gps(point)
            # ==================================== find lane
            dist = []
            dist_idx = []
            for lane in self.lane_shape:
                dlist = Utm.latlon_dist(lane, [lat, long])
                min_dist_idx = np.argmin(dlist)
                min_dist = dlist[min_dist_idx]
                dist.append(min_dist)
                dist_idx.append(min_dist_idx)
            c_lane = np.argmin(dist)
            c_lane_idx = dist_idx[int(c_lane)]

            if dist[int(c_lane)] < self.ON_LANE_THRESHOLD:
                out_of_lane = False
            else:
                out_of_lane = True
            # ==================================== find lane end

            # ==================================== find stop sign and get distance
            if (out_of_lane is False) and (c_lane in self.stop_lane_pair_list[:, 1]):
                ahead_stop = self.stop_lane_pair_list[np.where(self.stop_lane_pair_list[:, 1] == c_lane)][0, 0]
                mid = self.stop_shape[ahead_stop].shape[0] // 2
                stop_dist = Utm.latlon_dist([lat, long],
                                [self.stop_shape[ahead_stop][mid, 0], self.stop_shape[ahead_stop][mid, 1]])
            else:
                ahead_stop = None
                stop_dist = None
            # ==================================== find stop sign and get distance end

            yield lat, long, not out_of_lane, c_lane, c_lane_idx, dist[int(c_lane)], ahead_stop, stop_dist

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    gps = GpsLocalization()

    plt.figure(1)
    gps.hdmap.plot_map(gps.SHAPE_FILE_LIST[2], gps.COLOR_LIST[2], tag=True)
    gps.hdmap.plot_map(gps.SHAPE_FILE_LIST[1], gps.COLOR_LIST[1], tag=True)
    gps.hdmap.plot_map(gps.SHAPE_FILE_LIST[0], gps.COLOR_LIST[0], tag=False)
    plt.show()