# Game_Highlighter

a highlight extractor that extracts special moments from a video game video (or stream).

you can feed your video or stream to the system and it will summarize the given video to a smaller one with the best moments and actions.

it is very useful for the streamers who have a lot of long videos as the system can provide them an automatic summary instead of extracting the best moments manually (using video editors or something similar).

The system can extract special moments from any kind of games but it is more accurate when it comes to third person shooter games.

# System UI

## user input
![لقطة الشاشة 2022-09-18 005719](https://user-images.githubusercontent.com/92798033/190877807-33e64130-12c7-4f4b-bf82-c26845a5508f.png)

## editing the extracted best memonts
![لقطة الشاشة 2022-09-18 005622](https://user-images.githubusercontent.com/92798033/190877763-692f50e5-8fb0-496f-9f83-57e0dd68bffd.png)


## the output video
![لقطة الشاشة 2022-09-18 005647](https://user-images.githubusercontent.com/92798033/190877838-aec49315-5db1-4413-814a-b3c52a2f6595.png)


# The solution provided

## extract features from video frames

like: the number of characters, the health bar, the amount of motion etc...

using different computer vision algorithms.

## extract features from audio

like: the loudness and the different amplitudes of the sound etc...

## apply unsupervised machine learning algorithm

apply one-class svm algorithm to assign an outlier score for each frame and sort the frames from the most outliers to the least.

then pick from the sorted list of the frames as many frames as you need.

# Results 

our system scores 7.35 out of 10 depending on users ratings.

