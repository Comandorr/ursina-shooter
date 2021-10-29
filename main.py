from ursina import *
from ursina import curve
from ursina.shaders import lit_with_shadows_shader
from ursina.prefabs.first_person_controller import FirstPersonController
from random import*

app = Ursina()


class Gun(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.shooting = Sequence(Func(self.shoot), Wait(.1), loop=True, paused=True)

    def set_camera(self, c):
        self.move = c

    def shoot(self):
        shot.play()
        self.animate('rotation_x', randint(-10, -3))
        invoke(self.animate, 'rotation_x', 0, delay=.1)
        self.blink(color.orange)
        bullet = Entity(parent=self, model='cube', collider='box', scale=.5, color=color.red,
                        position=self.position + (-0.2, 2.5, 0) + self.forward * 10)
        bullets.append(bullet)
        bullet.world_parent = scene


class Player(FirstPersonController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gun = None
        self.body = Entity(collider='box', parent=self, position=self.position + (0, 1.1, 0))

    def drop(self):
        if self.gun:
            self.gun.shooting.pause()
            self.gun.parent = scene
            self.gun.position = self.position + self.forward * 3
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


ground = Entity(model='plane', scale=(100, 1, 100), texture='grass', texture_scale=(10, 10), collider='box')
player = Player()
gun = Gun(model='models/pistol.blend', color=color.black, position=(3, 1, 3), collider='mesh', scale=0.1,
          shader=lit_with_shadows_shader, auto=False)
gun2 = Gun(model='models/m4a1.blend', texture='m4a1', position=(-3, 1, -3), collider='mesh', scale=0.1,
           shader=lit_with_shadows_shader, auto=True)
gun.set_camera((12, 3, 4))
gun2.set_camera((5, 3, 3))

guns = [gun, gun2]
bullets = list()

box1 = Entity(model='cube', collider='box', position=(0, 0, 8), scale=6, rotation=(45, 0, 0), texture='brick',
              texture_scale=(8, 8), shader=lit_with_shadows_shader)
box2 = Entity(model='cube', collider='box', position=(5, 10, 10), scale=6, rotation=(45, 0, 0), texture='brick',
              texture_scale=(8, 8), shader=lit_with_shadows_shader)
hookshot_target = Button(parent=scene, model='cube', color=color.brown, position=(4, 5, 5),
                         shader=lit_with_shadows_shader, collider='box')
hookshot_target.on_click = Func(player.animate_position, hookshot_target.position + (0, 1, 0), duration=.5,
                                curve=curve.linear)
shot = Audio('shot', autoplay=False)
world = [box1, box2, hookshot_target]


def update():
    for g in guns:
        if g.parent == scene:
            g.rotation_y += 1
    if len(bullets) > 0:
        for b in bullets:
            b.position += b.forward * 50
            for w in world:
                if b.intersects(w):
                    bullets.remove(b)
                    w.disable()
                    b.disable()
    if player.body.intersects(gun) and player.gun != gun:
        player.grab(gun)
    if player.body.intersects(gun2) and player.gun != gun2:
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
