# Waveshare 160 Neopixel Board Basic
# Tony Goodhew 19th April 2022 for thepihut.com
import array, utime
from machine import Pin
import rp2
import random
# Configure the number of WS2812 LEDs.
NUM_LEDS = 160 # 10 rows of 16 Neopixels
PIN_NUM = 6
brightness = 0.1

# Boilerplate Neopixel driver for RP2040
@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
def ws2812():
    T1 = 2
    T2 = 5
    T3 = 3
    wrap_target()
    label("bitloop")
    out(x, 1)               .side(0)    [T3 - 1]
    jmp(not_x, "do_zero")   .side(1)    [T1 - 1]
    jmp("bitloop")          .side(1)    [T2 - 1]
    label("do_zero")
    nop()                   .side(0)    [T2 - 1]
    wrap()

# Create the StateMachine with the ws2812 program, outputting on pin
sm = rp2.StateMachine(0, ws2812, freq=8_000_000, sideset_base=Pin(PIN_NUM))

# Start the StateMachine, it will wait for data on its FIFO.
sm.active(1)

# Display a pattern on the LEDs via an array of LED RGB values.
ar = array.array("I", [0 for _ in range(NUM_LEDS)])

####################### Functions ##############################

def pixels_show():
    dimmer_ar = array.array("I", [0 for _ in range(NUM_LEDS)])
    for i,c in enumerate(ar):
        r = int(((c >> 8) & 0xFF) * brightness)
        g = int(((c >> 16) & 0xFF) * brightness)
        b = int((c & 0xFF) * brightness)
        dimmer_ar[i] = (g<<16) + (r<<8) + b
    sm.put(dimmer_ar, 8)
    utime.sleep_ms(10)

def pixels_set(i, colour):
    ar[i] = (colour[1]<<16) + (colour[0]<<8) + colour[2]
    
def xy_set(x, y, colour):
    # Valid Neopixel check
    if (x >= 0) and (x < 16) and (y >= 0) and (y < 11):
        pos = x + y*16
        pixels_set(pos, colour)

def pixels_fill(colour):
    for i in range(len(ar)):
        pixels_set(i, colour)

def clear():
    colour = (0,0,0)
    pixels_fill(colour)
    
def rect(x,y,w,h,r,g,b):
    # Hollow square at (x,y), w pixels wide coloured (r,g,b)
    cc = (r,g,b)
    for i in range(x,x+w):
        xy_set(i,y,cc)       # Top
        xy_set(i,y+h-1,cc)   # Bottom
    for i in range(y+1,y+h):
        xy_set(x,i,cc)       # Left
        xy_set(x+w-1,i,cc)   # Right

def vert(x,y,l,r,g,b):
    # Vertical line at (x,y) of length l coloured (r,g,b)
    cc = (r,g,b)
    for i in range(l):
        xy_set(x,i,cc)

def horiz(x,y,l,r,g,b):
    # Horizontal line from (x,y) of length l coloured (r,g,b)
    cc = (r,g,b)
    for i in range(l):
        xy_set(i,y,cc)


####################### Main Program ##############################
# Snake Game Program
# x = 0 ... 15
# y = 0 ... 9
snake = []
snake.append(32)
snake.append(16)
snake.append(0)
length = 3
apple = random.randint(0, 159)
pixels_set(apple, (255,0,0))

def makeApple():
    while True:
        apple = random.randint(0, 159)
        if apple not in snake:
            return apple

hamiltonianPath =    [1,2,3,4,20,6,7,8,9,10,11,12,13,14,15,31,
                      0, 33,17,18,36,5,21,22,23,24,42,26,27,28,46,30,
                     16, 32,35,19,37,38,39,40,41,25,43,59,45,29,47,63,
                     49, 65,35,50,51,52,53,54,55,56,74,58,44,60,61,62,
                     48, 81,67,68,69,70,86,72,73,57,75,91,77,78,79,95,
                     64, 82,66,99,83,101,85,71,87,105,89,107,76,92,93,111,
                     80, 96,97,115,84,117,103,104,88,121,90,123,109,125,94,127,
                    113,114,98,131,100,133,102,135,119,120,106,122,108,141,110,143,
                    112,145,129,147,116,134,118,136,137,138,139,140,124,142,126,159,
                    128,144,130,146,132,148,149,150,151,152,153,154,155,156,157,158]

for i in snake:
        pixels_set(i, (0,255,0))

pixels_show()

while length < 160 :
    pop = snake.pop(0)
    pixels_set(pop, (0,0,0))
    snake.append(hamiltonianPath[snake[length-2]])
    if snake[length-1] == apple:
        length += 1
        apple = makeApple()
        pixels_set(apple, (255,0,0))
        snake.append(pop)
    for i in snake:
        pixels_set(i, (0,255,0))
    pixels_show()
    utime.sleep_ms(10)
utime.sleep_ms(1000)
clear()
pixels_show()

    

