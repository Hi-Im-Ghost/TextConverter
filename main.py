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
    img_size = []
    saidText = ""

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

    def set_size(self, size):
        self.img_size = size

    def get_size(self):
        return self.img_size


class MyOptions:
    volume = 1  # 0 - 1
    rate = 150
    blur_strength = 5
    treshold_blocksize = 11
    treshold_constant = 2


global panel
bOptionsOpen = False
core = MyVariables()
options = MyOptions()
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


def opencv_to_tkinter(img):
    gray = cv2.split(img)
    img = cv2.merge(gray)
    im = Image.fromarray(img)
    return im


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


def save_file():
    types = [('Audio file', '*.mp3')]
    file = filedialog.asksaveasfilename(
        filetypes=types, defaultextension=types)

    # Nic nie rób jak okno zamknięte przyciskiem "cancel"
    if (file is None):
        return

    # Aktualizuj ustawienia TTS
    set_property_speach()
    save_text()

    engine.save_to_file(core.saidText, file)
    engine.runAndWait()
    print(file)


# Przycisk zapisywania musi być globalny
butSave = Button(root, font='arial 15 bold',
                 text='SAVE', width='4', command=save_file)

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

    core.set_size(imGotoSize)
    update_preview_image()
    # Przekonwertuj z obrazka na tekst
    save_text()

    # Włącz przycisk do zapisywania
    butSave['state'] = NORMAL


def Reset():
    # Czyści dane obrazka z programu
    core.set_img(None)
    core.saidText = ""
    panel.config(image='')
    butSave['state'] = DISABLED


def Options():
    # Otwiera okno opcji jak nie jest jeszcze otwarte
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

    # Slider głośności
    setup_volume_slider(optionsWindow)

    # Parametry TTS
    Label(optionsWindow, text="Parameters", font="arial 20 bold",
          bg='white smoke').pack(side=TOP, ipadx=5, ipady=5)

    setup_rate_slider(optionsWindow)
    setup_image_parameter_options(optionsWindow)

    # create_preview_image(optionsWindow)
    update_preview_image(True)

    optionsWindow.protocol(
        "WM_DELETE_WINDOW", lambda: option_window_destroy_sequence(optionsWindow))


def setup_volume_slider(window):
    Label(window, text="Volume", font="arial 20 bold",
          bg='white smoke').pack(side=TOP, ipadx=0, ipady=0)

    s = Scale(window, from_=0, to=100, orient=HORIZONTAL,
              command=lambda x: set_volume(s.get() / 100))
    s.set(options.volume * 100)
    s.pack()
    s.update()


def setup_rate_slider(window):
    Label(window, text="Rate", font="arial 12",
          bg='white smoke').pack(side=TOP, ipadx=0, ipady=0)

    s = Scale(window, from_=50, to=300, orient=HORIZONTAL,
              command=lambda x: set_rate(s.get()))
    s.set(options.rate)
    s.pack()
    s.update()


def set_volume(value):
    options.volume = value


def set_rate(value):
    options.rate = value


def setup_image_parameter_options(window):
    Label(window, text="Blur strength", font="arial 12",
          bg='white smoke').pack(side=TOP, ipadx=0, ipady=0)
    e1 = Entry(window, width=3)
    e1.pack()
    e1.insert(0, str(options.blur_strength))

    Label(window, text="Treshold block size", font="arial 12",
          bg='white smoke').pack(side=TOP, ipadx=0, ipady=0)
    e2 = Entry(window, width=3)
    e2.pack()
    e2.insert(0, str(options.treshold_blocksize))

    Label(window, text="Treshold constant", font="arial 12",
          bg='white smoke').pack(side=TOP, ipadx=0, ipady=0)
    e3 = Entry(window, width=3)
    e3.pack()
    e3.insert(0, str(options.treshold_constant))

    b = Button(window, text='Update', command=lambda: update_options(
        int(e1.get()), int(e2.get()), int(e3.get())))
    b.pack()


def update_options(blur, blocksize, constant):
    # blur i blocksize mają być nieparzyste i większe od 3
    if (blocksize < 3):
        blocksize = 3
    if (blur < 3):
        blur = 3
    if (blocksize % 2 == 0):
        blocksize -= 1
    if (blur % 2 == 0):
        blur -= 1

    print(f"Updated: {blur}, {blocksize}, {constant}")

    options.blur_strength = blur
    options.treshold_blocksize = blocksize
    options.treshold_constant = constant
    update_preview_image(True)
    # Regenerate the image
    save_text()


def update_preview_image(converted=False):
    if (core.get_src() == ''):
        return

    if (converted):
        img = convert_image()
        img = opencv_to_tkinter(img)
    else:
        img = Image.open(core.get_src())

    img = img.resize(core.get_size(), Image.Resampling.LANCZOS)
    img = ImageTk.PhotoImage(img)
    panel.config(image=img)
    panel.image = img
    panel.update()


def option_window_destroy_sequence(window):
    global bOptionsOpen
    bOptionsOpen = False
    update_preview_image()
    window.destroy()


def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def remove_noise(image):
    return cv2.medianBlur(image, options.blur_strength)


def thresholding(image):
    return cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                 cv2.THRESH_BINARY, options.treshold_blocksize, options.treshold_constant)


def set_property_speach():
    # Sets speed percent
    # Can be more than 100
    engine.setProperty('rate', options.rate)
    # Set volume 0-1
    engine.setProperty('volume', options.volume)


def convert_image():
    txt = get_grayscale(core.get_img())
    txt = thresholding(txt)
    txt = remove_noise(txt)
    return txt


def save_text():
    txt = convert_image()
    core.saidText = ocr_core(txt)
    print(core.saidText)


def say_text():
    # Ustaw parametry zgodne z opcjami
    set_property_speach()

    # Wypowiedz tekst
    engine.say(core.saidText)
    engine.runAndWait()


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


# initialisation pyttsx3
engine = pyttsx3.init()

set_buttons()
set_property_speach()

root.mainloop()
