import numpy as np
import cv2 as cv

###################################################################################################
# Klasse zum verwalten des Web Musters (Programms)
class Program:
  # constructor, read program from file
  def __init__(self):
    image = cv.imread("program.png", flags=cv.IMREAD_UNCHANGED)
    self.program = cv.cvtColor(image, cv.COLOR_BGRA2RGBA)
    self.ns, self.nk, _ = self.program.shape

  # Funktion zum Auslesen des Programms
  def getColor(self, k, s):
    # wenn k oder s außerhalb, dann mit Modulo nach innerhalb verschieben
    color = self.program[s % self.ns][k % self.nk]
    return tuple(color.tolist())

###################################################################################################
# Klasse für die Fadenkonfiguration
class Config:
  # Farben festlegen
  # color_k = (150, 77, 0, 255) # RGBA Kettenfarbe
  color_k = (100, 30, 0, 255) # RGBA Schussfarbe
  color_s = (255, 0, 0, 255) # RGBA Kettenfarbe
  color_g = (255, 150, 150, 255) # RGBA Glanzpunkt

  # Fadenbreiten in Pixeln
  width_k = 5
  width_s = 5

###################################################################################################
# Klasse für den Webstuhl
class Loom:
  # Constructor mit Fadenkonfig und Muster
  def __init__(self, config, program):
    self.config = config
    self.program = program

  # Funktion zum virtuellen Weben
  def render(self, kmin, kmax, smin, smax):
    # TODO: hier noch fest vorgegeben, Pixel pro Kette/Schuss
    ppk = 6
    pps = 20

    # offesets bestimmen
    ok = int((ppk-self.config.width_k)/2)
    os = int((pps-self.config.width_s)/2)

    # create diffuse color texture with black background
    x_max = (kmax-kmin) * ppk
    y_max = (smax-smin) * pps
    diffuse = np.zeros((y_max, x_max, 4), np.uint8)
    diffuse[:,:] = (0,0,0,255)

    displacemnt = np.zeros((y_max, x_max, 4), np.uint8)
    displacemnt[:,:] = (0,0,0,255)

    # Abrastern des Program
    for s in range(smin, smax):
      for k in range(kmin, kmax):
        # lese das Programm aus (Umwandlung in Python tuple)
        color = self.program.getColor(k, s)

        # Farbe bestimmen in Zieltextur setzen
        if color == (255, 0, 0, 255):
          # Kette oben
          # erst den Schuss, ...
          #          ymin                  ymax                 xmin       xmax
          diffuse[    s*pps+os  :  s*pps+os+self.config.width_s  , k*ppk    :  k*ppk+ppk] = self.config.color_s
          displacemnt[s*pps+os  :  s*pps+os+self.config.width_s  , k*ppk    :  k*ppk+ppk] = (100, 100, 100, 255)        
          
          # ... dann die Kette drüber zeichnen
          diffuse[    s*pps     :  s*pps+pps                     , k*ppk+ok :  k*ppk+ok+self.config.width_k] = self.config.color_k
          displacemnt[s*pps     :  s*pps+pps                     , k*ppk+ok :  k*ppk+ok+self.config.width_k] = (255, 255, 255, 255)
          
          # Glanzpunkte setzen
          if self.program.getColor(k, s-1) != (255, 0, 0, 255):
            of2 = 5
          else:
            of2 = 0
          if self.program.getColor(k, s+1) != (255, 0, 0, 255):
            of3 = 5
          else:
            of3 = 0
          
          diffuse[s*pps+of2:s*pps+pps-of3, k*ppk+ok+2:k*ppk+ok+4] = self.config.color_g
        else:
          # Schuss oben
          # erst die Kette, ...
          diffuse[s*pps:s*pps+pps, k*ppk+ok:k*ppk+ok+self.config.width_k] = self.config.color_k
          displacemnt[s*pps:s*pps+pps, k*ppk+ok:k*ppk+ok+self.config.width_k] = (100, 100, 100, 255)
          
          # ... dann den Schuss drüber zeichnen
          diffuse[s*pps+os:s*pps+os+self.config.width_s, k*ppk:k*ppk+ppk] = self.config.color_s
          displacemnt[s*pps+os:s*pps+os+self.config.width_s, k*ppk:k*ppk+ppk] = (255, 255, 255, 255)
          
          # Glanzpunkte
          diffuse[s*pps+os+2:s*pps+os+4, k*ppk:k*ppk+ppk] = self.config.color_g

    # save diffuse color texture
    cv.imwrite("out/diffuse.png", cv.cvtColor(diffuse, cv.COLOR_RGBA2BGRA))
    cv.imwrite("out/displacement.png", cv.cvtColor(displacemnt, cv.COLOR_RGBA2BGRA))

###################################################################################################
# Web Muster und Fadenkonfiguration erstellen
program = Program()
config = Config()

# Webstuhl initialisieren
loom = Loom(config, program)

# Stoff weben
# loom.render(0, 400, 0, 120)

loom.render(0, 10, 0, 10)