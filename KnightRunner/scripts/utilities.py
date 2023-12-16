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


class Animation:
    def __init__(self, images, img_dur=2, loop=True):
        self.images = images
        self.loop = loop
        self.img_duration = img_dur
        self.done = False
        self.frame = 0


    def copy(self):
        return Animation(self.images, self.img_duration, self.loop)


    def update(self):
        if self.loop: 
            self.frame = (self.frame + 1) % (self.img_duration * len(self.images))
        else:
            self.frame = min(self.frame + 1, self.img_duration * len(self.images) - 1)
            if self.frame >= self.img_duration * len(self.images) - 1:
                self.done = True


    def img(self):
        return self.images[int(self.frame / self.img_duration)]


