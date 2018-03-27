import cv2
import numpy as np
import os
import time

########## 定义变量 ##########
CAMERA = 'walk6.avi'
VIDEOFILE = 'walk'
VIDEONUMBER = 1
fps = 20
TEMPLATE = 'template.jpg'
threshold = 0.85
es = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 4))
background = None
##############################

##定义鼠标事件##
clicked = False
def onMouse(event, x, y, flags, param):
    global clicked
    if event == cv2.EVENT_LBUTTONUP:
        clicked = True

##开启视频流##
cameraCapture = cv2.VideoCapture(CAMERA)
cv2.namedWindow("walk")
cv2.setMouseCallback("walk", onMouse)

size = (int(cameraCapture.get(cv2.CAP_PROP_FRAME_WIDTH)),
        int(cameraCapture.get(cv2.CAP_PROP_FRAME_HEIGHT)))

while os.path.exists(VIDEOFILE + str(VIDEONUMBER) + '.avi'):
    VIDEONUMBER = VIDEONUMBER + 1

##载入模板##
template = cv2.imread(TEMPLATE,cv2.IMREAD_GRAYSCALE)
blurredTemplate = cv2.GaussianBlur(template,(5,5),0)
w, h = template.shape[::-1]
radius = int(max([w/2, h/2]))
# 加入倾斜的模板

##程序主循环##
success, frame = cameraCapture.read()
while success and cv2.waitKey(2) == -1 and not clicked:
    # startTime = time.time()

    if background is None:
        background = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        background = cv2.GaussianBlur(background, (5, 5), 0)
        continue

    frameCopy = frame.copy()
    grayFrame = cv2.cvtColor(frameCopy,cv2.COLOR_BGR2GRAY)
    blurredFrame = cv2.GaussianBlur(grayFrame,(5,5),0)
    # HSVFrame = cv2.cvtColor(blurredFrame,cv2.COLOR_BGR2HSV)

    diff = cv2.absdiff(background, blurredFrame)
    diff = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]
    diff = cv2.dilate(diff, es, iterations=2)
    image, cnts, hierarchy = cv2.findContours(diff.copy(),
        cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    zx, zy, zw, zh = [0, 0, 0, 0]
    for c in cnts:
        if cv2.contourArea(c) < 40000:
            continue
        (zx, zy, zw, zh) = cv2.boundingRect(c)
        cv2.rectangle(frameCopy, (zx, zy), (zx+zw, zy+zh), (0, 255, 0), 2)
        break

    # res是所有像素的评分
    res = cv2.matchTemplate(blurredFrame,blurredTemplate,cv2.TM_CCOEFF_NORMED)

    centers = []
    # loc包括两个array，一个表示行，另一个是列
    loc = np.where( res >= threshold )
    for pt in zip(*loc[::-1]):  # pt是（x，y），按y从小到大排列
        center = (int(pt[0] + w/2), int(pt[1] + h/2))  # （x，y）坐标系
        # 非极大值抑制
        invalidPoint = 0
        if center[0] < zx or center[0] > zx+zw or center[1] < zy or center[1] > zy+zh:
            invalidPoint = 1
        else:
            for testpt in centers:
                if abs(testpt[1] - center[1]) < 10:
                    invalidPoint = 1
        if not invalidPoint:
            centers.append(center)

        # 加核心颜色判断（HSV）
        


    # 画圆
    for chosedPt in centers:
            cv2.circle(frameCopy, chosedPt, radius, (255,0,0), 3)
            cv2.circle(frameCopy, chosedPt, 2, (0,0,255), 3)

    # 连线
    if len(centers) == 3 :
        for i in range(0, len(centers)):
            for j in range(i + 1, len(centers)):
                if centers[i][1] > centers[j][1]:
                    centers[i], centers[j] = centers[j], centers[i]
        [i1, i2, i3] = centers
        cv2.line(frameCopy, i1, i2, (0,0,255),3)
        cv2.line(frameCopy, i2, i3, (0,0,255),3)

    cv2.imshow("walk-original", frame)
    cv2.imshow("walk", frameCopy)
    # cv2.imshow("walk", blurredFrame)
    success, frame = cameraCapture.read()

    # endTime = time.time()
    # print(endTime - startTime)

cameraCapture.release()
cv2.destroyAllWindows()