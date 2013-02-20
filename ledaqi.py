import serial
import time
import urllib
from bs4 import BeautifulSoup
import Image
import base64
import tempfile

class blinkyBoard:
  def init(self, port, baud):
    self.serial = serial.Serial(port, baud)
    self.rgamma = 2.0
    self.ggamma = 2.0
    self.bgamma = 4.0

  def sendPixel(self,g,r,b):
    data = bytearray()
    
    r = self.gamma(r, self.rgamma)
    g = self.gamma(g, self.ggamma)
    b = self.gamma(b, self.bgamma)
    
    data.append(0x80 | (r>>1))
    data.append(0x80 | (g>>1))
    data.append(0x80 | (b>>1))
    self.serial.write(data)
    self.serial.flush()
    
  def gamma(self, input, tweak):
    return int(pow(input/256.0, tweak) * 256)

  def sendBreak(self):
    data = bytearray()
    for i in range(0,8):
      data.append(0x00)
    self.serial.write(data)
    self.serial.flush()

blink = blinkyBoard()
blink.init('/dev/cu.usbmodemfa131', 57600)

url = "http://www.aqicn.info/?city=Shenzhen"
#url = "http://www.aqicn.info/?city=Beijing"
#url = "http://www.aqicn.info/?city=Shanghai"
#url = "http://www.aqicn.info/"

positions = [243, 238, 233, 228, 223, 218, 213, 208, 203, 198, 193, 188, 183, 178, 173, 168, 163, 158, 153, 148, 143, 138, 133, 128, 123, 118, 113]

for i in range(0, 30):
  blink.sendPixel(0,0,0);
blink.sendBreak()

while True:
  print "Scraping %s" % url
  soup = BeautifulSoup(urllib.urlopen(url), "html5lib")
  imgs = soup.find_all(id="img_pm25")
  #print imgs
  if len(imgs):
    imgurl = imgs[0]['src']
  
    #print "Parsing image"
    imgdata = base64.b64decode(imgurl[22:])
    tmp = open("data.png", "w")
    tmp.write(imgdata)
    tmp.close()
    img = Image.open("data.png")
    img = img.convert('RGB')

    #print "Points"
    for x in positions:
      r, g, b = img.getpixel((x, 24))
      #print r, g, b
      blink.sendPixel(r, g, b);
    blink.sendBreak()
    time.sleep(60*30)
  else:
    print "Site down."
    time.sleep(60)

  pass
  