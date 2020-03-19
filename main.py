from GpsLocalization import GpsLocalization
from utils import BGenerator as Bg
import matplotlib.pyplot as plt


gps = GpsLocalization()

plt.figure(1)
gps.hdmap.plot_map(gps.SHAPE_FILE_LIST[2], None, tag=True)
gps.hdmap.plot_map(gps.SHAPE_FILE_LIST[1], gps.COLOR_LIST[1], tag=False)
gps.hdmap.plot_map(gps.SHAPE_FILE_LIST[0], gps.COLOR_LIST[0], tag=False)
# plt.pause(0.1)
plt.show()
plt.figure(2)
count = 0
#
for lat, long, on_lane, current_lane, current_lane_point, dist_from_lane, stop_sign, dist_from_stop in Bg.BGenerator(gps.lane_localization()):

    print('====================================================================')
    print('latitude: ', lat)  # 위도 - -90 ~ 90
    print('longitude: ', long)  # 경도 - 0 ~ 360
    print('on lane ?: ', on_lane)  # 차선 위에 있는가? - True, False
    print('current lane id: ', current_lane)  # 현재 차선 id - 0 ~ 162
    print('current lane point: ', current_lane_point)  # 현재 위치에서 가장 가까운 차선 점 - 0 ~ N
    print('distance from lane: ', dist_from_lane)  # 현재 차선 중심으로부터의 거리 - 미터
    print('ahead stop sign id: ', stop_sign)  # 현재 차선 기준 정지선 id - 0 ~ 62
    print('distance from ahead stop sign: ', dist_from_stop)  # 정지선으로부터의 거리 - 미터

    lane_number, total_lane_quantity, left_lane, right_lane = gps.get_lane_number(current_lane)

    print('lane number: ', lane_number)  # 차선 번호 - 1 ~ M
    print('total lane: ', total_lane_quantity)  # 현 위치에서 총 차선 개수 - 1 ~ M
    print('left lane id: ', left_lane)  # 좌측 차선 id - 0 ~ 162
    print('right lane id: ', right_lane)  # 우측 차선 id - 0 ~ 162

    if on_lane is True:
        # curve = gps.get_lane_curvature(current_lane, current_lane_point)
        curve = gps.curve_data[current_lane][current_lane_point, 1]
    else:
        curve = None

    print('curve: ', curve)  # 회전 정보 - 차선 위일 경우 ('left', 'right', 'straight') 중 하나, 차선 밖일 경우 None
    if count == 10:
        # plt.clf()
        gps.hdmap.plot_map(gps.SHAPE_FILE_LIST[2], gps.COLOR_LIST[2], tag=True)
        gps.hdmap.plot_map(gps.SHAPE_FILE_LIST[1], gps.COLOR_LIST[1], tag=False)

        plt.plot(gps.lane_shape[current_lane][:, 1], gps.lane_shape[current_lane][:, 0], color='cyan')
        if stop_sign is not None:
            plt.plot(gps.stop_shape[stop_sign][:, 1], gps.stop_shape[stop_sign][:, 0], color='yellow')

        plt.scatter(long, lat, s=20, c='black')
        plt.pause(0.0001)
        count = 0
    count += 1

    # LANE 접근 방법
    # gps.lane_shape[LANE_ID] - LANE_ID 는 current_lane, left_lane, right_lane 세가지 있음



