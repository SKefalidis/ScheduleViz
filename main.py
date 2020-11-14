import sys
import copy
from PyQt5.QtWidgets import QWidget, QApplication, QLabel
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QBrush
from PyQt5.QtCore import Qt, QRect
import scheduling


class ScheduleVizWindow(QWidget):
    def __init__(self, time_blocks: [scheduling.TimeBlock], process_exec_stats: [scheduling.ProcessExecStats]):
        super().__init__()
        self.time_blocks: [scheduling.TimeBlock] = time_blocks
        self.process_exec_stats: [scheduling.ProcessExecStats] = process_exec_stats
        self.init_ui()

    def init_ui(self):
        self.setGeometry(200, 300, 800, 400)
        self.setWindowTitle('ScheduleViz')
        self.show()

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setPen(QPen(Qt.black, 1, Qt.SolidLine))
        x = 20
        y = 20
        size = 20
        for tb in self.time_blocks:
            if tb.process:
                painter.setBrush(QBrush(tb.process.color, Qt.SolidPattern))
            else:
                painter.setBrush(QBrush())
            painter.drawRect(QRect(x, y, size * tb.duration, size))
            painter.drawText(QRect(x + size * tb.duration / 2 - 50, y, 100, y), Qt.AlignCenter, str(tb.duration))
            painter.drawText(QRect(x + size * tb.duration / 2 - 50, y, 100, y * 3), Qt.AlignCenter, tb.process_name)
            x += size * tb.duration
        x = 20
        y_offset = 5
        for pes in self.process_exec_stats:
            text = " arrived at " + str(pes.process.queue_arrival_time) \
                   + "ms, started at " + str(pes.start_time) \
                   + "ms, and had a turnover time of " + str(pes.turnaround_time) + "ms"
            painter.setPen(QPen(pes.process.color, 1, Qt.SolidLine))
            painter.drawText(QRect(x, y * y_offset, 500, y * y_offset), Qt.AlignLeft, pes.process.name + ":")
            painter.setPen(QPen())
            painter.drawText(QRect(x + 20, y * y_offset, 500, y * y_offset), Qt.AlignLeft, text)
            y_offset += 1
        painter.end()


if __name__ == '__main__':
    process_info_list = [
        scheduling.ProcessInfo("J0", 11, 0, QColor(200, 0, 0)),
        scheduling.ProcessInfo("J1", 7, 3, QColor(0, 200, 0)),
        scheduling.ProcessInfo("J2", 21, 14, QColor(0, 0, 200)),
        scheduling.ProcessInfo("J3", 5, 19, QColor(0, 200, 200)),
        scheduling.ProcessInfo("J4", 11, 23, QColor(200, 0, 200))
                         ]

    cpu = scheduling.Processor(6, 1)
    # time_blocks, process_exec_stats = cpu.exec(fcfs.fcfs, copy.deepcopy(process_info_list))
    # time_blocks, process_exec_stats = cpu.exec(fcfs.rr, copy.deepcopy(process_info_list))
    time_blocks, process_exec_stats = cpu.exec(scheduling.sjf, copy.deepcopy(process_info_list))

    app = QApplication(sys.argv)
    w = ScheduleVizWindow(time_blocks, process_exec_stats)
    sys.exit(app.exec())
