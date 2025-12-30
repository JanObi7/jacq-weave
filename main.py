import numpy as np
import cv2 as cv

###################################################################################################
# Klasse zum verwalten des Web Musters
class Program:
  # constructor, read program from file
  def __init__(self):
    image = cv.imread("program.png", flags=cv.IMREAD_UNCHANGED)
    self.program = cv.cvtColor(image, cv.COLOR_BGRA2RGBA)
    self.ns, self.nk, _ = self.program.shape

  # Funktion zum Auslesen des Programms
  def getColor(self, k, s):
    # wenn k oder s außerhalb, dann mit Modulo nach innerhalb verschieben
    return self.program[s % self.ns][k % self.nk]

###################################################################################################
# Klasse für die Fadenkonfiguration
class Config:
  # Farben festlegen
  color_k = (150, 77, 0, 255) # RGBA Kettenfarbe
  color_s = (100, 30, 0, 255) # RGBA Schussfarbe
  color_g = (255, 255, 255, 255) # RGBA Glanzpunkt

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
    x_max = kmax * ppk
    y_max = smax * pps
    diffuse = np.zeros((y_max, x_max, 4), np.uint8)
    diffuse[:,:] = (0,0,0,255)

    # Abrastern des Program
    for s in range(smax):
      for k in range(kmax):
        # lese das Programm aus (Umwandlung in Python tuple)
        color = tuple(self.program.getColor(k, s).tolist())

        # Farbe bestimmen in Zieltextur setzen
        if color == (255, 0, 0, 255):
          # Kette oben
          # erst den Schuss, ...
          diffuse[s*pps+os:s*pps+os+self.config.width_s, k*ppk:k*ppk+ppk] = self.config.color_s
          # ... dann die Kette drüber zeichnen
          diffuse[s*pps:s*pps+pps, k*ppk+ok:k*ppk+ok+self.config.width_k] = self.config.color_k
          
          # Glanzpunkte setzen
          if tuple(self.program.getColor(k, s-1).tolist()) != (255, 0, 0, 255):
            of2 = 5
          else:
            of2 = 0
          if tuple(self.program.getColor(k, s+1).tolist()) != (255, 0, 0, 255):
            of3 = 5
          else:
            of3 = 0
          
          diffuse[s*pps+of2:s*pps+pps-of3, k*ppk+ok+2:k*ppk+ok+4] = self.config.color_g
        else:
          # Schuss oben
          # erst die Kette, ...
          diffuse[s*pps:s*pps+pps, k*ppk+ok:k*ppk+ok+self.config.width_k] = self.config.color_k
          # ... dann den Schuss drüber zeichnen
          diffuse[s*pps+os:s*pps+os+self.config.width_s, k*ppk:k*ppk+ppk] = self.config.color_s
          # Glanzpunkte
          diffuse[s*pps+os+2:s*pps+os+4, k*ppk:k*ppk+ppk] = self.config.color_g

        # setze Farbe in Zieltextur (Bereich ppk Pixel breit und pps Pixel hoch)

    # save diffuse color texture
    image = cv.cvtColor(diffuse, cv.COLOR_RGBA2BGRA)
    cv.imwrite("diffuse.png", image)

###################################################################################################
# Web Muster und Fadenkonfiguration erstellen
program = Program()
config = Config()

# Webstuhl initialisieren
loom = Loom(config, program)

# Stoff weben
loom.render(0, 400, 0, 120)
