import random
import time
from PyQt5.QtCore import  QObject, pyqtSlot
from PyQt5 import QtCore
from main import ProjectOutput,ProjectOutputPhase1,ProjectOutputPhase2,BestShotOutput

class Worker(QObject):
    finished = QtCore.pyqtSignal()
    data_ready_str = QtCore.pyqtSignal(str)
    data_ready_list = QtCore.pyqtSignal(list)

    # input variables
    file_name = None
    seconds = None
    summarize_degree = None

    @pyqtSlot()
    def summarize_video(self):
        result_file = summarize_video(self.file_name, self.summarize_degree)
        self.data_ready_str.emit(result_file)
        self.finished.emit()

    @pyqtSlot()
    def prepare_video_to_edit(self):
        result_seconds = prepare_video_to_edit(self.file_name, self.summarize_degree)
        self.data_ready_list.emit(result_seconds)
        self.finished.emit()

    @pyqtSlot()
    def show_video_after_edit(self):
        result_file = show_video_after_edit(self.file_name, self.seconds)
        self.data_ready_str.emit(result_file)
        self.finished.emit()

    @pyqtSlot()
    def best_shot(self):
        result_file = best_shot(self.file_name)
        self.data_ready_str.emit(result_file)
        self.finished.emit()



##########################
### back end functions ###
##########################

def summarize_video(file_name, summarize_degree):
    return ProjectOutput(file_name, summarize_degree / 100)
    # for i in range(1, 5):
    #     time.sleep(1)
    #
    # return file_name


def prepare_video_to_edit(file_name, summarize_degree):
    return ProjectOutputPhase1(file_name, summarize_degree / 100)
    # random_seconds = []
    # for i in range(38):
    #     x = random.randint(1, 100)
    #     random_seconds.append(x % 2 == 1)
    #
    # for i in range(1, 5):
    #     time.sleep(1)
    #
    # return random_seconds


def show_video_after_edit(file_name, seconds):
    return ProjectOutputPhase2(file_name, seconds)
    # for i in range(1, 5):
    #     time.sleep(1)
    # return "C:/Users/Zaher/Downloads/Q1.mp4"


def best_shot(file_name):
    return BestShotOutput(file_name)
    # for i in range(1, 5):
    #     time.sleep(1)
    # return "C:/Users/Zaher/Downloads/Q1.mp4"

