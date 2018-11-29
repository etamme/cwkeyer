import time
import sys
import serial
import getopt
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
   pin="RTS"
   try:
      opts, args = getopt.getopt(argv,"d:w:t:p",["d=","w=","t=","p="])
   except getopt.GetoptError:
         print('test.py -d <device> -w <wpm> -t <text> -p <pin - R for RTS, D for DTR>')
         sys.exit(2)
   for opt, arg in opts:
      if opt in ("-d", "--device"):
         device = arg
      elif opt in ("-w", "--wpm"):
         wpm = arg
      elif opt in ("-t", "--text"):
         text = arg.upper()
      elif opt in ("-p", "--pin"):
         pinarg = arg.upper()
         print(opt)
         print(arg)
         if pinarg == "R":
           print("set pin RTS")
           pin="RTS"
         elif pinarg == "D":
           print("set pin DTR")
           pin="DTR"
      
         
   
   ser = serial.Serial(device, 9600);
   ditspeed = (1200.0 / float(wpm)) / 1000.0
   dahspeed = ditspeed * 3
   charspace = ditspeed * 1
   wordspace = ditspeed * 7

   for w in text.split():
       word(w)

if __name__ == "__main__":
   main(sys.argv[1:])

