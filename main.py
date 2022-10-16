import cv2
import numpy as np
from PIL import Image
import pytesseract
# Google online only speach
#from gtts import gTTS

# Offline speachs
import pyttsx3

# This module is imported so that we can
# play the converted audio
import os


def ocr_core(img):
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    text = pytesseract.image_to_string(img)
    return text


img = cv2.imread('img.png')


def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def remove_noise(image):
    return cv2.medianBlur(image, 5)


def thresholding(image):
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]


img = get_grayscale(img)
img = thresholding(img)
img = remove_noise(img)

mytext = ocr_core(img)
print(mytext)

#myobj = gTTS(text=mytext, lang='pl', slow=False)

#myobj.save("test.mp3")

#os.system("test.mp3") #or os.system("start test.mp3")

# initialisation pyttsx3
engine = pyttsx3.init()

# Sets speed percent
# Can be more than 100
#engine.setProperty('rate', 150)
# Set volume 0-1
#engine.setProperty('volume', 0.7)
# Use another voice
#engine.setProperty('voice', voice_id)
#engine.save_to_file(mytext, "test.mp3")

# testing pyttsx3
engine.say(mytext)
engine.runAndWait()


