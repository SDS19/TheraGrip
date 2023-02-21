import math
import numpy as np
import similaritymeasures as similaritymeasures
from matplotlib import pyplot as plt


def mod_velocity_curve(x):
    y = -5.83397691012945e-14 * pow(x, 9) + 4.01458396693356e-11 * pow(x, 8) - 9.62482037096911e-9 * pow(x, 7) + \
        1.06977262917339e-6 * pow(x, 6) - 5.68239363212274e-5 * pow(x, 5) + 0.00125022968775769 * pow(x, 4) - \
        0.0124822800434351 * pow(x, 3) + 0.531322885004075 * pow(x, 2) - 0.240497493514033 * x + 0.234808880863676
    return y / 2


def get_velocity_list(n):
    v_list = []
    v_interval = 100 / n
    for i in range(n + 1):  # n+1 => symmetrical
        v_list.append(mod_velocity_curve(i * v_interval))
    v_list[-1] = 0  # border condition
    return v_list


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
                                                                           "\nDistance X: 100 mm, Y: 150 mm")
    ax.legend()
    plt.show()


def get_diff(v_x, v_y):
    n = len(v_x) - 1
    d = int(100 / n)
    y1 = get_velocity_list(100)  # len: 101

    y2 = get_v_list(v_x, v_y)
    print('y2: ', len(y2), y2)

    # area = 0
    # abs_area = 0
    # for i in range(n):
    #     a = d * i
    #     b = d * (i + 1)
    #     diff = np.trapz(y1[a:b], dx=1) - np.trapz(y2[i:i + 2], dx=d)
    #     area = area + diff
    #     abs_area += abs(diff)
    #
    # print('area: ' + str(area))
    # print('abs_area: ' + str(abs_area))

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


def diff_5(v_x, v_y):
    y1 = get_velocity_list(100)
    y2 = get_v_list(v_x, v_y)

    c0 = np.trapz(y1[0:20], dx=1)
    l0 = np.trapz(y2[0:2], dx=20)

    c1 = np.trapz(y1[20:40], dx=1)
    l1 = np.trapz(y2[1:3], dx=20)

    c2 = np.trapz(y1[40:60], dx=1)
    l2 = np.trapz(y2[2:4], dx=20)

    c3 = np.trapz(y1[60:80], dx=1)
    l3 = np.trapz(y2[3:5], dx=20)

    c4 = np.trapz(y1[80:100], dx=1)
    l4 = np.trapz(y2[4:6], dx=20)

    a0 = c0 - l0
    a1 = c1 - l1
    a2 = c2 - l2
    a3 = c3 - l3
    a4 = c4 - l4

    area = a0 + a1 + a2 + a3 + a4
    abs_area = abs(a0) + abs(a1) + abs(a2) + abs(a3) + abs(a4)

    print(a0, c0, l0)
    print(a1, c1, l1)
    print(a2, c2, l2)
    print(a3, c3, l3)
    print(a4, c4, l4)

    print('area: ' + str(area))
    print('abs_area: ' + str(abs_area))


def diff_10(v_x, v_y):
    y1 = get_velocity_list(100)
    y2 = get_v_list(v_x, v_y)

    c0 = np.trapz(y1[0:10], dx=1)
    l0 = np.trapz(y2[0:2], dx=10)
    a0 = c0 - l0

    c1 = np.trapz(y1[10:20], dx=1)
    l1 = np.trapz(y2[1:3], dx=10)
    a1 = c1 - l1

    c2 = np.trapz(y1[20:30], dx=1)
    l2 = np.trapz(y2[2:4], dx=10)
    a2 = c2 - l2

    c3 = np.trapz(y1[30:40], dx=1)
    l3 = np.trapz(y2[3:5], dx=10)
    a3 = c3 - l3

    c4 = np.trapz(y1[40:50], dx=1)
    l4 = np.trapz(y2[4:6], dx=10)
    a4 = c4 - l4

    c5 = np.trapz(y1[50:60], dx=1)
    l5 = np.trapz(y2[5:7], dx=10)
    a5 = c5 - l5

    c6 = np.trapz(y1[60:70], dx=1)
    l6 = np.trapz(y2[6:8], dx=10)
    a6 = c6 - l6

    c7 = np.trapz(y1[70:80], dx=1)
    l7 = np.trapz(y2[7:9], dx=10)
    a7 = c7 - l7

    c8 = np.trapz(y1[80:90], dx=1)
    l8 = np.trapz(y2[8:10], dx=10)
    a8 = c8 - l8

    c9 = np.trapz(y1[90:100], dx=1)
    l9 = np.trapz(y2[9:11], dx=10)
    a9 = c9 - l9

    area = a0 + a1 + a2 + a3 + a4 + a5 + a6 + a7 + a8 + a9
    abs_area = abs(a0) + abs(a1) + abs(a2) + abs(a3) + abs(a4) + abs(a5) + abs(a6) + abs(a7) + abs(a8) + abs(a9)

    print(a0, c0, l0)
    print(a1, c1, l1)
    print(a2, c2, l2)
    print(a3, c3, l3)
    print(a4, c4, l4)

    print(a5, c5, l5)
    print(a6, c6, l6)
    print(a7, c7, l7)
    print(a8, c8, l8)
    print(a9, c9, l9)

    print('area: ' + str(area))
    print('abs_area: ' + str(abs_area))


if __name__ == '__main__':
    v_x = [0, 1.92, 8.59, 8.89, 65.19, 53.7, 96.41, 102.24, 107.18, 120.47, 140.96, 127.37, 141.57, 121.8, 110.01, 103.8, 98.92, 66.79, 61.14, 20.4, 62.11, 13.44, 35.38, 29.56, 1.47, 0.29]
    v_y = [0, 2.61, 7.69, 29.49, 45.9, 69.45, 105.52, 143.72, 164.44, 172.74, 207.38, 196.98, 202.14, 198.64, 177.66, 132.74, 127.41, 97.46, 67.32, 47.03, 43.65, 34.62, 27.23, 9.37, 6.38, 0.63]

    velocity_plot(v_x, v_y)
    get_diff(v_x, v_y)
