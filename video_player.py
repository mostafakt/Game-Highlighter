import copy
import random
import sys

from math import floor

from PyQt5.QtGui import QFont, QImage, QPalette, QBrush
from PyQt5.QtCore import Qt, QUrl, QSize, QDateTime, QDate, QTime, QThread
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout,
                             QPushButton, QSlider, QStyle, QVBoxLayout, QWidget, QStatusBar, QDateTimeEdit, QTimeEdit,
                             QInputDialog, QLineEdit, QDialogButtonBox, QFormLayout, QLabel, QRadioButton)

from fake_backend import show_video_after_edit, best_shot, Worker
from output import Output


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


class VideoPlayer(QWidget):

    def __init__(self, stacked_widget, parent=None):
        super(VideoPlayer, self).__init__(parent)

        self.stacked_widget = stacked_widget
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.file_name = ''
        self.new_seconds = []
        self.original_seconds = []

        btn_size = QSize(16, 16)
        video_widget = QVideoWidget()
        video_widget.setFixedWidth(800)
        video_widget.setFixedHeight(300)

        self.play_button = QPushButton()
        self.play_button.setEnabled(False)
        self.play_button.setFixedHeight(24)
        self.play_button.setIconSize(btn_size)
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_button.clicked.connect(self.play)

        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setRange(0, 0)
        self.position_slider.sliderMoved.connect(self.set_position)
        self.position_slider.setToolTip('00:00')

        self.status_bar = QStatusBar()
        self.status_bar.setFont(QFont("Noto Sans", 7))
        self.status_bar.setFixedHeight(14)

        self.position_slider1 = QSlider(Qt.Horizontal)
        self.position_slider1.setRange(0, 0)
        self.position_slider1.sliderMoved.connect(self.set_position)

        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.position_slider)

        control_layout1 = QHBoxLayout()
        control_layout1.setContentsMargins(0, 0, 0, 0)
        control_layout1.addWidget(self.play_button)
        control_layout1.addWidget(self.position_slider1)

        self.submit_button = QPushButton('Submit')
        self.submit_button.setFixedWidth(100)
        self.submit_button.setIconSize(btn_size)
        self.submit_button.setFont(QFont("Noto Sans", 10))
        self.submit_button.clicked.connect(self.handle_submit)
        self.submit_button.setStyleSheet("border-radius: 8px;\
                                    padding: 8px 0;\
                                    background: #0275d8;\
                                    border: #0275d8;\
                                    color: white")

        self.reset_button = QPushButton('Reset')
        self.reset_button.setFixedWidth(90)
        self.reset_button.setIconSize(btn_size)
        self.reset_button.setFont(QFont("Noto Sans", 10))
        self.reset_button.clicked.connect(self.reset)
        self.reset_button.setStyleSheet("border-radius: 8px;\
                                    padding: 8px 0;\
                                    background: #DC3545;\
                                    border: #DC3545;\
                                    color: white")

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 40, 0, 0)
        button_layout.addWidget(self.reset_button)
        button_layout.addWidget(self.submit_button)
        button_layout.setAlignment(Qt.AlignRight)
        button_layout.setSpacing(10)

        self.start_time = QLineEdit()
        self.start_time.setFixedWidth(80)
        self.start_time.setPlaceholderText('m:s')
        self.start_time.setFont(QFont("Noto Sans", 10))
        self.start_time.setStyleSheet('padding: 4px 4px; border: 0.3px solid; border-radius: 4px;')

        start_label = QLabel()
        start_label.setText('From: ')
        start_label.setFixedWidth(50)
        start_label.setFont(QFont("Noto Sans", 10))

        start_layout = QHBoxLayout()
        start_layout.setContentsMargins(0, 0, 0, 0)
        start_layout.addWidget(start_label)
        start_layout.addWidget(self.start_time)
        start_layout.setSpacing(0)

        self.end_time = QLineEdit()
        self.end_time.setFixedWidth(80)
        self.end_time.setPlaceholderText('m:s')
        self.end_time.setFont(QFont("Noto Sans", 10))
        self.end_time.setStyleSheet('padding: 4px 4px; border: 0.3px solid; border-radius: 4px;')

        end_label = QLabel()
        end_label.setText('To: ')
        end_label.setFixedWidth(40)
        end_label.setFont(QFont("Noto Sans", 10))

        end_layout = QHBoxLayout()
        end_layout.setContentsMargins(0, 0, 0, 0)
        end_layout.addWidget(end_label)
        end_layout.addWidget(self.end_time)
        end_layout.setSpacing(0)

        self.important = QRadioButton()
        self.important.setFixedWidth(100)
        self.important.setText('Important')
        self.important.setFont(QFont("Noto Sans", 10))
        self.important.setChecked(True)

        self.not_important = QRadioButton()
        self.not_important.setFixedWidth(150)
        self.not_important.setText('Not important')
        self.not_important.setFont(QFont("Noto Sans", 10))

        important_layout = QVBoxLayout()
        important_layout.addWidget(self.important)
        important_layout.addWidget(self.not_important)
        important_layout.setSpacing(10)

        self.edit_button = QPushButton('Edit')
        self.edit_button.setFixedWidth(80)
        self.edit_button.setIconSize(btn_size)
        self.edit_button.setFont(QFont("Noto Sans", 10))
        self.edit_button.clicked.connect(self.edit_seconds)
        self.edit_button.setStyleSheet("border-radius: 8px;\
                                    padding: 8px 0;\
                                    background: #0275d8;\
                                    border: #0275d8;\
                                    color: white")

        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(0, 30, 0, 0)
        input_layout.setSpacing(50)
        input_layout.addLayout(start_layout)
        input_layout.addLayout(end_layout)
        input_layout.addLayout(important_layout)
        input_layout.addWidget(self.edit_button)
        input_layout.setAlignment(Qt.AlignJustify)

        layout = QVBoxLayout()
        layout.addWidget(video_widget)
        layout.addLayout(control_layout)
        layout.addLayout(control_layout1)
        layout.addLayout(input_layout)
        layout.addLayout(button_layout)
        layout.setSpacing(0)

        self.setLayout(layout)

        self.media_player.setVideoOutput(video_widget)
        self.media_player.stateChanged.connect(self.media_state_changed)
        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.durationChanged.connect(self.duration_changed)
        self.media_player.error.connect(self.handle_error)
        self.status_bar.showMessage("Ready")

        oImage = QImage("C:/Users/Zaher/Downloads/background1.jpg")
        sImage = oImage.scaled(QSize(800, 620))
        sImage.setColor(0, 2)
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(sImage))
        self.setPalette(palette)


    def open(self, file_name):
        if file_name != '':
            self.media_player.setMedia(
                QMediaContent(QUrl.fromLocalFile(file_name)))
            self.play_button.setEnabled(True)
            self.status_bar.showMessage(str(self.media_player.duration().numerator))
            self.play()
            self.play()

    def play(self):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()

    def media_state_changed(self, state):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.play_button.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.play_button.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPlay))

    def position_changed(self, position):
        self.position_slider.setValue(position)
        self.position_slider1.setValue(position)
        duration = self.media_player.duration().numerator
        passed = floor(position / 1000)
        minutes = floor(passed / 60)
        seconds = str(passed - 60 * minutes)
        if len(seconds) == 1:
            seconds = '0' + seconds

        self.position_slider.setToolTip(str(minutes) + ':' + seconds)

    def duration_changed(self, duration):
        self.position_slider.setRange(0, duration)
        self.position_slider1.setRange(0, duration)

        video_length = floor(duration / 1000)
        minutes = floor(video_length / 60)
        seconds = video_length - 60 * minutes

        self.status_bar.showMessage(str(minutes) + ':' + str(seconds))

    def set_position(self, position):
        self.media_player.setPosition(position)

    def handle_error(self):
        self.play_button.setEnabled(False)
        self.status_bar.showMessage("Error: " + self.media_player.errorString())

    def change_color(self, seconds_status):
        color_range = []

        color = ['red', 'green']
        for sec in seconds_status:
            color_range.append(color[sec])

        self.groove_color = get_groove_color(color_range)
        self.position_slider1.setStyleSheet("QSlider::groove:horizontal {\
                border: 1px solid #999999;\
                height: 8px; \
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, " + self.groove_color + ");\
            }QSlider::handle:horizontal {\
                background-color: black;\
                border: 1px solid #5c5c5c;\
                border-radius: 0px;\
                border-color: black;\
                margin: -8px 2; \
            }")

    def setup_ui(self, file_name, seconds):
        self.file_name = file_name
        self.new_seconds = copy.deepcopy(seconds)
        self.original_seconds = copy.deepcopy(seconds)
        self.setWindowTitle("Edit Video")
        self.resize(800, 620)
        self.change_color(seconds)
        self.open(file_name)

    def open_window(self):
        name = show_video_after_edit(self.file_name, self.new_seconds)
        self.window = Output()
        self.window.setup_ui(name, 'Output')
        self.window.show()

    def handle_submit(self):
        self.submit_edited_video(self.file_name, self.new_seconds)

    def reset(self):
        self.change_color(self.original_seconds)
        self.new_seconds = copy.deepcopy(self.original_seconds)

    def edit_seconds(self):
        t1 = self.start_time.text().split(':')
        t2 = self.end_time.text().split(':')

        if len(t1) != 2 or len(t2) != 2:
            return

        m1 = int(t1[0])
        s1 = int(t1[1])
        m2 = int(t2[0])
        s2 = int(t2[1])

        state = self.important.isChecked()

        if s1 >= 60 or s2 >= 60 or s1 < 0 or s2 < 0:
            return

        ss = m1 * 60 + s1
        es = m2 * 60 + s2

        if ss > es:
            return
        if es >= len(self.new_seconds):
            return

        for i in range(ss, es + 1):
            self.new_seconds[i] = state

        self.change_color(self.new_seconds)

        self.start_time.setText('')
        self.end_time.setText('')
        self.important.setChecked(True)

    def submit_edited_video(self, file_name, seconds):
        self.submit_button.setText('Loading...')
        self.submit_button.setFixedWidth(100)
        self.submit_button.setEnabled(False)
        self.reset_button.setEnabled(False)
        self.edit_button.setEnabled(False)

        self.obj = Worker()
        self.thread = QThread()
        # input
        self.obj.file_name = file_name
        self.obj.seconds = seconds

        self.obj.moveToThread(self.thread)
        self.obj.finished.connect(self.thread.quit)

        self.thread.started.connect(self.obj.show_video_after_edit)  # backend function
        self.obj.data_ready_str.connect(self.ev_ready)  # output data
        self.thread.finished.connect(self.ev_done)  # process done

        self.thread.start()

    def ev_ready(self, name):
        self.file_name = name

    def ev_done(self):
        print("ev done1")
        self.submit_button.setEnabled(True)
        self.reset_button.setEnabled(True)
        self.edit_button.setEnabled(True)
        self.submit_button.setText('Submit')

        self.stacked_widget.setCurrentIndex(2)
        self.stacked_widget.currentWidget().setup_ui(self.file_name, 'Output')


def show():
    app = QApplication(sys.argv)

    seconds = []
    for i in range(38):
        x = random.randint(1, 100)
        seconds.append(x % 2 == 1)

    player = VideoPlayer()
    player.setWindowTitle("Player")
    player.resize(600, 800)
    player.change_color(seconds)
    player.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    show()