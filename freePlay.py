####################################
#Description:
    #Main file. Contains all code for "free play" mode where user can play virtual keyboard. Uses modes to different parts of application.
'''All notes on keyboard can be played with fingers and with mouse.
Keys are only momentarily highlighted after you press them. If your hands are not on the keyboard, then no keys will be highlighted. 
You can click a button in order to show the names of all the notes on the keyboard.
You can record melodies and play them back. You can also save melodies that you record and name them whatever you would like. All recorded melodies are stored even after the program is closed and reopened.'''

####################################

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
import random, math
import os, sys, inspect, thread, time
'''sys.path.insert(0, "C:\Users\ahanamukhopadhyay\Downloads\LeapDeveloperKit_2.3.1+31549_mac\LeapSDK\lib/x86")'''
from Tkinter import *
import tkFont
from PIL import Image
from image_util import *
import copy
from graphics import drawBackground

'''
CITATIONS: 
112 website for tkinter starter code
Leap motion starter code from Johnathan's Google Drive folder
Threads basic code: https://pymotw.com/2/threading/
PyAudio starter code: Google Drive folder shared with us from 15-112
https://freesound.org/people/pinkyfinger/sounds/68438/ Piano notes wav files
makeRecording() function --> altered code from here https://stackoverflow.com/questions/2890703/how-to-join-two-wav-files-using-python
https://www.clipartmax.com/middle/m2i8G6K9A0i8K9Z5_jazz-pianist-man-playing-piano-silhouette/ (citing image)
roundRectangles(): https://stackoverflow.com/questions/44099594/how-to-make-a-tkinter-canvas-rectangle-with-rounded-corners'''

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
    print threading.currentThread().getName(), 'Starting'
    play(file)
    print threading.currentThread().getName(), 'Exiting'

####################################
# Leap Motion
####################################


def init(data):
    
    ###HOME VARIABLES
    data.whiteCircles = []
    for i in range(15):
        x0 = random.randint(10, data.width - 10)
        y0 = random.randint(10, data.width - 10)
        r = 15
        if i < 5:
            dir = (1,1)
        elif i < 10:
            dir = (-1,1)
        else:
            dir = (1,-1)
        data.whiteCircles.append([x0, y0, x0+r, y0+r, dir, r])
    
    #big circles
    data.bigCircles = []
    for i in range(12):
        x0 = random.randint(10, data.width - 10)
        y0 = random.randint(10, data.width - 10)
        r = 100
        if i < 5:
            dir = (1,1)
        elif i < 10:
            dir = (-1,1)
        else:
            dir = (1,-1)
        data.bigCircles.append([x0, y0, x0+r, y0+r, dir, r])
        
    data.speed1 = 1.5
    data.speed2 = 1.1
    data.timerDelay = 100
    data.secs = 0
    
    data.boxRadius = 120
    data.x0FreePlayButton = data.width/2 - data.boxRadius
    data.x1FreePlayButton = data.width/2 + data.boxRadius
    data.y0FreePlayButton = data.height/3
    data.y1FreePlayButton = data.height/3 + 60
    
    
    ###FREE PLAY VARIABLES
    data.mode = "home"
    
    data.controller = Leap.Controller()
    data.frame = data.controller.frame()
    data.fingerNames = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
    data.boneNames = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']
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
    data.selection = [0,"nothing", 0] #key index, color, time
    data.selectionHand = [[0,"nothing"], [0,"nothing"], [0,"nothing"], [0,"nothing"], [0,"nothing"]]
    
    data.keysPlayed = []
    
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
    
    #contains elements like [(0, "black"), 12]
    data.notePlayed = []
    data.showNoteNames = False
    
    data.x0NamesButton = 357
    data.x1NamesButton = 459
    data.y0NamesButton = 101
    data.y1NamesButton = 147
    
    data.x0RecordButton = data.width/2-50
    data.y0RecordButton = 225
    data.x1RecordButton = data.width/2+10
    data.y1RecordButton = 285
    
    data.x0PlayButton = data.width/2+30
    data.x1PlayButton = data.width/2+90
    data.y0PlayButton = 225
    data.y1PlayButton = 285
    
    data.x0BackButton = 20
    data.x1BackButton = 80
    data.y0BackButton = 30
    data.y1BackButton = 90
    
    data.x0ForwardButton = data.width-80
    data.x1ForwardButton = data.width-20
    data.y0ForwardButton = 30
    data.y1ForwardButton = 90
    
    data.x0DialogBox = data.width/2-150,
    data.x1DialogBox = data.width/2+150
    data.y0DialogBox = 175
    data.y1DialogBox = 210
    
    data.notesPlayed = []
    data.record = False
    data.enterTxt = False
    data.recordingName = ""
    data.recordings = []
    data.numTimesRecordPressed = 0
    data.stopClockFP = False
    data.sleepTime = 0
    data.greyBg = False
    
    data.x0SeeRecordingsButton = 296
    data.x1SeeRecordingsButton = 702
    data.y0SeeRecordingsButton = 643
    data.y1SeeRecordingsButton = 679
    
    data.programOpened = False
    data.contentsRead = ""
    
    data.x0SaveRecordingsButton = 840
    data.x1SaveRecordingsButton = 930
    data.y0SaveRecordingsButton = 225
    data.y1SaveRecordingsButton = 285
    
    data.x0SBox = 0
    data.y0SBox = 0
    data.x1SBox = 0
    
    ###MELODY PLAYBACK VARIABLES
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
    
    data.x0AnswerMelButton = data.width/2+gap*1.5+rectWidth
    data.x1AnswerMelButton = data.width/2+gap*1.5+2*rectWidth
    data.y0AnswerMelButton = 215
    data.y1AnswerMelButton = 275
    
    data.x0ShowAnsMelButton = 418
    data.x1ShowAnsMelButton = 508
    data.y0ShowAnsMelButton = 646
    data.y1ShowAnsMelButton = 675
    
    data.currMelody = None
    data.notesPlayed = []
    data.correctMelody = None
    
    data.recMel = False
    data.firstNoteMel = (0,0)
    data.playAnswer = None
    data.stopClock = False
    
    ###INTERVALS
    data.intervals = dict({\
    "m2": [["C", "C#"], ["E", "F#"], ["G", "Ab"], ["B", "C2"]],\
    "M2": [["C", "D"], ["D", "E"], ["E", "F#"], ["F", "G"]],\
    "m3": [["C", "Eb"], ["E", "G"], ["D", "F"], ["C2", "Eb2"]],\
    "M3": [["C", "E"], ["D", "F#"], ["C2", "E2"], ["G", "B"]],\
    "P4": [["E", "A"], ["D", "G"], ["C#", "F#"], ["Eb", "Ab"]],\
    "P5": [["C", "G"], ["E", "B"], ["A", "E2"], ["Eb", "Bb"]],\
    "M6": [["C", "A"], ["D", "B"], ["E", "C#2"], ["C#", "Bb"]],\
    "m6": [["C", "Ab"], ["D", "Bb"], ["E", "C2"], ["C#", "B"]],\
    "M7": [["C", "B"], ["C#", "C2"], ["D", "C#2"], ["E", "Eb2"]],\
    "m7": [["C", "Bb"], ["C#", "B"], ["D", "C2"], ["E", "D2"]],\
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
    
    data.x0ResetIntervalButton = data.x0ReplayIntervalButton
    data.x1ResetIntervalButton = data.x1ReplayIntervalButton
    data.y0ResetIntervalButton = data.y0ReplayIntervalButton + 180
    data.y1ResetIntervalButton = data.y1ReplayIntervalButton + 180
    
    data.correctIntervals = 0
    data.wrongIntervals = 0
    
    
    
####################################
# mode dispatcher
####################################

def mousePressed(event, data):
    if (data.mode == "home"): homeMousePressed(event, data)
    elif (data.mode == "freePlay"):   freePlayMousePressed(event, data)
    elif (data.mode == "pickInterval"): pickIntervalMousePressed(event, data)
    elif (data.mode == "mainPg"):   mainPgMousePressed(event, data)
    elif (data.mode == "help"):       helpMousePressed(event, data)
    elif (data.mode == "melodyPlaybackMain"):       melodyPlaybackMainMousePressed(event, data)

def keyPressed(event, data):
    if (data.mode == "home"): homeKeyPressed(event, data)
    elif (data.mode == "freePlay"):   freePlayKeyPressed(event, data)
    elif (data.mode == "pickInterval"): pickIntervalKeyPressed(event, data)
    elif (data.mode == "mainPg"):   mainPgKeyPressed(event, data)
    elif (data.mode == "help"):       helpKeyPressed(event, data)
    elif (data.mode == "melodyPlaybackMain"):       melodyPlaybackMainKeyPressed(event, data)

def timerFired(data):
    if (data.mode == "home"): homeTimerFired(data)
    elif (data.mode == "freePlay"):   freePlayTimerFired(data)
    elif (data.mode == "pickInterval"): pickIntervalTimerFired(data)
    elif (data.mode == "mainPg"):   mainPgTimerFired(data)
    elif (data.mode == "help"):       helpTimerFired(data)
    elif (data.mode == "melodyPlaybackMain"):       melodyPlaybackMainTimerFired(data)

def redrawAll(canvas, data):
    drawBackground(canvas, data)
    if (data.mode == "home"): homeRedrawAll(canvas, data)
    elif (data.mode == "freePlay"):   freePlayRedrawAll(canvas, data)
    elif (data.mode == "pickInterval"): pickIntervalRedrawAll(canvas, data)
    elif (data.mode == "mainPg"):   mainPgRedrawAll(canvas, data)
    elif (data.mode == "help"):       helpRedrawAll(canvas, data)
    elif (data.mode == "melodyPlaybackMain"):       melodyPlaybackMainRedrawAll(canvas, data)
    
####################################
# home mode
####################################
from graphics import timerFired1 as homeTF
from graphics import redrawAll1 as homeRA
from graphics import roundRectangle
from intervals import roundRectangleButtons

def homeMousePressed(event, data):
    if event.x > data.x0FreePlayButton and event.x < data.x1FreePlayButton:
        #freePlay
        if event.y > data.y0FreePlayButton and event.y < data.y1FreePlayButton:
            data.mode = "freePlay"
        #pickInterval
        elif event.y > data.y0FreePlayButton +90 and event.y < data.y1FreePlayButton +90:
            data.mode = "pickInterval"
        #melodyPlayback
        elif event.y > data.y0FreePlayButton +180 and event.y < data.y1FreePlayButton +180:
            data.mode = "melodyPlaybackMain"
    
def homeKeyPressed(event, data):
    pass
    
def homeTimerFired(data):
    homeTF(data)

def homeRedrawAll(canvas, data):
    homeRA(canvas, data)

####################################
# freePlay mode
####################################

def freePlayMousePressed(event, data):
    #plays notes that are clicked with mouse
    getKeyMouse(data, event.x, event.y)
    if data.selection[1] != "nothing":
        note = data.keyToSound[(data.selection[0], data.selection[1])]
        t = threading.Thread(name='worker', target=worker, args=(note,))
        t.start()
            
    #clicked show note names
    if event.x > data.x0NamesButton and event.x < \
    data.x1NamesButton and event.y > data.y0NamesButton and \
    event.y < data.y1NamesButton:
        if data.showNoteNames:
            data.showNoteNames = False
        elif not data.showNoteNames:
            data.showNoteNames = True
      
    #stores key press
    if data.record:
        getKeyMouse(data, event.x, event.y)
        if data.selection[1] != "nothing":
            data.notesPlayed.append([(data.selection[0], data.selection[1]), data.clock])
            
    #clicked record
    if event.x > data.x0RecordButton and event.x < \
    data.x1RecordButton and event.y > data.y0RecordButton and \
    event.y < data.y1RecordButton:
        data.numTimesRecordPressed += 1
        if data.numTimesRecordPressed % 2 == 1 and data.numTimesRecordPressed != 1:
            data.notesPlayed = []
        if data.record and len(data.notesPlayed) != 0:
            pass
        if data.record:
            data.record = False
            data.enterTxt = True
        elif not data.record:
            data.record = True
        
    #if play back recording button is pressed
    if event.x > data.x0PlayButton and event.x < \
    data.x1PlayButton and event.y > data.y0PlayButton and \
    event.y < data.y1PlayButton:
        for i in range(len(data.notesPlayed)):
            t = threading.Thread(name='worker', target=worker, args=(data.keyToSound[data.notesPlayed[i][0]],))
            t.start()
            if i != len(data.notesPlayed) - 1:
                data.sleepTime = (data.notesPlayed[i+1][1]-data.notesPlayed[i][1])/8.0
                data.stopClockFP = True
                freePlayTimerFired(data)
            time.sleep(0.01)
        
    #if back button is pressed 
    if event.x > data.x0BackButton and event.x < \
    data.x1BackButton and event.y > data.y0BackButton and \
    event.y < data.y1BackButton:
        #pressed on normal screen
        if not data.greyBg:
            if data.mode == "freePlay":
                data.mode = "home"
                print data.mode
        #back button pressed on recordings screen
        else:
            data.greyBg = False
            
    #If dialog box is clicked in 
    if event.x > data.x0DialogBox and event.x < \
    data.x1DialogBox and event.y > data.y0DialogBox and \
    event.y < data.y1DialogBox:
        data.enterTxt = True
        
    #If see recordings button is clicked
    if event.x > data.x0SeeRecordingsButton and event.x < \
    data.x1SeeRecordingsButton and event.y > data.y0SeeRecordingsButton and \
    event.y < data.y1SeeRecordingsButton:
        data.greyBg = True
        
    #Read in previous recordings
    if not data.programOpened: 
        data.contentsRead = readFile("recordingsFile.txt")
        #only happens once when opening up the program for the first time
        oldContents = data.contentsRead.split(" ")
        for i in range(len(oldContents)):
            data.recordings.append(oldContents[i])
        data.programOpened = True
      
    #saves recordings to file
    if event.x > data.x0SaveRecordingsButton and event.x < \
    data.x1SaveRecordingsButton and event.y > data.y0SaveRecordingsButton and \
    event.y < data.y1SaveRecordingsButton:
        contentsToWrite = ""
        for i in range(len(data.recordings)):
            if i != len(data.recordings) - 1:
                contentsToWrite = contentsToWrite + data.recordings[i] + " "
            else:
                contentsToWrite = contentsToWrite + data.recordings[i]
        
        writeFile("recordingsFile.txt", contentsToWrite)
        
    #plays back a selected recording
    if data.greyBg:
        boxHeight = 35
        if event.x > data.x0SBox and event.x < data.x1SBox:
            index = (event.y - data.y0SBox) // boxHeight
            if index < len(data.recordings):
                song = data.recordings[index]
                print song
                t = threading.Thread(name='worker', target=worker, args=(song,))
                t.start()
                
def readFile(path):
    with open(path, "rt") as f:
        return f.read()

def writeFile(path, contents):
    with open(path, "wt") as f:
        f.write(contents)

def makeRecording(data):
    notes = []
    for i in range(len(data.notesPlayed)):
        note = data.keyToSound[data.notesPlayed[i][0]]
        notes.append(note)
    infiles = notes
    outfile = data.recordingName + ".wav"
    
    data = []
    for infile in infiles:
        w = wave.open(infile, 'rb')
        data.append( [w.getparams(), w.readframes(w.getnframes())] )
        w.close()
    
    output = wave.open(outfile, 'wb')
    output.setparams(data[0][0])
    for i in range(len(notes)):
        output.writeframes(data[i][1])
    output.close()
    
def freePlayKeyPressed(event, data):
    if event.keysym == "Return":
        data.enterTxt = False
        makeRecording(data)
        data.recordings.append(data.recordingName + ".wav")
        data.recordingName = ""
    if data.enterTxt:
        if event.keysym.isalnum():
            data.recordingName = data.recordingName + event.keysym

def freePlayTimerFired(data):
    data.clock += 1
    if data.stopClockFP:
        time.sleep(data.sleepTime)
        data.stopClockFP = False
        
    updateLeapMotionData(data)
    printLeapMotionData(data)
        
    #unhighlights a key that was played after 1 second
    notePlayedCopy = copy.deepcopy(data.notePlayed)
    for i in range(len(notePlayedCopy)):
        if data.clock - notePlayedCopy[i][1] >= 10:
            data.notePlayed.pop(i)
            
    if data.clock - data.selection[2] > 10:
        data.selection[1] = "nothing"
        
        
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
            #print "HERE", data.lPointerPos
        else:
            data.rPointerPos = hand.palm_position
            data.rHandOnScreen = True
            
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
            
            #stores tip positions on fingers in Leap coordinates (y is opposite)
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
                d = {0:13, 1:20, 2:20, 3:17, 4:13}
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
    #dictionary of yCoor: time
    dic[int(data.rFingerLst[finger][1])] = data.clock
    
    #loops through possible range of y movements that count as key being pressed
    for i in range(lowerBound, 45):
        #checks finger is on piano
        if data.rFingerLst[finger][1] < 135 and data.rFingerLst[finger][1] > 40:
            if int(data.rFingerLst[finger][1]) + i in dic:
                #check downwards movement was quick enough
                if dic[int(data.rFingerLst[finger][1])] - \
                dic[int(data.rFingerLst[finger][1]) + i] <= 2 and\
                 dic[int(data.rFingerLst[finger][1])] - \
                 dic[int(data.rFingerLst[finger][1]) + i] >= 0:
                    #check if movements are far enough apart timewise
                    if data.clock - data.prevTime[finger] > 2:
                        data.prevTime[finger] = data.clock
                        getKeyHand(data, data.rFingerLst[finger][0], \
                        (data.rFingerLst[finger][1] + \
                        int(data.rFingerLst[finger][1]) + i)/2, 1)
                        #plays note
                        if tuple(data.selectionHand[finger]) in data.keyToSound:
                            note = data.keyToSound[tuple(data.selectionHand[finger])]
                            data.notePlayed.append([tuple(data.selectionHand[finger]), data.clock])
                            a = threading.Thread(name='worker', target=worker, \
                            args=(note,))
                            a.start()
                            time.sleep(0.01)
                        break


def getKeyMouse(data, x, y):
    #updates where user presses
    wKeyIndex = (x - data.xMargin) // data.wKeyWidth
    #bottom half of key
    if y > data.yMargin + data.bKeyLength and y < data.yMargin + data.wKeyLength:
        data.selection[0] = (x - data.xMargin) // data.wKeyWidth 
        data.selection[1] = "white"
        data.selection[2] = data.clock
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
        data.selection[2] = data.clock
    else:
        data.selection[1] = "nothing"
        data.selection[2] = data.clock
            
    data.keysPlayed.append([data.selection[0], data.selection[1]])
            
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
    wPlayedIndexes = set()
    bPlayedIndexes = set()
    wNoteNames = {0:"C", 1:"D", 2:"E", 3:"F", 4:"G", 5:"A", 6:"B", 7:"C", 8:"D", 9:"E"}
    bNoteNames = {0:"C#", 1:"Eb", 3:"F#", 4:"Ab", 5:"Bb", 7:"C#", 8:"Eb"}
    
    for i in range(len(data.notePlayed)):
        if data.notePlayed[i][0][1] == "white":
            wPlayedIndexes.add(data.notePlayed[i][0][0])
        elif data.notePlayed[i][0][1] == "black":
            bPlayedIndexes.add(data.notePlayed[i][0][0])
    
    #stores locations of fingers
    for i in range(len(data.selectionHand)):
        if data.selectionHand[i][1] == "white":
            wSelectedIndexes.add(data.selectionHand[i][0])
        elif data.selectionHand[i][1] == "black":
            bSelectedIndexes.add(data.selectionHand[i][0])
   
    #print wSelectedIndexes
    for i in range(10):
        #draw white keys
        if i == data.selection[0] and data.selection[1] == "white": #mouse on key
            rgb2 = (113, 169, 247)
            color = "#%02x%02x%02x" % rgb2
        elif i in wPlayedIndexes:
            color = "green"
        else:
            color = "white"
        canvas.create_rectangle(wKeyWidth*i+margin, startYOnScreen,\
        margin+wKeyWidth*(i+1), startYOnScreen + wKeyLength, outline = "black", fill=color)
        if data.showNoteNames:
            canvas.create_text((wKeyWidth*i+margin + margin+wKeyWidth*(i+1))*1/2, (startYOnScreen + startYOnScreen + wKeyLength)*1/2+100, text=wNoteNames[i], font="Palatino 20 bold")
            
    for i in range(10):
        #draw black keys
        if i == data.selection[0] and data.selection[1] == "black":
            rgb2 = (113, 169, 247)
            color = "#%02x%02x%02x" % rgb2
        elif i in bPlayedIndexes:
            color = "green"
        else:
            color = "black"
            
        if i != 2 and i!= 6 and i != 9 and i != 11:
            canvas.create_rectangle(wKeyWidth*i+margin+bKeyShift, startYOnScreen,\
            wKeyWidth*i+margin+bKeyShift+bKeyWidth, startYOnScreen + bKeyLength,\
            fill = color)
            if data.showNoteNames:
                canvas.create_text((wKeyWidth*i+margin+bKeyShift + wKeyWidth*i+margin+bKeyShift+bKeyWidth)*1/2, (2*startYOnScreen + bKeyLength)*1/2+50, text = bNoteNames[i], font="Palatino 20 bold", fill="white")
              
def drawMainPointers(canvas, data):
    #draw RH pointer
    data.yRCoor = data.height - ((data.rPointerPos[1]-40) * data.height/160)
    data.xRCoor = (data.rPointerPos[0] - (-70))*data.width/140

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
    for i in range(len(data.rFingerLst)):
        xCoor = (data.rFingerLst[i][0] - (-100))*data.width/250
        yCoor = data.height - ((data.rFingerLst[i][1]-40) * data.height/160)
        getKeyHand(data, xCoor, yCoor, i)
        canvas.create_oval(xCoor-10, yCoor-10, xCoor+10, \
        yCoor+10, outline = "green")
        
    
def freePlayRedrawAll(canvas, data):
    drawPiano(canvas, data)
    drawMainPointers(canvas, data)
    drawFingerPointers(canvas, data)
    #forwardArrow(canvas, data)
    backArrow(canvas, data)
    
    #Show note names
    if data.showNoteNames:
        rgb2 = (85, 50, 211)
        color = "#%02x%02x%02x" % rgb2
        canvas.create_line(data.x0NamesButton+15, data.y1NamesButton-25, data.x1NamesButton+10, data.y1NamesButton-25, width=4, fill=color)
    
    #Record and stop recording buttons
    if not data.record:
        canvas.create_oval(data.width/2-50,225,data.width/2+10,285,fill='', width=4)
        canvas.create_oval(data.width/2-40,235,data.width/2,275,fill="red")
    elif data.record:
        canvas.create_oval(data.width/2-50,225,data.width/2+10,285,fill='', width=4)
        roundRectangle(canvas, data, data.width/2-40,235,data.width/2,275,2,20,"red")
    
    #Playback recording
    canvas.create_oval(data.width/2+30, 225, data.width/2+90,285, width=4, fill='')
    canvas.create_polygon(data.width/2+45,235,data.width/2+45,275,data.width/2+80,255)
    
    rgb = (76, 16, 54)
    f = "#%02x%02x%02x" % rgb
    #Text
    if not data.greyBg:
        canvas.create_text(data.width/2, 60, text="Press a note to get started!", font="Palatino 40 bold", fill="#%02x%02x%02x" % rgb)
        canvas.create_text(data.width/2, 110, text="Confuzzled? Click here to learn the names of the notes", font="Palatino 20 bold", fill="#%02x%02x%02x" % rgb)
        canvas.create_text(data.width/2, 140, text="Feeling good? Click the buttons to record yourself and play it back", font="Palatino 20 bold", fill="#%02x%02x%02x" % rgb)
    
    #if user has finished a recording
    if data.enterTxt:
        if data.recordingName == "":
            txt = "Enter recording name"
            col = "gray"
        else:
            txt = data.recordingName
            col = "black"
        canvas.create_rectangle(data.width/2-150, 175, data.width/2+150, 210, outline="black", fill="white")
        canvas.create_text(data.width/2, 193, text=txt, fill=col)
        
    canvas.create_text(data.width/2, 659, text="Click here to view your recordings", font="Palatino 25 bold", fill="#%02x%02x%02x" % rgb)
    
    #shows screen when user wants to see all recordings they've made
    if data.greyBg:
        showRecordings(canvas, data)
        
    #draws save recording button
    if not data.greyBg:
        roundRectangleButtons(canvas, data, data.x0SaveRecordingsButton, data.y0SaveRecordingsButton, data.x1SaveRecordingsButton, data.y1SaveRecordingsButton)
        canvas.create_text((data.x0SaveRecordingsButton+data.x1SaveRecordingsButton)/2, (data.y0SaveRecordingsButton+data.y1SaveRecordingsButton)/2, text="Save", font='Palatino 20', fill='white')

        
def showRecordings(canvas, data):
    rgb = (238, 108, 77)
    f = "#%02x%02x%02x" % rgb
    x0BigBox = data.width/2-150
    x1BigBox = data.width/2+150
    
    #draws big box
    canvas.create_rectangle(x0BigBox, 125, x1BigBox, 542, fill=f, outline = "white", width = 4)
    canvas.create_text(data.width/2, 150, text="Recordings", fill="white", font="Palatino 30 bold")
    canvas.create_line(data.width/2-150, 170, data.width/2+150, 170, fill="white", width=3)
    
    #draws small box
    data.x0SBox = x0BigBox + 15
    data.x1SBox = x1BigBox - 15
    data.y0SBox = 185
    boxHeight = 35
    pbWidth = 20
    pbYPad = 7.5
    if '' in data.recordings or ' ' in data.recordings:
        data.recordings.remove('')
    for i in range(len(data.recordings)):
        recName = data.recordings[i].split(".")[0]
        canvas.create_rectangle(data.x0SBox, data.y0SBox+boxHeight*(i), data.x1SBox, data.y0SBox+boxHeight*(i+1), fill="white")
        canvas.create_text(data.x0SBox + 10,\
         (data.y0SBox+boxHeight*(i+1)+data.y0SBox+boxHeight*i)/2, text=recName, anchor=W, font="Palatino 15")
        y0 = data.y0SBox+pbYPad+boxHeight*(i)
        canvas.create_oval(data.x1SBox-10-pbWidth, y0, data.x1SBox-10,y0+pbWidth, width=2, fill='')
    
def forwardArrow(canvas, data):
    #forward arrow
    rgb = (238, 108, 77)
    f = "#%02x%02x%02x" % rgb
    canvas.create_oval(data.width-20, 30, data.width-80,90, width=4, outline = 'white', fill=f)
    canvas.create_oval(60,38,63,41,outline='white',fill='white')
    canvas.create_oval(data.width-37,58,data.width-34,61,outline='white',fill='white')
    canvas.create_oval(data.width-61,77,data.width-58,80,outline='white',fill='white')
    canvas.create_oval(data.width-61,39,data.width-58,42,outline='white',fill='white')
    canvas.create_line(data.width-60,40,data.width-35,60, width = 4, fill='white')
    canvas.create_line(data.width-35,60,data.width-60,80, width = 4, fill='white')
    
def backArrow(canvas, data):
    #back arrow
    rgb = (238, 108, 77)
    f = "#%02x%02x%02x" % rgb
    canvas.create_oval(22, 30, 82,90, width=4, outline = 'white', fill=f)
    canvas.create_oval(60,38,63,41,outline='white',fill='white')
    canvas.create_oval(35,58,38,61,outline='white',fill='white')
    canvas.create_oval(60,78,63,81,outline='white',fill='white')
    canvas.create_line(62,40,37,60, width = 4, fill='white')
    canvas.create_line(37,60,62,80, width = 4, fill='white')
####################################
# Intervals pickInterval mode
####################################
from intervals import pickIntervalMousePressed as pickIntervalMP
from intervals import pickIntervalKeyPressed as pickIntervalKP
from intervals import pickIntervalTimerFired as pickIntervalTF
from intervals import pickIntervalRedrawAll as pickIntervalRA
from intervals import getButtonPressed, getButtonPressedMP

def pickIntervalMousePressed(event, data):
    #clicked back
    if event.x > data.x0BackButton and event.x < \
    data.x1BackButton and event.y > data.y0BackButton and \
    event.y < data.y1BackButton:
        data.mode = "home"
    #clicked forward
    elif event.x > data.x0ForwardButton and event.x < \
    data.x1ForwardButton and event.y > data.y0ForwardButton and \
    event.y < data.y1ForwardButton:
        data.mode = "mainPg"
    
    pickIntervalMP(event, data)
    
def pickIntervalKeyPressed(event, data):
    pickIntervalKP(event, data)
    
def pickIntervalTimerFired(data):
    pickIntervalTF(data)
    
def pickIntervalRedrawAll(canvas, data):
    backArrow(canvas, data)
    forwardArrow(canvas, data)
    pickIntervalRA(canvas, data)

####################################
# Intervals mainPg mode
####################################
from intervals import mainPgMousePressed as mainPgMP
from intervals import mainPgRedrawAll as mainPgRA
from intervals import mainPgTimerFired as mainPgTF

def mainPgMousePressed(event, data):
    #clicked back
    if event.x > data.x0BackButton and event.x < \
    data.x1BackButton and event.y > data.y0BackButton and \
    event.y < data.y1BackButton:
        data.mode = "pickInterval"
    
    mainPgMP(event, data)
    
def mainPgRedrawAll(canvas, data):
    backArrow(canvas, data)
    mainPgRA(canvas, data)
    
def mainPgTimerFired(data):
    mainPgTF(data)
    
def mainPgKeyPressed(event, data):
    pass
    
####################################
# melodyPlaybackMain mode
####################################
from melodyPlayback import mousePressed as melodyPlaybackMP
from melodyPlayback import redrawAll as melodyPlaybackRA
from melodyPlayback import timerFired as melodyPlaybackTF

def melodyPlaybackMainMousePressed(event, data):
    #clicked back
    if event.x > data.x0BackButton and event.x < \
    data.x1BackButton and event.y > data.y0BackButton and \
    event.y < data.y1BackButton:
        data.mode = "home"
        
    melodyPlaybackMP(event, data)
    
def melodyPlaybackMainRedrawAll(canvas, data):
    backArrow(canvas, data)
    melodyPlaybackRA(canvas, data)
    
def melodyPlaybackMainTimerFired(data):
    melodyPlaybackTF(data)
    
def melodyPlaybackMainKeyPressed(event, data):
    pass

####################################
# use the run function as-is
####################################

def run(width=300, height=300):
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

run(1000, 700)