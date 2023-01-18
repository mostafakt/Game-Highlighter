import random
import sys

from math import floor

from PyQt5.QtCore import Qt, QUrl, QSize, QThread
from PyQt5.QtGui import QFont, QPalette, QImage, QBrush
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QHBoxLayout,
                             QPushButton, QSlider, QStyle, QVBoxLayout, QWidget, QStatusBar, QDateTimeEdit, QTimeEdit)

from fake_backend import Worker


class Output(QWidget):
    def __init__(self, stacked_widget, parent=None):
        super(Output, self).__init__(parent)

        self.stacked_widget = stacked_widget
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        btn_size = QSize(16, 16)
        video_widget = QVideoWidget()

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

        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.position_slider)

        self.back_button = QPushButton('Back to main screen')
        self.back_button.setFixedWidth(200)
        self.back_button.setIconSize(btn_size)
        self.back_button.setFont(QFont("Noto Sans", 10))
        self.back_button.clicked.connect(self.handle_back)
        self.back_button.setStyleSheet("border-radius: 8px;\
                                    padding: 8px 0;\
                                    background: #0275d8;\
                                    border: #0275d8;\
                                    color: white")

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 40, 0, 0)
        button_layout.addWidget(self.back_button)
        button_layout.setAlignment(Qt.AlignJustify)
        button_layout.setSpacing(0)

        layout = QVBoxLayout()
        layout.addWidget(video_widget)
        layout.addLayout(control_layout)
        # layout.addLayout(button_layout)

        self.setLayout(layout)

        self.media_player.setVideoOutput(video_widget)
        self.media_player.stateChanged.connect(self.media_state_changed)
        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.durationChanged.connect(self.duration_changed)
        self.media_player.error.connect(self.handle_error)

    def open(self, file_name):
        if file_name != '':
            self.media_player.setMedia(
                QMediaContent(QUrl.fromLocalFile(file_name)))
            self.play_button.setEnabled(True)
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
        duration = self.media_player.duration().numerator
        passed = floor((duration - position) / 1000)
        minutes = floor(passed / 60)
        seconds = str(passed - 60 * minutes)
        if len(seconds) == 1:
            seconds = '0' + seconds

        self.position_slider.setToolTip(str(minutes) + ':' + seconds)

    def duration_changed(self, duration):
        self.position_slider.setRange(0, duration)

    def set_position(self, position):
        self.media_player.setPosition(position)

    def handle_error(self):
        self.play_button.setEnabled(False)

    def setup_ui(self, file_name, title):
        self.setWindowTitle(title)
        self.resize(800, 620)
        self.open(file_name)

    def handle_submit(self):
        self.close()

    def submit_edited_video(self, file_name, seconds):
        self.back_button.setText('Loading...')
        self.back_button.setEnabled(False)

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
        print("ev done2")
        self.back_button.setEnabled(True)
        self.back_button.setText('Back to main screen')

        self.stacked_widget.setCurrentIndex(2)
        self.stacked_widget.currentWidget().setup_ui(self.file_name, 'Output')

    def handle_back(self):
        self.stacked_widget.setCurrentIndex(0)
        self.stacked_widget.currentWidget().setup_ui()
        oImage = QImage("C:/Users/Zaher/Downloads/background1.jpg")
        sImage = oImage.scaled(QSize(800, 420))
        sImage.setColor(0, 2)
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(sImage))
        self.stacked_widget.setPalette(palette)
        self.stacked_widget.setFixedHeight(420)
