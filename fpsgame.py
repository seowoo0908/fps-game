from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random
import math
import time

# Initialize the game
app = Ursina()

# Add environment
ground = Entity(model='plane', scale=(50, 1, 50), texture='white_cube', color=color.green, collider='box')
wall = Entity(model='cube', position=(0, 1, 5), scale=(5, 2, 1), texture='brick', collider='box')

# Add lighting for better graphics
sun = DirectionalLight()
sun.look_at(Vec3(-1, -1, -1))

# Add trees
for i in range(5):
    x, z = random.randint(-20, 20), random.randint(-20, 20)
    trunk = Entity(model='cylinder', position=(x, 1, z), scale=(1, 5, 1), color=color.brown)
    leaves = Entity(model='sphere', position=(x, 4, z), scale=3, color=color.green)

# Add player with first-person controller
player = FirstPersonController()
player.health = 100  # Player health

# Health bar UI for player
health_bar = Entity(parent=camera.ui, model='quad', color=color.red, scale=(0.5, 0.05), position=(-0.25, 0.45))

# Bullet Speed and Bullet Color
bullet_speed = 40  # Increased bullet speed for further travel
bullet_radius = 0.5  # Bullet radius
bullet_color = color.yellow  # Bullet color

class Bullet(Entity):
    def __init__(self, position, velocity):
        super().__init__(model='sphere', color=bullet_color, scale=bullet_radius, position=position)
        self.velocity = velocity
        self.gravity = 0.5  # Gravity effect
        self.max_distance = 100  # Max distance the bullet can travel
        self.initial_position = position  # Store the initial position

    def move_bullet(self):
        """Move the bullet and check for collisions."""
        self.position += self.velocity * time.dt  # Bullet moves forward
        self.velocity.y -= self.gravity * time.dt  # Apply gravity

        # Check if bullet has traveled beyond its maximum distance
        if distance(self.position, self.initial_position) > self.max_distance:
            destroy(self)

        # Check for collision with player
        if distance(self.position, player.position) < 1:
            player.health -= 10  # Reduce health of the player
            health_bar.scale_x = player.health / 100
            destroy(self)
            if player.health <= 0:
                print("Game Over!")
                application.quit()

# Shooting function
def shoot():
    """Player shooting logic."""
    direction = player.forward.normalized()  # Direction where the player is facing
    bullet_position = player.position + Vec3(0, 1, 0)  # Bullet spawn position
    velocity = direction * bullet_speed  # Bullet velocity

    bullet = Bullet(position=bullet_position, velocity=velocity)  # Create bullet entity
    bullet.update = bullet.move_bullet  # Assign movement logic to the bullet

# Input handling (left mouse click to shoot)
def input(key):
    if key == 'left mouse down':
        shoot()

# Game update logic
def update():
    enemy_ai()  # Update the enemies' movements and shooting

# 3D Gun Parts (Resembling the gun in the image)
# Create the Gun Entity (keep gun fixed relative to player)
gun = Entity(parent=player, model=None, scale=(1, 1, 1), position=(0.5, 0.6, 1.5))  # Raised the Y position

# Gun body (blue color)
gun_body = Entity(model='cube', scale=(0.6, 0.1, 0.2), position=(0.4, -0.3, 0.9), color=color.azure, parent=gun)

# Gun barrel (yellow and purple combination)
gun_barrel = Entity(model='cylinder', scale=(0.1, 0.1, 1.0), position=(0.6, 0, 1.0), color=color.yellow, parent=gun)

# Gun handle (purple color using RGB)
gun_handle = Entity(model='cube', scale=(0.2, 0.1, 0.3), position=(-0.3, -0.3, 1), color=color.rgb(128, 0, 128), parent=gun)

# Gun trigger (purple color using RGB)
gun_trigger = Entity(model='cube', scale=(0.1, 0.1, 0.2), position=(0.3, -0.5, 1), color=color.rgb(128, 0, 128), parent=gun)

# Gun sight (yellow detail)
gun_sight = Entity(model='cube', scale=(0.1, 0.1, 0.1), position=(0.4, 0.3, 1.1), color=color.yellow, parent=gun)

# Enemies Class
class Enemy(Entity):
    def __init__(self, position):
        super().__init__(model='cube', color=color.red, scale=(1, 2, 1), position=position, collider='box')
        self.health = 30  # Reduced enemy health to make them weaker
        self.speed = 0.01  # Slower movement speed
        self.last_shot_time = time.time()  # Track when the enemy last shot
        self.health_bar = Entity(parent=self, model='quad', color=color.red, scale=(0.6, 0.05), position=(0, 1.3, 0))  # Health bar above enemy

    def shoot(self):
        """Enemy shooting logic."""
        direction = (player.position - self.position).normalized()  # Direction to player
        bullet_position = self.position + Vec3(0, 1, 0)  # Bullet spawn position
        velocity = direction * bullet_speed  # Bullet velocity

        bullet = Bullet(position=bullet_position, velocity=velocity)  # Create bullet entity
        bullet.update = bullet.move_bullet  # Assign movement logic to the bullet

    def move(self):
        """Move towards the player."""
        direction = (player.position - self.position).normalized()  # Direction to player
        self.position += direction * self.speed  # Move towards the player at a slower speed

    def can_shoot(self):
        """Check if the enemy can shoot."""
        return time.time() - self.last_shot_time > 2  # Allow shooting every 2 seconds (slower shooting)

    def update(self):
        """Enemy behavior each frame."""
        self.move()
        if self.can_shoot():  # Check if enough time has passed since last shot
            self.shoot()
            self.last_shot_time = time.time()  # Update last shot time
        
        # Update the enemy's health bar according to its current health
        self.health_bar.scale_x = self.health / 30  # Health bar scale based on the enemy's current health
        if self.health <= 0:
            destroy(self)  # Destroy enemy if health reaches 0

# Create enemies
enemies = []
for i in range(3):
    x = random.randint(-20, 20)
    z = random.randint(-20, 20)
    enemy = Enemy(position=(x, 1, z))
    enemies.append(enemy)

# Enemy AI Logic
def enemy_ai():
    """Move and shoot enemies."""
    for enemy in enemies:
        enemy.update()  # Update enemy's move and shooting logic

# Start the game loop
def update():
    enemy_ai()  # Update the enemies' movements and shooting

# Start the game
app.run()