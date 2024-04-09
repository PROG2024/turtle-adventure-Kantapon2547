"""
The turtle_adventure module maintains all classes related to the Turtle's
adventure game.
"""
from turtle import RawTurtle
import random
import math

from gamelib import Game, GameElement


class TurtleGameElement(GameElement):
    """
    An abstract class representing all game elemnets related to the Turtle's
    Adventure game
    """

    def __init__(self, game: "TurtleAdventureGame"):
        super().__init__(game)
        self.__game: "TurtleAdventureGame" = game

    @property
    def game(self) -> "TurtleAdventureGame":
        """
        Get reference to the associated TurtleAnvengerGame instance
        """
        return self.__game


class Waypoint(TurtleGameElement):
    """
    Represent the waypoint to which the player will move.
    """

    def __init__(self, game: "TurtleAdventureGame"):
        super().__init__(game)
        self.__id1: int
        self.__id2: int
        self.__active: bool = False

    def create(self) -> None:
        self.__id1 = self.canvas.create_line(0, 0, 0, 0, width=2, fill="green")
        self.__id2 = self.canvas.create_line(0, 0, 0, 0, width=2, fill="green")

    def delete(self) -> None:
        self.canvas.delete(self.__id1)
        self.canvas.delete(self.__id2)

    def update(self) -> None:
        # there is nothing to update because a waypoint is fixed
        pass

    def render(self) -> None:
        if self.is_active:
            self.canvas.itemconfigure(self.__id1, state="normal")
            self.canvas.itemconfigure(self.__id2, state="normal")
            self.canvas.tag_raise(self.__id1)
            self.canvas.tag_raise(self.__id2)
            self.canvas.coords(self.__id1, self.x-10, self.y-10, self.x+10, self.y+10)
            self.canvas.coords(self.__id2, self.x-10, self.y+10, self.x+10, self.y-10)
        else:
            self.canvas.itemconfigure(self.__id1, state="hidden")
            self.canvas.itemconfigure(self.__id2, state="hidden")

    def activate(self, x: float, y: float) -> None:
        """
        Activate this waypoint with the specified location.
        """
        self.__active = True
        self.x = x
        self.y = y

    def deactivate(self) -> None:
        """
        Mark this waypoint as inactive.
        """
        self.__active = False

    @property
    def is_active(self) -> bool:
        """
        Get the flag indicating whether this waypoint is active.
        """
        return self.__active


class Home(TurtleGameElement):
    """
    Represent the player's home.
    """

    def __init__(self, game: "TurtleAdventureGame", pos: tuple[int, int], size: int):
        super().__init__(game)
        self.__id: int
        self.__size: int = size
        x, y = pos
        self.x = x
        self.y = y

    @property
    def size(self) -> int:
        """
        Get or set the size of Home
        """
        return self.__size

    @size.setter
    def size(self, val: int) -> None:
        self.__size = val

    def create(self) -> None:
        self.__id = self.canvas.create_rectangle(0, 0, 0, 0, outline="brown", width=2)

    def delete(self) -> None:
        self.canvas.delete(self.__id)

    def update(self) -> None:
        # there is nothing to update, unless home is allowed to moved
        pass

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size/2,
                           self.y - self.size/2,
                           self.x + self.size/2,
                           self.y + self.size/2)

    def contains(self, x: float, y: float):
        """
        Check whether home contains the point (x, y).
        """
        x1, x2 = self.x-self.size/2, self.x+self.size/2
        y1, y2 = self.y-self.size/2, self.y+self.size/2
        return x1 <= x <= x2 and y1 <= y <= y2


class Player(TurtleGameElement):
    """
    Represent the main player, implemented using Python's turtle.
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 turtle: RawTurtle,
                 speed: float = 5):
        super().__init__(game)
        self.__speed: float = speed
        self.__turtle: RawTurtle = turtle

    def create(self) -> None:
        turtle = RawTurtle(self.canvas)
        turtle.getscreen().tracer(False)  # disable turtle's built-in animation
        turtle.shape("turtle")
        turtle.color("green")
        turtle.penup()

        self.__turtle = turtle

    @property
    def speed(self) -> float:
        """
        Give the player's current speed.
        """
        return self.__speed

    @speed.setter
    def speed(self, val: float) -> None:
        self.__speed = val

    def delete(self) -> None:
        pass

    def update(self) -> None:
        # check if player has arrived home
        if self.game.home.contains(self.x, self.y):
            self.game.game_over_win()
        turtle = self.__turtle
        waypoint = self.game.waypoint
        if self.game.waypoint.is_active:
            turtle.setheading(turtle.towards(waypoint.x, waypoint.y))
            turtle.forward(self.speed)
            if turtle.distance(waypoint.x, waypoint.y) < self.speed:
                waypoint.deactivate()

    def render(self) -> None:
        self.__turtle.goto(self.x, self.y)
        self.__turtle.getscreen().update()

    # override original property x's getter/setter to use turtle's methods
    # instead
    @property
    def x(self) -> float:
        return self.__turtle.xcor()

    @x.setter
    def x(self, val: float) -> None:
        self.__turtle.setx(val)

    # override original property y's getter/setter to use turtle's methods
    # instead
    @property
    def y(self) -> float:
        return self.__turtle.ycor()

    @y.setter
    def y(self, val: float) -> None:
        self.__turtle.sety(val)


class Enemy(TurtleGameElement):
    """
    Define an abstract enemy for the Turtle's adventure game
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str,
                 speed: float):
        super().__init__(game)
        self.__size = size
        self.__color = color
        self.__speed = speed

    @property
    def size(self) -> float:
        """
        Get the size of the enemy
        """
        return self.__size

    @property
    def speed(self) -> float:
        """
        Get the speed of the enemy
        """
        return self.__speed

    @property
    def color(self) -> str:
        """
        Get the color of the enemy
        """
        return self.__color

    def hits_player(self):
        """
        Check whether the enemy is hitting the player
        """
        return (
            (self.x - self.size/2 < self.game.player.x < self.x + self.size/2)
            and
            (self.y - self.size/2 < self.game.player.y < self.y + self.size/2)
        )


# TODO
# * Define your enemy classes
# * Implement all methods required by the GameElement abstract class
# * Define enemy's update logic in the update() method
# * Check whether the player hits this enemy, then call the
#   self.game.game_over_lose() method in the TurtleAdventureGame class.
class DemoEnemy(Enemy):
    """
    Demo enemy
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str,
                 speed: float):
        super().__init__(game, size, color, speed)
        self.__id = None

    def create(self) -> None:
        self.__id = self.canvas.create_oval(0, 0, 0, 0, fill="red")

    def update(self) -> None:
        self.x += 1
        self.y += 1
        if self.hits_player():
            self.game.game_over_lose()

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size/2,
                           self.y - self.size/2,
                           self.x + self.size/2,
                           self.y + self.size/2)

    def delete(self) -> None:
        self.canvas.delete(self.__id)


class RandomWalkEnemy(Enemy):

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str,
                 speed: float):
        super().__init__(game, size, color, speed)
        self.__id = None
        self.__x_speed = random.uniform(-1, 1)
        self.__y_speed = random.uniform(-1, 1)

    def create(self) -> None:
        self.__id = self.canvas.create_rectangle(0, 0, 0, 0, fill=self.color)

    def update(self) -> None:
        self.x += self.__x_speed
        self.y += self.__y_speed

        if self.x - self.size / 2 <= 0 or self.x + self.size / 2 >= self.game.screen_width:
            self.__x_speed *= -1  # Reverse x direction if hitting left or right boundary
        if self.y - self.size / 2 <= 0 or self.y + self.size / 2 >= self.game.screen_height:
            self.__y_speed *= -1  # Reverse y direction if hitting top or bottom boundary

        self.canvas.move(self.__id, self.__x_speed, self.__y_speed)

        if self.hits_player():
            self.game.game_over_lose()

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size / 2,
                           self.y - self.size / 2,
                           self.x + self.size / 2,
                           self.y + self.size / 2)

        self.canvas.update()

    def delete(self) -> None:
        self.canvas.delete(self.__id)


class ChasingEnemy(Enemy):
    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str,
                 speed: float):
        super().__init__(game, size, color, speed)
        self.__id = None

    def create(self) -> None:
        self.__id = self.canvas.create_oval(0, 0, 0, 0, fill=self.color)

    def update(self) -> None:
        player = self.game.player
        dx = player.x - self.x
        dy = player.y - self.y
        distance_to_player = (dx ** 2 + dy ** 2) ** 0.5  # Calculate distance to player

        # Adjust speed based on the distance to the player
        if distance_to_player > 0:
            if distance_to_player < 50:
                speed_modifier = 0.5  # Slow down if too close to the player
            else:
                speed_modifier = 1.0

            # Calculate movement direction towards the player
            dx /= distance_to_player
            dy /= distance_to_player

            # Move enemy towards the player
            self.x += dx * self.speed * speed_modifier
            self.y += dy * self.speed * speed_modifier

        if self.hits_player():
            self.game.game_over_lose()

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size / 2,
                           self.y - self.size / 2,
                           self.x + self.size / 2,
                           self.y + self.size / 2)

        self.canvas.update()

    def delete(self) -> None:
        self.canvas.delete(self.__id)


class FencingEnemy(Enemy):
    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str,
                 speed: float):
        super().__init__(game, size, color, speed)
        self.__id = None
        self.__waypoint = game.waypoint
        self.__corner_index = 0  # Index of the current corner in the square path
        self.__corner_positions = []  # Positions of the corners of the square path

        if self.__waypoint.is_active:
            self.x = self.__waypoint.x
            self.y = self.__waypoint.y

    def create(self) -> None:
        self.__id = self.canvas.create_rectangle(0, 0, 0, 0, fill=self.color)

    def update(self) -> None:
        if not self.__waypoint.is_active:
            return

        if not self.__corner_positions:
            # Calculate the square path around the waypoint
            self.calculate_square_path()

        if not self.__corner_positions:
            return

        # Move towards the next corner in the square path
        target_x, target_y = self.__corner_positions[self.__corner_index]

        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance > self.speed:
            # Move towards the corner
            direction_x = dx / distance
            direction_y = dy / distance
            self.x += direction_x * self.speed
            self.y += direction_y * self.speed
        else:
            # Reached the corner, move to the next corner
            self.__corner_index = (self.__corner_index + 1) % len(self.__corner_positions)

        # Check if the enemy hits the player
        if self.hits_player():
            self.game.game_over_lose()

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size / 2,
                           self.y - self.size / 2,
                           self.x + self.size / 2,
                           self.y + self.size / 2)

    def delete(self) -> None:
        self.canvas.delete(self.__id)

    def calculate_square_path(self) -> None:
        """
        Calculate the square path around the waypoint
        """
        waypoint_x, waypoint_y = self.__waypoint.x, self.__waypoint.y
        distance = 50  # Distance from the waypoint to the corners
        self.__corner_positions = [
            (waypoint_x - distance, waypoint_y - distance),
            (waypoint_x + distance, waypoint_y - distance),
            (waypoint_x + distance, waypoint_y + distance),
            (waypoint_x - distance, waypoint_y + distance)
        ]


class CircularEnemy(Enemy):
    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str,
                 speed: float,
                 center: tuple[float, float],
                 radius: float,
                 angular_speed: float):
        super().__init__(game, size, color, speed)
        self.__id = None
        self.__center = center
        self.__radius = radius
        self.__angle = 0
        self.__angular_speed = angular_speed

    def create(self) -> None:
        self.__id = self.canvas.create_oval(0, 0, 0, 0, fill=self.color)

    def update(self) -> None:
        # Calculate the new position based on the circular motion
        self.__angle += self.__angular_speed
        self.__angle %= 360  # Keep angle within 0-359 degrees range
        radian_angle = math.radians(self.__angle)
        self.x = self.__center[0] + self.__radius * math.cos(radian_angle)
        self.y = self.__center[1] + self.__radius * math.sin(radian_angle)

        # Check if the enemy hits the player
        if self.hits_player():
            self.game.game_over_lose()

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size / 2,
                           self.y - self.size / 2,
                           self.x + self.size / 2,
                           self.y + self.size / 2)

    def delete(self) -> None:
        self.canvas.delete(self.__id)


# TODO
# Complete the EnemyGenerator class by inserting code to generate enemies
# based on the given game level; call TurtleAdventureGame's add_enemy() method
# to add enemies to the game at certain points in time.
#
# Hint: the 'game' parameter is a tkinter's frame, so it's after()
# method can be used to schedule some future events.


class EnemyGenerator:
    """
    An EnemyGenerator instance is responsible for creating enemies of various
    kinds and scheduling them to appear at certain points in time.
    """

    def __init__(self, game: "TurtleAdventureGame", level: int):
        self.__game: TurtleAdventureGame = game
        self.__level: int = level
        # self.__interval = 1000

        # example
        self.__game.after(100, self.create_enemy)

    @property
    def game(self) -> "TurtleAdventureGame":
        """
        Get reference to the associated TurtleAnvengerGame instance
        """
        return self.__game

    @property
    def level(self) -> int:
        """
        Get the game level
        """
        return self.__level

    def create_enemy(self) -> None:
        """
        Create a new enemy, possibly based on the game level
        """
        # Create a new instance of RandomWalkEnemy
        new_random_enemy = RandomWalkEnemy(self.__game, size=20, color="blue", speed=7.0)
        # Set the position of the RandomWalkEnemy instance randomly within the game screen
        new_random_enemy.x = random.randint(0, self.__game.screen_width)
        new_random_enemy.y = random.randint(0, self.__game.screen_height)
        # Add the RandomWalkEnemy instance to the game
        self.game.add_enemy(new_random_enemy)

        # Create a new instance of ChasingEnemy
        new_chasing_enemy = ChasingEnemy(self.__game, size=20, color="red", speed=3.0)
        # Set the position of the ChasingEnemy instance randomly within the game screen
        new_chasing_enemy.x = random.randint(0, self.__game.screen_width)
        new_chasing_enemy.y = random.randint(0, self.__game.screen_height)
        # Add the ChasingEnemy instance to the game
        self.game.add_enemy(new_chasing_enemy)

        # Create a new instance of FencingEnemy
        new_fencing_enemy = FencingEnemy(self.__game, size=10, color="green", speed=2.0)
        self.game.add_enemy(new_fencing_enemy)

        # Create a new instance of CircularEnemy
        center = (self.__game.screen_width // 2, self.__game.screen_height // 2)  # Center of the screen
        radius = 100  # Radius of the circular motion
        angular_speed = 2  # Angular speed in degrees per frame
        new_circular_enemy = CircularEnemy(self.__game, size=15, color="orange", speed=2.5,
                                           center=center, radius=radius, angular_speed=angular_speed)
        # Add the CircularEnemy instance to the game
        self.game.add_enemy(new_circular_enemy)

        # Schedule the creation of the next enemy with a random delay
        delay = random.randint(1000, 2000)
        self.__game.after(delay, self.create_enemy)


class TurtleAdventureGame(Game):  # pylint: disable=too-many-ancestors
    """
    The main class for Turtle's Adventure.
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(self, parent, screen_width: int, screen_height: int, level: int = 1):
        self.level: int = level
        self.screen_width: int = screen_width
        self.screen_height: int = screen_height
        self.waypoint: Waypoint
        self.player: Player
        self.home: Home
        self.enemies: list[Enemy] = []
        self.enemy_generator: EnemyGenerator
        super().__init__(parent)

        self.enemy_generator = EnemyGenerator(self, level=self.level)

    def init_game(self):
        self.canvas.config(width=self.screen_width, height=self.screen_height)
        turtle = RawTurtle(self.canvas)
        # set turtle screen's origin to the top-left corner
        turtle.screen.setworldcoordinates(0, self.screen_height-1, self.screen_width-1, 0)

        self.waypoint = Waypoint(self)
        self.add_element(self.waypoint)
        self.home = Home(self, (self.screen_width-100, self.screen_height//2), 20)
        self.add_element(self.home)
        self.player = Player(self, turtle)
        self.add_element(self.player)
        self.canvas.bind("<Button-1>", lambda e: self.waypoint.activate(e.x, e.y))

        self.player.x = 50
        self.player.y = self.screen_height//2

    def add_enemy(self, enemy: Enemy) -> None:
        """
        Add a new enemy into the current game
        """
        self.enemies.append(enemy)
        self.add_element(enemy)

    def game_over_win(self) -> None:
        """
        Called when the player wins the game and stop the game
        """
        self.stop()
        font = ("Arial", 36, "bold")
        self.canvas.create_text(self.screen_width/2,
                                self.screen_height/2,
                                text="You Win",
                                font=font,
                                fill="green")

    def game_over_lose(self) -> None:
        """
        Called when the player loses the game and stop the game
        """
        self.stop()
        font = ("Arial", 36, "bold")
        self.canvas.create_text(self.screen_width/2,
                                self.screen_height/2,
                                text="You Lose",
                                font=font,
                                fill="red")
