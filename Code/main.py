import math
import pygame
import random
from enemy import Enemy
import os
import button
import sound_effects as se
pygame.init()
pygame.mixer.init()
pygame.mixer.music.load("Music/background.mp3") 
pygame.mixer.music.play(-1,0.0)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Cyber Ninza')
clock = pygame.time.Clock()
FPS = 60
level = 1
high_score = 0
level_difficulty = 0
target_difficulty = 1000
DIFFICULTY_MULTIPLIER = 1.1
game_over = False
next_level = False
ENEMY_TIMER = 1000
last_enemy = pygame.time.get_ticks()
enemies_alive = 0
max_towers = 4
TOWER_COST = 5000
tower_positions = [
[SCREEN_WIDTH - 250, SCREEN_HEIGHT - 200],
[SCREEN_WIDTH - 200, SCREEN_HEIGHT - 150],
[SCREEN_WIDTH - 150, SCREEN_HEIGHT - 150],
[SCREEN_WIDTH - 100, SCREEN_HEIGHT - 150],
]
if os.path.exists('high_score.txt'):
	with open('high_score.txt', 'r') as file:
		high_score = int(file.read())
WHITE = (0, 0, 0)
GREY = (100, 100, 100)
font = pygame.font.SysFont('Futura', 30)
font_60 = pygame.font.SysFont('Futura', 60)
bg = pygame.image.load('img/bg.png').convert_alpha()
castle_img_100 = pygame.image.load('img/castle/castle_100.png').convert_alpha()
castle_img_50 = pygame.image.load('img/castle/castle_50.png').convert_alpha()
castle_img_25 = pygame.image.load('img/castle/castle_25.png').convert_alpha()
tower_img_100 = pygame.image.load('img/tower/tower_100.png').convert_alpha()
tower_img_50 = pygame.image.load('img/tower/tower_50.png').convert_alpha()
tower_img_25 = pygame.image.load('img/tower/tower_25.png').convert_alpha()
bullet_img = pygame.image.load('img/bullet.png').convert_alpha()
b_w = bullet_img.get_width()
b_h = bullet_img.get_height()
bullet_img = pygame.transform.scale(bullet_img, (int(b_w * 0.075), int(b_h * 0.075)))
enemy_animations = []
enemy_types = ['knight', 'goblin', 'purple_goblin', 'red_goblin']
enemy_health = [75, 100, 125, 150]

animation_types = ['walk', 'attack', 'death']
for enemy in enemy_types:
	animation_list = []
	for animation in animation_types:
		temp_list = []
		num_of_frames = 20
		for i in range(num_of_frames):
			img = pygame.image.load(f'img/enemies/{enemy}/{animation}/{i}.png').convert_alpha()
			e_w = img.get_width()
			e_h = img.get_height()
			img = pygame.transform.scale(img, (int(e_w * 0.2), int(e_h * 0.2)))
			temp_list.append(img)
		animation_list.append(temp_list)
	enemy_animations.append(animation_list)
repair_img = pygame.image.load('img/repair.png').convert_alpha()
armour_img = pygame.image.load('img/armour.png').convert_alpha()
def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))
def show_info():
	draw_text('Coins: ' + str(castle.money), font, WHITE, 10, 10)
	draw_text('Score: ' + str(castle.score) + "/" + str(high_score), font, WHITE, 180, 10)
	draw_text('Level: ' + str(level), font, WHITE, SCREEN_WIDTH // 2, 10)
	draw_text('Hearts: ' + str(castle.health) + " / " + str(castle.max_health), font, WHITE, SCREEN_WIDTH - 230, SCREEN_HEIGHT - 50)
	draw_text('1000', font, WHITE, SCREEN_WIDTH - 220 , 70)
	draw_text(str(TOWER_COST), font, WHITE, SCREEN_WIDTH - 150, 70)
	draw_text('500', font, WHITE, SCREEN_WIDTH - 70 , 70)
class Castle():
	def __init__(self, image100, image50, image25, x, y, scale):
		self.health = 1000
		self.max_health = self.health
		self.fired = False
		self.money = 0
		self.score = 0
		width = image100.get_width()
		height = image100.get_height()
		self.image100 = pygame.transform.scale(image100, (int(width * scale), int(height * scale)))
		self.image50 = pygame.transform.scale(image50, (int(width * scale), int(height * scale)))
		self.image25 = pygame.transform.scale(image25, (int(width * scale), int(height * scale)))
		self.rect = self.image100.get_rect()
		self.rect.x = x
		self.rect.y = y
	def shoot(self):
		pos = pygame.mouse.get_pos()
		x_dist = pos[0] - self.rect.midleft[0]
		y_dist = -(pos[1] - self.rect.midleft[1])
		self.angle = math.degrees(math.atan2(y_dist, x_dist))
		if pygame.mouse.get_pressed()[0] and self.fired == False and pos[1] > 70:
			se.fire.play()
			self.fired = True
			bullet = Bullet(bullet_img, self.rect.midleft[0], self.rect.midleft[1], self.angle)
			bullet_group.add(bullet)
		if pygame.mouse.get_pressed()[0] == False:
			self.fired = False
	def draw(self):
		if self.health <= 250:
			self.image = self.image25
		elif self.health <= 500:
			self.image = self.image50
		else:
			self.image = self.image100
		screen.blit(self.image, self.rect)
	def repair(self):
		if self.money >= 1000 and self.health < self.max_health:
			self.health += 500
			self.money -= 1000
			if castle.health > castle.max_health:
				castle.health = castle.max_health
	def armour(self):
		if self.money >= 500:
			self.max_health += 250
			self.money -= 500
class Tower(pygame.sprite.Sprite):
	def __init__(self, image100, image50, image25, x, y, scale):
		pygame.sprite.Sprite.__init__(self)
		self.got_target = False
		self.angle = 0
		self.last_shot = pygame.time.get_ticks()
		width = image100.get_width()
		height = image100.get_height()
		self.image100 = pygame.transform.scale(image100, (int(width * scale), int(height * scale)))
		self.image50 = pygame.transform.scale(image50, (int(width * scale), int(height * scale)))
		self.image25 = pygame.transform.scale(image25, (int(width * scale), int(height * scale)))
		self.image = self.image100
		self.rect = self.image100.get_rect()
		self.rect.x = x
		self.rect.y = y
	def update(self, enemy_group):
		self.got_target = False
		for e in enemy_group:
			if e.alive:
				target_x, target_y = e.rect.midbottom
				self.got_target = True
				break
		if self.got_target:
			x_dist = target_x - self.rect.midleft[0]
			y_dist = -(target_y - self.rect.midleft[1])
			self.angle = math.degrees(math.atan2(y_dist, x_dist))
			shot_cooldown = 1000
			if pygame.time.get_ticks() - self.last_shot > shot_cooldown:
				self.last_shot = pygame.time.get_ticks()
				bullet = Bullet(bullet_img, self.rect.midleft[0], self.rect.midleft[1], self.angle)
				bullet_group.add(bullet)
		if castle.health <= 250:
			self.image = self.image25
		elif castle.health <= 500:
			self.image = self.image50
		else:
			self.image = self.image100
class Bullet(pygame.sprite.Sprite):
	def __init__(self, image, x, y, angle):
		pygame.sprite.Sprite.__init__(self)
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.angle = math.radians(angle)
		self.speed = 10
		self.dx = math.cos(self.angle) * self.speed
		self.dy = -(math.sin(self.angle) * self.speed)
	def update(self):
		if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
			self.kill()	
		self.rect.x += self.dx
		self.rect.y += self.dy
class Crosshair():
	def __init__(self, scale):
		image = pygame.image.load('img/crosshair.png').convert_alpha()
		width = image.get_width()
		height = image.get_height()
		self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
		self.rect = self.image.get_rect()
		pygame.mouse.set_visible(False)
	def draw(self):
		mx, my = pygame.mouse.get_pos()
		self.rect.center = (mx, my)
		screen.blit(self.image, self.rect)
castle = Castle(castle_img_100, castle_img_50, castle_img_25, SCREEN_WIDTH - 250, SCREEN_HEIGHT - 300, 0.2)
crosshair = Crosshair(0.025)
repair_button = button.Button(SCREEN_WIDTH - 220, 10, repair_img, 0.5)
tower_button = button.Button(SCREEN_WIDTH - 140, 10, tower_img_100, 0.1)
armour_button = button.Button(SCREEN_WIDTH - 75, 10, armour_img, 1.5)
tower_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
run = True
while run:
	clock.tick(FPS)
	if game_over == False:
		screen.blit(bg, (0, 0))
		castle.draw()
		castle.shoot()
		# se.fire.play()
		tower_group.draw(screen)
		tower_group.update(enemy_group)
		crosshair.draw()
		bullet_group.update()
		bullet_group.draw(screen)
		enemy_group.update(screen, castle, bullet_group)
		show_info()
		if repair_button.draw(screen):
			castle.repair()
		if tower_button.draw(screen):
			if castle.money >= TOWER_COST and len(tower_group) < max_towers:
				tower = Tower(
					tower_img_100,
					tower_img_50,
					tower_img_25,
					tower_positions[len(tower_group)][0],
					tower_positions[len(tower_group)][1],
					0.2
					)
				tower_group.add(tower)
				castle.money -= TOWER_COST
		if armour_button.draw(screen):
			castle.armour()
		if level_difficulty < target_difficulty:
			if pygame.time.get_ticks() - last_enemy > ENEMY_TIMER:
				e = random.randint(0, len(enemy_types) -1)
				enemy = Enemy(enemy_health[e], enemy_animations[e], -100, SCREEN_HEIGHT - 100, 1)
				enemy_group.add(enemy)
				last_enemy = pygame.time.get_ticks()
				level_difficulty += enemy_health[e]
		if level_difficulty >= target_difficulty:
			enemies_alive = 0
			for e in enemy_group:
				if e.alive == True:
					enemies_alive += 1
			if enemies_alive == 0 and next_level == False:
				next_level = True
				level_reset_time = pygame.time.get_ticks()
		if next_level == True:
			se.levelup.play()
			draw_text('LEVEL COMPLETE!', font_60, WHITE, 200, 300)
			if castle.score > high_score:
				high_score = castle.score
				with open('high_score.txt', 'w') as file:
					file.write(str(high_score))
			if pygame.time.get_ticks() - level_reset_time > 1500:
				next_level = False
				level += 1
				last_enemy = pygame.time.get_ticks()
				target_difficulty *= DIFFICULTY_MULTIPLIER
				level_difficulty = 0
				enemy_group.empty()
		if castle.health <= 0:
			game_over = True
	else:
		draw_text('GAME OVER!', font, WHITE, 300, 300)
		pygame.mixer.music.stop()
		se.gameover.play()
		draw_text('PRESS "Enter" TO PLAY AGAIN!', font, WHITE, 250, 360)
		pygame.mouse.set_visible(True)
		key = pygame.key.get_pressed()
		if key[pygame.K_RETURN]:
			pygame.mixer.music.play()
			game_over = False
			level = 1
			target_difficulty = 1000
			level_difficulty = 0
			last_enemy = pygame.time.get_ticks()
			enemy_group.empty()
			tower_group.empty()
			castle.score = 0
			castle.health = 1000
			castle.max_health = castle.health
			castle.money = 0
			pygame.mouse.set_visible(False)
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
	pygame.display.update()
pygame.quit()