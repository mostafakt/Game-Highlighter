import numpy as np
import cv2
from matplotlib import pyplot as plt
from audio_amplitudes import get_amplitudes
from moviepy.editor import *
from health_bar import get_health_values,get_video_frames_dimensions
from dense_optical_flow import amount_of_movement
from numberofcharacters import get_Number_Of_Characters_values
from split_to_two_videos import split_video_to_2_videos
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
import librosa
import soundfile as sf

from scoop_detection import get_scope


def create_two_videos(videoURL, skip, minNumberOfZeroFramesToBeCounted):
    split_res = split_video_to_2_videos(videoURL, skip, minNumberOfZeroFramesToBeCounted)
    H, W, D = get_video_frames_dimensions(videoURL)
    # cap = cv2.VideoCapture(videoURL)
    # fps = cap.get(cv2.CAP_PROP_FPS)
    # cap.release()
    # cv2.destroyAllWindows()
    fourcc1 = cv2.VideoWriter_fourcc(*'mp4v')
    ThirdPersonVideo = cv2.VideoWriter('ThirdPersonVideo.avi', fourcc1, 30, (W, H))
    fourcc2 = cv2.VideoWriter_fourcc(*'mp4v')
    RestVideo = cv2.VideoWriter('RestVideo.avi', fourcc2, 30, (W, H))
    cap = cv2.VideoCapture(videoURL)
    if (cap.isOpened() == False):
        print("Error opening video stream or file")
    frameNumber = 0
    while (cap.isOpened()):
        ret, frame = cap.read()
        frameNumber += 1
        if ret == True:
            if split_res[frameNumber - 1] == 0:
                RestVideo.write(frame)
            else:
                ThirdPersonVideo.write(frame)
        else:
            break
    cap.release()
    cv2.destroyAllWindows()
    ThirdPersonVideo.release()
    RestVideo.release()
    return split_res


def ThirdPersonVideoProcessing(videoURL, splitResult, skip,fps,length):
    thirdPersonFrameNumbers = []
    for i in range(len(splitResult)):
        if splitResult[i] == 1:
            thirdPersonFrameNumbers.append(i)
    # Health Feature
    Health = get_health_values('ThirdPersonVideo.avi', 200)
    # Number Of Characters Feature
    NumberOfCharacters = get_Number_Of_Characters_values('ThirdPersonVideo.avi', skip)
    # Opened Scope Feature
    OpenedScope = get_scope('ThirdPersonVideo.avi', skip)
    # laugh feature
    #laugh_all = get_laughs('myaudio.wav')
    #laugh = []
    #for r in thirdPersonFrameNumbers:
        #laugh.append(laugh_all[r])
    # audio amplitude feature
    amplitude_all = get_amplitudes('myaudio.wav',fps,length)
    amplitudes = []
    for r in thirdPersonFrameNumbers:
        amplitudes.append(amplitude_all[r])
    # TO NUMPY
    Health_numpy = np.array(Health)
    NumberOfCharacters_numpy = np.array(NumberOfCharacters)
    #laugh_numpy = np.array(laugh)
    amplitude_numpy = np.array(amplitudes)
    OpenedScope_numpy = np.array(OpenedScope)
    # stack features
    ThirdPersonfeatures = np.stack(
        (Health_numpy, NumberOfCharacters_numpy, amplitude_numpy, OpenedScope_numpy), axis=-1)
    # fit isolation forest model
    clf = OneClassSVM(gamma='auto').fit(ThirdPersonfeatures)
    clf_df = clf.decision_function(ThirdPersonfeatures)
    # clf = IsolationForest(n_estimators = 200,random_state=0).fit(ThirdPersonfeatures)
    # clf_df = clf.decision_function(ThirdPersonfeatures)
    clf_df_list = clf_df.tolist()
    ret = list(zip(clf_df_list, thirdPersonFrameNumbers))
    return ret


def RestOfStreamVideoProcessing(videoURL, splitResult, skip,fps,length):
    RestFrameNumbers = []
    for i in range(len(splitResult)):
        if splitResult[i] == 0:
            RestFrameNumbers.append(i)
    # amount of movement feature
    movementAmount = amount_of_movement('RestVideo.avi', skip)
    # laugh feature
    # laugh_all = get_laughs('myaudio.wav')
    # laugh = []
    # for r in RestFrameNumbers:
    #     laugh.append(laugh_all[r])
    # audio amplitude feature
    amplitude_all = get_amplitudes('myaudio.wav',fps,length)
    amplitudes = []
    for r in RestFrameNumbers:
        amplitudes.append(amplitude_all[r])
    # TO NUMPY
    movementAmount_numpy = np.array(movementAmount)
    #laugh_numpy = np.array(laugh)
    amplitude_numpy = np.array(amplitudes)
    # stack features
    RestOfVideoFeatures = np.stack((movementAmount_numpy, amplitude_numpy), axis=-1)
    # fit isolation forest model
    clf = OneClassSVM(gamma='auto').fit(RestOfVideoFeatures)
    clf_df = clf.decision_function(RestOfVideoFeatures)
    # clf = IsolationForest(n_estimators = 200,random_state=0).fit(RestOfVideoFeatures)
    # clf_df = clf.decision_function(RestOfVideoFeatures)
    clf_df_list = clf_df.tolist()
    ret = list(zip(clf_df_list, RestFrameNumbers))
    return ret


def MergeResultsAndSort(result1,result2):
  result1.extend(result2)
  result1.sort()
  FinalResult = [x[1] for x in result1]
  return FinalResult

def get_best_k_frame(FinalResult,k):
  return FinalResult[:k]

def get_audio(videoURL):
  y, sr = librosa.load(videoURL)
  return y,sr


def write_highlight_video(videoURL, frames):
    cap = cv2.VideoCapture(videoURL)
    fps = cap.get(cv2.CAP_PROP_FPS)
    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    cv2.destroyAllWindows()
    H, W, D = get_video_frames_dimensions(videoURL)
    fourcc1 = cv2.VideoWriter_fourcc(*'mp4v')
    FinalVideo = cv2.VideoWriter('finalvideo.avi', fourcc1, fps, (W, H))
    cap = cv2.VideoCapture(videoURL)
    if (cap.isOpened() == False):
        print("Error opening video stream or file")
    frameNumber = 0
    while (cap.isOpened()):
        ret, frame = cap.read()
        frameNumber += 1
        if ret == True:
            if frames[frameNumber - 1] == 1:
                FinalVideo.write(frame)
        else:
            break
    cap.release()
    cv2.destroyAllWindows()
    FinalVideo.release()
    y, sr = get_audio("myaudio.wav")
    value = int(sr / fps)
    x = []
    for i in range(len(frames)):
        if frames[i] == 1:
            st = i * value
            en = (i + 1) * value
            for j in range(st, en):
                x.append(y[j])
    sf.write('finalaudio.wav', x, int(sr))
    # librosa.output.write_wav('finalaudio.wav', x, sr)
    clip = VideoFileClip('finalvideo.avi')
    audioclip = AudioFileClip("finalaudio.wav")
    videoclip = clip.set_audio(audioclip)
    videoclip.write_videofile("output.mp4")
    dirname = os.path.dirname(__file__)
    output = os.path.join(dirname, 'output.mp4')
    return output


def ProjectOutput(videoURL,summarizationPercentage):
  print('Summarizing Percentage = ' + str(summarizationPercentage))
  SKIP = 30
  cap = cv2.VideoCapture(videoURL)
  totalFrames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
  fps = cap.get(cv2.CAP_PROP_FPS)
  cap.release()
  cv2.destroyAllWindows()
  split_res = create_two_videos(videoURL,SKIP,150)

  my_clip = VideoFileClip(videoURL)
  my_clip.audio.write_audiofile(r"myaudio.wav")

  Result1=ThirdPersonVideoProcessing(videoURL,split_res,SKIP,fps,totalFrames)
  Result2=RestOfStreamVideoProcessing(videoURL,split_res,SKIP,fps,totalFrames)
  FinalResult= MergeResultsAndSort(Result1,Result2)
  best = get_best_k_frame(FinalResult,totalFrames)
  takenFrames = []
  for i in range(totalFrames):
    takenFrames.append(0)
  cnt = 0
  for b in best:
    st = max(0,b-10*fps)
    en = min(totalFrames-1,b+ 5*fps)
    st = int(st)
    en = int(en)
    for i in range(st,en+1):
      if takenFrames[i] ==0:
        takenFrames[i]=1
        cnt+=1
    if cnt/totalFrames >=summarizationPercentage:
      break
  return write_highlight_video(videoURL,takenFrames)

def FramesToSeconds(frames,fps):
    length = len(frames)
    secLen = int(length/fps)
    sec = []
    for i in range(secLen):
        sec.append(0)
    for i in range(length):
        if frames[i]==1:
            fn = i
            value = int(fn/fps)
            if value<secLen:
                sec[value] = 1
    return sec

def ProjectOutputPhase1(videoURL,summarizationPercentage):
    SKIP = 30
    cap = cv2.VideoCapture(videoURL)
    totalFrames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    cv2.destroyAllWindows()
    split_res = create_two_videos(videoURL, SKIP, 150)

    my_clip = VideoFileClip(videoURL)
    my_clip.audio.write_audiofile(r"myaudio.wav")

    Result1 = ThirdPersonVideoProcessing(videoURL, split_res, SKIP, fps, totalFrames)
    Result2 = RestOfStreamVideoProcessing(videoURL, split_res, SKIP, fps, totalFrames)
    FinalResult = MergeResultsAndSort(Result1, Result2)
    best = get_best_k_frame(FinalResult, totalFrames)
    takenFrames = []
    for i in range(totalFrames):
        takenFrames.append(0)
    cnt = 0
    for b in best:
        st = max(0, b - 10 * fps)
        en = min(totalFrames - 1, b + 5 * fps)
        st = int(st)
        en = int(en)
        for i in range(st, en + 1):
            if takenFrames[i] == 0:
                takenFrames[i] = 1
                cnt += 1
        if cnt / totalFrames >= summarizationPercentage:
            break
    return FramesToSeconds(takenFrames,fps)

def SecondsToFrames(seconds,totalframes,fps):
    secLen = len(seconds)
    frames = []
    for i in range(totalframes):
        s = int(i/fps)
        if s<secLen and seconds[s] ==1:
            frames.append(1)
        else:
            frames.append(0)
    # for i in range(secLen):
    #     if seconds[i] == 1:
    #         st = i*fps
    #         en = (i+1)*fps
    #         for j in range(st,en):
    #             if j < totalframes:
    #                 frames[j] = 1
    return frames


def ProjectOutputPhase2(videoURL,seconds):
    cap = cv2.VideoCapture(videoURL)
    totalFrames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    cv2.destroyAllWindows()
    frames = SecondsToFrames(seconds,totalFrames,fps)
    return write_highlight_video(videoURL,frames)

def BestShotOutput(videoURL):
  SKIP = 30
  cap = cv2.VideoCapture(videoURL)
  totalFrames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
  fps = cap.get(cv2.CAP_PROP_FPS)
  cap.release()
  cv2.destroyAllWindows()
  split_res = create_two_videos(videoURL,SKIP,150)

  my_clip = VideoFileClip(videoURL)
  my_clip.audio.write_audiofile(r"myaudio.wav")

  Result1=ThirdPersonVideoProcessing(videoURL,split_res,SKIP,fps,totalFrames)
  Result2=RestOfStreamVideoProcessing(videoURL,split_res,SKIP,fps,totalFrames)
  FinalResult= MergeResultsAndSort(Result1,Result2)
  best = get_best_k_frame(FinalResult,1)
  takenFrames = []
  for i in range(totalFrames):
    takenFrames.append(0)
  for b in best:
    st = max(0,b-10*fps)
    en = min(totalFrames-1,b+ 10*fps)
    st = int(st)
    en = int(en)
    for i in range(st,en+1):
      if takenFrames[i] ==0:
        takenFrames[i]=1
  return write_highlight_video(videoURL,takenFrames)

if __name__ == '__main__':
    print('Main Script')

