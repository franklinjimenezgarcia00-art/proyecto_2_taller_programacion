import asyncio
import pygame as pg
import math, random
import os

async def main():
    screen_size = [320, 180]
    ruta = os.path.dirname(os.path.abspath(__file__))
    
    screen = pg.display.set_mode(screen_size, pg.SCALED)

    clock = pg.time.Clock()
    clock.tick(); pg.time.wait(16)
    road_texture = pg.image.load(os.path.join(ruta, "assets/road.png")).convert()
    fondo1_texture = pg.image.load(os.path.join(ruta, "assets/fondo1.png")).convert()
    nave_sprite = pg.image.load(os.path.join(ruta, "assets/nave.png")).convert()
    asteroide_sprite = pg.image.load(os.path.join(ruta, "assets/asteroide.png")).convert()
    meteoro_sprite = pg.image.load(os.path.join(ruta, "assets/meteoro.png")).convert()


    nave_sprite.set_colorkey((255,0,255))
    asteroide_sprite.set_colorkey((255,0,255))
    meteoro_sprite.set_colorkey((255,0,255))

    nave = Player()
    asteroides = [asteroide(-50), asteroide(200), asteroide(7)]
    meteoros = [meteoro(-67), meteoro(-55), meteoro(-43), meteoro(-33), meteoro(-25), meteoro(-13), meteoro(-3)]

    running = 1
    total_time = 0

    while running: # game loop

        delta = clock.tick()/1000 + 0.00001
        total_time += delta
        nave.controls(delta)

        for event in pg.event.get():
            if event.type == pg.QUIT: running = 0

        screen.blit(fondo1_texture, (-65- nave.angle*82,0))#screen.fill((100,150,250))
        vertical, draw_distance = 180, 1
        nave.z = calc_z(nave.x)
        z_buffer = [999 for element in range(180)]
        while draw_distance < 120:
            last_vertical = vertical
            while vertical >= last_vertical and draw_distance < 120:
                draw_distance += draw_distance/150
                x = nave.x + draw_distance
                scale = 1/draw_distance
                z = calc_z(x) - nave.z
                vertical = int(60+160*scale + z*scale)

            if draw_distance < 120:
                z_buffer[int(vertical)] = draw_distance
                road_slice = road_texture.subsurface((0, 10*x%360,320, 1))
                color = (int(50-draw_distance/3),int(130-draw_distance), int(50-z/20+30*math.sin(x)))
                #pg.draw.rect(screen, color, (0, vertical, 320, 1))
                render_element(screen, road_slice, 500*scale, 1, scale, x,  nave, nave.y, z_buffer)
        
        for index in reversed(range(len(meteoros))):
            scale = max(0.0001, 1/(meteoros[index].x - nave.x))
            render_element(screen, meteoro_sprite, 200*scale, 300*scale, scale, meteoros[index].x, nave, meteoros[index].y+nave.y, z_buffer)
        
        if meteoros[0].x < nave.x+1:
            meteoros.pop(0)
            meteoros.append(meteoro(meteoros[-1].x))

        for index in reversed(range(len(asteroides))):
            scale = max(0.0001, 1/(asteroides[index].x - nave.x))
            render_element(screen, asteroide_sprite, 100*scale, 80*scale, scale, asteroides[index].x, nave, asteroides[index].y+nave.y, z_buffer)
            asteroides[index].x -= 10*delta
        
        if asteroides[0].x < nave.x+1:
            asteroides.pop(0)
            asteroides.append(asteroide(nave.x))

        screen.blit(nave_sprite, (120, 120+math.sin(total_time*nave.velocity)))
        

        if abs(nave.y - calc_y(nave.x+2) -100) > 280 and nave.velocity > 5:
            nave.velocity += -nave.velocity*delta
            nave.acceleration += -nave.acceleration*delta
            pg.draw.circle(screen, (255,0,0), (300, 170), 3)
        pg.display.update()

        await asyncio.sleep(0)

class meteoro():
    def __init__(self, distance):
        self.x = distance +random.randint(10, 20) + 0.5
        self.y = random.randint(500, 1500)*random.choice([-1,1])

def calc_y(x):
    return 200*math.sin(x/17) + 170*math.sin(x/8)

def calc_z(x):
    return 200+80*math.sin(x/13)-120*math.sin(x/7)

def render_element(screen, sprite, width, height, scale, x, nave, y, z_buffer):
    y = calc_y(x) - y
    z = calc_z(x) - nave.z

    vertical = int(60+160*scale + z*scale)
    if vertical >= 1 and vertical < 180 and z_buffer[vertical-1] > 1/scale -10:
        horizontal = 160-(160 - y)*scale +  nave.angle*(vertical-150)

        width = max(1, int(width))
        height = max(1, int(height))

        scaled_sprite = pg.transform.scale(sprite, (width, height))
        screen.blit(scaled_sprite, (horizontal, vertical-height+1))

class asteroide():
    def __init__(self, distance):
        self.x = distance + random.randint(50, 220)

        carriles = [-14, -192, -375]
        self.y = random.choice(carriles)

class Player():
    def __init__(self):
        self.x = 0
        self.y = 300
        self.z = 0
        self.angle = 0
        self.velocity = 0
        self.acceleration = 0

    def controls(self, delta):
        pressed_keys = pg.key.get_pressed()
        self.acceleration += -0.5*self.acceleration *delta
        self.velocity += -0.5*self.velocity*delta

        if pressed_keys[pg.K_w] or pressed_keys[pg.K_UP]:
            if self.velocity > -1:
                self.acceleration  += 4*delta
            else:
                self.acceleration  = 0
                self.velocity += -self.velocity*delta
        elif pressed_keys[pg.K_s] or pressed_keys[pg.K_DOWN]:
            if self.velocity < 1:
                self.acceleration  -= delta
            else:
                self.acceleration  = 0
                self.velocity += -self.velocity*delta
        if pressed_keys[pg.K_a] or pressed_keys[pg.K_LEFT]:
            self.angle -= delta*self.velocity/10
        elif pressed_keys[pg.K_d] or pressed_keys[pg.K_RIGHT]:
            self.angle += delta*self.velocity/10
        self.velocity = max(-10,min(self.velocity, 20))
        self.angle = max(-0.8,(min(0.8, self.angle)))
        self.velocity += self.acceleration *delta
        self.x += self.velocity*delta*math.cos(self.angle)
        self.y += self.velocity*math.sin(self.angle)*delta*100

if __name__ == "__main__":
    pg.init()
    asyncio.run(main())
    pg.quit()