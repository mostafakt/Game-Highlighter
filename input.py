import random
import sys

import PyQt5
from PyQt5.QtGui import QFont, QImage, QPalette, QBrush, QIcon, QMovie
from PyQt5.QtCore import Qt, QUrl, QSize, QThread
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout,
                             QPushButton, QSlider, QStyle, QVBoxLayout, QWidget, QStatusBar, QLabel, QMainWindow,
                             QStackedWidget)

from fake_backend import summarize_video, best_shot, prepare_video_to_edit, Worker
from loading import Loading
from output import Output
from video_player import VideoPlayer

player = None


class Input(QWidget):
    def __init__(self, parent=None):
        super(Input, self).__init__(parent)

        self.file_name = ''
        self.slider_value = 1
        btn_size = QSize(16, 16)

        self.setObjectName('QInputWindow')
        self.spinner = QMovie()

        self.seconds = []

        label = QLabel()
        label.setText('Video: ')
        label.setFixedHeight(20)
        label.setFont(QFont('Noto Sans', 11))
        label.setStyleSheet('color: #FFF')

        open_button = QPushButton("Click to Upload")
        open_button.setFixedWidth(140)
        open_button.setIconSize(btn_size)
        open_button.setFont(QFont("Noto Sans", 10))
        open_button.clicked.connect(self.abrir)
        open_button.setStyleSheet('padding: 8px 0;\
            background:#495057;\
            border:#292b2c;\
            border-radius: 4px;\
            color:white')

        self.status_bar = QLabel()
        self.status_bar.setFont(QFont("Noto Sans", 9))
        # self.status_bar.setFixedHeight(20)
        self.status_bar.setStyleSheet('color: #A4AAB0;')
        self.status_bar.setText("Choose a file...")
        self.status_bar.setContentsMargins(15, 2, 0, 0)

        control_layout = QVBoxLayout()
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.addWidget(label)
        control_layout.addWidget(open_button)
        control_layout.addWidget(self.status_bar)

        video_layout = QHBoxLayout()
        video_layout.setContentsMargins(0, 0, 0, 0)
        video_layout.addWidget(label)
        video_layout.addLayout(control_layout)
        video_layout.setSpacing(2)
        video_layout.setAlignment(Qt.AlignLeft)

        slider_label = QLabel()
        slider_label.setText('Summarize degree: ')
        slider_label.setFixedHeight(20)
        slider_label.setFixedWidth(155)
        slider_label.setFont(QFont('Noto Sans', 11))
        slider_label.setStyleSheet('color: white')

        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setRange(1, 100)
        self.position_slider.setFixedWidth(275)
        self.position_slider.setToolTip('1')
        self.position_slider.valueChanged.connect(self.change_value)

        self.value_label = QLabel()
        self.value_label.setText('Summarize degree: ' + str(self.slider_value))
        self.value_label.setFixedHeight(20)
        self.value_label.setFixedWidth(150)
        self.value_label.setFont(QFont('Noto Sans', 8))
        self.value_label.setStyleSheet('color: white')

        slider_layout = QHBoxLayout()
        slider_layout.setSpacing(5)
        slider_layout.setContentsMargins(0, 0, 0, 0)
        slider_layout.addWidget(slider_label)
        slider_layout.addWidget(self.position_slider)
        slider_layout.setAlignment(Qt.AlignLeft)

        slider_layout1 = QVBoxLayout()
        slider_layout1.setSpacing(0)
        slider_layout1.setContentsMargins(0, 0, 0, 0)
        slider_layout1.addLayout(slider_layout)
        slider_layout1.addWidget(self.value_label)
        slider_layout1.setAlignment(Qt.AlignLeft)

        self.submit_button = QPushButton('Summarize video')
        self.submit_button.setFixedWidth(150)
        self.submit_button.setIconSize(btn_size)
        self.submit_button.setFont(QFont("Noto Sans", 10))
        self.submit_button.clicked.connect(self.handle_summarize)
        self.submit_button.setStyleSheet("border-radius: 8px;\
                                    padding: 8px 0;\
                                    background: #0275d8;\
                                    border: #0275d8;\
                                    color: white")

        self.edit_button = QPushButton('Summarize and edit')
        self.edit_button.setFixedWidth(170)
        self.edit_button.setIconSize(btn_size)
        self.edit_button.setFont(QFont("Noto Sans", 10))
        self.edit_button.clicked.connect(self.handle_edit_video)
        self.edit_button.setStyleSheet("border-radius: 8px;\
                                    padding: 8px 0;\
                                    background: #0275d8;\
                                    border: #0275d8;\
                                    color: white")

        self.shot_button = QPushButton('Show best shot')
        self.shot_button.setFixedWidth(150)
        self.shot_button.setIconSize(btn_size)
        self.shot_button.setFont(QFont("Noto Sans", 10))
        self.shot_button.clicked.connect(self.handle_best_shot)
        self.shot_button.setStyleSheet("border-radius: 8px;\
                                    padding: 8px 0;\
                                    background: #198754;\
                                    border: #198754;\
                                    color: white")

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 75, 0, 0)
        button_layout.setSpacing(15)
        button_layout.addWidget(slider_label)
        button_layout.addWidget(self.submit_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.shot_button)
        button_layout.setAlignment(Qt.AlignRight)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(80)
        layout.addLayout(video_layout)
        layout.addLayout(slider_layout1)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.setup_ui()


    def abrir(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select the video",
                                                   ".", "Video Files (*.mp4 *.flv *.ts *.mts *.avi)")

        if file_name != '':
            self.file_name = file_name
            self.status_bar.setText(file_name)

    def set_position(self, position):
        self.slider_value = position
        self.position_slider.setToolTip(position)
        self.value_label.setText('Summarize degree: ' + str(self.slider_value))

    def change_value(self, value):
        self.slider_value = value
        self.position_slider.setToolTip(str(value))
        self.value_label.setText('Summarize degree: ' + str(self.slider_value))

    def setup_ui(self):
        self.setWindowTitle("Input")
        self.resize(800, 420)
        oImage = QImage("background1.jpg")
        sImage = oImage.scaled(QSize(800, 420))
        sImage.setColor(0, 2)
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(sImage))
        self.setPalette(palette)

    def open_best_shot_window(self):
        name = best_shot(self.file_name)
        self.window = Output()
        self.window.setup_ui(name, 'Best shot')
        self.window.show()

    def handle_best_shot(self):
        if self.file_name == '':
            return

        self.show_best_shot(self.file_name, self.slider_value)

    def handle_edit_video(self):
        if self.file_name == '':
            return

        self.show_edit_video(self.slider_value)

        # seconds = prepare_video_to_edit(self.file_name, self.slider_value)
        # self.window = VideoPlayer()
        # self.window.setup_ui(self.file_name, seconds)
        # self.window.show()
        # self.close()

    def show_best_shot(self, file_name, summarize_degree):
        self.shot_button.setText('Loading...')
        self.submit_button.setEnabled(False)
        self.shot_button.setEnabled(False)
        self.edit_button.setEnabled(False)

        self.obj = Worker()
        self.thread = QThread()
        # input
        self.obj.file_name = file_name
        self.obj.summarize_degree = summarize_degree

        self.obj.moveToThread(self.thread)
        self.obj.finished.connect(self.thread.quit)

        self.thread.started.connect(self.obj.best_shot)  # backend function
        self.obj.data_ready_str.connect(self.sv_ready)  # output data
        self.thread.finished.connect(self.bs_done)  # process done

        self.thread.start()

    def bs_done(self):
        print('done')
        self.submit_button.setEnabled(True)
        self.shot_button.setEnabled(True)
        self.edit_button.setEnabled(True)
        self.shot_button.setText('Show best shot')

        stacked_widget.setCurrentIndex(3)
        stacked_widget.setFixedHeight(620)
        stacked_widget.setPalette(QPalette())
        stacked_widget.currentWidget().setup_ui(self.file_name, 'Best shot')

    def summarize_video(self, file_name, summarize_degree):
        # stacked_widget.setCurrentIndex(4)  # switch to loading screen

        self.submit_button.setText('Loading...')
        self.submit_button.setEnabled(False)
        self.shot_button.setEnabled(False)
        self.edit_button.setEnabled(False)

        self.obj = Worker()
        self.thread = QThread()
        # input
        self.obj.file_name = file_name
        self.obj.summarize_degree = summarize_degree

        self.obj.moveToThread(self.thread)
        self.obj.finished.connect(self.thread.quit)

        self.thread.started.connect(self.obj.summarize_video)  # backend function
        self.obj.data_ready_str.connect(self.sv_ready)  # output data
        self.thread.finished.connect(self.sv_done)  # process done

        self.thread.start()

    def sv_ready(self, file_name):
        print("ready")
        self.file_name = file_name

    def sv_done(self):
        print("done")
        self.submit_button.setEnabled(True)
        self.shot_button.setEnabled(True)
        self.edit_button.setEnabled(True)
        self.submit_button.setText('Summarize video')

        stacked_widget.setCurrentIndex(2)
        stacked_widget.setFixedHeight(620)
        stacked_widget.setPalette(QPalette())
        stacked_widget.currentWidget().setup_ui(self.file_name, 'Output')

    def handle_summarize(self):
        if self.file_name == '':
            return
        self.summarize_video(self.file_name, self.slider_value)

    def show_edit_video(self, summarize_degree):
        self.edit_button.setText('Loading...')
        self.submit_button.setEnabled(False)
        self.shot_button.setEnabled(False)
        self.edit_button.setEnabled(False)

        self.obj = Worker()
        self.thread = QThread()
        # input
        self.obj.file_name = self.file_name
        self.obj.summarize_degree = summarize_degree

        self.obj.moveToThread(self.thread)
        self.obj.finished.connect(self.thread.quit)

        self.thread.started.connect(self.obj.prepare_video_to_edit)  # backend function
        self.obj.data_ready_list.connect(self.ev_ready)  # output data
        self.thread.finished.connect(self.ev_done)  # process done

        self.thread.start()

    def ev_ready(self, result_seconds):
        self.seconds = result_seconds

    def ev_done(self):
        print("ev done")
        self.submit_button.setEnabled(True)
        self.shot_button.setEnabled(True)
        self.edit_button.setEnabled(True)
        self.edit_button.setText('Summarize and edit')

        stacked_widget.setCurrentIndex(1)
        stacked_widget.setFixedHeight(620)
        stacked_widget.setPalette(QPalette())
        stacked_widget.currentWidget().setup_ui(self.file_name, self.seconds)


def get_groove_color(color_range):
    groove_color_range = 'stop:0 ' + color_range[0]
    current_color = color_range[0]
    for i in range(0, len(color_range), 1):
        if color_range[i] == current_color:
            continue
        else:
            current_color = color_range[i]
            groove_color_range += ', stop:' + str((2 * i - 1) / 2 / len(color_range)) + ' ' + color_range[
                i - 1] + ', stop:' + str((2 * i) / 2 / len(color_range)) + ' ' + color_range[i]

    groove_color_range += ', stop:1 ' + color_range[-1]
    return groove_color_range


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # app.setStyleSheet("""
    #     #QInputWindow {
    #         background: url("C:/Users/Zaher/Downloads/background1.jpg");
    #         background-position: center;
    #         background-repeat: no-repeat;
    #         background-size: cover;
    #     }
    # """)

    stacked_widget = QStackedWidget()

    mainW = Input()
    editingW = VideoPlayer(stacked_widget)
    finalOutputW = Output(stacked_widget)
    bestShotW = Output(stacked_widget)
    loading = Loading()

    stacked_widget.addWidget(mainW)
    stacked_widget.addWidget(editingW)
    stacked_widget.addWidget(finalOutputW)
    stacked_widget.addWidget(bestShotW)
    stacked_widget.addWidget(loading)

    stacked_widget.setGeometry(20, 50, 1200, 800)
    stacked_widget.setFixedWidth(800)
    stacked_widget.setFixedHeight(420)

    oImage = QImage("background1.jpg")
    sImage = oImage.scaled(QSize(800, 420))
    sImage.setColor(0, 2)
    palette = QPalette()
    palette.setBrush(QPalette.Window, QBrush(sImage))
    stacked_widget.setPalette(palette)

    stacked_widget.show()

    sys.exit(app.exec_())

