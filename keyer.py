import time
import sys
import serial
import argparse

chars =   {'A':'.-',
           'B':'-...',
           'C':'-.-.',
           'D':'-..',
           'E':'.',
           'F':'..-.',
           'G':'--.',
           'H':'....',
           'I':'..',
           'J':'.---',
           'K':'-.-',
           'L':'.-..',
           'M':'--',
           'N':'-.',
           'O':'---',
           'P':'.--.',
           'Q':'--.-',
           'R':'.-.',
           'S':'...',
           'T':'-',
           'U':'..-',
           'V':'...-',
           'W':'.--',
           'X':'-..-',
           'Y':'-.--',
           'Z':'--..',
           '0':'-----',
           '1':'.----',
           '2':'..---',
           '3':'...--',
           '4':'....-',
           '5':'.....',
           '6':'-....',
           '7':'--...',
           '8':'---..',
           '9':'----.',
           '?':'..--..',
	   '.':'.-.-.-',
           ',':'--..--'
           }


def gap():
  time.sleep(charspace)

def wordgap():
  time.sleep(wordspace)

def dah():
  cw_key(key_open)
  cw_key(key_close)
  time.sleep(dahspeed)
  cw_key(key_open)
  time.sleep(ditspeed)

def dit():
  cw_key(key_open)
  cw_key(key_close)
  time.sleep(ditspeed)
  cw_key(key_open)
  time.sleep(ditspeed)

def word(w):
  for c in w:
      try:
          code = chars[c]
      except KeyError:
          # FIXME: Use proper logging facility here
          print('Skipping unknown character %s' % c)
          continue

      for dahdit in code:
        if dahdit == '-':
          dah()
        else:
          dit()
      gap()
  wordgap()

def paris():
  count=0
  while True:
    word("PARIS")
    count+=1
    print(count)

parser = argparse.ArgumentParser(description='CW keyer for serial interface.')
parser.add_argument('-d', '--device', dest='device', default='/dev/ttyUSB0', help='Path to serial device. (default: /dev/ttyUSB0)')
parser.add_argument('-w', '--wpm', dest='wpm', type=int, default=20, help='CW keying speed in words per minutes. (default: 20 wpm)')
parser.add_argument('-t', '--text', dest='text', required=True, help='Text to transmit. Surround multiple words by quotes.')
parser.add_argument('--dtr', dest='dtr', action='store_true', help='Use DTR pin instead of RTS pin for keying.')
parser.add_argument('--invert', dest='invert', action='store_true', help='Invert logic signals on pin used for keying.')
args = parser.parse_args()

ser = serial.Serial(args.device, 9600)
if args.dtr:
  cw_key = ser.setDTR
else:
  cw_key = ser.setRTS

if args.invert:
  key_close = False
  key_open = True
else:
  key_close = True
  key_open = False

ditspeed = (1200.0 / float(args.wpm)) / 1000.0
dahspeed = ditspeed * 3
charspace = ditspeed * 1
wordspace = ditspeed * 7

for w in args.text.upper().split():
   word(w)
