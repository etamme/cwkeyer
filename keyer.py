import time
import sys
import serial
import argparse

chars =   {'A':'._',
           'B':'_...',
           'C':'_._.',
           'D':'_..',
           'E':'.',
           'F':'.._.',
           'G':'__.',
           'H':'....',
           'I':'..',
           'J':'.___',
           'K':'_._',
           'L':'._..',
           'M':'__',
           'N':'_.',
           'O':'___',
           'P':'.__.',
           'Q':'__._',
           'R':'._.',
           'S':'...',
           'T':'_',
           'U':'.._',
           'V':'..._',
           'W':'.__',
           'X':'_.._',
           'Y':'_.__',
           'Z':'__..',
           '0':'_____',
           '1':'.____',
           '2':'..___',
           '3':'...__',
           '4':'...._',
           '5':'.....',
           '6':'_....',
           '7':'__...',
           '8':'___..',
           '9':'____.',
           '?':'..__..',
	   '.':'._._._',
           ',':'__..__',
           '/':'_.._.'
           }

cut_nums = {
            '1':'._',
            '9':'_.',
            '0':'_'
           }

# These are the default macro keys/CW prosigns in fldigi
#fldigi_default_macros = {
#  '=':'<BT>',
#  '~':'<AA>',
#  '>':'<AR>',
#  '<':'<AS>',
#  '{':'<HM>',
#  '&':'<INT>',
#  '%':'<SK>',
#  '+':'<KN>',
#  '}':'<VE>' } 

#fldigi_prosigns = {
#  '=':'_..._',
#  '~':'._._',
#  '>':'._._.',
#  '<':'._...',
#  '{':'....__',
#  '&':'.._._',
#  '%':'..._._',
#  '+':'_.__.',
#  '}':'..._.' }
  

class cw_text_parser:
  def __init__(self, wpm):
    # FIXME: Check if we really need float() here
    self.wpm = float(wpm)
    self.recalculate_speeds()

  def recalculate_speeds(self):
    self.ditspeed = (1200. / self.wpm) / 1000.
    self.dahspeed = self.ditspeed * 3
    self.charspace = self.dahspeed
    self.intracharspace = self.ditspeed
    self.wordspace = self.ditspeed * 7

  def wait_charspace(self):
    # sleep between characters
    time.sleep(self.charspace)

  def wait_intracharspace(self):
    # sleep between dits and dahs within a character
    time.sleep(self.intracharspace)

  def wait_wordspace(self):
    # sleep between words
    time.sleep(self.wordspace)

  # keydown for "duration" time, and pad after with "gap" time
  def key(self, keydown_time):
    cw_key(key_open)
    cw_key(key_close)
    time.sleep(keydown_time)
    cw_key(key_open)

  def word(self, w):
    i=0
    while i < len(w):
      c=w[i]
      # catch a new macro escape
      if c == "<":
        code=""
        # setup the first char of the macro past the macro escape char '<'
        i+=1
        macro=w[i]
        # loop matching macro commands, till we find '>'
        # each time a macro "match" is found, execute it
        # then reset the macro command, and increment index
        while True:
          if macro == "+" or macro == "-":
            if macro == "+":
              self.wpm += 5
              if args.debugmacro:
                print("<SPEED INCREASE>")
            else:
              self.wpm += -5
              if args.debugmacro:
                print("<SPEED DECREASE>")
                #TODO index speed macros if they are used with prosigns
                #     so that the macros are displayed in chronological
                #     order.
            self.recalculate_speeds()
            #reset current macro command
            macro = ""
          elif macro not in ("+","-",">","<"):
            code = code + chars[macro]
            macro=""
          elif macro == ">":
            self.send_char(code, i, w)
            #break out of the while loop
            if i < len(w)-1:
              i+=1
              c=w[i]
              macro=""
              code=""
            break
          
          i+=1
          macro = macro + str(w[i])
      else:
        try:
          code = chars[c]
          self.send_char(code, i, w)
          i+=1
          
        except KeyError:
          # skip unknown chars
          i+=1
          continue

  def send_char(self, code, word_index, parsed_word):
    if args.debugmacro:
      if parsed_word[word_index] == ">":
        for x in "+-":
           parsed_word = parsed_word.replace(x,"")
        if parsed_word != "<>":
          print(parsed_word + ":" + code)
      else:  
        print(parsed_word[word_index] + ":" + code)
    codeidx=0
    while codeidx < len(code):
      dahdit=code[codeidx]
      if dahdit == '_':
        self.key(self.dahspeed)
      else:
        self.key(self.ditspeed)
      # include intRA char spacing unless this is the last dah/dit
      if codeidx < len(code)-1:
        self.wait_intracharspace()
      codeidx+=1
    # include intER char spacing unless this is the last char in the word
    if word_index < len(parsed_word):
      self.wait_charspace()
    else:
      self.wait_wordspace()

# this is for diagnostic purposes only
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
parser.add_argument('--cut-nums',dest='cutnums',action='store_true',help='Use contest-style abbreviated numbers.')
parser.add_argument('--debug-macro',dest='debugmacro',action='store_true',help='Show Prosign and character code patterns as they are sent.')
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

if args.cutnums:
  chars.update(cut_nums)  

# iterate over the passed string as individual words
p = cw_text_parser(args.wpm)
for w in args.text.upper().split():
  p.word(w)
