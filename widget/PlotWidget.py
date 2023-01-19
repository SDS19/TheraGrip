import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QApplication
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg


class PlotCanvas(QWidget):
    def __init__(self, x, y):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.figure = plt.figure()
        self.axes = self.figure.add_subplot(111)
        self.axes.plot(x, y)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = PlotCanvas([0, 1, 2, 3, 4], [10, 1, 20, 3, 40])
    sys.exit(app.exec_())
