import cv2
import numpy

from tkinter import *
from tkinter import filedialog

import pytesseract
import pyttsx3
# This module is imported so that we can
# play the converted audio
import os

from PIL import ImageTk, Image


class MyVariables:
    src = ""
    img = None

    def __init__(self, src="", img=None):
        self._img = img
        self._src = src

    def set_img(self, img):
        self._img = img

    def get_img(self):
        return self._img

    def get_src(self):
        return self._src

    def set_src(self, src):
        self._src = src


global panel
core = MyVariables()
# Okienko
root = Tk()

root.geometry("550x350")
root.resizable(width=True, height=True)
root.configure(bg='ghost white')
root.title("Text speaker")

Label(root, text="Image", font="arial 20 bold", bg='white smoke').pack(side=TOP, ipadx=5, ipady=5)

panel = Label(root, image="")
panel.pack(side=TOP, ipadx=5, ipady=5, expand=True)


def ocr_core(img):
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    text = pytesseract.image_to_string(img)
    return text


def open_file():
    src = filedialog.askopenfilename(initialdir="Obrazy", title='Select a file') #BIERZE SCIEZKE ABSOLUTNA I GDY ZNAJDUJA SIE SPACE TO POWODUJE BLEDY
    core.set_src(src)
    return src


# UWAGA GDY SCIEZKA DO OBRAZKA MA SPACJE TO NIE DZIALA MOWIENIE
def open_img():
    panel.config(image='')
    src = open_file()

    cv2img = cv2.imread(src)
    core.set_img(cv2img)

    img = Image.open(src)

    img = img.resize((200, 200), Image.Resampling.LANCZOS)
    img = ImageTk.PhotoImage(img)
    panel.config(image=img)
    panel.image = img
    panel.pack(side=TOP, ipadx=5,
               ipady=5, expand=True)


def Exit():
    root.destroy()


def Reset():
    core.set_img(None)
    panel.config(image='')


def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def remove_noise(image):
    return cv2.medianBlur(image, 5)


def thresholding(image):
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]


def set_property_speach():
    # Sets speed percent
    # Can be more than 100
    engine.setProperty('rate', 150)
    # Set volume 0-1s
    engine.setProperty('volume', 0.7)
    # Use another voice
    # engine.setProperty('voice', voice_id)
    # engine.save_to_file(mytext, "test.mp3")


def say_text():
    txt = get_grayscale(core.get_img())
    # cv2.imshow('gray', txt)
    txt = thresholding(txt)
    # cv2.imshow('thresh', txt)
    txt = remove_noise(txt)
    # Jak nie czyta jakiegos obrazka to trzeba pobawic sie tym przetwarzaniem, np dla test 5 po remove noise nie przeczyta bo usuwa po prostu kontury liter
    # cv2.imshow('noise', txt)
    # cv2.waitKey(0)
    txt = ocr_core(txt)
    print(txt)
    engine.say(txt)
    engine.runAndWait()


def set_button():
    Button(root, text='Open Image', font='arial 15 bold', width='10', command=open_img).pack(side=LEFT, ipadx=5,
                                                                                             ipady=5, expand=True)
    Button(root, text="PLAY", font='arial 15 bold', command=say_text, width='10').pack(side=LEFT, ipadx=5,
                                                                                       ipady=5, expand=True)
    Button(root, font='arial 15 bold', text='RESET', width='6', command=Reset).pack(side=LEFT, ipadx=5,
                                                                                    ipady=5, expand=True)
    Button(root, font='arial 15 bold', text='EXIT', width='4', command=Exit, bg='OrangeRed1').pack(side=LEFT, ipadx=5,
                                                                                                   ipady=5, expand=True)


# initialisation pyttsx3
engine = pyttsx3.init()

set_button()
set_property_speach()

root.mainloop()
