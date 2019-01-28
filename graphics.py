'''A short random melody will be played and the user has to attempt to play it back correctly. The first note of the melody will be displayed on the screen. Once the user is ready to submit an answer, they click the “Start” button and start playing. They click the “end” button once they are done. Clicking “Check” allows them to check their work. They’ll be told whether they got it right or wrong. They can also replay melodies. If they’re stuck, then they can ask for help (this will play the notes while highlighting the corresponding key)'''

import random, math
from Tkinter import *
import tkFont
from PIL import Image
from image_util import *

def init(data):
    
    #little circles
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
    
def drawBackground(canvas, data):
    '''https://stackoverflow.com/questions/10158552/how-to-use-an-image-for-the-background-in-tkinter'''
    background = PhotoImage(file="bg1.gif")
    canvas.create_image(0, 0, anchor = NW, image = background)
    #makes sure image doesn't disappear
    label = Label(image=background)
    label.image = background # keep a reference!
    label.pack()
    if data.greyBg:
        background1 = PhotoImage(file="bg2.gif")
        canvas.create_image(0, 0, anchor = NW, image = background1)
        #makes sure image doesn't disappear
        label = Label(image=background1)
        label.image = background1 # keep a reference!
        label.pack()
    
    
def redrawAll1(canvas, data):
    #background
    drawBackground(canvas, data)
    
    #draws small sparkling circles
    for i in range(15):
        x0 = random.randint(10, data.width - 10)
        y0 = random.randint(10, data.width - 10)
        r = 1
        canvas.create_oval(x0, y0, x0 + r, y0 + r, fill = "white", outline="white")
        
    #draws little circles
    for circle in data.whiteCircles:
        rgb = (235, 227, 244)
        x0, y0, x1, y1 = circle[0], circle[1], circle[2], circle[3]
        canvas.create_oval(x0, y0, x1, y1, fill="#%02x%02x%02x" % rgb, outline="#%02x%02x%02x" % rgb)
        
    #draws big circles
    for circle in data.bigCircles:
        rgb = (203, 224, 244)
        x0, y0, x1, y1 = circle[0], circle[1], circle[2], circle[3]
        canvas.create_oval(x0, y0, x1, y1, fill="#%02x%02x%02x" % rgb, outline="#%02x%02x%02x" % rgb)
        
    rgb = (85, 50, 211)
    canvas.create_text(data.width/2, data.height/5, text = "Piano To Go", fill = "#%02x%02x%02x" % rgb, font = "Palatino 100 bold")
    
    x0 = data.x0FreePlayButton = data.width/2 - data.boxRadius
    x1 = data.x1FreePlayButton = data.width/2 + data.boxRadius
    y0 = data.y0FreePlayButton = data.height/3
    y1 = data.y1FreePlayButton = data.height/3 + 60
    
    roundRectangle(canvas, data, x0, y0, x1, y1, \
    2, 25, "#%02x%02x%02x" % rgb)
    canvas.create_text(data.width/2, (y0 + y1)/2, text="Free play", fill ="white", font="Palatino 25")
    
    roundRectangle(canvas, data, x0, y0 + 90, x1, y1 + 90, \
    2, 25, "#%02x%02x%02x" % rgb)
    canvas.create_text(data.width/2, (y0 + y1 + 180)/2, \
    text="Practice Intervals", fill ="white", font="Palatino 25")
    
    roundRectangle(canvas, data, x0, y0 + 180, x1, y1 + 180,\
     2, 25, "#%02x%02x%02x" % rgb)
    canvas.create_text(data.width/2, (y0 + y1 + 360)/2, text="Melody Playback", \
    fill ="white", font="Palatino 25")
    
    #draws white edges
    roundRectangle(canvas, data, 10, 10, data.width-10, data.height-10, 3)
    roundRectangle(canvas, data, 15, 15, data.width-15, data.height-15, 2)
    roundRectangle(canvas, data, 18, 18, data.width-18, data.height-18, 1)


def timerFired1(data):
    if data.timerDelay % 1000 == 0:
        data.secs += 1
    moveCircles(data, data.speed1, data.bigCircles)
    moveCircles(data, data.speed2, data.whiteCircles)

            
def moveCircles(data, speed, circType):
    #wrap around
    for i in range(len(circType)):
        circType[i][0] += speed * circType[i][4][0]
        circType[i][1] += speed * circType[i][4][1]
        circType[i][2] += speed * circType[i][4][0]
        circType[i][3] += speed * circType[i][4][1]
        reactToWallHit(data, circType[i])
        
def reactToWallHit(data, circle):
    x0, y0, x1, y1 = circle[0], circle[1], circle[2], circle[3]
    if x1 > data.width:
        circle[0], circle[2] = 0, circle[5]
    elif x0 < 0:
        circle[0], circle[2] = data.width - circle[5], data.width
    elif y1 > data.height:
        circle[1], circle[3] = 0, circle[5]
    elif y0 < 0:
        circle[1], circle[3] = data.height - circle[5], data.height
    
def roundRectangle(canvas, data, x1, y1, x2, y2, w, radius=25, f = ''):
    #https://stackoverflow.com/questions/44099594/how-to-make-a-tkinter-canvas-rectangle-with-rounded-corners
    points = [x1+radius, y1, x1+radius, y1, x2-radius, y1, x2-radius, y1, \
    x2, y1, x2, y1+radius, x2, y1+radius, x2, y2-radius, x2, y2-radius, x2, \
    y2, x2-radius, y2, x2-radius, y2, x1+radius, y2, x1+radius, y2, x1, y2,\
    x1, y2-radius, x1, y2-radius, x1, y1+radius, x1, y1+radius, x1, y1]

    canvas.create_polygon(points, smooth=True, outline="white", width = w, fill=f)

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