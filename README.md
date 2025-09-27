Methods

setup_level()

Purpose: Creates level layout based on level number

Level 1: Basic platforms for learning
Level 2: Introduces moving platforms
Level 3: Adds danger zones
Level 4: Complex layout with moving platforms and dangers
Level 5: Challenging layout with narrow platforms
Level 6+: Randomly generated levels with increasing difficulty

generate_random_level()

Purpose: Creates random level for levels beyond 5
Generates platforms with decreasing size as level increases
Adds dangers with increasing probability
Creates progressively more challenging layouts


Game Class

Variables

clock: pygame.Clock     # Game clock for FPS control
level_num: int          # Current level number
max_level: int          # Maximum level number (8)
level: Level            # Current level object
player: Player          # Player object
particles: list         # List of active particles
game_state: str         # "playing", "win", "game_over"
win_timer: int          # Timer for win screen display
level_transition_timer: int     # Timer for level transitions

Methods

reset_game()

Purpose: Resets game to initial state for current level
Creates new level object
Resets player position and stats
Clears particles
Sets game state to "playing"

next_level()

Purpose: Advances to next level
Increments level number (loops back after max level)
Plays level transition sound
Calls reset_game() for new level