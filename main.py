from tkinter import *
import random

direction = None


class Player:

    def __init__(self):
        self.x = 50
        self.life = 3

        self.ship = Gcanv.create_image(50, 550, image=ship_sprite, tag="player_hurtbox")

    def player_collide(self, xt, yt):
        xr = range(self.x - 30, self.x + 32)
        yr = range(550, 585)
        if xt in xr and yt in yr:
            return True
        return False


class Enemy_group:

    def __init__(self):

        self.enemy_list = []
        self.enemy_coord_list = []
        self.armada_dir = 'right'
        y = 0
        for i in range(32):
            if i > 1 and (i % 8 == 0):
                y += 1
            enemy = Gcanv.create_image(50 + ((i % 8) * 100), 100 + (y * 70), image=enemy_sprite, tag="enemy_hurtbox")
            self.enemy_list.append(enemy)
            xs = 30 + ((i % 8) * 100)
            ys = 100 + (y * 70)
            self.enemy_coord_list.append([xs, ys, 52 + xs, 39 + ys])

    def enemy_collide(self, xt, yt):
        cn = 0
        for x1, y1, x2, y2 in self.enemy_coord_list:
            xr = range(x1, x2)
            yr = range(y1, y2)
            if xt in xr and yt in yr:
                return cn
            cn += 1
        return None

    def enemy_fire(self, Bullet, ind):
        xb, yb, _, _ = self.enemy_coord_list[ind]
        if len(Bullet.enem_projectile_list) <= 5:
            Bullet.enem_projectile_list.insert(0, [xb + 20, yb + 30])
            proj = Gcanv.create_image(xb + 20, yb + 30, image=pellet, tag="enemy_bullet")
            Bullet.enem_projectile_shape_list.insert(0, proj)

    def armada_sway(self, spd):
        spd = int(spd)
        for i, _, j, _ in self.enemy_coord_list:
            if j + spd >= 950:
                self.armada_dir = 'left'
            elif i - spd <= 50:
                self.armada_dir = 'right'

        if self.armada_dir == 'left':
            armads_dir = lambda data: (data[0] - spd, data[1], data[2] - spd, data[3])
        else:
            armads_dir = lambda data: (data[0] + spd, data[1], data[2] + spd, data[3])
        self.enemy_coord_list = list(map(armads_dir, self.enemy_coord_list))
        return


class Bullet:

    def __init__(self):
        self.projectile_list = []
        self.projectile_shape_list = []
        self.enem_projectile_list = []
        self.enem_projectile_shape_list = []


# spawns a bullet from ship

def shoot(Player, Bullet):
    if len(Bullet.projectile_list) <= 1:
        Bullet.projectile_list.insert(0, [Player.x, 520])
        proj = Gcanv.create_image(Player.x, 520, image=pellet, tag="bullet")
        Bullet.projectile_shape_list.insert(0, proj)


def on_keypress(event):
    global direction

    if event.keysym == "Right" or event.keysym == "d":
        direction = "right"
    elif event.keysym == "Left" or event.keysym == "a":
        direction = "left"


def on_keyrelease(event):
    global direction
    direction = None


def game_over(WoL):
    global rof, life, score
    life = 3
    rof = 100
    Sc.config(text="Score:{}                Life:{}" \
              .format(score, "O"))
    window.bind("<s>", lambda e: boundary_of_life_and_death())
    if WoL:
        col = "green"
        gametext = "YOU WIN!!!!"
    else:
        col = "red"
        gametext = "YOU LOST..."
        score = 0
    Gcanv.delete(ALL)
    Gcanv.create_text(Gcanv.winfo_width() / 2, Gcanv.winfo_height() / 2 - 100,
                      font=('consolas', 70), text="GAME OVER\n {}".format(gametext), fill=col, tag="gameover")
    Gcanv.create_text(Gcanv.winfo_width() / 2, Gcanv.winfo_height() / 2 + 100,
                      font=('consolas', 70), text="Press S to retry", fill=col)


def nextmove(Player, Bullet, Enemy_group):
    global direction
    global score, rof, life
    Gcanv.delete(Player.ship)
    del Player.ship

    if not (len(Enemy_group.enemy_coord_list)):
        game_over(True)
        return

    rof -= 1
    if rof <= 0:
        enemy_fire = random.randrange(len(Enemy_group.enemy_list))
        Enemy_group.enemy_fire(Bullet, enemy_fire)
        sc_dif = score * 5
        rof = 100 - sc_dif

    projectile_up = lambda data: (data[0], data[1] - 7)  # set projectile speed
    projectile_down = lambda data: (data[0], data[1] + 3)
    Bullet.projectile_list = list(map(projectile_up, Bullet.projectile_list))
    Bullet.enem_projectile_list = list(map(projectile_down, Bullet.enem_projectile_list))

    sc_panic = 1
    if score >= 27:
        sc_panic = 10
    elif score >= 24:
        sc_panic = 5
    elif score >= 16:
        sc_panic = 3
    elif score >= 8:
        sc_panic = 2
    Enemy_group.armada_sway(sc_panic)

    for i in Enemy_group.enemy_list:  # the for loops for bullet animation
        Gcanv.delete(i)
    Enemy_group.enemy_list = []

    for xe, ye, _, _ in Enemy_group.enemy_coord_list:
        new_enemy = Gcanv.create_image(xe + 30, ye, image=enemy_sprite, tag="enemy_hurtbox")
        Enemy_group.enemy_list.append(new_enemy)

    for i in Bullet.projectile_shape_list:  # the for loops for bullet animation
        Gcanv.delete(i)
    Bullet.projectile_shape_list = []

    i = 0
    for x, y in Bullet.projectile_list:
        proj = Gcanv.create_image(x, y, image=pellet, tag="bullet")
        Bullet.projectile_shape_list.insert(0, proj)
        check_hit = Enemy_group.enemy_collide(x, y)
        if check_hit != None:
            del Bullet.projectile_list[i]
            del Enemy_group.enemy_coord_list[check_hit]
            Gcanv.delete(Enemy_group.enemy_list[check_hit])
            del Enemy_group.enemy_list[check_hit]
            score += 1
            Sc.config(text="Score:{}                Life:{}" \
                      .format(score, life))
        if y <= 0:
            del Bullet.projectile_list[i]
        i += 1

    for j in Bullet.enem_projectile_shape_list:  # the for loops for bullet animation
        Gcanv.delete(j)
    Bullet.enem_projectile_shape_list = []

    j = 0
    for a, b in Bullet.enem_projectile_list:
        proj = Gcanv.create_image(a, b, image=pellet, tag="enemy_bullet")
        Bullet.enem_projectile_shape_list.insert(0, proj)
        check_hit_player = Player.player_collide(a, b)
        if check_hit_player == True:
            del Bullet.enem_projectile_list[j]
            life -= 1
            Sc.config(text="Score:{}                Life:{}" \
                      .format(score, life))

        if b >= 600:
            del Bullet.enem_projectile_list[j]
        j += 1

    if direction == "left" and not (Player.x <= 50):
        Player.x -= 10
    if direction == "right" and not (Player.x >= 950):
        Player.x += 10
    Player.ship = Gcanv.create_image(Player.x, 550, image=ship_sprite, tag="player_hurtbox")

    if life < 0:
        game_over(False)
    else:
        window.after(10, nextmove, Player, Bullet, Enemy_group)


def boundary_of_life_and_death():
    Gcanv.delete(ALL)
    window.unbind("<s>")
    Sc.config(text="Score:{}                Life:{}" \
              .format(score, life))

    p1 = Player()
    bullet_data = Bullet()
    enemy_group = Enemy_group()
    nextmove(p1, bullet_data, enemy_group)

    window.bind_all('<KeyPress>', on_keypress)
    window.bind_all('<KeyRelease>', on_keyrelease)
    window.bind("<space>", lambda e: shoot(p1, bullet_data))


window = Tk()

window.title("Space Invaders")
window.configure(width=1000, height=700)
window.resizable(False, False)

ship_sprite = PhotoImage(file='main_char_sprite.png')
pellet = PhotoImage(file='pellet.png')
enemy_sprite = PhotoImage(file='enemy_sprite.png')

score = 0
life = 3
rof = 100
Sc = Label(window, text="Score:{}                Life:{}" \
           .format(score, life), font=("Helvetica", 36))
Sc.pack()

Gcanv = Canvas(window, bg="#000000", height=600, width=1000)
Gcanv.pack()

window.bind("<s>", lambda e: boundary_of_life_and_death())

Gcanv.create_text(500, 200,
                  font=('consolas', 70), text="Welcome to \nSpace Invaders", fill="red", tag="gameover")
Gcanv.create_text(500, 400,
                  font=('consolas', 70), text="Press S to start", fill="red")

window.mainloop()
