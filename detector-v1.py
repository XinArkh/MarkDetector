import cv2
import numpy as np
import os
import re
import time
import math

########## 定义变量 ##########
VIDEONUMBER = 1
VIDEOFILE = 'walk-original'
CAMERA = VIDEOFILE + str(VIDEONUMBER) + '.avi'
fps = 20
TEMPLATE = 'template.jpg'
threshold = 0.9
es = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 4))
background = None
##############################

##定义鼠标事件##
clicked = False
def onMouse(event, x, y, flags, param):
    global clicked
    if event == cv2.EVENT_LBUTTONUP:
        clicked = True

def rgb2hsv(r, g, b):
    r, g, b = r/255.0, g/255.0, b/255.0
    mx = max(r, g, b)
    mn = min(r, g, b)
    df = mx-mn
    if mx == mn:
        h = 0
    elif mx == r:
        h = (60 * ((g-b)/df) + 360) % 360
    elif mx == g:
        h = (60 * ((b-r)/df) + 120) % 360
    elif mx == b:
        h = (60 * ((r-g)/df) + 240) % 360
    if mx == 0:
        s = 0
    else:
        s = df/mx
    v = mx
    return h, s, v

##开启视频流##
cameraCapture = cv2.VideoCapture(CAMERA)
cv2.namedWindow("walk-original")
cv2.setMouseCallback("walk-original", onMouse)
# 宽高
size = (int(cameraCapture.get(cv2.CAP_PROP_FRAME_WIDTH)),
        int(cameraCapture.get(cv2.CAP_PROP_FRAME_HEIGHT)))

while os.path.exists('original/' + VIDEOFILE + \
    str(VIDEONUMBER) + '.avi'):
    VIDEONUMBER = VIDEONUMBER + 1

# 原始视频
videoWriter1 = cv2.VideoWriter(
    'original/' + VIDEOFILE + str(VIDEONUMBER) + '.avi',
    cv2.VideoWriter_fourcc('I', '4', '2', '0'), fps, size)
# 处理后视频
videoWriter2 = cv2.VideoWriter(
    'processed/' + VIDEOFILE + str(VIDEONUMBER) + '.avi',
    cv2.VideoWriter_fourcc('I', '4', '2', '0'), fps, size)
# 记录角度数据的txt文件
position = open('angle/' + VIDEOFILE + str(VIDEONUMBER) + '.txt', 
        'a', encoding='utf-8')

##载入模板##
template = cv2.imread(TEMPLATE,cv2.IMREAD_GRAYSCALE)
blurredTemplate = cv2.GaussianBlur(template,(5,5),0)
w, h = template.shape[::-1]
radius = int(max([w/2, h/2]))

# 优化方向：加入倾斜的模板，形成一组模板

##程序主循环##
started = False
success, frame = cameraCapture.read()
# startTime = time.time()
while success and cv2.waitKey(1) == -1:
    if clicked:
        position.write('***Start***'+'\n')
        print('***Start***'+'\n')
        clicked = False

    # 设定背景帧（默认第一帧为背景帧）
    if background is None:
        background = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        background = cv2.GaussianBlur(background, (5, 5), 0)
        continue

    frameCopy = frame.copy()
    grayFrame = cv2.cvtColor(frameCopy,cv2.COLOR_BGR2GRAY)
    blurredFrame = cv2.GaussianBlur(grayFrame,(5,5),0)

    # 优化方向：用HSV颜色格式辅助判断
    # HSVFrame = cv2.cvtColor(Frame的另一个copy,cv2.COLOR_BGR2HSV)

    # 前景分割，找到运动区域
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
        cv2.rectangle(frameCopy, (zx, zy), (zx+zw, zy+zh), \
            (0, 255, 0), 2)
        break

    # res是当前帧上所有像素的评分矩阵
    res = cv2.matchTemplate(blurredFrame,blurredTemplate,\
        cv2.TM_CCOEFF_NORMED)

    centers = []
    # loc包括两个array，一个表示行，另一个是列
    loc = np.where( res >= threshold )
    for pt in zip(*loc[::-1]):  # pt是（x，y），按y从小到大排列
        center = (int(pt[0] + w/2), int(pt[1] + h/2)) #（x，y）坐标系
        # if(center[0] >= 640 or center[1] >= 480):
        #     continue
        invalidPoint = 0
        # 判断目标点是否在前景区域范围内
        if center[0] < zx or center[0] > zx+zw \
            or center[1] < zy or center[1] > zy+zh:
            invalidPoint = 1
        elif centers:
            # 非极大值抑制
            for testpt in centers:
                # 判断：高度不能相近
                # if abs(testpt[1] - center[1]) < 20:
                #     invalidPoint = 1
                #     break

                # 判断：距离不能相近
                if ((testpt[0] - center[0])**2 + \
                    (testpt[1] - center[1])**2)**0.5 < 30:
                    invalidPoint = 1
                    break

                # 核心颜色判断（HSV）
                # b, g, r = frameCopy[center[1]-1][center[0]-1]
                # h, s, v = rgb2hsv(b, g, r)
                # if s < 0.1 or v < 0.9:
                #     invalidPoint = 1
                #     break

        if not invalidPoint:
            centers.append(center)        


    # 画圆
    for chosedPt in centers:
            cv2.circle(frameCopy, chosedPt, radius, (255,0,0), 3)
            cv2.circle(frameCopy, chosedPt, 2, (0,0,255), 3)


    # 连线
    if len(centers) == 3:
        for i in range(0, len(centers)):
            for j in range(i + 1, len(centers)):
                if centers[i][1] > centers[j][1]:
                    centers[i], centers[j] = centers[j], centers[i]
        [i1, i2, i3] = centers
        cv2.line(frameCopy, i1, i2, (0,0,255),3)
        cv2.line(frameCopy, i2, i3, (0,0,255),3)
        # 保存角度数据
        position.write(str(centers)+'\n')
        print(str(centers)+'\n')
    else:
        position.write(str([(0, 0), (0, 0), (0, 0)])+'\n')
        print(str([(0, 0), (0, 0), (0, 0)])+'\n')

    cv2.imshow("walk-original", frame)
    cv2.imshow("walk-processed", frameCopy)   
    videoWriter1.write(frame)   
    videoWriter2.write(frameCopy)
    success, frame = cameraCapture.read()

    # currentTime = time.time()
    # print(currentTime - startTime)

cameraCapture.release()
videoWriter1.release()
videoWriter2.release()
cv2.destroyAllWindows()
position.close()