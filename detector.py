import cv2
import numpy as np
import os
import re


class detector:
    """docstring for detector"""

    def __init__(self, mode=0, name='video', number=1):
        self.name = name
        self.number = number
        self.fullname = self.name + str(self.number) + '.avi'
        if mode == 0:
            self.cameraCapture = cv2.VideoCapture(0)
        else:
            self.cameraCapture = cv2.VideoCapture(self.fullname)
        cv2.namedWindow(self.name)
        cv2.setMouseCallback(self.name, self._onMouse)


    def getTemplate(self, Tname='template.jpg'):
        self.Tname = Tname
        self.template = cv2.imread(self.Tname, cv2.IMREAD_GRAYSCALE)
        self.blurredTemplate = cv2.GaussianBlur(self.template, (5,5), 0)
        self.w, self.h = self.template.shape[::-1]
        self.radius = int(max([self.w/2, self.h/2]))


    _clicked = False
    def _onMouse(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONUP:
            self._clicked = True


    _videoFlag = False
    def saveVideo(self, fps=20):
        self._videoFlag = True
        self.fps = fps
        try:
            self.size = (int(self.cameraCapture.get(cv2.CAP_PROP_FRAME_WIDTH)),
                        int(self.cameraCapture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        except Exception as e:
            print(e)
            raise
        if not os.path.isdir('processed'):
            os.makedirs('processed')
        self.videoWriter = cv2.VideoWriter(
            'processed/' + self.fullname,
            cv2.VideoWriter_fourcc('I', '4', '2', '0'), self.fps, self.size)


    _dataFlag = False
    def saveData(self):
        self._dataFlag = True
        if not os.path.isdir('data'):
            os.makedirs('data')
        self.position = open('data/' + self.name + str(self.number) + '.txt', 
                'a', encoding='utf-8')


    es = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 4))
    def _Rect(self, area):
        diff = cv2.absdiff(self.bg, self.blurredFrame)
        diff = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]
        diff = cv2.dilate(diff, self.es, iterations=2)
        image, cnts, hierarchy = cv2.findContours(diff,
            cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        zx, zy, zw, zh = [0, 0, 0, 0]
        for c in cnts:
            if cv2.contourArea(c) < area:
                continue
            (zx, zy, zw, zh) = cv2.boundingRect(c)
            cv2.rectangle(self.frameCopy, (zx, zy), \
                (zx+zw, zy+zh), \
                (0, 255, 0), 2)
            break
        return zx, zy, zw, zh


    def _filter(self, threshold):
        centers = []
        loc = np.where( self.res >= threshold )
        for pt in zip(*loc[::-1]):  # pt是（x，y），按y从小到大排列
            # center是(x，y)坐标系
            center = (int(pt[0] + self.w/2), int(pt[1] + self.h/2))

            invalidPoint = False
            # 判断目标点是否在前景区域范围内
            if center[0] < self.zx or center[0] > self.zx+self.zw \
                or center[1] < self.zy or center[1] > self.zy+self.zh:
                invalidPoint = True
            # 在前景区域，则判断其它细分条件
            elif centers:
                # 非极大值抑制
                for testpt in centers:
                    # 判断：高度不能相近
                    # if abs(testpt[1] - center[1]) < 20:
                    #     invalidPoint = True
                    #     break

                    # 判断：距离不能相近
                    if ((testpt[0] - center[0])**2 + \
                        (testpt[1] - center[1])**2)**0.5 < 30:
                        invalidPoint = True
                        break
            if not invalidPoint:
                centers.append(center)
        return centers


    def _draw(self, centers):
        # 画圆
        for chosedPt in centers:
                cv2.circle(self.frameCopy, chosedPt, self.radius, (255,0,0), 3)
                cv2.circle(self.frameCopy, chosedPt, 2, (0,0,255), 3)

        # 连线
        if len(centers) == 3:
            # 三个点根据y坐标从上（小）到下（大）进行冒泡排序
            for i in range(0, len(centers)-1):
                for j in range(i + 1, len(centers)):
                    if centers[i][1] > centers[j][1]:
                        centers[i], centers[j] = centers[j], centers[i]
            [i1, i2, i3] = centers
            cv2.line(self.frameCopy, i1, i2, (0,0,255),3)
            cv2.line(self.frameCopy, i2, i3, (0,0,255),3)

    def _save(self, centers):
        if self._videoFlag:
            self.videoWriter.write(self.frameCopy)

        if self._dataFlag:
            if len(centers) == 3:
                self.position.write(str(centers)+'\n')
                print(str(centers)+'\n')
            else:
                self.position.write(str([(0, 0), (0, 0), (0, 0)])+'\n')
                print(str([(0, 0), (0, 0), (0, 0)])+'\n')


    def _show(self):
        cv2.imshow(self.name, self.frame)
        cv2.imshow(self.name+'-processed', self.frameCopy)  


    def _close(self):
        try:
            self.cameraCapture.release()
            self.videoWriter.release()
            cv2.destroyAllWindows()
            self.position.close()
        except:
            raise


    def run(self, threshold=0.9, bgPath=None, area=40000):
        self.bgPath = bgPath
        self.bg = None
        if self.bgPath:
            self.bg = cv2.imread(self.bgPath, cv2.IMREAD_GRAYSCALE)
            self.bg = cv2.GaussianBlur(self.bg, (5, 5), 0)

        success, self.frame = self.cameraCapture.read()
        while success and cv2.waitKey(1) == -1:
            if self._clicked:
                self.position.write('***Start***'+'\n')
                print('***Start***'+'\n')
                self._clicked = False

            if str(self.bg) == 'None':
                self.bg = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
                self.bg = cv2.GaussianBlur(self.bg, (5, 5), 0)
                continue

            self.frameCopy = self.frame.copy()
            self.grayFrame = cv2.cvtColor(self.frameCopy,cv2.COLOR_BGR2GRAY)
            self.blurredFrame = cv2.GaussianBlur(self.grayFrame,(5,5),0)

            self.zx, self.zy, self.zw, self.zh = self._Rect(area)
            # res是当前帧上所有像素的评分构成的一个矩阵
            self.res = cv2.matchTemplate(self.blurredFrame,self.blurredTemplate,\
                cv2.TM_CCOEFF_NORMED)

            centers = self._filter(threshold)
            self._draw(centers)
            self._save(centers)
            self._show()

            success, self.frame = self.cameraCapture.read()

        self._close()


    def data2angle(self, right=True):
        f = open('data/' + self.name + str(self.number) + '.txt', 
                'r', encoding='utf-8')
        if not os.path.isdir('angle'):
            os.makedirs('angle')
        output = open('angle/' + self.name + str(self.number) + '.txt', 
        'a', encoding='utf-8')
        lines = f.readlines()
        for line in lines:
            print(line)
            if line == '***Start***\n':
                output.write(line)
                continue
            items = re.sub('\[|\(| |\)|\]|\n', '', line)
            items = re.split(',' ,items)
            # x1, y1, x2, y2, x3, y3 = [1, 0, 0, 1, 1, 1]
            x1, y1, x2, y2, x3, y3 = [int(a) for a in items]
            # 以下为（x，y）坐标系
            vector0 = np.array([0,1])
            s0 = np.sqrt(vector0.dot(vector0))

            vector1 = np.array([x2-x1, y2-y1])
            s1 = np.sqrt(vector1.dot(vector1))

            vector2 = np.array([x3-x2, y3-y2])
            s2 = np.sqrt(vector2.dot(vector2))

            cos_t = vector0.dot(vector1)/(s0*s1)
            cos_a = vector1.dot(vector2)/(s1*s2)
            # print(cos_t, cos_a)
            angle_t = np.arccos(cos_t)*180/np.pi
            angle_a = np.arccos(cos_a)*180/np.pi
            # print(angle_t, angle_a)

            angle_a = abs(angle_a)
            if right:
                if x2 < x1:
                    angle_t = -abs(angle_t)
            else:
                if x2 > x1:
                    angle_t = -abs(angle_t)

            output.write(str(angle_t)+' '+str(angle_a)+'\n')

        f.close()
        output.close()


if __name__ == '__main__':
    d = detector(0, 'walk', 1)
    d.getTemplate('template.jpg')
    # d.saveVideo()
    # d.saveData()
    d.run(threshold=0.8)
    # d.data2angle(right=True)
