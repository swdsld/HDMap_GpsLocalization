from GpsLocalization import GpsLocalization
from utils import BGenerator as Bg
import matplotlib.pyplot as plt
import time
import numpy as np
import threading

commands = np.linspace(0, 30, 31, dtype=np.int32)
commands = [str(c) for c in commands]
g_command = None
prev_command = None
prev_lane = None
prev_point = None
cur_lane = None

def main(gps):
    global g_command
    global cur_lane
    global prev_lane
    global prev_point
    global prev_command

    for lat, long, on_lane, current_lane, current_lane_point, dist_from_lane, stop_sign, dist_from_stop in Bg.BGenerator(gps.lane_localization()):
        cur_lane = current_lane
        if on_lane is True:
            if g_command in commands:
                if prev_command is not None:
                    if prev_lane != current_lane:
                        print(current_lane)
                        gps.curve_data[prev_lane][prev_point:, 1] = int(prev_command)
                        gps.curve_data[current_lane][:current_lane_point, 1] = int(prev_command)
                    elif prev_lane == current_lane:
                        gps.curve_data[current_lane][prev_point:current_lane_point, 1] = int(prev_command)
                gps.curve_data[current_lane][current_lane_point, 1] = int(g_command)
                prev_lane = current_lane
                prev_point = current_lane_point
                prev_command = g_command
        if g_command == 'exit':
            break


def ipt_command():
    global g_command
    while True:
        g_command = input()
        time.sleep(0.001)
        if g_command == 'exit':
            break

if __name__ == '__main__':
    gps = GpsLocalization()
    worker1 = threading.Thread(target=main, args=(gps, ))
    worker2 = threading.Thread(target=ipt_command, args=())

    worker1.start()
    worker2.start()

    x = ['/', '-', '\\', '|']
    count = 0
    while True:
        print('\r{0} current command: {1}, current lane: {2}    '.format(x[count % 4], g_command, cur_lane), end='')
        if g_command == 'exit':
            break
        count += 1
        count %= 4

    gps.save_curve_data()
    worker1.join()
    worker2.join()
