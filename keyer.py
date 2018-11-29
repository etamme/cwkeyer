import time
import sys
import serial
import argparse

ser = ditspeed = dahspeed = charspace = wordspace = ""
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
           '9':'----.'
           }


def gap():
  time.sleep(charspace)

def wordgap():
  time.sleep(wordspace)

def dah():
  global pin
  if pin=="RTS":
    ser.setRTS(False)
    ser.setRTS(True)
  else: 
    ser.setDTR(False)
    ser.setDTR(True)
  time.sleep(dahspeed)
  if pin=="RTS":
    ser.setRTS(False)
  else:
    ser.setDTR(False)
  time.sleep(ditspeed)


def dit():
  global pin
  if pin=="RTS":
    ser.setRTS(False)
    ser.setRTS(True)
  else: 
    ser.setDTR(False)
    ser.setDTR(True)
  time.sleep(ditspeed)
  if pin=="RTS":
    ser.setRTS(False)
  else:
    ser.setDTR(False)
  time.sleep(ditspeed)

def word(w):
  for c in w:
      code = chars[c]
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

def main(argv):
   # set defaults
   text = ''
   wpm = 20
   device = '/dev/ttyUSB0'
   global ser,ditspeed,dahspeed,charspace,wordspace,pin
   parser = argparse.ArgumentParser(description='CW keyer for serial interface.')
   parser.add_argument('-d', '--device', dest='device', required=True, help='Path to serial device. (e.g. /dev/ttyUSB0)')
   parser.add_argument('-w', '--wpm', dest='wpm', type=int, default=20, help='CW keying speed in words per minutes. (default: 20 wpm)')
   parser.add_argument('-t', '--text', dest='text', required=True, help='Text to transmit. Surround multiple words by quotes.')
   parser.add_argument('--dtr', dest='dtr', action='store_true', help='Use DTR pin instead of RTS pin for keying')
   args = parser.parse_args()

   if args.dtr:
       pin='DTR'
   else:
       pin='RTS'

   ser = serial.Serial(args.device, 9600);
   ditspeed = (1200.0 / float(args.wpm)) / 1000.0
   dahspeed = ditspeed * 3
   charspace = ditspeed * 1
   wordspace = ditspeed * 7

   for w in args.text.upper().split():
       word(w)

if __name__ == "__main__":
   main(sys.argv[1:])

