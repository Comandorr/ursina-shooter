from ursina import *
from ursina import curve
from ursina.shaders import lit_with_shadows_shader
from ursina.prefabs.first_person_controller import FirstPersonController
from random import*

app = Ursina(vsync=1)
guns = list()
bullets = list()


class Gun(Entity):
    def __init__(self, **kwargs):
        super().__init__(scale=0.1, shader=lit_with_shadows_shader, collider='box', **kwargs)
        self.shooting = Sequence(Func(self.shoot), Wait(.1), loop=True, paused=True)
        guns.append(self)

    def shoot(self):
        shot.play()
        self.animate('rotation_x', randint(-7, -3))
        invoke(self.animate, 'rotation_x', 0, delay=.1)
        self.blink(color.orange)
        bullet = Entity(parent=self, model='cube', collider='box', scale=.5, color=color.red)
        bullet.position += player.gun.forward
        bullet.rotation = player.gun.rotation
        bullet.world_parent = scene
        bullet.animate_position(bullet.position+(bullet.forward*1000), curve=curve.linear, duration=1)
        bullets.append(bullet)


class Player(FirstPersonController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gun = None
        self.body = Entity(collider='None', parent=self, position=self.position + (0, 1.1, 0))

    def drop(self):
        if self.gun:
            self.gun.shooting.pause()
            self.gun.parent = scene
            self.gun.position = self.position + self.forward * 2.5
            self.gun.y = 1
            self.gun.rotation = (0, 0, 0)
            self.gun.collider = 'mesh'

    def grab(self, g):
        self.drop()
        g.rotation = camera.rotation
        g.position = camera.position
        g.position += g.forward*g.move[0] + g.down*g.move[1] + g.right*g.move[2]
        g.parent = camera
        g.collider = None
        self.gun = g
        self.gun.collider = None
        print(player.gun.bounds)


ground = Entity(model='plane', scale=(100, 1, 100), texture='grass', texture_scale=(10, 10), collider='box')
player = Player()
gun = Gun(model='models/pistol.obj', texture='textures/pistol.png', position=(3, 1, 3), auto=False, move=(11, 3, 6))
gun2 = Gun(model='models/m4a1.obj', texture='textures/m4a1.png', position=(-3, 1, -3), auto=True, move=(10, 3, 2))

box1 = Entity(model='cube', collider='box', position=(0, 0, 8), scale=6, rotation=(45, 0, 0), texture='brick',
              texture_scale=(8, 8), shader=lit_with_shadows_shader)
box2 = Entity(model='cube', collider='box', position=(5, 10, 10), scale=6, rotation=(45, 0, 0), texture='brick',
              texture_scale=(8, 8), shader=lit_with_shadows_shader)

enemy1 = Entity(model='models/tank.obj', texture='textures/tank.png', collider='mesh', position=(5, 0, 5))
enemy2 = Entity(model='models/tank.obj', texture='textures/tank.png', collider='mesh', position=(-5, 0, -5))
enemy3 = Entity(model='models/tank.obj', texture='textures/tank.png', collider='mesh', position=(-5, 0, 5))


shot = Audio('shot', autoplay=False)
enemies = [enemy1, enemy2, enemy3]


def update():
    for g in guns:
        if g.parent == scene:
            g.rotation_y += 1
    if len(bullets) > 0:
        for b in bullets:
            for e in enemies:
                if b.intersects(e):
                    bullets.remove(b)
                    e.blink(color.red, duration=.4)
                    enemies.remove(e)
                    invoke(Func(e.disable), delay=.4)
                    b.disable()

    if distance(player, gun) <= 1.3 and player.gun != gun:
        player.grab(gun)
    if distance(player, gun2) <= 1.3 and player.gun != gun2:
        player.grab(gun2)


player.gun = gun
shooting = Sequence(Func(player.gun.shoot), Wait(.1), loop=True, paused=True)
player.gun = None


def input(key):
    if key == 'left mouse down' and not player.gun.auto:
        player.gun.shoot()
        # bullet.animate_position(bullet.position+bullet.forward*5000, curve=curve.linear, duration=1)
    elif key == 'left mouse down' and player.gun.auto:
        player.gun.shooting.start()
    elif key == 'left mouse up' and player.gun.auto:
        player.gun.shooting.pause()


app.run()
