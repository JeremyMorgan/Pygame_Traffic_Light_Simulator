import pygame
import sys

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
CENTER_X = SCREEN_WIDTH // 2
CENTER_Y = SCREEN_HEIGHT // 2
ROAD_WIDTH = 100
LANE_OFFSET = 15
CAR_LENGTH = 40
CAR_WIDTH = 20
SPEED = 100  # pixels per second
GAP = 10  # gap between cars
SPAWN_INTERVAL = 2  # seconds
CYCLE_TIME = 26  # seconds for full light cycle
GREEN_TIME = 10  # seconds
YELLOW_TIME = 3  # seconds

# Colors
BLACK = (0, 0, 0)
GREY = (100, 100, 100)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)

# Directions
DIRECTIONS = ['south', 'north', 'west', 'east']

# Spawn positions (cars start at screen edges)
SPAWN_POSITIONS = {
    'south': (CENTER_X - LANE_OFFSET, 0),
    'north': (CENTER_X + LANE_OFFSET, SCREEN_HEIGHT),
    'west': (SCREEN_WIDTH, CENTER_Y - LANE_OFFSET),
    'east': (0, CENTER_Y + LANE_OFFSET)
}

# Stop lines (where car fronts should stop at red lights)
STOP_LINES = {
    'south': CENTER_Y - ROAD_WIDTH / 2,
    'north': CENTER_Y + ROAD_WIDTH / 2,
    'west': CENTER_X + ROAD_WIDTH / 2,
    'east': CENTER_X - ROAD_WIDTH / 2
}

# Car class to manage vehicle properties and behavior
class Car:
    """
    Represents a car in the simulation, with position, direction, speed, and size.
    Cars move towards the intersection and stop based on traffic lights and other cars.
    """
    def __init__(self, direction):
        """
        Initialize a car with its direction and starting position.

        Args:
            direction (str): 'south', 'north', 'west', or 'east'.
        """
        self.direction = direction
        self.x, self.y = SPAWN_POSITIONS[direction]
        self.speed = SPEED
        self.length = CAR_LENGTH
        self.width = CAR_WIDTH
        # Assign different colors for cars based on direction
        self.color = {'south': BLUE, 'north': RED, 'west': GREEN, 'east': ORANGE}[direction]

    def update(self, dt, light_state, leader):
        if self.direction == 'south':
            stop_line = STOP_LINES['south']
            front_y = self.y + self.length / 2
            if light_state == 'green' or front_y > stop_line:
                target_y = SCREEN_HEIGHT + 1000  # Far beyond the screen
            else:
                target_y = stop_line - self.length / 2
            if leader:
                leader_front_y = leader.y - leader.length / 2
                target_y = min(target_y, leader_front_y - self.length / 2 - GAP)
            if self.y < target_y:
                self.y += self.speed * dt
            if self.y > target_y:
                self.y = target_y

        elif self.direction == 'north':
            stop_line = STOP_LINES['north']
            front_y = self.y - self.length / 2
            if light_state == 'green' or front_y < stop_line:
                target_y = -1000  # Far beyond the screen
            else:
                target_y = stop_line + self.length / 2
            if leader:
                leader_front_y = leader.y + leader.length / 2
                target_y = max(target_y, leader_front_y + self.length / 2 + GAP)
            if self.y > target_y:
                self.y -= self.speed * dt
            if self.y < target_y:
                self.y = target_y

        elif self.direction == 'west':
            stop_line = STOP_LINES['west']
            front_x = self.x - self.length / 2
            if light_state == 'green' or front_x < stop_line:
                target_x = -1000  # Far beyond the screen
            else:
                target_x = stop_line + self.length / 2
            if leader:
                leader_front_x = leader.x + leader.length / 2
                target_x = max(target_x, leader_front_x + self.length / 2 + GAP)
            if self.x > target_x:
                self.x -= self.speed * dt
            if self.x < target_x:
                self.x = target_x

        elif self.direction == 'east':
            stop_line = STOP_LINES['east']
            front_x = self.x + self.length / 2
            if light_state == 'green' or front_x > stop_line:
                target_x = SCREEN_WIDTH + 1000  # Far beyond the screen
            else:
                target_x = stop_line - self.length / 2
            if leader:
                leader_front_x = leader.x - leader.length / 2
                target_x = min(target_x, leader_front_x - self.length / 2 - GAP)
            if self.x < target_x:
                self.x += self.speed * dt
            if self.x > target_x:
                self.x = target_x
            
    def draw(self, screen):
        """
        Draw the car on the screen, oriented based on direction.

        Args:
            screen (pygame.Surface): The surface to draw on.
        """
        if self.direction in ['south', 'north']:
            # Vertical cars: width = car_width, height = car_length
            rect = pygame.Rect(self.x - self.width / 2, self.y - self.length / 2, self.width, self.length)
        else:
            # Horizontal cars: width = car_length, height = car_width
            rect = pygame.Rect(self.x - self.length / 2, self.y - self.width / 2, self.length, self.width)
        pygame.draw.rect(screen, self.color, rect)

def draw_roads(screen):
    """
    Draw the grey roads forming a 4-way intersection.

    Args:
        screen (pygame.Surface): The surface to draw on.
    """
    # Vertical road
    pygame.draw.rect(screen, GREY, (CENTER_X - ROAD_WIDTH / 2, 0, ROAD_WIDTH, SCREEN_HEIGHT))
    # Horizontal road
    pygame.draw.rect(screen, GREY, (0, CENTER_Y - ROAD_WIDTH / 2, SCREEN_WIDTH, ROAD_WIDTH))

def draw_traffic_lights(screen, NS_light, EW_light):
    """
    Draw traffic lights for each approach, showing the current state.

    Args:
        screen (pygame.Surface): The surface to draw on.
        NS_light (str): State for North-South lights ('green', 'yellow', 'red').
        EW_light (str): State for East-West lights ('green', 'yellow', 'red').
    """
    positions = {
        'north': (CENTER_X, CENTER_Y - ROAD_WIDTH / 2 - 20),
        'south': (CENTER_X, CENTER_Y + ROAD_WIDTH / 2 + 20),
        'west': (CENTER_X - ROAD_WIDTH / 2 - 20, CENTER_Y),
        'east': (CENTER_X + ROAD_WIDTH / 2 + 20, CENTER_Y)
    }
    light_colors = {'red': RED, 'yellow': YELLOW, 'green': GREEN}
    # Draw lights for North and South approaches (NS_light)
    for dir in ['north', 'south']:
        pos = positions[dir]
        state = NS_light
        for i, color in enumerate(['red', 'yellow', 'green']):
            circle_pos = (pos[0], pos[1] + i * 10)
            if color == state:
                pygame.draw.circle(screen, light_colors[color], circle_pos, 5)
            else:
                pygame.draw.circle(screen, (50, 50, 50), circle_pos, 5)
    # Draw lights for East and West approaches (EW_light)
    for dir in ['east', 'west']:
        pos = positions[dir]
        state = EW_light
        for i, color in enumerate(['red', 'yellow', 'green']):
            circle_pos = (pos[0] + i * 10, pos[1])
            if color == state:
                pygame.draw.circle(screen, light_colors[color], circle_pos, 5)
            else:
                pygame.draw.circle(screen, (50, 50, 50), circle_pos, 5)

def main():
    """
    Main function to run the traffic intersection simulation.
    Initializes Pygame, sets up the window, and handles the main loop.
    """
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("4-Way Traffic Intersection Simulation")
    clock = pygame.time.Clock()
    cars = []
    last_spawn_time = {dir: 0 for dir in DIRECTIONS}

    while True:
        dt = clock.tick(30) / 1000  # Delta time in seconds for 30 FPS

        # Handle events (only for quitting)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Determine traffic light states based on current time
        current_time = pygame.time.get_ticks() / 1000  # seconds
        time_in_cycle = current_time % CYCLE_TIME
        if time_in_cycle < GREEN_TIME:
            NS_light = 'green'
            EW_light = 'red'
        elif time_in_cycle < GREEN_TIME + YELLOW_TIME:
            NS_light = 'yellow'
            EW_light = 'red'
        elif time_in_cycle < GREEN_TIME + YELLOW_TIME + GREEN_TIME:
            NS_light = 'red'
            EW_light = 'green'
        else:
            NS_light = 'red'
            EW_light = 'yellow'

        # Spawn new cars if interval is exceeded and spawn area is clear
        for dir in DIRECTIONS:
            if current_time - last_spawn_time[dir] > SPAWN_INTERVAL:
                spawn_x, spawn_y = SPAWN_POSITIONS[dir]
                clear = True
                for car in cars:
                    if car.direction == dir:
                        if dir == 'south' and car.y < CAR_LENGTH + GAP:
                            clear = False
                        elif dir == 'north' and car.y > SCREEN_HEIGHT - CAR_LENGTH - GAP:
                            clear = False
                        elif dir == 'west' and car.x > SCREEN_WIDTH - CAR_LENGTH - GAP:
                            clear = False
                        elif dir == 'east' and car.x < CAR_LENGTH + GAP:
                            clear = False
                if clear:
                    cars.append(Car(dir))
                    last_spawn_time[dir] = current_time

        # Update cars: sort by lane and update positions
        for dir in DIRECTIONS:
            if dir in ['south', 'north']:
                light_state = NS_light
            else:
                light_state = EW_light
            # Sort cars by position along their direction of travel
            if dir == 'south':
                dir_cars = sorted([car for car in cars if car.direction == dir], key=lambda c: c.y)
            elif dir == 'north':
                dir_cars = sorted([car for car in cars if car.direction == dir], key=lambda c: c.y, reverse=True)
            elif dir == 'west':
                dir_cars = sorted([car for car in cars if car.direction == dir], key=lambda c: c.x, reverse=True)
            elif dir == 'east':
                dir_cars = sorted([car for car in cars if car.direction == dir], key=lambda c: c.x)
            # Update each car with its leader (if any)
            for i, car in enumerate(dir_cars):
                leader = dir_cars[i+1] if i+1 < len(dir_cars) else None
                car.update(dt, light_state, leader)

        # Remove cars that have left the screen
        cars = [car for car in cars if not (
            (car.direction == 'south' and car.y > SCREEN_HEIGHT + car.length / 2) or
            (car.direction == 'north' and car.y < -car.length / 2) or
            (car.direction == 'west' and car.x < -car.length / 2) or
            (car.direction == 'east' and car.x > SCREEN_WIDTH + car.length / 2)
        )]

        # Draw everything
        screen.fill(BLACK)
        draw_roads(screen)
        draw_traffic_lights(screen, NS_light, EW_light)
        for car in cars:
            car.draw(screen)
        pygame.display.flip()

if __name__ == '__main__':
    main()