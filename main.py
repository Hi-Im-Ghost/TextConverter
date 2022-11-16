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
bOptionsOpen = False
core = MyVariables()
# Okienko
root = Tk()

root.geometry("550x350")
root.resizable(width=True, height=True)
root.configure(bg='ghost white')
root.title("Text speaker")

Label(root, text="Image", font="arial 20 bold",
      bg='white smoke').pack(side=TOP, ipadx=5, ipady=5)

panel = Label(root, image="")
panel.pack(side=TOP, ipadx=5, ipady=5, expand=True)


def Save():
    return


# Przycisk zapisywania musi być globalny
butSave = Button(root, font='arial 15 bold',
                 text='SAVE', width='4', command=Save)


def ocr_core(img):
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
    text = pytesseract.image_to_string(img)
    return text


def open_file():
    # BIERZE SCIEZKE ABSOLUTNA I GDY ZNAJDUJA SIE SPACE TO POWODUJE BLEDY
    src = filedialog.askopenfilename(
        initialdir="Obrazy", title='Select a file')
    core.set_src(src)
    return src


# UWAGA GDY SCIEZKA DO OBRAZKA MA SPACJE TO NIE DZIALA MOWIENIE
def open_img():
    panel.config(image='')
    src = open_file()

    cv2img = cv2.imread(src)
    core.set_img(cv2img)

    img = Image.open(src)

    # Pobiera wymiary otwieranego obrazu
    imH, imW, Channels = cv2img.shape
    # Bool jest true jak szerokość obrazu jest większa niż jego wysokość
    bIsLandscape = (imW > imH)

    if (bIsLandscape):
        # Jeśli szerokość większa niż wysokość skaluj obrazek do szerokości i zachowaj proporcje przy wysokości
        imResizeRatio = 400 / imW
        imGotoSize = [400, round(imH * imResizeRatio)]
    else:
        # Skaluj do wysokości i zachowaj proporcje przy szerokości
        imResizeRatio = 200 / imH
        imGotoSize = [round(imW * imResizeRatio), 200]

    img = img.resize(imGotoSize, Image.Resampling.LANCZOS)
    img = ImageTk.PhotoImage(img)
    panel.config(image=img)
    panel.image = img
    panel.pack(side=TOP, ipadx=5,
               ipady=5, expand=True)


def Reset():
    core.set_img(None)
    panel.config(image='')
    butSave['state'] = DISABLED


def Options():
    global bOptionsOpen
    if (bOptionsOpen):
        return

    bOptionsOpen = True
    # Utwórz okno opcji zależne od główego okna
    optionsWindow = Toplevel(root)

    optionsWindow.geometry("550x350")
    optionsWindow.resizable(width=True, height=True)
    optionsWindow.configure(bg='ghost white')
    optionsWindow.title("Text speaker options")

    Label(optionsWindow, text="Voice", font="arial 20 bold",
          bg='white smoke').pack(side=TOP, ipadx=5, ipady=5)
    Label(optionsWindow, text="Parameters", font="arial 20 bold",
          bg='white smoke').pack(side=TOP, ipadx=5, ipady=5)

    optionsWindow.protocol(
        "WM_DELETE_WINDOW", lambda: option_window_destroy_sequence(optionsWindow))


def option_window_destroy_sequence(window):
    global bOptionsOpen
    bOptionsOpen = False
    window.destroy()


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

    # Włącz przycisk do zapisywania
    butSave['state'] = NORMAL


def set_buttons():
    # Otwieranie nowego obrazu z dysku
    Button(root, text='Open Image', font='arial 15 bold', width='10', command=open_img).pack(side=LEFT, ipadx=5,
                                                                                             ipady=5, expand=True)
    # Próba odczytania tekstu z obrazka
    Button(root, text="PLAY", font='arial 15 bold', command=say_text, width='10').pack(side=LEFT, ipadx=5,
                                                                                       ipady=5, expand=True)
    # Zapisanie pliku mp3 z odczytywanym tekstem
    butSave.pack(side=LEFT, ipadx=5, ipady=5, expand=True)
    butSave['state'] = DISABLED
    # Wyczyszczenie obrazu z programu
    Button(root, font='arial 15 bold', text='RESET', width='6', command=Reset).pack(side=LEFT, ipadx=5,
                                                                                    ipady=5, expand=True)
    # Otwarcie okna opcji
    Button(root, font='arial 15 bold', text='Options', width='6', command=Options).pack(side=LEFT, ipadx=5,
                                                                                        ipady=5, expand=True)
    # Zakończenie działania programu
    # Button(root, font='arial 15 bold', text='EXIT', width='4', command=Exit, bg='OrangeRed1').pack(side=LEFT, ipadx=5,
    #                                                                                               ipady=5, expand=True)


# initialisation pyttsx3
engine = pyttsx3.init()

set_buttons()
set_property_speach()

root.mainloop()
