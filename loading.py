import qtawesome as qtawesome
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt, QUrl, QSize, QThread
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QStackedWidget,
                             QPushButton, QSlider, QStyle, QVBoxLayout, QWidget, QStatusBar, QLabel)
# from PyQt5.uic import loadUi
# from PyQt5.uic.properties import QtGui


class Loading(QWidget):
    def __init__(self, parent=None):
        super(Loading, self).__init__(parent)

        label = QLabel()
        label.setText('Loading...')
        label.setFixedHeight(510)
        label.setFixedWidth(510)
        label.setFont(QFont('Noto Sans', 60))
        label.setStyleSheet("""
            background: url('C:/Users/Zaher/Downloads/loading2.png');
            background-repeat: no-repeat;
            background-size: cover;
        """)

        pixmap = QPixmap("C:/Users/Zaher/Downloads/loading.png")
        # label.setPixmap(pixmap)

        layout = QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)
