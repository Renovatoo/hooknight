import pygame as pg
import random, math
from scripts.particle import Particle
from scripts.spark import Spark

class EntityPhysx: # класс который будет отвечать за фмзику мобов и игрока
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type # справа не type т.к. это может создать конфликт со встроенной функцией.
        self.pos = list(pos) # именно list чтобы у каждой entity сохранялась позиция даже при collision сразу нескольких entity
        self.size = size
        self.velocity = [0, 0] # это будет отображать частоту смены позиции
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        # это изначальные статусы collision чтобы сбрасывать ускорение свободного падения

        self.action = ''
        self.anim_offset = (-3, -3)
        self.flip = False
        self.set_action('idle')

        self.last_movement = [0, 0]


    def rect(self):
        return pg.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
    

    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()


    def update(self, tilemap, movement=(0, 0)):
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])

        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
            
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0: # если движешься вправо
                    entity_rect.right = rect.left 
            # просто сталкиваем позиции игрока и тайла вплотную чтобы сработал collision ниже
                    self.collisions['right'] = True # обновление статуса collision
                if frame_movement[0] < 0: # если движешься влево
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                self.pos[0] = entity_rect.x
        # всё те же фокусы с физикой но по вертикали:
        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True    
                self.pos[1] = entity_rect.y
        
        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True

        self.last_movement = movement

        self.velocity[1] = min(5, self.velocity[1] + 0.1) 
        # min чтобы не было бесконечного ускорения падения, т.е. 5 - это максимальная "скорость" падения
        
        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0
        # просто сбрасываем ускорение свободного падения когда сталкиваемся с землёй или потолком

        self.animation.update()


    def render(self, surf, offset=(0, 0)):                          # false для отключение переворота по Y
        surf.blit(pg.transform.flip(self.animation.img(), self.flip, False), (self.pos[0] - offset[0], self.pos[1] - offset[1]))


class Player(EntityPhysx):
    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos, size)
        self.air_time = 0
        self.jumps = 1
        self.wall_slide = False
        self.striking = 0


    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement=movement)

        self.air_time += 1

        if self.air_time > 170:
            self.game.dead += 1

        if self.collisions['down']:
            self.air_time = 0
            self.jumps = 1

        self.wall_slide = False
        if (self.collisions['right'] or self.collisions['left']) and self.air_time > 4:
            self.wall_slide = True
            self.velocity[1] = min(self.velocity[1], 0.5)
            if self.collisions['right']:
                self.flip = False
            else:
                self.flip = True
            self.set_action('wall_slide')

        if not self.wall_slide:
            if self.air_time > 4:
                self.set_action('jump')
            elif movement[0] != 0:
                self.set_action('run')
            else:
                self.set_action('idle')

        if self.velocity[0] > 0:
            self.velocity[0] = max(self.velocity[0] - 0.1, 0)
        else:
            self.velocity[0] = min(self.velocity[0] + 0.1, 0)

        if self.striking > 0:
            self.striking = max(0, self.striking - 1)
        if self.striking < 0:
            self.striking = min(0, self.striking + 1)
        if abs(self.striking) > 50:
            self.velocity[0] = abs(self.striking) / self.striking * 3.5
            if abs(self.striking) == 51:
                self.velocity[0] *= 0.1 # Резко затормаживаем игрока
                # оставшиеся 51 фрейм нам нужен также для отката атаки
            pvelocity = [abs(self.striking) / self.striking * 0.3, 0]
            self.game.particles.append(Particle(self.game, 'strike', self.rect().center, velocity=pvelocity, frame=4))
    

    def jump(self):
        if self.wall_slide:
            if self.flip and self.last_movement[0] < 0:
                self.velocity[0] = 2.55
                self.velocity[1] = -2.7
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)
            elif not self.flip and self.last_movement[0] > 0:
                self.velocity[0] = -2.55
                self.velocity[1] = -2.7
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)

        elif self.jumps:
            self.velocity[1] = -3.14
            self.jumps -= 1
            self.air_time = 5


    def strike(self):
        if not self.striking:
            if self.flip:
                self.striking = -60
            else:
                self.striking = 60


class Enemy(EntityPhysx):
    def __init__(self, game, pos, size):
        super().__init__(game, 'mage', pos, size)
        self.walking = 0


    def update(self, tilemap, movement=(0, 0)):
        if self.walking:
            if tilemap.solid_check((self.rect().centerx + (-10 if self.flip else 10), self.pos[1] + 23)):
                if (self.collisions['right'] or self.collisions['left']):
                    self.flip = not self.flip
                movement = (movement[0] - 0.5 if self.flip else 0.5, movement[1])
            else:
                self.flip = not self.flip
            self.walking = max(0, self.walking - 1)
            if not self.walking:
                distance = (self.game.player.pos[0] - self.pos[0], self.game.player.pos[1] - self.pos[1])
                if abs(distance[1] < 16):
                    if (self.flip and distance[0] < 0): # еслм игрок слева и он смотрит влево
                        self.game.projectiles.append([[self.rect().centerx - 7, self.rect().centery], -1.7, 0])
                        for i in range(4):
                            self.game.sparks.append(Spark(self.game.projectiles[-1][0], random.random() - 0.5 + math.pi, 2 + random.random()))
                    if (not self.flip and distance[0] > 0): # если игрок справа и он смотрит вправо
                        self.game.projectiles.append([[self.rect().centerx + 7, self.rect().centery], 1.7, 0])
                        for i in range(4):
                            self.game.sparks.append(Spark(self.game.projectiles[-1][0], random.random() - 0.5, 2 + random.random()))

        elif random.random() < 0.01: # Выбираем рандомное время для передвижения
            self.walking = random.randint(30, 120)

        super().update(tilemap, movement=movement)

        if movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')

        if abs(self.game.player.striking) >= 50:
            if self.rect().colliderect(self.game.player.rect()):
                for i in range(20):
                    angle = random.random() * math.pi * 2
                    speed = random.random() * 5
                    self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                    self.game.particles.append(Particle(self.game, 'enemy_kill', self.game.player.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 4)))
                return True

    
    def render(self, surf, offset=(0, 0)):
        super().render(surf, offset=offset)
        if self.flip:
            surf.blit(pg.transform.flip(self.game.assets['wand'], True, False), (self.rect().centerx - 4 - self.game.assets['wand'].get_width() - offset[0], self.rect().centery - 3 - offset[1]))
        else:
            surf.blit(self.game.assets['wand'], (self.rect().centerx + 4 - offset[0], self.rect().centery - 3 - offset[1]))
