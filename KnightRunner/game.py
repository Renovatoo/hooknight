import pygame as pg
import sys
from scripts.entities import EntityPhysx, Player
from scripts.utilities import load_image, load_images, Animation
from scripts.tilemap import Tilemap

class Game: 
    def __init__(self): # метод-конструктор, где мы выполняем инициализационные шаги, базовые функции
        # self в скобочках будет ссылаться на объект, который будет создаваться на основе вышеуказанного класса.
        pg.init() # инициализация всех модулей pygame
        pg.display.set_caption('KnightRunner: Pixel Dash') 
        icon = pg.image.load('assets/gameicon.png')
        pg.display.set_icon(icon)
        # дали имя и иконку окну игры

        self.display = pg.Surface((320, 240)) 
        # просто добавляем пространство (по размеру в 2 раза меньше) чтобы потом всю картину в 2 раза увеличить

        self.screen = pg.display.set_mode((640, 480))
        self.clock = pg.time.Clock() 
        # создаём фиксированную частоту кадров чтобы игровые тики были равномерны и не перегружали процессор

        self.assets = { # создаём shortcuts для разных типов тайлов
            'player': load_image('entities/player/player.png'),
            'enemies': load_images('entities/enemies'),
            'grass': load_images('grass'),
            'blocks': load_images('blocks'),
            'tree': load_images('tree'),
            'misc': load_images('misc'),
            'background': load_image('background.png'),
            'player/idle': Animation(load_images('entities/player/idle'), img_dur=45),
            'player/run': Animation(load_images('entities/player/run'), img_dur=7),
            'player/jump': Animation(load_images('entities/player/jump')),
            'player/wall_slide': Animation(load_images('entities/player/wall_slide'), img_dur=12),
            'player/strike': Animation(load_images('entities/player/strike'), img_dur=3)
        } # в папке из load images должны быть только png с int-именами.

        self.movement = [False, False]
        self.player = Player(self, (50, 50), (15, 15))
        self.tilemap = Tilemap(self, tile_size=16)
        self.tilemap.load('level1.json')
        self.scroll = [0, 0] # scroll будет относительно экрана, т.е. это реализует камеру


    def run(self):
        while True: # бесконечный цикл чтобы игра не закрывалась
            self.display.blit(self.assets['background'], (0, 0))

            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 20
            # сдвиг камеры по X = текущая позиция игрока - "позиция" дисплея (делённая на два иначе камера улетит) - где мы уже находимя
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 20
            render_scroll = (int(self.scroll[0]), int(self.scroll[1])) # избавление от дергания камеры

            self.tilemap.render(self.display, offset=render_scroll)
            self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0)) # изменения по X и Y осям
            self.player.render(self.display, offset=render_scroll) 
            # добавили параметры сдвига (offset) чтобы использовать это для камеры, обновлять видимые тайлы

            for event in pg.event.get(): 
                if event.type == pg.QUIT:
                    pg.quit() # просто закроет pygame
                    sys.exit() # а это уже полностью выйдет из приложения

                # меняем статусы вертикального перемещения:
                if event.type == pg.KEYDOWN: # Если какая-нить клавиша нажата
                    if event.key == pg.K_LEFT:
                        self.movement[0] = True
                    if event.key == pg.K_RIGHT:
                        self.movement[1] = True
                    if event.key == pg.K_UP:  
                        self.player.jump()
                        # сделали стартовую точку ускорению чтобы прыжок был плавным.
                    if event.key == pg.K_SPACE:
                        self.player.strike()
                if event.type == pg.KEYUP: # Если какая-нить клавиша опущена
                    if event.key == pg.K_LEFT:
                        self.movement[0] = False
                    if event.key == pg.K_RIGHT:
                        self.movement[1] = False
            
            self.screen.blit(pg.transform.scale(self.display, self.screen.get_size()), (0, 0)) 
            # Делаем так чтобы маленькая область растянулась на весь экран и от этого текстурки стали больше.
            pg.display.update() # обновляем экран чтобы видеть изменения
            self.clock.tick(70)


Game().run()




 


