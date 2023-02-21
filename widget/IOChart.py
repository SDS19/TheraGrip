import os
import time
import numpy
import shutil
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator


def single_plot(y, ylabel, title):
    x = list(range(len(y)))
    y = to_clean_list(y)

    max_y = max(y)
    min_y = min(y)

    fig, ax = plt.subplots()
    ax.grid()
    ax.plot(x, y, color='green')
    ax.set(xlabel='time (ms)', ylabel=ylabel, title=title)
    ax.annotate('max: ' + str(max_y),
                 xy=(y.index(max_y), max_y),
                 xytext=(y.index(max_y), max_y))
    ax.annotate('min: ' + str(min_y),
                 xy=(y.index(min_y), min_y),
                 xytext=(y.index(min_y), min_y))

    plt.show()


def dual_plot(name, y1, y2, title_1, title_2, y_label):
    x = list(range(len(y1)))

    max_y1 = max(y1)
    min_y1 = min(y1)
    max_y2 = max(y2)
    min_y2 = min(y2)

    plt.figure(name)

    plt.subplot(2, 1, 1)
    plt.title(title_1)
    plt.xlabel("time (ms)")
    plt.ylabel(y_label)
    plt.plot(x, y1, color='red')
    plt.grid()
    plt.annotate('max: ' + str(max_y1),
                 xy=(y1.index(max_y1), max_y1),
                 xytext=(y1.index(max_y1), max_y1))
    plt.annotate('min: ' + str(min_y1),
                 xy=(y1.index(min_y1), min_y1),
                 xytext=(y1.index(min_y1), min_y1))

    plt.subplot(2, 1, 2)
    plt.title(title_2)
    plt.xlabel("time (ms)")
    plt.ylabel(y_label)
    plt.plot(x, y2)
    plt.grid()
    plt.annotate('max: ' + str(max_y2),
                 xy=(y2.index(max_y2), max_y2),
                 xytext=(y2.index(max_y2), max_y2))
    plt.annotate('min: ' + str(min_y2),
                 xy=(y2.index(min_y2), min_y2),
                 xytext=(y2.index(min_y2), min_y2))

    plt.tight_layout()
    plt.show()


def triple_plot(name, y1, y2, title_1, title_2, title_3, y_label):
    x = list(range(len(y1)))
    y3 = Pythagorean_Theorem(y1, y2)

    max_y1 = max(y1)
    min_y1 = min(y1)
    max_y2 = max(y2)
    min_y2 = min(y2)
    max_y3 = max(y3)
    min_y3 = min(y3)

    plt.figure(name)

    plt.subplot(3, 1, 1)
    plt.title(title_1)
    plt.xlabel("time (ms)")
    plt.ylabel(y_label)
    plt.plot(x, y1, color='red')
    plt.grid()
    plt.annotate('max: ' + str(max_y1),
                 xy=(y1.index(max_y1), max_y1),
                 xytext=(y1.index(max_y1), max_y1))
    plt.annotate('min: ' + str(min_y1),
                 xy=(y1.index(min_y1), min_y1),
                 xytext=(y1.index(min_y1), min_y1))

    plt.subplot(3, 1, 2)
    plt.title(title_2)
    plt.xlabel("time (ms)")
    plt.ylabel(y_label)
    plt.plot(x, y2)
    plt.grid()
    plt.annotate('max: ' + str(max_y2),
                 xy=(y2.index(max_y2), max_y2),
                 xytext=(y2.index(max_y2), max_y2))
    plt.annotate('min: ' + str(min_y2),
                 xy=(y2.index(min_y2), min_y2),
                 xytext=(y2.index(min_y2), min_y2))

    plt.subplot(3, 1, 3)
    plt.title(title_3)
    plt.xlabel("time (ms)")
    plt.ylabel(y_label)
    plt.plot(x, y3, color='green')
    plt.grid()
    plt.annotate('max: ' + str(max_y3),
                 xy=(y3.index(max_y3), max_y3),
                 xytext=(y3.index(max_y3), max_y3))
    plt.annotate('min: ' + str(min_y3),
                 xy=(y3.index(min_y3), min_y3),
                 xytext=(y3.index(min_y3), min_y3))

    plt.tight_layout()
    plt.show()


def xy_force_plot(name, y1, y2):
    dual_plot(name, to_force_list(y1), to_force_list(y2), "X Axis: component force", "Y Axis: component force", "force (N)")


def force_plot(name, y1, y2):
    single_plot(name, to_force_list(Pythagorean_Theorem(y1, y2)), "force (N)", "resultant force")


""" ******************** log I/O ******************** """


# def clear_log(dir):
#     shutil.rmtree(os.path.join(os.path.dirname(__file__), 'log', dir))
#     os.mkdir(os.path.join(os.path.dirname(__file__), 'log', dir))


def write_user_log(username, folder, param, data):
    filename = time.strftime('%d-%m-%Y_%H%M%S') + '_' + param + '.txt'
    file = open(os.path.join(os.path.dirname(__file__), 'user', username, 'log', folder, filename), "a")
    file.write(str(data))
    file.close()


# def read_log(folder, filename):
#     y1 = []
#     y2 = []
# 
#     file = open(os.path.join(os.path.dirname(__file__), 'log', folder, filename), "r")
#     str_lines = file.readlines()
# 
#     str_line_1 = str_lines[0].replace('[', '').replace(']', '').replace(' ', '').replace('\'', '').split(',')
#     str_line_2 = str_lines[1].replace('[', '').replace(']', '').replace(' ', '').replace('\'', '').split(',')
# 
#     for s1, s2 in zip(str_line_1, str_line_2):
#         y1.append(float(s1))
#         y2.append(float(s2))
# 
#     file.close()
#     return [y1, y2]


def load_chart(file_path):
    y1 = []
    y2 = []

    file = open(file_path, "r")
    str_lines = file.readlines()

    str_line_1 = str_lines[0].replace('[', '').replace(']', '').replace(' ', '').replace('\'', '').split(',')
    str_line_2 = str_lines[1].replace('[', '').replace(']', '').replace(' ', '').replace('\'', '').split(',')

    for s1, s2 in zip(str_line_1, str_line_2):
        y1.append(float(s1))
        y2.append(float(s2))

    file.close()

    if not str(file_path).find('position') == -1:
        dual_plot(file_path, clean_position_list(y1), clean_position_list(y2), 'X Axis: Range', 'Y Axis: Range', 'position (mm)')
    elif not str(file_path).find('velocity') == -1:
        dual_plot(file_path, to_clean_list(y1), to_clean_list(y2), 'X Axis: Velocity', 'Y Axis: Velocity', 'velocity (mm/s)')
    elif not str(file_path).find('force') == -1:
        triple_plot(file_path, to_clean_list(y1), to_clean_list(y2), 'X Axis: component force', 'Y Axis: component force', 'resultant force', 'force (N)')


""" ******************** config I/O ******************** """

def read_user_config(task, username):
    file = open(os.path.join(os.path.dirname(__file__), 'user', username, 'config', task + '.txt'), "r")
    return file.read().replace('[', '').replace(']', '').replace(' ', '').replace('\'', '').split(',')

def write_user_config(task, data, username):
    file = open(os.path.join(os.path.dirname(__file__), 'user', username, 'config', task + '.txt'), "w")
    file.write(str(data))
    file.close()

""" ******************** data processing ******************** """


def parse_to_list(point):
    if len(point) > 0:
        x = int(point.split(',')[0].strip())
        y = int(point.split(',')[1].strip())
        return [x, y]
    else:
        return []


def Pythagorean_Theorem(a, b):
    c = []
    for e1, e2 in zip(a, b):
        c.append(round(numpy.sqrt(numpy.square(e1) + numpy.square(e2)), 2))
    return c


def three_sigma_filter(data):
    mean = numpy.mean(data)
    std = numpy.std(data)

    for i in range(len(data)):
        if data[i] < mean - 3 * std or data[i] > mean + 3 * std:
            for item in data[i:]:
                if mean - 3 * std <= item <= mean + 3 * std:
                    data[i] = item
                    break

    return data


def amp_to_force(mA):
    torque_Nm = 2
    current_A = 4.2
    torque_constant = torque_Nm / current_A
    d_mm = 6.35
    force_N = round(mA * torque_constant / (d_mm / 2), 2)
    return force_N


def clean_position_list(data):
    for i in range(len(data)):
        if data[i] > 350:
            for item in data[i:]:
                if item <= 350:
                    data[i] = item
    return data


def to_clean_list(data):
    return three_sigma_filter(three_sigma_filter(data))


def to_clean_position_list(data):
    for i in range(len(data)):
        if data[i] > 350:
            for item in data[i:]:
                if item <= 350:
                    data[i] = item
                    break


def to_force_list(data):
    filtered_data = three_sigma_filter(three_sigma_filter(data))

    clean_data = []
    for item in filtered_data:
        clean_data.append(amp_to_force(item))

    return clean_data


if __name__ == '__main__':
    filename = "22-12-2022_155238_arm_current.txt"
    arr = read_log('arm', filename)
    triple_plot(filename, to_force_list(arr[0]), to_force_list(arr[1]), "X component force", "Y component force", "resultant force", "force (N)")