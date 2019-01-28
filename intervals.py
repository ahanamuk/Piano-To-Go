'''On the first intervals screen, users can select which intervals they would like to practice. An interval is the distance between two notes. On the following screen, clicking the “next” button will produce two notes. Once the user knows which interval it is, they can click on the answer. If they get it wrong, then “maybe next time” will be played and if they get it right then “nice work” will be played. Users can also replay intervals and view and reset their score'''

import threading
import pyaudio
import wave
from array import array
from struct import pack
import numpy as np
import time


####################################
# PyAudio
####################################

def pausePlay(file, data):
    frame = data.frame
    CHUNK = 1024

    wf = wave.open(file, 'rb')

    p = pyaudio.PyAudio()

    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    data1 = wf.readframes(CHUNK)
    while len(data1) > 0:
        stream.write(data1)
        data1 = wf.readframes(CHUNK)
        updateLeapMotionData(data)
        printLeapMotionData(data)
        if data.pause:
            break

    stream.stop_stream()
    stream.close()

    p.terminate()
    

def play(file):
    
    CHUNK = 1024

    wf = wave.open(file, 'rb')

    p = pyaudio.PyAudio()

    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    data = wf.readframes(CHUNK)

    while len(data) > 0:
        stream.write(data)
        data = wf.readframes(CHUNK)
        

    stream.stop_stream()
    stream.close()

    p.terminate()
    
def worker(file):
    print threading.currentThread().getName(), 'Starting'
    play(file)
    print threading.currentThread().getName(), 'Exiting'
    
def note(data):
    play("pianoNotes/C.wav")

####################################
# Leap Motion
####################################

import random, math
import os, sys, inspect, thread, time
sys.path.insert(0, "C:\Users\ahanamukhopadhyay\Downloads\LeapDeveloperKit_2.3.1+31549_mac\LeapSDK\lib/x86")

import Leap
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture

import random, math
from Tkinter import *


def init(data):
    data.mode = "pickInterval"
    
    data.controller = Leap.Controller()
    data.frame = data.controller.frame()
    data.fingerNames = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
    data.boneNames = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']
    data.pause = False
    data.rPointerPos = (data.width//2, data.height//2)
    data.lPointerPos = (data.width//2, data.height//2)
    data.lHandOnScreen = False
    data.rHandOnScreen = False
    data.rFingerLst = [(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0)]
    
    data.selection = [0,"nothing"]
    data.selectionHand = [[0,"nothing"], [0,"nothing"], [0,"nothing"], [0,"nothing"], [0,"nothing"]]
    
    data.keysPlayed = []
    data.pauseButton = [20, 20, 50, 50] #x0, y0, x1, y1
    data.terminateProg = False
    
    data.keyToSound = dict({\
    (0, "white"): "pianoNotes/C.wav", \
    (1, "white"): "pianoNotes/D.wav",\
    (2, "white"): "pianoNotes/E.wav",\
    (3, "white"): "pianoNotes/F.wav",\
    (4, "white"): "pianoNotes/G.wav",\
    (5, "white"): "pianoNotes/A.wav",\
    (6, "white"): "pianoNotes/B.wav",\
    (7, "white"): "pianoNotes/C2.wav",\
    (8, "white"): "pianoNotes/D2.wav",\
    (9, "white"): "pianoNotes/E2.wav",\
    (0, "black"): "pianoNotes/C#.wav",\
    (1, "black"): "pianoNotes/Eb.wav",\
    (3, "black"): "pianoNotes/F#.wav",\
    (4, "black"): "pianoNotes/Ab.wav",\
    (5, "black"): "pianoNotes/Bb.wav",\
    (7, "black"): "pianoNotes/C#2.wav",\
    (8, "black"): "pianoNotes/Eb2.wav"})
    
    data.playedOnce = False
    
    data.intervals = dict({\
    "m2": [["C", "C#"], ["E", "F#"], ["G", "Ab"], ["B", "C2"]],\
    "M2": [["C", "D"], ["D", "E"], ["E", "F#"], ["F", "G"]],\
    "m3": [["C", "Eb"], ["E", "G"], ["D", "F"], ["C2", "Eb2"]],\
    "M3": [["C", "E"], ["D", "F#"], ["C2", "E2"], ["G", "B"]],\
    "P4": [["E", "A"], ["D", "G"], ["C#", "F#"], ["Eb", "Ab"]],\
    "P5": [["C", "G"], ["E", "B"], ["A", "E2"], ["Eb", "Bb"]],\
    "M6": [["C", "A"], ["D", "B"], ["E", "C#2"], ["C#", "Bb"]],\
    "M7": [["C", "B"], ["C#", "C2"], ["D", "C#2"], ["E", "Eb2"]],\
    "P8": [["C", "C2"], ["D", "D2"], ["E", "E2"], ["C#", "C#2"]]})
    
    data.intervalsIndex = dict({\
    (1,1): "M2", (2,1): "M3", (3,1): "M6", (4,1): "M7",\
    (1,2): "m2", (2,2): "m3", (3,2): "m6", (4,2): "m7",\
    (1,3): "P4", (2,3): "P5", (3,3): "P8"})
    
    data.y0Interval = 0
    data.y1Interval = 0
    data.y0Major = 0
    data.y1Major = 0
    data.y0Minor = 0
    data.y1Minor = 0
    data.y0Perfect = 0
    data.y1Perfect = 0
    
    data.x0Intervals = 0
    data.x1Intervals = 0
    
    data.lBoxHeight = 50
    data.lBoxWidth = 75
    data.bBoxWidth = 200
    data.gap = 25
    
    data.currSel = [-1,0]
    data.allSel = set()
    
    #mainPg variables
    data.currSelMP = [-1,0]
    data.currIntervalIndex = (-1,-1)
    data.currIntervalNote1 = None
    data.currIntervalNote2 = None
    
    data.x0NextIntervalButton = data.width*5/6
    data.x1NextIntervalButton = data.width*5/6 + 100
    data.y0NextIntervalButton = 30
    data.y1NextIntervalButton = 90
    
    data.x0ReplayIntervalButton = data.width*5/6
    data.x1ReplayIntervalButton = data.width*5/6 + 100
    data.y0ReplayIntervalButton = 110
    data.y1ReplayIntervalButton = 170
    
    
####################################
# mode dispatcher
####################################

def mousePressed(event, data):
    if (data.mode == "pickInterval"): pickIntervalMousePressed(event, data)
    elif (data.mode == "mainPg"):   mainPgMousePressed(event, data)
    elif (data.mode == "help"):       helpMousePressed(event, data)

def keyPressed(event, data):
    if (data.mode == "pickInterval"): pickIntervalKeyPressed(event, data)
    elif (data.mode == "mainPg"):   mainPgKeyPressed(event, data)
    elif (data.mode == "help"):       helpKeyPressed(event, data)

def timerFired(data):
    if (data.mode == "pickInterval"): pickIntervalTimerFired(data)
    elif (data.mode == "mainPg"):   mainPgTimerFired(data)
    elif (data.mode == "help"):       helpTimerFired(data)

def redrawAll(canvas, data):
    if (data.mode == "pickInterval"): pickIntervalRedrawAll(canvas, data)
    elif (data.mode == "mainPg"):   mainPgRedrawAll(canvas, data)
    elif (data.mode == "help"):       helpRedrawAll(canvas, data)

####################################
# pickInterval mode
####################################

def pickIntervalMousePressed(e, data):
    getButtonPressed(e, data)
    
    #Cliking the same interval twice deselects it
    if tuple(data.currSel) not in data.allSel:
        data.allSel.add(tuple(data.currSel))
    elif tuple(data.currSel) in data.allSel and e.x > data.x0Intervals+50 and e.x < data.x1Intervals and e.y < data.y1Perfect and e.y > data.y0Major:
        data.allSel.remove(tuple(data.currSel))
        

def pickIntervalKeyPressed(event, data):
    if event.keysym == "Return":
        data.mode = "mainPg"
        print data.mode

def pickIntervalTimerFired(data):
    pass

def pickIntervalRedrawAll(canvas, data):
    x0 = data.width/2 - 300 #left of intervals box
    y1 = data.height/4 + 130 
    gap = data.gap
    lBoxHeight = data.lBoxHeight
    lBoxWidth = data.lBoxWidth
    bBoxWidth = data.bBoxWidth
    
    #Intervals box
    data.x0Intervals = x0
    data.x1Intervals = x0 + 600
    data.y0Interval = data.height/4 + 70
    data.y1Interval = y1
    
    rgb = (76, 16, 54)
    rgb1 = (238, 108, 77)
    f = "#%02x%02x%02x" % rgb
    f1 = "#%02x%02x%02x" % rgb1
    canvas.create_text(data.width/2, 65, text="Select the intervals you want to", font='Palatino 40 bold', fill = f)
    canvas.create_text(data.width/2, 110, text="practice recognizing by ear", font='Palatino 40 bold', fill = f)
    canvas.create_text(data.width/2, 185, text="Go to the next page to start practicing!", font='Palatino 25', fill=f)
    roundRectangle(canvas, data, x0, data.y0Interval, data.width/2 + 300, y1, [0,0])
    canvas.create_text((x0 + data.width/2 + 300)/2, (data.y0Interval+data.y1Interval)/2, text="Intervals", font="Palatino 40 bold", fill="white")
    
    #Major 
    yStart = y1 + gap
    yEnd = y1 + gap + lBoxHeight
    data.y0Major = yStart
    data.y1Major = yEnd
    roundRectangle(canvas, data, x0, yStart, x0 + bBoxWidth, yEnd, [0,1])
    canvas.create_text((x0 + x0 + bBoxWidth)/2, (yStart + yEnd)/2, text="Major", font="Palatino 25", fill="white")
    #M2
    roundRectangle(canvas, data, x0 + bBoxWidth + gap, yStart, x0 + gap + bBoxWidth + \
    lBoxWidth, yEnd, [1,1])
    canvas.create_text((2*x0 + bBoxWidth*2 + gap*2 + lBoxWidth)/2, (yStart + yEnd)/2, text="M2", font="Palatino 25", fill="white")
    #M3
    roundRectangle(canvas, data, x0 + bBoxWidth + 2*gap + lBoxWidth, yStart, x0 + bBoxWidth + 2*gap + 2*lBoxWidth, yEnd, [2,1])
    canvas.create_text((2*x0 + bBoxWidth*2 + gap*4 + 3*lBoxWidth)/2, (yStart + yEnd)/2, text="M3", font="Palatino 25", fill="white")
    #M6
    roundRectangle(canvas, data, x0 + bBoxWidth + 3*gap + 2*lBoxWidth, yStart, x0 + bBoxWidth + 3*gap + 3*lBoxWidth, yEnd, [3,1])
    canvas.create_text((2*x0 + bBoxWidth*2 + gap*6 + 5*lBoxWidth)/2, (yStart + yEnd)/2, text="M6", font="Palatino 25", fill="white")
    #M7
    roundRectangle(canvas, data, x0 + bBoxWidth + 4*gap + 3*lBoxWidth, yStart, x0 + bBoxWidth \
    + 4*gap + 4*lBoxWidth, yEnd, [4,1])
    canvas.create_text((2*x0 + bBoxWidth*2 + gap*8 + 7*lBoxWidth)/2, (yStart + yEnd)/2, text="M7", font="Palatino 25", fill="white")
    
    #Minor box
    yStart =  y1 + 2*gap + lBoxHeight
    yEnd = y1 + 2*gap + 2*lBoxHeight
    data.y0Minor = yStart
    data.y1Minor = yEnd
    roundRectangle(canvas, data, x0, yStart, x0 + bBoxWidth, yEnd, [0,2])
    canvas.create_text((x0 + x0 + bBoxWidth)/2, (yStart+yEnd)/2, text="Minor", font="Palatino 25 bold", fill="white")
    #m2
    roundRectangle(canvas, data, x0 + bBoxWidth + gap, yStart, x0 + gap + bBoxWidth + \
    lBoxWidth, yEnd, [1,2])
    canvas.create_text((2*x0 + bBoxWidth*2 + gap*2 + lBoxWidth)/2, (yStart + yEnd)/2, text="m2", font="Palatino 25", fill="white")
    #m3
    roundRectangle(canvas, data, x0 + bBoxWidth + 2*gap + lBoxWidth, yStart, x0 + bBoxWidth + \
    2*gap + 2*lBoxWidth, yEnd, [2,2])
    canvas.create_text((2*x0 + bBoxWidth*2 + gap*4 + 3*lBoxWidth)/2, (yStart + yEnd)/2, text="m3", font="Palatino 25", fill="white")
    #m6
    roundRectangle(canvas, data, x0 + bBoxWidth + 3*gap + 2*lBoxWidth, yStart, x0 + bBoxWidth \
    + 3*gap + 3*lBoxWidth, yEnd, [3,2])
    canvas.create_text((2*x0 + bBoxWidth*2 + gap*6 + 5*lBoxWidth)/2, (yStart + yEnd)/2, text="m6", font="Palatino 25", fill="white")
    #m7
    roundRectangle(canvas, data, x0 + bBoxWidth + 4*gap + 3*lBoxWidth, yStart, x0 + bBoxWidth \
    + 4*gap + 4*lBoxWidth, yEnd, [4,2])
    canvas.create_text((2*x0 + bBoxWidth*2 + gap*8 + 7*lBoxWidth)/2, (yStart + yEnd)/2, text="m7", font="Palatino 25", fill="white")
    
    #Perfect box
    yStart =  y1 + 3*gap + 2*lBoxHeight
    yEnd = y1 + 3*gap + 3*lBoxHeight
    data.y0Perfect = yStart
    data.y1Perfect = yEnd
    roundRectangle(canvas, data, x0, yStart, x0 + bBoxWidth, yEnd, [0,3])
    canvas.create_text((x0 + x0 + bBoxWidth)/2, (yStart+yEnd)/2, text="Perfect", font="Palatino 25 bold", fill="white")
    #3 little boxes in perfect
    roundRectangle(canvas, data, x0 + bBoxWidth + gap, yStart, x0 + gap + bBoxWidth + \
    lBoxWidth, yEnd, [1,3])
    canvas.create_text((2*x0 + bBoxWidth*2 + gap*2 + lBoxWidth)/2, (yStart + yEnd)/2, text="P4", font="Palatino 25", fill="white")
    roundRectangle(canvas, data, x0 + bBoxWidth + 2*gap + lBoxWidth, yStart, x0 + bBoxWidth + \
    2*gap + 2*lBoxWidth, yEnd, [2,3])
    canvas.create_text((2*x0 + bBoxWidth*2 + gap*4 + 3*lBoxWidth)/2, (yStart + yEnd)/2, text="P5", font="Palatino 25", fill="white")
    roundRectangle(canvas, data, x0 + bBoxWidth + 3*gap + 2*lBoxWidth, yStart, x0 + bBoxWidth \
    + 3*gap + 3*lBoxWidth, yEnd, [3,3])
    canvas.create_text((2*x0 + bBoxWidth*2 + gap*6 + 5*lBoxWidth)/2, (yStart + yEnd)/2, text="P8", font="Palatino 25", fill="white")
    

                       
####################################
# mainPg mode
####################################

def mainPgMousePressed(event, data):
    intervalClicked = getButtonPressedMP(event, data)
    
    #plays next interval if button pressed
    if event.x > data.x0NextIntervalButton and event.x < \
    data.x1NextIntervalButton and event.y > data.y0NextIntervalButton and \
    event.y < data.y1NextIntervalButton:
        if len(data.allSel) != 0:
            index = random.choice(list(data.allSel))
            print index
            data.currIntervalIndex = index
            interval = data.intervalsIndex[index] 
            notes = random.choice(data.intervals[interval])
            note1, note2 = notes[0], notes[1]
            file1 = "pianoNotes/" + note1 + ".wav"
            file2 = "pianoNotes/" + note2 + ".wav"
            data.currIntervalNote1 = file1
            data.currIntervalNote2 = file2
            
            t = threading.Thread(name='worker', target=worker, args=(file1,))
            t.start()
            
            time.sleep(1)
            
            w = threading.Thread(name='worker', target=worker, args=(file2,))
            w.start()
    #if replay button clicked
    elif event.x > data.x0ReplayIntervalButton and event.x < \
    data.x1ReplayIntervalButton and event.y > data.y0ReplayIntervalButton and \
    event.y < data.y1ReplayIntervalButton:
        if data.currIntervalNote1 != None and data.currIntervalNote2 != None:
            a = threading.Thread(name='worker', target=worker, \
            args=(data.currIntervalNote1,))
            a.start()
            
            time.sleep(1)
            
            b = threading.Thread(name='worker', target=worker, \
            args=(data.currIntervalNote2,))
            b.start()
    #if reset score button clicked
    elif event.x > data.x0ResetIntervalButton and event.x < \
    data.x1ResetIntervalButton and event.y > data.y0ResetIntervalButton and \
    event.y < data.y1ResetIntervalButton:
        data.correctIntervals = 0
        data.wrongIntervals = 0
        
    #if selection is correct
    if data.currIntervalIndex == tuple(data.currSelMP):
        file1 = "nice-work.wav"
        c = threading.Thread(name='worker', target=worker, args=(file1,))
        c.start()
        data.correctIntervals += 1
        data.currSelMP = [0,0]
    #answer is incorrect
    elif data.currIntervalIndex != tuple(data.currSelMP) and intervalClicked:
        file1 = "maybe-next-time.wav"
        c = threading.Thread(name='worker', target=worker, args=(file1,))
        c.start()
        data.wrongIntervals += 1
        data.currSelMP = [0,0]
        
        

def mainPgKeyPressed(event, data):
    if event.keysym == "b":
        data.mode = "pickInterval"

def mainPgTimerFired(data):
    pass

def roundRectangleButtons(canvas, data, x1, y1, x2, y2, radius=25):
    #https://stackoverflow.com/questions/44099594/how-to-make-a-tkinter-canvas-rectangle-with-rounded-corners
    points = [x1+radius, y1, x1+radius, y1, x2-radius, y1, x2-radius, y1, \
    x2, y1, x2, y1+radius, x2, y1+radius, x2, y2-radius, x2, y2-radius, x2, \
    y2, x2-radius, y2, x2-radius, y2, x1+radius, y2, x1+radius, y2, x1, y2,\
    x1, y2-radius, x1, y2-radius, x1, y1+radius, x1, y1+radius, x1, y1]
    
    rgb = (238, 108, 77)
    fColor = "#%02x%02x%02x" % rgb
    
    canvas.create_polygon(points, smooth=True, outline='white', fill=fColor, width = 4)
    
def mainPgRedrawAll(canvas, data):
    rgb = (76, 16, 54)
    rgb1 = (238, 108, 77)
    f = "#%02x%02x%02x" % rgb
    f1 = "#%02x%02x%02x" % rgb1
    canvas.create_text(data.width/2, 60, text="Ready to practice?", font='Palatino 50 bold', fill=f)
    canvas.create_text(data.width/2, 150, text="Click 'Next' to play an interval", font='Palatino 25', fill=f)
    canvas.create_text(data.width/2, 190, text="Click 'Replay' to replay an interval", font='Palatino 25', fill=f)
    canvas.create_text(data.width/2, 230, text="Once you figure out which interval", font='Palatino 25', fill=f)
    canvas.create_text(data.width/2, 260, text="was played, click the name of the interval", font='Palatino 25', fill=f)
    canvas.create_text(data.width/2, 300, text="View your score on the right", font='Palatino 25', fill=f)
    
    #next interval button
    roundRectangleButtons(canvas, data, data.x0NextIntervalButton, data.y0NextIntervalButton, data.x1NextIntervalButton, data.y1NextIntervalButton)
    canvas.create_text((data.x0NextIntervalButton + data.x1NextIntervalButton)/2, (data.y0NextIntervalButton+data.y1NextIntervalButton)/2, text="Next", font='Palatino 20', fill='white')
    
    #replay interval button
    roundRectangleButtons(canvas, data, data.x0ReplayIntervalButton, data.y0ReplayIntervalButton, data.x1ReplayIntervalButton, data.y1ReplayIntervalButton)
    canvas.create_text((data.x0ReplayIntervalButton + data.x1ReplayIntervalButton)/2, (data.y0ReplayIntervalButton+data.y1ReplayIntervalButton)/2, text="Replay", font='Palatino 20', fill='white')
    
    #displays score
    if data.wrongIntervals == 0:
        score = 100
    else:
        score = int(data.correctIntervals*\
        1.0 / (data.correctIntervals+data.wrongIntervals)*100)
    canvas.create_text((data.x0ReplayIntervalButton + data.x1ReplayIntervalButton)/2, (data.y0ReplayIntervalButton+data.y1ReplayIntervalButton)/2 + 70, text="Score: "+str(score)+"%", font='Palatino 20')
    canvas.create_text((data.x0ReplayIntervalButton + data.x1ReplayIntervalButton)/2, (data.y0ReplayIntervalButton+data.y1ReplayIntervalButton)/2 + 110, text="Correct: "+str(data.correctIntervals), font='Palatino 20')
    
    #reset score button
    roundRectangleButtons(canvas, data, data.x0ResetIntervalButton, data.y0ResetIntervalButton, data.x1ResetIntervalButton, data.y1ResetIntervalButton)
    canvas.create_text((data.x0ResetIntervalButton + data.x1ResetIntervalButton)/2, (data.y0ResetIntervalButton+data.y1ResetIntervalButton)/2, text="Reset", font='Palatino 20', fill='white')
    
    x0 = data.width/2 - 300 #left of intervals box
    y1 = data.height/2 + 60 
    gap = data.gap
    lBoxHeight = data.lBoxHeight
    lBoxWidth = data.lBoxWidth
    bBoxWidth = data.bBoxWidth
    
    #Intervals box
    data.x0Intervals = x0
    data.x1Intervals = x0 + 600
    data.y0Interval = data.height/2
    data.y1Interval = y1
    
    roundRectangle(canvas, data, x0, data.y0Interval, data.width/2 + 300, y1, [0,0])
    canvas.create_text((x0 + data.width/2 + 300)/2, (data.height/2 + y1)/2, text="Identify Interval", font="Palatino 40 bold", fill="white")
    
    #Major 
    yStart = y1 + gap
    yEnd = y1 + gap + lBoxHeight
    data.y0Major = yStart
    data.y1Major = yEnd
    roundRectangle(canvas, data, x0, yStart, x0 + bBoxWidth, yEnd, [0,1])
    canvas.create_text((x0 + x0 + bBoxWidth)/2, (yStart + yEnd)/2, text="Major", font="Palatino 25 bold", fill="white")
    #M2
    roundRectangle(canvas, data, x0 + bBoxWidth + gap, yStart, x0 + gap + bBoxWidth + \
    lBoxWidth, yEnd, [1,1])
    canvas.create_text((2*x0 + bBoxWidth*2 + gap*2 + lBoxWidth)/2, (yStart + yEnd)/2, text="M2", font="Palatino 25", fill="white")
    #M3
    roundRectangle(canvas, data, x0 + bBoxWidth + 2*gap + lBoxWidth, yStart, x0 + bBoxWidth + 2*gap + 2*lBoxWidth, yEnd, [2,1])
    canvas.create_text((2*x0 + bBoxWidth*2 + gap*4 + 3*lBoxWidth)/2, (yStart + yEnd)/2, text="M3", font="Palatino 25", fill="white")
    #M6
    roundRectangle(canvas, data, x0 + bBoxWidth + 3*gap + 2*lBoxWidth, yStart, x0 + bBoxWidth + 3*gap + 3*lBoxWidth, yEnd, [3,1])
    canvas.create_text((2*x0 + bBoxWidth*2 + gap*6 + 5*lBoxWidth)/2, (yStart + yEnd)/2, text="M6", font="Palatino 25", fill="white")
    #M7
    roundRectangle(canvas, data, x0 + bBoxWidth + 4*gap + 3*lBoxWidth, yStart, x0 + bBoxWidth \
    + 4*gap + 4*lBoxWidth, yEnd, [4,1])
    canvas.create_text((2*x0 + bBoxWidth*2 + gap*8 + 7*lBoxWidth)/2, (yStart + yEnd)/2, text="M7", font="Palatino 25", fill="white")
    
    #Minor box
    yStart =  y1 + 2*gap + lBoxHeight
    yEnd = y1 + 2*gap + 2*lBoxHeight
    data.y0Minor = yStart
    data.y1Minor = yEnd
    roundRectangle(canvas, data, x0, yStart, x0 + bBoxWidth, yEnd, [0,2])
    canvas.create_text((x0 + x0 + bBoxWidth)/2, (yStart+yEnd)/2, text="Minor", font="Palatino 25 bold", fill="white")
    #m2
    roundRectangle(canvas, data, x0 + bBoxWidth + gap, yStart, x0 + gap + bBoxWidth + \
    lBoxWidth, yEnd, [1,2])
    canvas.create_text((2*x0 + bBoxWidth*2 + gap*2 + lBoxWidth)/2, (yStart + yEnd)/2, text="m2", font="Palatino 25", fill="white")
    #m3
    roundRectangle(canvas, data, x0 + bBoxWidth + 2*gap + lBoxWidth, yStart, x0 + bBoxWidth + \
    2*gap + 2*lBoxWidth, yEnd, [2,2])
    canvas.create_text((2*x0 + bBoxWidth*2 + gap*4 + 3*lBoxWidth)/2, (yStart + yEnd)/2, text="m3", font="Palatino 25", fill="white")
    #m6
    roundRectangle(canvas, data, x0 + bBoxWidth + 3*gap + 2*lBoxWidth, yStart, x0 + bBoxWidth \
    + 3*gap + 3*lBoxWidth, yEnd, [3,2])
    canvas.create_text((2*x0 + bBoxWidth*2 + gap*6 + 5*lBoxWidth)/2, (yStart + yEnd)/2, text="m6", font="Palatino 25", fill="white")
    #m7
    roundRectangle(canvas, data, x0 + bBoxWidth + 4*gap + 3*lBoxWidth, yStart, x0 + bBoxWidth \
    + 4*gap + 4*lBoxWidth, yEnd, [4,2])
    canvas.create_text((2*x0 + bBoxWidth*2 + gap*8 + 7*lBoxWidth)/2, (yStart + yEnd)/2, text="m7", font="Palatino 25", fill="white")
    
    #Perfect box
    yStart =  y1 + 3*gap + 2*lBoxHeight
    yEnd = y1 + 3*gap + 3*lBoxHeight
    data.y0Perfect = yStart
    data.y1Perfect = yEnd
    roundRectangle(canvas, data, x0, yStart, x0 + bBoxWidth, yEnd, [0,3])
    canvas.create_text((x0 + x0 + bBoxWidth)/2, (yStart+yEnd)/2, text="Perfect", font="Palatino 25 bold", fill="white")
    #3 little boxes in perfect
    roundRectangle(canvas, data, x0 + bBoxWidth + gap, yStart, x0 + gap + bBoxWidth + \
    lBoxWidth, yEnd, [1,3])
    canvas.create_text((2*x0 + bBoxWidth*2 + gap*2 + lBoxWidth)/2, (yStart + yEnd)/2, text="P4", font="Palatino 25", fill="white")
    roundRectangle(canvas, data, x0 + bBoxWidth + 2*gap + lBoxWidth, yStart, x0 + bBoxWidth + \
    2*gap + 2*lBoxWidth, yEnd, [2,3])
    canvas.create_text((2*x0 + bBoxWidth*2 + gap*4 + 3*lBoxWidth)/2, (yStart + yEnd)/2, text="P5", font="Palatino 25", fill="white")
    roundRectangle(canvas, data, x0 + bBoxWidth + 3*gap + 2*lBoxWidth, yStart, x0 + bBoxWidth \
    + 3*gap + 3*lBoxWidth, yEnd, [3,3])
    canvas.create_text((2*x0 + bBoxWidth*2 + gap*6 + 5*lBoxWidth)/2, (yStart + yEnd)/2, text="P8", font="Palatino 25", fill="white")

####################################
# end mode
####################################

def endMousePressed(event, data):
    data.score = 0

def endKeyPressed(event, data):
    if (event.keysym == 'h'):
        data.mode = "help"

def endTimerFired(data):
    data.score += 1

def endRedrawAll(canvas, data):
    canvas.create_text(data.width/2, data.height/2-40,
                       text="This is a fun game!", font="Arial 26 bold")
    canvas.create_text(data.width/2, data.height/2-10,
                       text="Score = " + str(data.score), font="Arial 20")
    canvas.create_text(data.width/2, data.height/2+15,
                       text="Click anywhere to reset score", font="Arial 20")
    canvas.create_text(data.width/2, data.height/2+40,
                       text="Press 'h' for help!", font="Arial 20")
                       
####################################
# Regular piano code
####################################
    
def getButtonPressed(e, data):
    if e.y > data.y0Interval and e.y < data.y1Interval:
        if e.x > data.x0Intervals and e.x < data.x1Intervals:
            data.currSel = [0,0]
    elif e.y > data.y0Major and e.y < data.y1Major:
        #click in Major box
        if e.x > data.x0Intervals and e.x < data.x0Intervals + data.bBoxWidth:
            data.currSel[0], data.currSel[1] = 0, 1
        #M2
        elif e.x > data.x0Intervals + data.bBoxWidth + data.gap and e.x < \
        data.x0Intervals + data.bBoxWidth + data.lBoxWidth + data.gap:
            data.currSel[0], data.currSel[1] = 1, 1
        #M3
        elif e.x > data.x0Intervals + data.bBoxWidth + data.lBoxWidth + \
        data.gap*2 and e.x < data.x0Intervals + data.bBoxWidth + \
        data.lBoxWidth*2 + data.gap*2:
            data.currSel[0], data.currSel[1] = 2, 1
        #M6
        elif e.x > data.x0Intervals + data.bBoxWidth + data.lBoxWidth*2 + \
        data.gap*3 and e.x < data.x0Intervals + data.bBoxWidth + \
        data.lBoxWidth*3 + data.gap*3:
            data.currSel[0], data.currSel[1] = 3, 1
        #M7
        elif e.x > data.x0Intervals + data.bBoxWidth + data.lBoxWidth*2 + \
        data.gap*4 and e.x < data.x0Intervals + data.bBoxWidth + \
        data.lBoxWidth*4 + data.gap*4:
            data.currSel[0], data.currSel[1] = 4, 1
    elif e.y > data.y0Minor and e.y < data.y1Minor:
        #click in minor box
        if e.x > data.x0Intervals and e.x < data.x0Intervals + data.bBoxWidth:
            data.currSel = [0, 2]
        #m2
        elif e.x > data.x0Intervals + data.bBoxWidth + data.gap and e.x < \
        data.x0Intervals + data.bBoxWidth + data.lBoxWidth + data.gap:
            data.currSel = [1, 2]
        #m3
        elif e.x > data.x0Intervals + data.bBoxWidth + data.lBoxWidth + \
        data.gap*2 and e.x < data.x0Intervals + data.bBoxWidth + \
        data.lBoxWidth*2 + data.gap*2:
            data.currSel = [2, 2]
        #m6
        elif e.x > data.x0Intervals + data.bBoxWidth + data.lBoxWidth*2 + \
        data.gap*3 and e.x < data.x0Intervals + data.bBoxWidth + \
        data.lBoxWidth*3 + data.gap*3:
            data.currSel = [3, 2]
        #m7
        elif e.x > data.x0Intervals + data.bBoxWidth + data.lBoxWidth*2 + \
        data.gap*4 and e.x < data.x0Intervals + data.bBoxWidth + \
        data.lBoxWidth*4 + data.gap*4:
            data.currSel = [4, 2]
    elif e.y > data.y0Perfect and e.y < data.y1Perfect:
        #click in Perfect box
        if e.x > data.x0Intervals and e.x < data.x0Intervals + data.bBoxWidth:
            data.currSel = [0, 3]
        #P4
        elif e.x > data.x0Intervals + data.bBoxWidth + data.gap and e.x < \
        data.x0Intervals + data.bBoxWidth + data.lBoxWidth + data.gap:
            data.currSel = [1, 3]
        #P5
        elif e.x > data.x0Intervals + data.bBoxWidth + data.lBoxWidth + \
        data.gap*2 and e.x < data.x0Intervals + data.bBoxWidth + \
        data.lBoxWidth*2 + data.gap*2:
            data.currSel = [2, 3]
        #P8
        elif e.x > data.x0Intervals + data.bBoxWidth + data.lBoxWidth*2 + \
        data.gap*3 and e.x < data.x0Intervals + data.bBoxWidth + \
        data.lBoxWidth*3 + data.gap*3:
            data.currSel = [3, 3]
            
def getButtonPressedMP(e, data):
    if e.y > data.y0Interval and e.y < data.y1Interval:
        if e.x > data.x0Intervals and e.x < data.x1Intervals:
            data.currSelMP = [0,0]
    elif e.y > data.y0Major and e.y < data.y1Major:
        #click in Major box
        if e.x > data.x0Intervals and e.x < data.x0Intervals + data.bBoxWidth:
            data.currSelMP[0], data.currSelMP[1] = 0, 1
        #M2
        elif e.x > data.x0Intervals + data.bBoxWidth + data.gap and e.x < \
        data.x0Intervals + data.bBoxWidth + data.lBoxWidth + data.gap:
            data.currSelMP[0], data.currSelMP[1] = 1, 1
        #M3
        elif e.x > data.x0Intervals + data.bBoxWidth + data.lBoxWidth + \
        data.gap*2 and e.x < data.x0Intervals + data.bBoxWidth + \
        data.lBoxWidth*2 + data.gap*2:
            data.currSelMP[0], data.currSelMP[1] = 2, 1
        #M6
        elif e.x > data.x0Intervals + data.bBoxWidth + data.lBoxWidth*2 + \
        data.gap*3 and e.x < data.x0Intervals + data.bBoxWidth + \
        data.lBoxWidth*3 + data.gap*3:
            data.currSelMP[0], data.currSelMP[1] = 3, 1
        #M7
        elif e.x > data.x0Intervals + data.bBoxWidth + data.lBoxWidth*2 + \
        data.gap*4 and e.x < data.x0Intervals + data.bBoxWidth + \
        data.lBoxWidth*4 + data.gap*4:
            data.currSelMP[0], data.currSelMP[1] = 4, 1
    elif e.y > data.y0Minor and e.y < data.y1Minor:
        #click in minor box
        if e.x > data.x0Intervals and e.x < data.x0Intervals + data.bBoxWidth:
            data.currSelMP = [0, 2]
        #m2
        elif e.x > data.x0Intervals + data.bBoxWidth + data.gap and e.x < \
        data.x0Intervals + data.bBoxWidth + data.lBoxWidth + data.gap:
            data.currSelMP = [1, 2]
        #m3
        elif e.x > data.x0Intervals + data.bBoxWidth + data.lBoxWidth + \
        data.gap*2 and e.x < data.x0Intervals + data.bBoxWidth + \
        data.lBoxWidth*2 + data.gap*2:
            data.currSelMP = [2, 2]
        #m6
        elif e.x > data.x0Intervals + data.bBoxWidth + data.lBoxWidth*2 + \
        data.gap*3 and e.x < data.x0Intervals + data.bBoxWidth + \
        data.lBoxWidth*3 + data.gap*3:
            data.currSelMP = [3, 2]
        #m7
        elif e.x > data.x0Intervals + data.bBoxWidth + data.lBoxWidth*2 + \
        data.gap*4 and e.x < data.x0Intervals + data.bBoxWidth + \
        data.lBoxWidth*4 + data.gap*4:
            data.currSelMP = [4, 2]
    elif e.y > data.y0Perfect and e.y < data.y1Perfect:
        #click in Perfect box
        if e.x > data.x0Intervals and e.x < data.x0Intervals + data.bBoxWidth:
            data.currSelMP = [0, 3]
        #P4
        elif e.x > data.x0Intervals + data.bBoxWidth + data.gap and e.x < \
        data.x0Intervals + data.bBoxWidth + data.lBoxWidth + data.gap:
            data.currSelMP = [1, 3]
        #P5
        elif e.x > data.x0Intervals + data.bBoxWidth + data.lBoxWidth + \
        data.gap*2 and e.x < data.x0Intervals + data.bBoxWidth + \
        data.lBoxWidth*2 + data.gap*2:
            data.currSelMP = [2, 3]
        #P8
        elif e.x > data.x0Intervals + data.bBoxWidth + data.lBoxWidth*2 + \
        data.gap*3 and e.x < data.x0Intervals + data.bBoxWidth + \
        data.lBoxWidth*3 + data.gap*3:
            data.currSelMP = [3, 3]
    else:
        #no interval is selected
        return False
    return True
            


def timerFired(data):
    if data.terminateProg == False:
        updateLeapMotionData(data)
        printLeapMotionData(data)
        #note(data)
        #play("africa-toto.wav", data)
    else:
        if data.playedOnce == False:
            w = threading.Thread(name='worker', target=playNotes(data))
            w.start()
        data.playedOnce = True
        pass
        
def noteToPlay(file):
    time.sleep(0.1)
    play(file)
    
def playNotes(data):
    for i in range(len(data.keysPlayed)):
        note = tuple(data.keysPlayed[i])
        if note in data.keyToSound:
            noteToPlay(data.keyToSound[note])
        

def updateLeapMotionData(data):
    data.frame = data.controller.frame()

def printLeapMotionData(data):
    frame = data.frame

    print "Frame id: %d, timestamp: %d, hands: %d, fingers: %d" % (
          frame.id, frame.timestamp, len(frame.hands), len(frame.fingers))

    # Get hands
    for hand in frame.hands:
        if hand.grab_strength == 1.0:
            print hand.grab_strength
            play("maybe-next-time.wav", data)

        handType = "Left hand" if hand.is_left else "Right hand"
        
        #palm position for generating pointer
        if handType == "Left hand":
            data.lPointerPos = hand.palm_position
            data.lHandOnScreen = True
            print "HERE", data.lPointerPos
        else:
            data.rPointerPos = hand.palm_position
            data.rHandOnScreen = True
            
        data.lHandOnScreen, data.rHandOnScreen = False, False

        print "  %s, id %d, position: %s" % (
            handType, hand.id, hand.palm_position)

        # Get the hand's normal vector and direction
        normal = hand.palm_normal
        direction = hand.direction

        # Calculate the hand's pitch, roll, and yaw angles
        print "  pitch: %f degrees, roll: %f degrees, yaw: %f degrees" % (
            direction.pitch * Leap.RAD_TO_DEG,
            normal.roll * Leap.RAD_TO_DEG,
            direction.yaw * Leap.RAD_TO_DEG)

        # Get arm bone
        arm = hand.arm
        print "  Arm direction: %s, wrist position: %s, elbow position: %s" % (
            arm.direction,
            arm.wrist_position,
            arm.elbow_position)

        # Get fingers
        for finger in hand.fingers:

            print "    %s finger, id: %d, length: %fmm, width: %fmm" % (
                data.fingerNames[finger.type],
                finger.id,
                finger.length,
                finger.width)
            
            #stores tip positions on fingers
            if data.fingerNames[finger.type] == "Thumb":
                data.rFingerLst[0] = finger.tip_position
            elif data.fingerNames[finger.type] == "Index":
                data.rFingerLst[1] = finger.tip_position
            elif data.fingerNames[finger.type] == "Middle":
                data.rFingerLst[2] = finger.tip_position 
            elif data.fingerNames[finger.type] == "Ring":
                data.rFingerLst[3] = finger.tip_position
            elif data.fingerNames[finger.type] == "Pinky":
                data.rFingerLst[4] = finger.tip_position

            print "IMPORTANT", data.rFingerLst
            # Get bones
            for b in range(0, 4):
                bone = finger.bone(b)
                print "      Bone: %s, start: %s, end: %s, direction: %s" % (
                    data.boneNames[bone.type],
                    bone.prev_joint,
                    bone.next_joint,
                    bone.direction)

              
def drawMainPointers(canvas, data):
    #draw RH pointer
    data.yRCoor = data.height - ((data.rPointerPos[1]-40) * data.height/160)
    data.xRCoor = (data.rPointerPos[0] - (-70))*data.width/140
    canvas.create_oval(data.xRCoor-10, data.yRCoor-10, data.xRCoor+10,\
        data.yRCoor+10, outline = "red")

    #draw LH pointer
    data.yLCoor = data.height - ((data.lPointerPos[1]-40) * data.height/160)
    data.xLCoor = (data.lPointerPos[0] - (-70))*data.width/140
    canvas.create_oval(data.xLCoor-10, data.yLCoor-10, data.xLCoor+10,\
        data.yLCoor+10, outline = "blue")
        
def drawFingerPointers(canvas, data):
    #print data.rFingerLst
    for i in range(len(data.rFingerLst)):
        xCoor = (data.rFingerLst[i][0] - (-100))*data.width/250
        yCoor = data.height - ((data.rFingerLst[i][1]-40) * data.height/160)
        getKeyHand(data, xCoor, yCoor, i)
        canvas.create_oval(xCoor-10, yCoor-10, xCoor+10, \
        yCoor+10, outline = "green")
        
def drawPauseButton(canvas, data):
    coords = data.pauseButton
    x0, y0, x1, y1 = coords[0], coords[1], coords[2], coords[3]
    canvas.create_rectangle(x0, y0, x1, y1, fill = "green")
    
def roundRectangle(canvas, data, x1, y1, x2, y2, currCoords, radius=25):
    #https://stackoverflow.com/questions/44099594/how-to-make-a-tkinter-canvas-rectangle-with-rounded-corners
    points = [x1+radius, y1, x1+radius, y1, x2-radius, y1, x2-radius, y1, \
    x2, y1, x2, y1+radius, x2, y1+radius, x2, y2-radius, x2, y2-radius, x2, \
    y2, x2-radius, y2, x2-radius, y2, x1+radius, y2, x1+radius, y2, x1, y2,\
    x1, y2-radius, x1, y2-radius, x1, y1+radius, x1, y1+radius, x1, y1]
    
    #selecting things in blue in "pickInterval" mode
    if tuple(currCoords) in data.allSel and tuple(currCoords) != (0,0) and data.mode == "pickInterval":
        rgb = (238, 108, 77)
        fColor = "#%02x%02x%02x" % rgb
    #selecting things in green in "mainPg" mode
    elif data.mode == "mainPg" and currCoords == data.currSelMP and currCoords not in [[0,0], [0,1], [0,2], [0,3]]:
        fColor = "green" 
    else:
        rgb = (85, 50, 211)
        fColor = "#%02x%02x%02x" % rgb
    #print "currCoords",currCoords, data.currSelMP
        
    rgb = (224, 232, 249)
    oline = "#%02x%02x%02x" % rgb
    canvas.create_polygon(points, smooth=True, outline='white', fill=fColor, width = 4)
    
####################################
# use the run function as-is
####################################

'''def run(width=300, height=300):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, data.width, data.height,
                                fill='white', width=0)
        redrawAll(canvas, data)
        canvas.update()    

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 20 # milliseconds
    init(data)
    # create the root and the canvas
    root = Tk()
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.pack()
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

run(1000, 700)'''