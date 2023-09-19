#!/usr/bin/env python3
from psychopy import visual, core, event
import re


def anyin(a, b):
    return(any([x in b for x in a]))


class showCal:
    def __init__(self, w=None):
        innerRadius = 5
        self.outerRadius = 20
        self.nrow, self.ncol = (3, 3)

        if(w is None):
            print("creating window b/c one wasn't given to showCal")
            w = visual.Window() # always fullscreen
            w.color = (-1,-1,-1)
            w.flip() # flip to get color change

        self.w = w

        self.showText = True

        self.c = visual.Circle(self.w)
        rx = self.w.size[0]
        ry = self.w.size[1]

        self.offset = 75

        effx = rx - 2 * self.offset
        effy = ry - 2 * self.offset

        self.spacingx = round(effx / (self.nrow - 1))
        self.spacingy = round(effy / (self.ncol - 1))

        self.outerC = visual.Circle(
            self.w,
            units='pix',
            radius=self.outerRadius,
            lineColor=None)
        self.innerC = visual.Circle(
            self.w,
            units='pix',
            radius=innerRadius,
            lineColor=None)
        self.txt = visual.TextStim(
            self.w, name='num', color='white', units='pix')

    def show(self, rednum=9):

        self.txt.color = 'white'
        for xi in range(self.ncol):
            xi = xi + 1
            cx = self.offset + self.spacingx * (xi - 1) - self.w.size[0] / 2
            for yi in range(self.nrow):
                yi = yi + 1
                cy = self.offset + self.spacingy * \
                    (yi - 1) - self.w.size[1] / 2
                cy = -1 * cy

                num = 3 * (yi - 1) + xi
                if num == rednum:
                    ovalcolor = 'red'  # [240, 30, 30]
                    innercolor = 'white'
                else:
                    ovalcolor = 'lightblue'  # [.46, .54, .60]*255
                    innercolor = 'black'

                # outer circle
                self.outerC.fillColor = ovalcolor
                self.outerC.pos = [cx, cy]
                self.outerC.draw()

                # inner circle
                self.innerC.pos = [cx, cy]
                self.innerC.fillColor = innercolor
                self.innerC.draw()

                # number
                self.txt.text = "%d" % num
                self.txt.pos = [cx + self.outerRadius, cy + self.outerRadius]
                self.txt.draw()

                #print("%d %d,%d %d,%d %s" % (num, xi, yi, cx, cy, ovalcolor))

        # upper help text
        if(self.showText):
            self.txt.text = "Eye calibrate: look at white center"
            self.txt.pos = [0, self.w.size[1] / 2 * .33]
            self.txt.draw()
            # lower help text
            self.txt.text = "q:quit, enter:center, 1:start, space:advance\nt:toggle text"
            self.txt.color = '#333333'
            self.txt.pos = [0, -self.w.size[1] / 2 * .33]
            self.txt.draw()
        self.w.flip()
        core.wait(.05)

    def calibrate(self):
        num = 1
        self.show(num)
        movekeys = ['space', 'left', 'right', 'up', 'down',
                    'q', 'escape',
                    'c', 'return',
                    't',
                    '1','2', '3', '4', '5', '6', '7', '8', '9']
        while(True):
            keys = event.waitKeys(keyList=movekeys)
            if 'left' in keys:
                num = num - 1
            elif anyin(keys, ['right', 'space']):
                num = num + 1
            elif 'up' in keys:
                num = num - self.nrow
            elif 'down' in keys:
                num = num + self.nrow
            elif anyin(keys, ['return', 'c']):
                num = 5
            elif 't' in keys:
                self.showText = not self.showText
            elif re.match('[1-9]', keys[0]):
                num = int(keys[0])
            else:  # anyin(keys, ['q','escape']):
                break
            num = num % (self.nrow * self.ncol)
            if num == 0:
                num = 9
            self.show(num)


if __name__ == "__main__":
    win = visual.Window(fullscr=True)
    win.color=(-1,-1,-1)
    win.flip()
    c = showCal(win)
    c.calibrate()
