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


def interpolation_plot(y_p, y_v, y_a, y_t, ylabel, title):  # finish
    x = list(range(len(y_v)))

    fig, ax = plt.subplots()
    ax.grid()
    ax.plot(x, y_v, color='red')
    ax.set(xlabel='interpolation point (n)', ylabel=ylabel, title=title + '  ' + str(y_p[0]) + ' -> ' + str(y_p[-1]))

    for i, j, k, t in zip(y_p, y_v, y_a, y_t):
        if i != 0:
            ax.annotate('p = ' + str(i[0]) + ' mm, ' + str(i[1]) + ' mm\n' +
                        'v = ' + str(round(j, 2)) + ' mm/s\n' +
                        'a = ' + str(round(k, 2)) + ' mm^2/s\n' +
                        't = ' + str(t) + ' s',
                        xy=(y_v.index(j), j),
                        xytext=(y_v.index(j), j - 20))

    plt.show()


# display the interpolation curve and parameter of each interpolation point
def show_interpolation_curve(n, start_point, end_point):
    p_list = get_position_list(n, start_point, end_point)
    v_list = get_velocity_list(n)
    t_list = get_time_list(v_list, start_point, end_point)
    a_list = get_acceleration_list(v_list, t_list)

    interpolation_plot(p_list, v_list, a_list, t_list, "Velocity (mm/s)", "Velocity Curve with " + str(n) + " interpolation-points")


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
    # ax.set(xlabel='Movement Progress [%]', ylabel='Velocity [mm/s]', title="Theoretische Geschwindigkeitskurve")
    ax.set(xlabel='Movement Progress [%]', ylabel='Velocity [mm/s]', title="Interpolation Points: " + str(n) +
                                                                           "\nDistance X: 100 mm, Y: 150 mm")
    ax.legend()
    plt.show()


def get_diff(v_x, v_y):
    n = len(v_x) - 1
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
#
#
# def diff_10(v_x, v_y):
#     y1 = get_velocity_list(100)
#     y2 = get_v_list(v_x, v_y)
#
#     c0 = np.trapz(y1[0:10], dx=1)
#     l0 = np.trapz(y2[0:2], dx=10)
#     a0 = c0 - l0
#
#     c1 = np.trapz(y1[10:20], dx=1)
#     l1 = np.trapz(y2[1:3], dx=10)
#     a1 = c1 - l1
#
#     c2 = np.trapz(y1[20:30], dx=1)
#     l2 = np.trapz(y2[2:4], dx=10)
#     a2 = c2 - l2
#
#     c3 = np.trapz(y1[30:40], dx=1)
#     l3 = np.trapz(y2[3:5], dx=10)
#     a3 = c3 - l3
#
#     c4 = np.trapz(y1[40:50], dx=1)
#     l4 = np.trapz(y2[4:6], dx=10)
#     a4 = c4 - l4
#
#     c5 = np.trapz(y1[50:60], dx=1)
#     l5 = np.trapz(y2[5:7], dx=10)
#     a5 = c5 - l5
#
#     c6 = np.trapz(y1[60:70], dx=1)
#     l6 = np.trapz(y2[6:8], dx=10)
#     a6 = c6 - l6
#
#     c7 = np.trapz(y1[70:80], dx=1)
#     l7 = np.trapz(y2[7:9], dx=10)
#     a7 = c7 - l7
#
#     c8 = np.trapz(y1[80:90], dx=1)
#     l8 = np.trapz(y2[8:10], dx=10)
#     a8 = c8 - l8
#
#     c9 = np.trapz(y1[90:100], dx=1)
#     l9 = np.trapz(y2[9:11], dx=10)
#     a9 = c9 - l9
#
#     area = a0 + a1 + a2 + a3 + a4 + a5 + a6 + a7 + a8 + a9
#     abs_area = abs(a0) + abs(a1) + abs(a2) + abs(a3) + abs(a4) + abs(a5) + abs(a6) + abs(a7) + abs(a8) + abs(a9)
#
#     print(a0, c0, l0)
#     print(a1, c1, l1)
#     print(a2, c2, l2)
#     print(a3, c3, l3)
#     print(a4, c4, l4)
#
#     print(a5, c5, l5)
#     print(a6, c6, l6)
#     print(a7, c7, l7)
#     print(a8, c8, l8)
#     print(a9, c9, l9)
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


if __name__ == '__main__':
    n = 5
    start_point = [0, 0]
    end_point = [350, 250]

    show_interpolation_curve(n, start_point, end_point)

    d_x = abs(end_point[0] - start_point[0])
    d_y = abs(end_point[1] - start_point[1])

    p_list = get_position_list(n, start_point, end_point)
    print('p: ' + str(p_list))

    v_x_y_list = get_xy_velocity_list(n, start_point, end_point)
    v_x_list = v_x_y_list[0]
    v_y_list = v_x_y_list[1]
    v_list = v_x_y_list[2]
    print('v: ' + str(v_list))
    print('vx: ' + str(v_x_list))
    print('vy: ' + str(v_y_list))

    v_x_byte = v_to_byte(v_x_list, direction(start_point[0], end_point[0]))
    v_y_byte = v_to_byte(v_y_list, direction(start_point[1], end_point[1]))
    print(v_x_byte)
    print(v_y_byte)

    t_list = get_time_list(v_list, start_point, end_point)
    print('t: ' + str(t_list))

    a_x_list = get_acceleration_list(v_x_list, t_list)
    a_y_list = get_acceleration_list(v_y_list, t_list)
    print('ax: ' + str(a_x_list))
    print('ay: ' + str(a_y_list))

    a_x_byte = a_to_byte(a_x_list)
    a_y_byte = a_to_byte(a_y_list)
    print(a_x_byte)
    print(a_y_byte)

    x_matrix = get_v_a_matrix(v_x_byte, a_x_byte)
    print(x_matrix)



    i = -100
    # print(to_four_byte(i))
    # print(to_byte1(i))

    # v_x = [0, 2.82, 12.27, 18.48, 29.61, 76.07, 106.1, 123.35, 127.13, 136.01, 140.31, 118.87, 93.66, 87.97, 78.82, 16.2, 15.27, 26.84, 43.18, 22.12, 0.91]
    # v_y = [0, 3.8, 7.61, 44.36, 78.46, 108.5, 146.9, 188.49, 195.31, 199.46, 205.58, 168.53, 141.38, 120.49, 96.75, 57.32, 39.92, 32.33, 12.34, 6.89, 0.45]
    #
    # velocity_plot(v_x, v_y)
    # get_diff(v_x, v_y)
