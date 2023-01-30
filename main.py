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
global textPanel
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
textPanel = Label()

#Funkcja do zwracania przekonwertowanego obrazka
def opencv_to_tkinter(img):
    gray = cv2.split(img)
    img = cv2.merge(gray)
    im = Image.fromarray(img)
    return im

#Funkcja do uruchomienia silnika tesseract i pobrania oraz zwrócenia z wskazego obrazka tekstu
def ocr_core(img):
    # WARUNEKIEM DZIALANIA JEST POSIADANIE PROGRAMU TESSERACT. PONIZEJ TRZEBA PODAC SCIEZKE
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    text = pytesseract.image_to_string(img)
    return text

#Funkcja do uruchomienia okna wyboru obrazka
def open_file():
    # BIERZE SCIEZKE ABSOLUTNA I GDY ZNAJDUJA SIE SPACE TO POWODUJE BLEDY
    src = filedialog.askopenfilename(
        initialdir="Obrazy", title='Select a file')
    core.set_src(src)
    return src

#Funkcja do zapisywania pliku audio czytanego tekstu
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

#Funkcja do ustawienia wybranego obrazka w miejsce etykiety okna glownego aplikacji
def open_img():
    panel.config(image='')
    src = open_file()
    if (src == ''):
        return

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

#Utworzenie okna do konfiguracji
def Options():
    # Otwiera okno opcji jak nie jest jeszcze otwarte
    global bOptionsOpen
    global textPanel
    if (bOptionsOpen):
        return

    bOptionsOpen = True
    # Utwórz okno opcji zależne od główego okna
    optionsWindow = Toplevel(root)

    optionsWindow.geometry("550x450")
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

    # delete
    textPanel = Label(optionsWindow, text="None", font="arial 11")
    textPanel.pack(side=BOTTOM)
    update_preview_text()

    # create_preview_image(optionsWindow)
    update_preview_image(True)

    optionsWindow.protocol(
        "WM_DELETE_WINDOW", lambda: option_window_destroy_sequence(optionsWindow))

#Funkcja do utworzenia slidera dla glosnosci czytania
def setup_volume_slider(window):
    Label(window, text="Volume", font="arial 20 bold",
          bg='white smoke').pack(side=TOP, ipadx=0, ipady=0)

    s = Scale(window, from_=0, to=100, orient=HORIZONTAL,
              command=lambda x: set_volume(s.get() / 100))
    s.set(options.volume * 100)
    s.pack()
    s.update()

#Funkcja do utworzenia slidera dla szybkosci czytania
def setup_rate_slider(window):
    Label(window, text="Rate", font="arial 12",
          bg='white smoke').pack(side=TOP, ipadx=0, ipady=0)

    s = Scale(window, from_=50, to=300, orient=HORIZONTAL,
              command=lambda x: set_rate(s.get()))
    s.set(options.rate)
    s.pack()
    s.update()

#Funkcja do ustawienia glosnosci
def set_volume(value):
    options.volume = value

#Funkcja do ustawienia szybkosci
def set_rate(value):
    options.rate = value

#Funkcja do utworzenia pol konfiguracyjnych dla parametrow progowania oraz rozmycia
def setup_image_parameter_options(window):
    Label(window, text="Blur strength (0, 3+)", font="arial 12",
          bg='white smoke').pack(side=TOP, ipadx=0, ipady=0)
    e1 = Entry(window, width=3)
    e1.pack()
    e1.insert(0, str(options.blur_strength))

    Label(window, text="Treshold block size (3+)", font="arial 12",
          bg='white smoke').pack(side=TOP, ipadx=0, ipady=0)
    e2 = Entry(window, width=3)
    e2.pack()
    e2.insert(0, str(options.treshold_blocksize))

    Label(window, text="Treshold constant", font="arial 12",
          bg='white smoke').pack(side=TOP, ipadx=0, ipady=0)
    e3 = Entry(window, width=3)
    e3.pack()
    e3.insert(0, str(options.treshold_constant))

    b = Button(window, text='Update',
               command=lambda: update_options(e1, e2, e3))
    b.pack()

#Funkcja do aktualizacji parametrow progowania i rozmycia
def update_options(e1, e2, e3):
    blur = int(e1.get())
    blocksize = int(e2.get())
    constant = int(e3.get())

    # blur i blocksize mają być nieparzyste i większe od 3
    if (blocksize < 3):
        blocksize = 3
    if (blur < 3):
        blur = 3
    if (blocksize % 2 == 0):
        blocksize -= 1
    if (blur % 2 == 0):
        blur -= 1

    if (int(e1.get()) == 0):
        blur = 0

    print(f"Updated: {blur}, {blocksize}, {constant}")

    # Wyczyść okna z wartościami
    e1.delete(0, 'end')
    e2.delete(0, 'end')
    e3.delete(0, 'end')

    # Wstaw prawidłowe wartości okien
    e1.insert(0, str(blur))
    e2.insert(0, str(blocksize))
    e3.insert(0, str(constant))

    # Ustaw nowe wartości w opcjach
    options.blur_strength = blur
    options.treshold_blocksize = blocksize
    options.treshold_constant = constant

    if (core.get_src() != ''):
        update_preview_image(True)
        # Wygeneruj TTS ponownie
        save_text()
        update_preview_text()

#Funckja do aktualizacji podgladu obrazka
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

#Funkcja do aktualizacji podgladu tekstu, rozpoznanego z zdjecia przez aplikacje
def update_preview_text():
    global textPanel
    if (core.get_src() != ''):
        textPanel.configure(text=core.saidText)
        textPanel.configure(font="arial 11")
        textPanel.update()

#Funkcja do zamykania okna opcji
def option_window_destroy_sequence(window):
    global bOptionsOpen
    bOptionsOpen = False
    update_preview_image()
    window.destroy()

#Funkcja do zwracania przekonwertowanego do skali szarosci obrazka
def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

#Funkcja do usuwania szumu z obrazu za pomoca medianBlur
def remove_noise(image):
    if (options.blur_strength == 0):
        return image
    return cv2.medianBlur(image, options.blur_strength)

#Funkcja do progowania obrazu
def thresholding(image):
    return cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                 cv2.THRESH_BINARY, options.treshold_blocksize, options.treshold_constant)

#Funkcja do ustawiania parametrow czytania
def set_property_speach():
    # Sets speed percent
    # Can be more than 100
    engine.setProperty('rate', options.rate)
    # Set volume 0-1
    engine.setProperty('volume', options.volume)

#Funkcja do zwracania tekstu po przekonwertowaniu obrazu
def convert_image():
    txt = get_grayscale(core.get_img())
    txt = thresholding(txt)
    txt = remove_noise(txt)
    return txt

#Funkcja do zapisywania tekstu do przeczytania
def save_text():
    txt = convert_image()
    core.saidText = ocr_core(txt)
    print(core.saidText)

#Funkcja do uruchomienia czytania
def say_text():
    # Ustaw parametry zgodne z opcjami
    set_property_speach()

    # Wypowiedz tekst
    engine.say(core.saidText)
    engine.runAndWait()

#Funkcja do ustawienia przyciskow glownego okna
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
