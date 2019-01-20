import re
import numpy as np


NUMBER = '3'

f = open('walk'+NUMBER+'.txt', 'r')
output = open('angles/angles'+NUMBER+'.txt', 
        'a', encoding='utf-8')
lines = f.readlines()
for line in lines:
    print(line)
    items = re.sub('\[|\(| |\)|\]|\n', '', line)
    items = re.split(',' ,items)
    x1, y1, x2, y2, x3, y3 = [int(a) for a in items]
    # x1, y1, x2, y2, x3, y3 = [1, 0, 0, 1, 1, 1]
    vector0 = np.array([0,1]); s0 = np.sqrt(vector0.dot(vector0))
    vector1 = np.array([x2-x1, y2-y1]); s1 = np.sqrt(vector1.dot(vector1))
    vector2 = np.array([x3-x2, y3-y2]); s2 = np.sqrt(vector2.dot(vector2))
    cos_t = vector0.dot(vector1)/(s0*s1)
    cos_a = vector1.dot(vector2)/(s1*s2)
    # print(cos_a, cos_r)
    angle_t = np.arccos(cos_t)*180/np.pi
    angle_a = np.arccos(cos_a)*180/np.pi
    # print(angle_a, angle_r)

    angle_a = abs(angle_a)

    right = 1

    if right:
        if x2 < x1:
            angle_t = -abs(angle_t)
    else:
        if x2 > x1:
            angle_t = -abs(angle_t)

    output.write(str(angle_t)+' '+str(angle_a)+'\n')

f.close()
output.close()