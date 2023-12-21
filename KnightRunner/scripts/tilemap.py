import pygame as pg
import json

NEIGHBOR_OFFSETS = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (0, 0), (-1, 1), (0, 1), (1, 1)]
# Это нужно для проверки collision (проверки 9-ти позиций, вокруг игрока и в самом игроке)
PHYSICS_TILES = {'grass', 'blocks'}
# типы тайлов на которые мы распространим физику.

class Tilemap:
    def __init__(self, game, tile_size=16): # размер тайлов у нас 16 на 16 пикселей
        self.game = game
        self.tile_size = tile_size
        self.tilemap = {}
        self.offgrid_tiles = [] # в отличии от tilemap тут физики не будет, т.е. это tilemap для декора

    def tiles_around(self, pos):
        tiles = []
        # чтобы провека NEIGHBOR_OFFSETS была корректной нужно пиксели перевести в сетку.
        tile_loc = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size)) 
        # именно целочисленное деление чтобы не возникало некорректной конвертации при отрицательных значениях.
        for offset in NEIGHBOR_OFFSETS:
            check_loc = str(tile_loc[0] + offset[0]) + ';' + str(tile_loc[1] + offset[1])
            # сама проверка по двум осям.
            if check_loc in self.tilemap:
                tiles.append(self.tilemap[check_loc])
        return tiles


    def save(self, path):
        f = open(path, 'w')
        json.dump({'tilemap': self.tilemap, 'tile_size': self.tile_size, 'offgrid': self.offgrid_tiles}, f)
        f.close()


    def load(self, path):
        f = open(path, 'r')
        map_data = json.load(f)
        f.close()
        
        self.tilemap = map_data['tilemap']
        self.tile_size = map_data['tile_size']
        self.offgrid_tiles = map_data['offgrid']

    # необходимо для получения данных о локации какого-нить тайла
    def extract(self, id_pairs, keep=False):
        matches = []
        for tile in self.offgrid_tiles.copy(): # именно .copy чтобы мы смогли убрать тайл, когда нам нужно
             if (tile['type'], tile['variant']) in id_pairs:
                  matches.append(tile.copy()) # просто получаем информацию о тайле
                  if not keep:
                       self.offgrid_tiles.remove(tile)
        
        for loc in self.tilemap:
            tile = self.tilemap[loc]
            if (tile['type'], tile['variant']) in id_pairs:
                matches.append(tile.copy())
                matches[-1]['pos'] = matches[-1]['pos'].copy()
                matches[-1]['pos'][0] *= self.tile_size
                matches[-1]['pos'][1] *= self.tile_size
                if not keep:
                     del self.tilemap[loc]

        return matches


    def physics_rects_around(self, pos):
        rects = []
        for tile in self.tiles_around(pos):
            # Далее идет уже проверка на то, что коллизия идёт с "физическим объектом"
            if tile['type'] in PHYSICS_TILES:
                rects.append(pg.Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size, self.tile_size))
        return rects


    def render(self, surf, offset=(0, 0)):
        # сначала задаём offgrid тайлы чтобы на них наложились тайлы на сетке, а не наоборот
        for tile in self.offgrid_tiles:                                # при изменении offset тайлы будут сдвигаться и создавать эффект камеры
            surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] - offset[0], tile['pos'][1] - offset[1]))
            # Тут нету адаптации под размер тайлов т.к. эти тайлы не находятся на сетке (с которой мы взаимодействуем)
            # offset именно с вычитанием т.к. когда мы движемся вправо (положит. вектор), всё на деле смещается влево (т.е. минус позиция)
            
        for x in range(offset[0] // self.tile_size, (offset[0] + surf.get_width()) // self.tile_size + 1):
                    for y in range(offset[1] // self.tile_size, (offset[1] + surf.get_height()) // self.tile_size + 1):
                        loc = str(x) + ';' + str(y)
                        if loc in self.tilemap:
                            tile = self.tilemap[loc]
                            surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] * self.tile_size - offset[0], tile['pos'][1] * self.tile_size - offset[1]))
