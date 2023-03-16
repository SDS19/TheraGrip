import math
import numpy as np
import similaritymeasures
from matplotlib import pyplot as plt


""" 
    Title: Nils Hoppe's paper P118 Geschwindigkeitsverlauf
    Author: Yukai 
    Date: 16.03.2023 
"""


def mod_velocity_curve(x):
    y = -5.83397691012945e-14 * pow(x, 9) + 4.01458396693356e-11 * pow(x, 8) - 9.62482037096911e-9 * pow(x, 7) + \
        1.06977262917339e-6 * pow(x, 6) - 5.68239363212274e-5 * pow(x, 5) + 0.00125022968775769 * pow(x, 4) - \
        0.0124822800434351 * pow(x, 3) + 0.531322885004075 * pow(x, 2) - 0.240497493514033 * x + 0.234808880863676
    return y / 2


def show_mod_velocity_curve(n):
    x = list(range(n + 1))
    y = get_velocity_list(n)

    fig, ax = plt.subplots()
    ax.grid()
    ax.plot(x, y, color='red')
    ax.set(xlabel='Movement Progress (%)', ylabel='Velocity (mm/s)', title='Modified Velocity Curve')

    plt.show()


# display the interpolation curve and parameter of each interpolation point
def show_interpolation_curve(n, start_point, end_point):
    p_list = get_position_list(n, start_point, end_point)
    v_list = get_velocity_list(n)
    t_list = get_time_list(v_list, start_point, end_point)
    a_list = get_acceleration_list(v_list, t_list)

    x = list(range(len(v_list)))

    fig, ax = plt.subplots()
    ax.grid()
    ax.plot(x, v_list, color='red')
    ax.set(xlabel='Movement Progress (%)', ylabel='Velocity (mm/s)', title='Velocity Curve with ' + str(n) + ' Interpolation-points' + '  ' + str(p_list[0]) + ' -> ' + str(p_list[-1]))

    for i, j, k, t in zip(p_list, v_list, a_list, t_list):
        if i != 0:
            ax.annotate('p = ' + str(i[0]) + ' mm, ' + str(i[1]) + ' mm\n' +
                        'v = ' + str(round(j, 2)) + ' mm/s\n' +
                        'a = ' + str(round(k, 2)) + ' mm^2/s\n' +
                        't = ' + str(t) + ' s',
                        xy=(v_list.index(j), j),
                        xytext=(v_list.index(j), j - 20))

    plt.show()


""" ******************** position (mm) ******************** """


# get position of each interpolation point
def get_position_list(n, start_point, end_point):
    start_x = start_point[0]
    start_y = start_point[1]

    end_x = end_point[0]
    end_y = end_point[1]

    d_x = end_x - start_x
    d_y = end_y - start_y

    s_x = d_x / n  # n: sample number = segment number
    s_y = d_y / n

    p_list = []
    for i in range(n + 1):
        position = [round(start_x + i * s_x, 2), round(start_y + i * s_y, 2)]
        p_list.append(position)

    return p_list


""" ******************** velocity (mm/s) ******************** """


# get velocity of each interpolation point
def get_velocity_list(n):
    v_list = []
    v_interval = 100 / n
    for i in range(n + 1):  # n+1 => symmetrical
        v_list.append(mod_velocity_curve(i * v_interval))
    v_list[0] = v_list[-1] = 0  # border condition
    return v_list


# get velocity list in x and y axis (x^2 + y^2 = v^2)
def get_xy_velocity_list(n, start_point, end_point):
    start_x = start_point[0]
    start_y = start_point[1]

    end_x = end_point[0]
    end_y = end_point[1]

    d_x = abs(end_x - start_x)  # distance in x axis
    d_y = abs(end_y - start_y)  # distance in y axis

    x_list = []
    y_list = []
    v_list = get_velocity_list(n)

    if d_x == 0:
        for v in v_list:
            x_list.append(0)
            y_list.append(v)
    elif d_y == 0:
        for v in v_list:
            x_list.append(v)
            y_list.append(0)
    else:
        deg = math.degrees(math.atan(d_y / d_x))
        for v in v_list:
            x_list.append(round(v * math.cos(math.radians(deg)), 2))
            y_list.append(round(v * math.sin(math.radians(deg)), 2))

    return [x_list, y_list, v_list]


def to_byte(x):  # factor
    return list(int(x).to_bytes(4, byteorder='little', signed=True))


def negNumToFourByte(num):  # check negative num 23.02
    # byte_list = [255, 255, 255, 255]
    num = abs(num)
    byte_list = to_byte(num)
    for i in range(0, 4):
        byte_list[i] = 255 - byte_list[i]
    return byte_list


""" ******************** time (s) ******************** """


# time = distance / mean(velocity)
def get_time_list(v_list, start_point, end_point):
    n = len(v_list) - 1

    start_x = start_point[0]
    start_y = start_point[1]

    end_x = end_point[0]
    end_y = end_point[1]

    d_x = abs(end_x - start_x)
    d_y = abs(end_y - start_y)

    d = np.sqrt(d_x ** 2 + d_y ** 2)
    s = d / n  # segment distance

    t_list = []
    for i in range(1, len(v_list)):
        v = (v_list[i - 1] + v_list[i]) / 2
        t_list.append(round((s / v), 2))

    return t_list


""" ******************** acceleration (mm^2/s) ******************** """


# acceleration = abs(velocity) / time
def get_acceleration_list(v_list, t_list):
    a_list = [0]
    for i in range(1, len(v_list)):
        dv = abs(v_list[i] - v_list[i - 1])
        dt = t_list[i - 1]
        a_list.append(round(dv / dt))
    return a_list





# def diff_5(v_x, v_y):
#     y1 = get_velocity_list(100)
#     y2 = get_v_list(v_x, v_y)
#
#     c0 = np.trapz(y1[0:20], dx=1)
#     l0 = np.trapz(y2[0:2], dx=20)
#
#     c1 = np.trapz(y1[20:40], dx=1)
#     l1 = np.trapz(y2[1:3], dx=20)
#
#     c2 = np.trapz(y1[40:60], dx=1)
#     l2 = np.trapz(y2[2:4], dx=20)
#
#     c3 = np.trapz(y1[60:80], dx=1)
#     l3 = np.trapz(y2[3:5], dx=20)
#
#     c4 = np.trapz(y1[80:100], dx=1)
#     l4 = np.trapz(y2[4:6], dx=20)
#
#     a0 = c0 - l0
#     a1 = c1 - l1
#     a2 = c2 - l2
#     a3 = c3 - l3
#     a4 = c4 - l4
#
#     area = a0 + a1 + a2 + a3 + a4
#     abs_area = abs(a0) + abs(a1) + abs(a2) + abs(a3) + abs(a4)
#
#     print(a0, c0, l0)
#     print(a1, c1, l1)
#     print(a2, c2, l2)
#     print(a3, c3, l3)
#     print(a4, c4, l4)
#
#     print('area: ' + str(area))
#     print('abs_area: ' + str(abs_area))

def v_to_byte(v_list, forward):
    row = len(v_list)
    velo_mat = np.arange(row * 4).reshape(row, 4)

    if forward:
        for i in range(0, row):
            velo_mat[i] = negNumToFourByte(v_list[i])
    else:
        for i in range(0, row):
            velo_mat[i] = to_byte(v_list[i])

    velo_mat[0] = [0, 0, 0, 0]
    velo_mat[row - 1] = [0, 0, 0, 0]

    return velo_mat


def a_to_byte(a_list):
    row = len(a_list)
    acc_mat = np.arange(row * 4).reshape(row, 4)
    for i in range(0, row):
        acc_mat[i] = to_byte(abs(a_list[i]))
    return acc_mat


def get_v_a_matrix(v_byte, a_byte):
    return np.hstack((v_byte, a_byte))


def direction(start, end):
    return True if start >= end else False

""" ******************** difference between real curve and theoretical curve ******************** """


def get_v_list(v_x, v_y):
    v_list = []
    for i in range(len(v_x)):
        v_list.append(math.sqrt(v_x[i] ** 2 + v_y[i] ** 2))
    return v_list


def velocity_plot(v_x, v_y):
    n = len(v_x) - 1

    x = np.arange(0, 101, 1)  # [0, 1, .., 99, 100] len: 101
    y = get_velocity_list(100)  # len: 101

    x1 = np.arange(0, 101, 100 / n)
    y1 = []
    for i in range(n + 1):
        y1.append(math.sqrt(v_x[i]**2 + v_y[i]**2))
    print(x1)
    print(y1)

    fig, ax = plt.subplots()
    ax.grid()
    ax.plot(x, y, label='target velocity', color='orange')
    ax.plot(x1, y1, label='real velocity', color='royalblue', marker='.')
    plt.fill(np.append(x, x1[::-1]), np.append(y, y1[::-1]), 'lightgrey')
    ax.set(xlabel='Movement Progress [%]', ylabel='Velocity [mm/s]', title="Interpolation Points: " + str(n) +
                                                                           "\nDistance X: 350 mm, Y: 250 mm")
    ax.legend()
    plt.show()


def get_diff(v_x, v_y):
    n = len(v_x) -1
    d = int(100 / n)

    y1 = get_velocity_list(100)  # len: 101
    y2 = get_v_list(v_x, v_y)
    print('y2: ', len(y2), y2)

    x1 = np.arange(0, 101, 1)  # [0, 1, ..., 100]
    exp_data = np.zeros((101, 2))  # [[x0, y0], [x1, y1] ...]
    exp_data[:, 0] = x1
    exp_data[:, 1] = y1

    x2 = np.arange(0, 101, d)
    num_data = np.zeros((len(x2), 2))
    num_data[:, 0] = x2
    num_data[:, 1] = y2
    print(num_data)

    diff = similaritymeasures.area_between_two_curves(exp_data, num_data)
    print('area: ' + str(diff))

    df = similaritymeasures.frechet_dist(exp_data, num_data)
    print('Discrete Frechet distance: ' + str(df))


if __name__ == '__main__':
    # n = 5
    # start_point = [0, 0]
    # end_point = [350, 250]
    #
    # show_mod_velocity_curve(100)
    #
    # show_interpolation_curve(n, start_point, end_point)
    #
    # d_x = abs(end_point[0] - start_point[0])
    # d_y = abs(end_point[1] - start_point[1])
    #
    # p_list = get_position_list(n, start_point, end_point)
    # print('p: ' + str(p_list))
    #
    # v_x_y_list = get_xy_velocity_list(n, start_point, end_point)
    # v_x_list = v_x_y_list[0]
    # v_y_list = v_x_y_list[1]
    # v_list = v_x_y_list[2]
    # print('v: ' + str(v_list))
    # print('vx: ' + str(v_x_list))
    # print('vy: ' + str(v_y_list))

    # v_x_byte = v_to_byte(v_x_list, direction(start_point[0], end_point[0]))
    # v_y_byte = v_to_byte(v_y_list, direction(start_point[1], end_point[1]))
    # print(v_x_byte)
    # print(v_y_byte)
    #
    # t_list = get_time_list(v_list, start_point, end_point)
    # print('t: ' + str(t_list))
    #
    # a_x_list = get_acceleration_list(v_x_list, t_list)
    # a_y_list = get_acceleration_list(v_y_list, t_list)
    # print('ax: ' + str(a_x_list))
    # print('ay: ' + str(a_y_list))
    #
    # a_x_byte = a_to_byte(a_x_list)
    # a_y_byte = a_to_byte(a_y_list)
    # print(a_x_byte)
    # print(a_y_byte)
    #
    # x_matrix = get_v_a_matrix(v_x_byte, a_x_byte)
    # print(x_matrix)

    v_x = [0.0, 30.64, 7.34, 39.3, 104.67, 128.85, 195.61, 191.51, 174.32, 146.49, 87.02, 93.9, 42.9, 81.8, 29.33, 0]
#[0.0, 34.83, 34.65, 46.92, 117.6, 159.75, 144.63, 151.18, 159.06, 114.12, 103.91, 68.91, 82.61, 75.81, 14.62, 0.0, 33.48, 7.25, 54.28, 109.3, 130.1, 191.76, 164.12, 143.79, 143.68, 111.19, 57.79, 72.29, 27.52, 20.2]
#[ 0.0, 1.81, 34.45, 61.42, 94.18, 152.07, 165.88, 175.36, 172.96, 125.24, 108.97, 79.86, 58.17, 37.27, 49.1, 0.0, 2.0, 32.01, 65.36, 98.83, 129.88, 158.08, 183.06, 165.48, 150.5, 95.37, 76.28, 51.19, 39.84, 39.03]
    v_y = [0.0, 2.62, 31.69, 62.21, 115.14, 128.52, 159.19, 161.76, 163.19, 143.98, 112.64, 81.71, 64.32, 39.78, 43.12, 0]

    velocity_plot(v_x, v_y)
    get_diff(v_x, v_y)

    # 5
    # sample 1: area 1980.5465454807436 distance 76.61197566151633
    # sample 2: area 1779.0460433478029 distance 84.65293407347012
    # sample 3: area 3340.5461165714783 distance 118.47558881042534

    # 10
    # sample 1: area 1990.2924229120895 distance 48.78699972507088
    # sample 2: area 1667.4068160045063 distance 53.794254240344024
    # sample 3: area 1779.4606680655522 distance 37.273599448578786

    # 15
    # sample 1: area 1990.2924229120895 distance 48.78699972507088
    # sample 2: area 1667.4068160045063 distance 53.794254240344024
    # sample 3: area 1779.4606680655522 distance 37.273599448578786
