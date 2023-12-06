import os
import pygame as pg

BASE_IMG_PATH = 'assets/images/'


def load_image(path): # функция нужна чтобы ускорить ввод пути спрайтов
    img = pg.image.load(BASE_IMG_PATH + path).convert() # convert чтобы рендеринг был эффективнее
    img.set_colorkey((0, 0, 0))
    return img


def load_images(path): # эта функция нужна чтобы загружать сразу несколько спрайтов
    images = []
    for img_name in os.listdir(BASE_IMG_PATH + path):
        images.append(load_image(path + '/' + img_name))
    return images
