import pygame as pg

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
        self.flip = False
        self.set_action('idle')


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
        # Дальше происходит магия...    
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


    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement=movement)

        self.air_time += 1
        if self.collisions['down']:
            self.air_time = 0

        if self.air_time > 4:
            self.set_action('jump')
        elif movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')

