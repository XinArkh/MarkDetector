import cv2
import numpy as np
import os

########## 定义变量 ##########
CAMERA = 0#'walk1.avi'
VIDEOFILE = 'walk-original'
VIDEONUMBER = 1
fps = 20
##############################

##定义鼠标事件##
clicked = False
def onMouse(event, x, y, flags, param):
    global clicked
    if event == cv2.EVENT_LBUTTONUP:
        clicked = True

##开启视频流##
cameraCapture = cv2.VideoCapture(CAMERA)
cv2.namedWindow("walk-original")
cv2.setMouseCallback("walk-original", onMouse)
# 宽高
size = (int(cameraCapture.get(cv2.CAP_PROP_FRAME_WIDTH)),
        int(cameraCapture.get(cv2.CAP_PROP_FRAME_HEIGHT)))

while os.path.exists(VIDEOFILE + str(VIDEONUMBER) + '.avi'):
    VIDEONUMBER = VIDEONUMBER + 1

videoWriter = cv2.VideoWriter(
    VIDEOFILE + str(VIDEONUMBER) + '.avi',
    cv2.VideoWriter_fourcc('I', '4', '2', '0'), fps, size)

##程序主循环##
success, frame = cameraCapture.read()
while success and cv2.waitKey(1) == -1 and not clicked:
    cv2.imshow("walk-original", frame) 
    videoWriter.write(frame)
    success, frame = cameraCapture.read()

cameraCapture.release()
videoWriter.release()
cv2.destroyAllWindows()