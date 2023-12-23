import pygame as pg
import sys, math, random
from scripts.entities import EntityPhysx, Player, Enemy
from scripts.utilities import load_image, load_images, Animation
from scripts.tilemap import Tilemap
from scripts.spark import Spark
from scripts.particle import Particle

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
            'grass': load_images('tiles/grass'),
            'blocks': load_images('tiles/blocks'),
            'tree': load_images('tiles/tree'),
            'misc': load_images('tiles/misc'),
            'background': load_image('background.png'),
            'player/idle': Animation(load_images('entities/player/idle'), img_dur=45),
            'player/run': Animation(load_images('entities/player/run'), img_dur=7),
            'player/jump': Animation(load_images('entities/player/jump')),
            'player/wall_slide': Animation(load_images('entities/player/wall_slide'), img_dur=12),
            'mage/idle': Animation(load_images('entities/enemies/mage/idle'), img_dur=45),
            'mage/run': Animation(load_images('entities/enemies/mage/run'), img_dur=7),
            'particle/strike': Animation(load_images('particles/strike'), img_dur=8, loop=False),
            'particle/particle': Animation(load_images('particles/particle'), img_dur=6, loop=False),
            'particle/enemy_kill': Animation(load_images('particles/enemy_kill'), img_dur=4, loop=False),
            'wand': load_image('wand.png'),
            'projectile': load_image('projectile.png')
        } # в папке из load images должны быть только png с int-именами.

        self.movement = [False, False]
        self.player = Player(self, (50, 50), (16, 16))
        self.tilemap = Tilemap(self, tile_size=16)
        self.load_level(0)


    def load_level(self, map_id):
        self.tilemap.load('assets/maps/' + str(map_id) + '.json')

        self.particles = []
        self.projectiles = []
        self.enemies = []
        self.sparks = []
        self.scroll = [0, 0] # scroll будет относительно экрана, т.е. это реализует камеру
        self.dead = 0

        for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1)]):
            if spawner['variant'] == 0:
                self.player.pos = spawner['pos']
                self.player.air_time = 0
            else:
                self.enemies.append(Enemy(self, spawner['pos'], (16, 16)))

        
    def run(self):
        while True: # бесконечный цикл чтобы игра не закрывалась
            self.display.blit(self.assets['background'], (0, 0))

            if self.dead:
                self.dead += 1 # Это запускает таймер со смерти игрока - 40 кадров
                if self.dead > 60:
                    self.load_level(0)

            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 20
            # сдвиг камеры по X = текущая позиция игрока - "позиция" дисплея (делённая на два иначе камера улетит) - где мы уже находимя
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 20
            render_scroll = (int(self.scroll[0]), int(self.scroll[1])) # избавление от дергания камеры

            self.tilemap.render(self.display, offset=render_scroll)

            if not self.dead:
                self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0)) # изменения по X и Y осям
                self.player.render(self.display, offset=render_scroll) 
            # добавили параметры сдвига (offset) чтобы использовать это для камеры, обновлять видимые тайлы

# вид списка: [[x,y], направление, время полёта]
            for projectile in self.projectiles.copy():
                projectile[0][0] += projectile[1]
                projectile[2] += 1
                img = self.assets['projectile']
                self.display.blit(img, (projectile[0][0] - img.get_width() / 2 - render_scroll[0], projectile[0][1] - img.get_height() / 2 - render_scroll[1]))
                if self.tilemap.solid_check(projectile[0]):
                    self.projectiles.remove(projectile)
                    for i in range(4):
                         self.sparks.append(Spark(projectile[0], random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0), 2 + random.random()))
                elif projectile[2] > 420:
                    self.projectiles.remove(projectile)
                elif abs(self.player.striking) < 50:
                    if self.player.rect().collidepoint(projectile[0]):
                        self.projectiles.remove(projectile)
                        self.dead += 1
                        for i in range(20):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.sparks.append(Spark(self.player.rect().center, angle, 2 + random.random()))
                            self.particles.append(Particle(self, 'particle', self.player.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))

            for spark in self.sparks.copy():
                kill = spark.update()
                spark.render(self.display, offset=render_scroll)
                if kill:
                    self.sparks.remove(spark)

            for enemy in self.enemies.copy():
                kill = enemy.update(self.tilemap, (0, 0))
                enemy.render(self.display, offset=render_scroll)
                if kill:
                    self.enemies.remove(enemy)

            for particle in self.particles.copy():
                kill = particle.update()
                particle.render(self.display, offset=render_scroll)
                if kill:
                    self.particles.remove(particle)

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




 


