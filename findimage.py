from distutils.filelist import FileList
from operator import concat
from time import time
import cv2
from cv2 import split
import numpy as np
from matplotlib import pyplot as plt
import datetime
import os
import subprocess

clipCt = 0
fps = 30
killFrameArray = []
secondArray = []
frameArray = []

def getFiles(path):
    return os.listdir(path)

def process_img(img_rgb, template, count):
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    w, h = template.shape[::-1]

    res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
    threshold = 0.8
    loc = np.where( res >= threshold)
    for pt in zip(*loc[::-1]):
        if(len(killFrameArray) == 0 or count - killFrameArray[len(killFrameArray)-1] > (fps * 5.5)):
            killFrameArray.append(count)
            cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)
            cv2.imwrite('./log/res'+str(count)+'.png',img_rgb)  
            print(count)

def editing(times, fileName):
    try:
        txtFile = open("./output/temp.txt","a")
        ct=0
        for i in range(len(times)-1):
            print(times[i+1], times[i])
            if i % 2 != 1:
                min = int(float(times[i+1].split(':')[1]))
                if(min == 1):
                    recordSec = (60 - int(float(times[i].split(':')[2]))) + int(float(times[i+1].split(':')[2]))
                else:
                    recordSec = int(float(times[i+1].split(':')[2])) - int(float(times[i].split(':')[2]))
                if(recordSec<10):
                    secStr = '0' + str(recordSec)
                else:
                    secStr = str(recordSec)
                ct+=1
                command = "ffmpeg -i ./footage/"+fileName+" -ss "+times[i]+" -t 00:00:"+secStr+" -async 1 ./output/"+fileName.replace('.mp4','')+"-cut-"+str(ct)+".mp4"
                print(command)
                os.system('cmd /c'+command)

                filterCommand = "ffmpeg -i ./output/"+fileName.replace('.mp4','')+"-cut-"+str(ct)+".mp4 -vf fade=t=in:st=0:d=0.5,fade=t=out:st="+str(int(secStr)-0.5)+":d=0.5' -c:a copy ./output/"+fileName.replace('.mp4','')+"-fade-"+str(ct)+".mp4"
                print(filterCommand)
                os.system('cmd /c'+filterCommand)
                txtFile.write("file '"+fileName.replace('.mp4','')+"-fade-"+str(ct)+".mp4'\n")           
            else:
                continue
        txtFile.write("file 'dolan.mp4'\n")      
        txtFile.close()         
        return True
    except:
        return False

# def detectAgent():
#     vdoFiles = getFiles("F://ffmpeg-5.0.1-essentials_build//bin//footage")
#     iconFiles = getFiles("F://ffmpeg-5.0.1-essentials_build//bin//asset//skill-icon")
#     for vdoFile in vdoFiles:
#         vidcap = cv2.VideoCapture('./footage/'+vdoFile)
#         for iconFile in iconFiles:
#             template = cv2.imread('./asset/skill-icon/'+iconFile,0)
#             success,image = vidcap.read()
#             if not success: break         # loop and a half construct is useful
#             img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

#             w, h = template.shape[::-1]

#             res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
#             threshold = 0.5
#             loc = np.where( res >= threshold)
#             for pt in zip(*loc[::-1]):
#                 cv2.rectangle(image, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)
#                 cv2.imwrite('res.png',image)             

def main():
    print('Running...')
    files = getFiles("F://ffmpeg-5.0.1-essentials_build//bin//footage")
    for file in files:
        killFrameArray.clear()
        secondArray.clear()
        frameArray.clear()
        vidcap = cv2.VideoCapture('./footage/'+file)
        template = cv2.imread('./asset/'+file.split('-')[1]+'.PNG',0)  # open template only once
        count = 0
        while True:
            success,image = vidcap.read()
            if not success: break         # loop and a half construct is useful
            process_img(image, template, count)
            count += 1
        print(killFrameArray)
        for frame in killFrameArray:
            startFrame = frame-(fps*4)
            endFrame = frame+(fps*3)
            if len(frameArray)==0:
                frameArray.append(startFrame)
            elif(frameArray[len(frameArray)-1]  > startFrame):
                frameArray.pop()
            elif(frameArray[len(frameArray)-1]  < startFrame and startFrame - frameArray[len(frameArray)-1] <= 30):
                frameArray.pop()
            else:
                frameArray.append(startFrame)
            frameArray.append(endFrame)
        print(frameArray)
        
        for frame in frameArray:  
            sec = frame/fps         
            secondArray.append(str(datetime.timedelta(seconds = sec)))
        print(secondArray)
        editing(secondArray, file)
    joinCommand = "ffmpeg -f concat -safe 0 -i ./output/temp.txt -c copy finalVdo.mp4"
    os.system('cmd /c'+joinCommand)

    for file in getFiles("F://ffmpeg-5.0.1-essentials_build//bin//output"):
        if(file != "dolan.mp4"):
            os.remove("./output/"+file)
    
main()

# detectAgent()

# editing(['0:00:21.3333','0:00:28.3333','0:00:35.3333','0:00:47.3333'],'sova-1.mp4')

# getFiles()