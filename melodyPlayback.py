import threading
import pyaudio
import wave
from array import array
from struct import pack
import numpy as np
import time
import Leap
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture
import os, sys, inspect, thread, time
sys.path.insert(0, "C:/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages/LeapDeveloperKit_2.3.1+31549_mac/LeapSDK/lib/x86")
from intervals import roundRectangleButtons
import copy



####################################
# PyAudio
####################################

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
    play(file)

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
    
    #piano variables
    data.wKeyWidth = 90
    data.wKeyLength = 320
    data.bKeyWidth = 60
    data.bKeyLength = 170
    data.yMargin = 300
    data.xMargin = 30
    data.bKeyShift = 60
    data.numWhiteKeys = 0
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
    
    data.tap_point = (0,0)
    
    data.timerDelay = 100
    data.clock = 0
    data.notePressedTime = [0, 0, 0, 0, 0]
    
    data.indexFingerMvmts = []
    data.lastTime = 0
    #stores all finger movements
    data.fingerMvmts0 = dict()
    data.fingerMvmts1 = dict()
    data.fingerMvmts2 = dict()
    data.fingerMvmts3 = dict()
    data.fingerMvmts4 = dict()
    
    data.prevTime = [0,0,0,0,0]
    
    data.melodies = dict({\
    0: ["pianoNotes/E.wav", "pianoNotes/F.wav", "pianoNotes/D.wav", "pianoNotes/E.wav", "pianoNotes/C.wav"], \
    1: ["pianoNotes/G.wav", "pianoNotes/E.wav", "pianoNotes/F#.wav", "pianoNotes/G.wav", "pianoNotes/A.wav", "pianoNotes/G.wav"]})
    
    rectWidth = 100
    gap = 40
    
    data.x0NextMelButton = data.width/2-gap*1.5-2*rectWidth
    data.x1NextMelButton = data.width/2-gap*1.5-1*rectWidth
    data.y0NextMelButton = 215
    data.y1NextMelButton = 275
    
    data.x0ReplayMelButton = data.width/2-120
    data.x1ReplayMelButton = data.width/2-20
    data.y0ReplayMelButton = 215
    data.y1ReplayMelButton = 275
    
    data.x0DoneButton = data.width/2+gap/2
    data.x1DoneButton = data.width/2+gap/2+1*rectWidth
    data.y0DoneButton = 215
    data.y1DoneButton = 275
    
    data.x0AnswerMelButton = data.width/2+gap/2
    data.x1AnswerMelButton = data.width/2+gap/2+1*rectWidth
    data.y0AnswerMelButton = 215
    data.y1AnswerMelButton = 275
    
    rectWidth = 100
    gap = 40
    
    
    roundRectangleButtons(canvas, data, data.width/2+gap*1.5+rectWidth, 215, data.width/2+gap*1.5+2*rectWidth, 275)
    
    data.currMelody = None
    data.notesPlayed = []
    data.correctMelody = None

def mousePressed(event, data):
    print event.x, event.y
            
    #if next melody button clicked
    if event.x > data.x0NextMelButton and event.x < \
    data.x1NextMelButton and event.y > data.y0NextMelButton and \
    event.y < data.y1NextMelButton:
        #stores first note in melody
        index = random.randint(0, len(data.melodies)-1)
        data.currMelody = index
        notes = data.melodies[index]
        firstNote = data.melodies[data.currMelody][0]
        for index in data.keyToSound:
            if data.keyToSound[index] == firstNote:
                data.firstNoteMel = index
        for note in notes:
            t = threading.Thread(name='worker', target=worker, args=(note,))
            t.start()
            time.sleep(1)
            
    #if replay button clicked
    if event.x > data.x0ReplayMelButton and event.x < \
    data.x1ReplayMelButton and event.y > data.y0ReplayMelButton and \
    event.y < data.y1ReplayMelButton:
        #stores first note in melody
        firstNote = data.melodies[data.currMelody][0]
        for index in data.keyToSound:
            if data.keyToSound[index] == firstNote:
                data.firstNoteMel = index
        if data.currMelody != None:
            for note in data.melodies[data.currMelody]:
                t = threading.Thread(name='worker', target=worker, args=(note,))
                t.start()
                time.sleep(1)
      
    getKeyMouse(data, event.x, event.y)
    if data.selection[1] != "nothing":
        note = data.keyToSound[(data.selection[0], data.selection[1])]
        print note
        t = threading.Thread(name='worker', target=worker, args=(note,))
        t.start()
    #stores key press if start/end buttons is clicked
    if data.recMel:
        #getKeyMouse(data, event.x, event.y)
        if data.selection[1] != "nothing":
            data.notesPlayed.append(tuple(data.selection))
            print "MELODY PLAYED BACK:", data.notesPlayed
    
    if event.x > data.x0DoneButton and event.x < \
    data.x1DoneButton and event.y > data.y0DoneButton and \
    event.y < data.y1DoneButton:
        if data.recMel:
            data.recMel = False
        else:
            data.recMel = True
        
    #if answer button clicked
    if event.x > data.x0AnswerMelButton and event.x < \
    data.x1AnswerMelButton and event.y > data.y0AnswerMelButton and \
    event.y < data.y1AnswerMelButton:
        if len(data.notesPlayed) != len(data.melodies[data.currMelody]):
            data.correctMelody = False
        else:
            for i in range(len(data.notesPlayed)):
                if data.currMelody != None and data.keyToSound[(data.notesPlayed[i][0], data.notesPlayed[i][1])] != data.melodies[data.currMelody][i]:
                    data.correctMelody = False
                    break
        if data.correctMelody != False:
            data.correctMelody = True
            
        if data.correctMelody == True:
            t = threading.Thread(name='worker', target=worker, args=("nice-work.wav",))
            t.start()
        elif not data.correctMelody:
            t = threading.Thread(name='worker', target=worker, args=("maybe-next-time.wav",))
            t.start() 
            
        #print data.correctMelody, data.notesPlayed
        data.notesPlayed = []
        data.correctMelody = None
        
    #if show answer button clicked
    if event.x > data.x0ShowAnsMelButton and event.x < \
    data.x1ShowAnsMelButton and event.y > data.y0ShowAnsMelButton and \
    event.y < data.y1ShowAnsMelButton:
        data.playAnswer = copy.deepcopy(data.melodies[data.currMelody])
        for j in range(len(data.playAnswer)):
            for index in data.keyToSound:
                if data.keyToSound[index] == data.playAnswer[j]:
                    data.playAnswer[j] = index
        print data.playAnswer
        
            
def keyPressed(event, data):
    # use event.char and event.keysym
    pass

def timerFired(data):
    data.clock += 1
    if data.stopClock:
        time.sleep(1)
        data.stopClock = False
        
        
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

    '''print "Frame id: %d, timestamp: %d, hands: %d, fingers: %d" % (
          frame.id, frame.timestamp, len(frame.hands), len(frame.fingers))'''

    # Get hands
    for hand in frame.hands:
        if hand.grab_strength == 1.0:
            print hand.grab_strength
            #play("maybe-next-time.wav")

        handType = "Left hand" if hand.is_left else "Right hand"
        
        #palm position for generating pointer
        if handType == "Left hand":
            data.lPointerPos = hand.palm_position
            data.lHandOnScreen = True
            print "HERE", data.lPointerPos
        else:
            data.rPointerPos = hand.palm_position
            data.rHandOnScreen = True
        '''print "PALM pos: ", data.rPointerPos'''
            
        data.lHandOnScreen, data.rHandOnScreen = False, False

        '''print "  %s, id %d, position: %s" % (
            handType, hand.id, hand.palm_position[1])'''

        # Get the hand's normal vector and direction
        normal = hand.palm_normal
        direction = hand.direction


        # Get arm bone
        arm = hand.arm

        # Get fingers
        for finger in hand.fingers:
            print "    %s finger" % (
                data.fingerNames[finger.type]), finger.tip_position[1]
            
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
            
            for i in range(5):
                d = {0:13, 1:20, 2:20, 3:13, 4:13}
                isKeyPlayed(data, d[i], i)
            
                    
def isKeyPlayedList(data, finger):
    #checks if finger plays key
    thresholds = {0:27, 1:35, 2:35, 3:30, 4:27}
    if data.rPointerPos[1] - data.rFingerLst[finger][1] > thresholds[finger]:
        getKeyHand(data, data.rFingerLst[finger][0], data.rFingerLst[finger][1]-15, 1)
        if tuple(data.selectionHand[finger]) in data.keyToSound:
            if data.clock - data.notePressedTime[finger] > 4:
                data.notePressedTime[finger] = data.clock
                note = data.keyToSound[tuple(data.selectionHand[finger])]
                a = threading.Thread(name='worker', target=worker, \
                args=(note,))
                a.start()
                time.sleep(0.01)
            
def isKeyPlayed(data, lowerBound, finger):
    d = {0: data.fingerMvmts0, 1: data.fingerMvmts1, 2: data.fingerMvmts2, 3: data.fingerMvmts3, 4: data.fingerMvmts4}
    print finger
    dic = d[finger]
    dic[int(data.rFingerLst[finger][1])] = data.clock
    for i in range(lowerBound, 45):
        #print int(data.rFingerLst[1][1]) - i
        if int(data.rFingerLst[finger][1]) - i in dic:
            #print i
            #check downwards movement was quick enough
            if dic[int(data.rFingerLst[finger][1])] - dic[int(data.rFingerLst[finger][1]) - i] <= 2:
                if data.clock - data.prevTime[finger] > 2:
                    '''print "PLAY THIS", i, dic[int(data.rFingerLst[1][1])] - dic[int(data.rFingerLst[1][1]) - i], data.clock'''
                    data.prevTime[finger] = data.clock
                    getKeyHand(data, data.rFingerLst[finger][0], \
                    (data.rFingerLst[finger][1] + int(data.rFingerLst[finger][1]) - i)/2, 1)
                    if tuple(data.selectionHand[finger]) in data.keyToSound:
                        note = data.keyToSound[tuple(data.selectionHand[finger])]
                        a = threading.Thread(name='worker', target=worker, \
                        args=(note,))
                        a.start()
                    break


def getKeyMouse(data, x, y):
    #updates where user presses
    wKeyIndex = (x - data.xMargin) // data.wKeyWidth
    #bottom half of key
    if y > data.yMargin + data.bKeyLength and y < data.yMargin + data.wKeyLength:
        data.selection[0] = (x - data.xMargin) // data.wKeyWidth 
        data.selection[1] = "white"
    #top half of key
    elif y > data.yMargin and y < data.yMargin + data.bKeyLength:
        #left half of key
        if x < data.xMargin + data.wKeyWidth*wKeyIndex + data.bKeyWidth//2:
            if wKeyIndex not in {0, 3, 7}:
                data.selection[0], data.selection[1] = wKeyIndex-1, "black"
            else:
                data.selection[0], data.selection[1] = wKeyIndex, "white"
        #right half of key
        elif x > data.xMargin + data.wKeyWidth*(wKeyIndex+1) - data.bKeyWidth//2:
            if wKeyIndex not in {2, 6, 9}:
                data.selection[0], data.selection[1] = wKeyIndex, "black"
            else:
                data.selection[0], data.selection[1] = wKeyIndex, "white"
        #white part of key
        else:
            data.selection[0], data.selection[1] = wKeyIndex, "white"
    else:
        data.selection[1] = "nothing"
            
    print data.selection
    data.keysPlayed.append([data.selection[0], data.selection[1]])
    print "KEYS PRESSED:", data.keysPlayed
            
def getKeyHand(data, x, y, finger):
    i = finger
    #updates where user presses
    wKeyIndex = (x - data.xMargin) // data.wKeyWidth
    #bottom half of key
    if y > data.yMargin + data.bKeyLength and y < data.yMargin + data.wKeyLength:
        data.selectionHand[i][0] = (x - data.xMargin) // data.wKeyWidth 
        data.selectionHand[i][1] = "white"
    #top half of key
    elif y > data.yMargin and y < data.yMargin + data.bKeyLength:
        #left half of key
        if x < data.xMargin + data.wKeyWidth*wKeyIndex + data.bKeyWidth//2:
            if wKeyIndex not in {0, 3, 7}:
                data.selectionHand[i][0], data.selectionHand[i][1] = wKeyIndex-1, "black"
            else:
                data.selectionHand[i][0], data.selectionHand[i][1] = wKeyIndex, "white"
        #right half of key
        elif x > data.xMargin + data.wKeyWidth*(wKeyIndex+1) - data.bKeyWidth//2:
            if wKeyIndex not in {2, 6, 9}:
                data.selectionHand[i][0], data.selectionHand[i][1] = wKeyIndex, "black"
            else:
                data.selectionHand[i][0], data.selectionHand[i][1] = wKeyIndex, "white"
        #white part of key
        else:
            data.selectionHand[i][0], data.selectionHand[i][1] = wKeyIndex, "white"
    
        

def drawPiano(canvas, data):
    clock = True
    entered = False
    #draw keyBoard
    wKeyWidth = 90
    wKeyLength = 320
    bKeyWidth = 60
    bKeyLength = 170
    startYOnScreen = 300
    margin = 30
    bKeyShift = 60
    wSelectedIndexes = set()
    bSelectedIndexes = set()
    wNoteNames = {0:"C", 1:"D", 2:"E", 3:"F", 4:"G", 5:"A", 6:"B", 7:"C", 8:"D", 9:"E"}
    bNoteNames = {0:"C#", 1:"Eb", 3:"F#", 4:"Ab", 5:"Bb", 7:"C#", 8:"Eb"}
    
    #stores locations of fingers
    for i in range(len(data.selectionHand)):
        if data.selectionHand[i][1] == "white":
            wSelectedIndexes.add(data.selectionHand[i][0])
        elif data.selectionHand[i][1] == "black":
            bSelectedIndexes.add(data.selectionHand[i][0])
    
    if clock:
        clock = False
        for i in range(10):
            #draw white keys
            if i == data.selection[0] and data.selection[1] == "white": #mouse on key
                rgb = (85, 50, 211)
                color = "#%02x%02x%02x" % rgb
                #color = "red"
            elif i in wSelectedIndexes: #finger on key
                color = "blue"
            else:
                color = "white"
            canvas.create_rectangle(wKeyWidth*i+margin, startYOnScreen,\
            margin+wKeyWidth*(i+1), startYOnScreen + wKeyLength, outline = \
            "black", fill=color)
            #shows first note of melody
            if data.firstNoteMel[0] == i and data.firstNoteMel[1] == "white":
                canvas.create_text((wKeyWidth*i+margin + margin+wKeyWidth*(i+1))\
                *1/2, (startYOnScreen + startYOnScreen + wKeyLength)*1/2+100,\
                 text=wNoteNames[i], font="Palatino 20 bold")
            #plays back melody
            if data.playAnswer != None and len(data.playAnswer) != 0 and entered == False:
                clock = False
                rgb2 = (113, 169, 247)
                color = "#%02x%02x%02x" % rgb2
                if data.playAnswer[0][0] == i and data.playAnswer[0][1] == "white":
                    canvas.create_text((wKeyWidth*i+margin + margin+wKeyWidth*(i+1))*1/2,\
                    (startYOnScreen + startYOnScreen + wKeyLength)*1/2+100,\
                    text=wNoteNames[i], font="Palatino 20 bold", fill=color)
                    note = data.keyToSound[data.playAnswer[0]]
                    t = threading.Thread(name='worker', target=worker, args=(note,))
                    t.start()
                    data.playAnswer.pop(0)
                    data.stopClock = True
                    entered = True
    
    #checks to make sure you don't enter here twice
    entered1 = False
    if entered1 == False:
        for i in range(10):
            #draw black keys
            if i == data.selection[0] and data.selection[1] == "black":
                rgb = (85, 50, 211)
                color = "#%02x%02x%02x" % rgb
                #color = "red"
            elif i in bSelectedIndexes:
                color = "blue"
            else:
                color = "black"
            if i != 2 and i!= 6 and i != 9 and i != 11:
                canvas.create_rectangle(wKeyWidth*i+margin+bKeyShift, startYOnScreen,\
                wKeyWidth*i+margin+bKeyShift+bKeyWidth, startYOnScreen + bKeyLength,\
                fill = color)
            #shows first note of melody
            if data.firstNoteMel[0] == i and data.firstNoteMel[1] == "black" and clock:
                clock = False
                canvas.create_text((wKeyWidth*i+margin+bKeyShift +\
                 wKeyWidth*i+margin+bKeyShift+bKeyWidth)*1/2, (2*startYOnScreen \
                 + bKeyLength)*1/2+50, text=bNoteNames[i], font="Palatino 20 bold")
            #plays back melody
            if data.playAnswer != None and len(data.playAnswer) != 0 and \
            clock != data.clock and entered == False:
                rgb2 = (113, 169, 247)
                color = "#%02x%02x%02x" % rgb2
                if data.playAnswer[0][0] == i and data.playAnswer[0][1] == "black":
                    canvas.create_text((wKeyWidth*i+margin+bKeyShift +\
                     wKeyWidth*i+margin+bKeyShift+bKeyWidth)*1/2, \
                     (2*startYOnScreen + bKeyLength)*1/2+50, \
                     text=bNoteNames[i], font="Palatino 20 bold", fill=color)
                    #plays note
                    t = threading.Thread(name='worker', target=worker,\
                     args=(data.keyToSound[data.playAnswer[0]],))
                    t.start()
                    data.playAnswer.pop(0)
                    #pauses timer for 1 second
                    data.stopClock = True
                    #makes sure this section isn't entered twice
                    entered1 = True
              
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
        
def getFingerPointerCoords(data, x, y):
    xCoor = (x - (-100))*data.width/250
    yCoor = data.height - ((y-40) * data.height/160)
    return xCoor, yCoor
        
def drawFingerPointers(canvas, data):
    #print data.rFingerLst
    rgb = (85, 50, 211)
    oline = "#%02x%02x%02x" % rgb
    for i in range(len(data.rFingerLst)):
        xCoor = (data.rFingerLst[i][0] - (-100))*data.width/250
        yCoor = data.height - ((data.rFingerLst[i][1]-40) * data.height/160)
        getKeyHand(data, xCoor, yCoor, i)
        canvas.create_oval(xCoor-10, yCoor-10, xCoor+10, \
        yCoor+10, outline = oline)
        if i == 1:
            canvas.create_text(xCoor, yCoor, text=str(int(xCoor)) + ", " + str(int(yCoor)))
        
def drawPauseButton(canvas, data):
    coords = data.pauseButton
    x0, y0, x1, y1 = coords[0], coords[1], coords[2], coords[3]
    canvas.create_rectangle(x0, y0, x1, y1, fill = "green")
    
def redrawAll(canvas, data):
    drawPiano(canvas, data)
    drawMainPointers(canvas, data)
    drawFingerPointers(canvas, data)
    
    #text on screen
    rgb = (76, 16, 54)
    f = "#%02x%02x%02x" % rgb
    canvas.create_text(data.width/2, 65, text="Melody Playback", font="Palatino 40 bold", fill=f)
    canvas.create_text(data.width/2, 120, text="Ready to test how well you can remember and play back a melody?", font="Palatino 20 bold", fill=f)
    canvas.create_text(data.width/2, 145, text="To hear a melody, click 'Next'", font="Palatino 20 bold", fill=f)
    canvas.create_text(data.width/2, 170, text="To record your answer, click 'Start'", font="Palatino 20 bold", fill=f)
    canvas.create_text(data.width/2, 659, text="Stuck? Click me for the answer", font="Palatino 20 bold", fill=f)
    
    rectWidth = 100
    gap = 40
    
    #nextMel button
    roundRectangleButtons(canvas, data, data.x0NextMelButton, data.y0NextMelButton, data.x1NextMelButton, data.y1NextMelButton)
    canvas.create_text((data.x0NextMelButton + data.x1NextMelButton)/2, (data.y0NextMelButton+data.y1NextMelButton)/2, text="Next", font='Palatino 20', fill='white')
    
    #replayMel button
    roundRectangleButtons(canvas, data, data.x0ReplayMelButton, data.y0ReplayMelButton, data.x1ReplayMelButton, data.y1ReplayMelButton)
    canvas.create_text((data.x0ReplayMelButton + data.x1ReplayMelButton)/2, (data.y0ReplayMelButton+data.y1ReplayMelButton)/2, text="Replay", font='Palatino 20', fill='white')
    
    #Start/end Done button
    roundRectangleButtons(canvas, data, data.x0DoneButton, data.y0DoneButton, data.x1DoneButton, data.y1DoneButton)
    if data.recMel:
        txt = "End"
    else:
        txt = "Start"
    canvas.create_text((data.x0DoneButton + data.x1DoneButton)/2, (data.y0DoneButton+data.y1DoneButton)/2, text=txt, font='Palatino 20', fill='white')
    
    #answer button
    roundRectangleButtons(canvas, data, data.x0AnswerMelButton, data.y0AnswerMelButton, data.x1AnswerMelButton, data.y1AnswerMelButton)
    canvas.create_text((data.x0AnswerMelButton + data.x1AnswerMelButton)/2, (data.y0AnswerMelButton+data.y1AnswerMelButton)/2, text="Check", font='Palatino 20', fill='white')
    
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