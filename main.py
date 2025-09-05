# ---------- Imports ----------
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math

# ---------- Point System Variables ----------
player_score = 0
POINT_COLOR = (1.0, 0.0, 0.0)  # bright red
POINT_SIZE = 15.0  # increased base size for points
POINT_SPAWN_PROBABILITY_PER_SEGMENT = 0.3  # 30% chance for a point to spawn
POINT_HOVER_HEIGHT = 25.0  # height above the platform/obstacle
point_objects = []  # list to store point objects
POINT_TYPE_TILE = 0
POINT_TYPE_OBSTACLE = 1


### NEW: Double Jump Power-up Variables ###
DOUBLE_JUMP_COLOR = (0.0, 1.0, 0.0)  # Bright green
DOUBLE_JUMP_SIZE = 15.0
DOUBLE_JUMP_SPAWN_PROBABILITY = 0.05
DOUBLE_JUMP_HOVER_HEIGHT = 30.0
has_double_jump_charge = False 
DOUBLE_JUMP_DURATION = 8.0 ### NEW: Duration of double jump ability in seconds ###
double_jump_timer = 0.0 ### NEW: Timer to track remaining double jump duration ###

### NEW: Score Multiplier Pickup Variables ###
MULTIPLIER_COLOR = (1.0, 0.5, 0.0)  # Orange
MULTIPLIER_SIZE = 15.0
MULTIPLIER_SPAWN_PROBABILITY = 0.05
MULTIPLIER_HOVER_HEIGHT = 30.0
score_multiplier = 1 
multiplier_timer = 0.0 
MULTIPLIER_DURATION = 5.0 
MULTIPLIER_FACTOR = 2 
MULTIPLIER_STROKE_THICKNESS = 0.15



# ---------- Globals ----------
WINDOW_W, WINDOW_H = 1000, 800
ASPECT = WINDOW_W / WINDOW_H

# Camera / projection
fovY = 80.0                   # you can widen this later for speed feel
camera_height = 120.0         # height above the floor
camera_distance = 250.0       # distance behind the ball

# World / Platform
FLOOR_Y = 0.0 # The Y-coordinate of the platform surface

# Platform generation variables
platform_segments = []
platform_segment_length = 200.0 # Length of a single platform segment along Z-axis
base_lane_width = 50.0          # Width of a single visual 'lane'
base_num_lanes = 5              # Default number of lanes (e.g., 5 lanes wide)
base_platform_total_width = base_lane_width * base_num_lanes 

### NEW: Boost Pad Variables ###
BOOST_PAD_COLOR = (1.0, 0.0, 1.0)  # Magenta
BOOST_PAD_LENGTH = platform_segment_length * 0.3  # 30% of segment length
BOOST_PAD_SPAWN_PROBABILITY = 0.05  # 5% chance to spawn on a segment
BOOST_PAD_SPEED_BOOST = 1.2 ### MODIFIED: Slight speed increase (1.2x) ###
is_boost_active = False 
boost_timer = 0.0 
BOOST_DURATION = 3.0 

num_visible_tiles = 15          # Number of segments to keep ahead of the player
last_platform_tile_z_end = 0.0  # Tracks the furthest Z-coordinate of the last generated tile
platform_thickness = 15.0       # Thickness of the platform to make it 3D
PLATFORM_Y_SNAP_TOLERANCE = 0.5
SEGMENT_GAP = 0.1


### NEW: Shield Power-up Variables ###
SHIELD_COLOR = (0.1, 0.4, 0.9)  # Blue for shield icon
SHIELD_SIZE = 18.0 # Size of the shield icon
SHIELD_SPAWN_PROBABILITY = 0.05 # 5% chance to spawn
SHIELD_HOVER_HEIGHT = 30.0

# Shield aura color and radius factor
SHIELD_AURA_COLOR = (0.2, 0.6, 1.0) ### NEW: Color for the aura ###
SHIELD_AURA_RADIUS_FACTOR = 1.2 ### NEW: Aura is 20% larger than ball ###

has_shield_active = False ### NEW: Player state for shield ###
shield_charge_count = 0 ### NEW: Number of shield charges ###
shield_timer = 0.0 ### NEW: Timer for shield duration ###
SHIELD_DURATION = 10.0 ### NEW: How long one shield charge lasts ###

# Visual effect for ball when shielded (simulated translucent aura)
SHIELD_EFFECT_COLOR_AURA = (0.2, 0.6, 1.0) ### NEW: Color for the aura ###
SHIELD_EFFECT_AURA_RADIUS_FACTOR = 1.2 ### NEW: Aura is 20% larger than ball ###
SHIELD_EFFECT_PULSE_SPEED = 4.0 ### NEW: Speed of aura pulsation ###


# NEW: Segment Configuration Constants (for readability)
CONFIG_NUM_LANES = 0
CONFIG_X_OFFSET = 1
CONFIG_Y_LEVEL = 2 # Always FLOOR_Y for this version (no slopes)

### CONSOLIDATED AND CORRECTED Segment Type Definitions (Updated IDs for uniqueness) ###
SEGMENT_TYPE_NORMAL_FULL_CENTERED = 0

# Basic Hazards
SEGMENT_TYPE_HOLES = 1                   # Full width, random holes
SEGMENT_TYPE_STATIC_OBSTACLES = 2        ### CRITICAL FIX: Defined this as STATIC_OBSTACLES_KEY in generate_platform_tile was a string literal###
SEGMENT_TYPE_MOVING_OBSTACLES = 3        # Full width, moving cylinder obstacles

# Width/Offset Changes (90-degree)
SEGMENT_TYPE_NARROW_CENTERED = 4         # Narrows to 3 lanes, centered
SEGMENT_TYPE_SHIFT_LEFT = 5              # Full width, shifted left
SEGMENT_TYPE_SHIFT_RIGHT = 6             # Full width, shifted right
SEGMENT_TYPE_NARROW_LEFT_ALIGNED = 7     # Narrows to 2 lanes, aligned left
SEGMENT_TYPE_NARROW_RIGHT_ALIGNED = 8    # Narrows to 2 lanes, aligned right
SEGMENT_TYPE_SINGLE_LANE_LEFT = 9        
SEGMENT_TYPE_SINGLE_LANE_RIGHT = 10      

# Blockades / Forced Paths
SEGMENT_TYPE_BLOCKADE_INNER_HOLE = 11     # Full width, large center hole
SEGMENT_TYPE_BLOCKADE_LEFT_PATH = 12      # Full width, blocks right side
SEGMENT_TYPE_BLOCKADE_RIGHT_PATH = 13     # Full width, blocks left side
SEGMENT_TYPE_STAGGERED_BLOCKS = 14       # Full width, alternating left/right single blockers
SEGMENT_TYPE_FUNNEL = 15                 # Full width, blocks outer lanes, forces center
SEGMENT_TYPE_REVERSE_FUNNEL = 16         # Expands from narrow to wide
SEGMENT_TYPE_SAFE_LANE_RANDOM = 17       # Full width, only one random safe lane

# More Complex / Fused / Bizarre Variations
SEGMENT_TYPE_DEATH_GRID = 18             # Full width, checkerboard holes
SEGMENT_TYPE_SPLIT_DECISION_HOLE = 19    # Full width, large central hole implying two paths
SEGMENT_TYPE_CHOKE_POINT_SINGLE_LANE = 20 # Narrows aggressively to a single center lane
SEGMENT_TYPE_SHIFT_LEFT_WITH_OBSTACLE = 21 # Shifted left, with a static obstacle on it
SEGMENT_TYPE_SHIFT_RIGHT_WITH_OBSTACLE = 22 # Shifted right, with a static obstacle on it
SEGMENT_TYPE_NARROW_CENTER_WITH_HOLES = 23 # Narrow center, with holes inside
SEGMENT_TYPE_NARROW_BEAM_CENTER = 24       # Very narrow 1-lane path, centered (Used for visual type)


# NEW: Initial Safe Segments
INITIAL_SAFE_SEGMENTS_COUNT = 3
segments_until_hazards_start = 0 

# NEW: Parameters for variations
SEGMENT_VARIATION_PROBABILITY = 0.7 # Overall chance for a segment to NOT be normal
# Holes
HOLE_PROBABILITY_PER_LANE = 0.15 
MIN_SEGMENTS_BETWEEN_HOLES = 3
segments_since_last_hole = 0

# Static Obstacles
MIN_SEGMENTS_BETWEEN_OBSTACLES = 2
segments_since_last_obstacle = 0

# Moving Obstacles
MOVING_OBSTACLE_PROBABILITY = 0.25 # This will now be a hazard choice
MOVING_OBSTACLE_SPEED = 150.0 
MOVING_OBSTACLE_RADIUS = base_lane_width * 0.4
MOVING_OBSTACLE_HEIGHT = base_lane_width * 0.8
MIN_SEGMENTS_BETWEEN_MOVING_OBSTACLES = 2
segments_since_last_moving_obstacle = 0

# Narrowing/Shifting Specifics
NARROW_LANES_COUNT = 3 # For SEGMENT_TYPE_NARROW_CENTERED, NARROW_CENTER_WITH_HOLES
NARROW_ALIGNED_LANES_COUNT = 2 # For SEGMENT_TYPE_NARROW_LEFT/RIGHT_ALIGNED
SINGLE_LANE_COUNT = 1 # For SEGMENT_TYPE_SINGLE_LANE_LEFT/RIGHT, and NARROW_BEAM_CENTER
PLATFORM_SHIFT_AMOUNT = base_lane_width * 1.5 # For SEGMENT_TYPE_SHIFT_LEFT/RIGHT

# Player (ball)
ball_radius = 20.0
ball_pos = [0.0, FLOOR_Y + ball_radius, -100.0]
forward_speed = -500.0  # units per second (toward -Z)
last_time_ms = None  # for delta time
ball_lateral_speed = 300.0 # Lateral speed in units/sec, applied in idle
ball_rotation_angle = 0.0
BALL_COLOR_FLAT = (0.0, 0.4, 1.0) ### NEW: Define a flat color for the ball ###

### NEW: Game State Management (Enum-like) ###
STATE_PLAYING = 0
STATE_ANIMATING_DEATH = 1
STATE_GAME_OVER = 2
game_state = STATE_PLAYING ### NEW: Current state of the game ###

# Game State Flags
is_falling = False
game_over = False
is_grounded = True 
is_breaking_animation_active = False
is_obstacle_breaking_active = False


# Physics variables for falling
fall_velocity_x = 0.0
fall_velocity_y = 0.0
fall_threshold_y = FLOOR_Y - 50.0
GRAVITY = -1500.0 
JUMP_STRENGTH = 550.0 

### NEW: Point Pulsation Variables ###
point_pulse_scale = 1.0 # Current scale factor for pulsation
point_pulse_time = 0.0 # Accumulator for pulse animation timing
point_hover_offset = 0.0 ### NEW: Global variable for hover animation ###
POINT_PULSE_SPEED = 3.0 # Increased speed for more noticeable pulsation
POINT_PULSE_MIN_SCALE = 0.6 # Decreased min size for more dramatic effect
POINT_PULSE_MAX_SCALE = 1.4 # Increased max size for more dramatic effect

### NEW: Ball Breaking Animation Variables ###
breaking_particles = [] # List to hold particle dictionaries
NUM_BREAKING_PARTICLES = 30
PARTICLE_LIFETIME = 0.8 # Seconds
PARTICLE_INITIAL_SPEED_MAX = 300.0 # Max initial velocity for explosion
PARTICLE_SIZE_MAX_FACTOR = 0.3 # Max size of a particle relative to ball_radius
BALL_EXPLOSION_COLOR = (1.0, 0.5, 0.0) # E.g., orange/red for explosion
animation_timer = 0.0 # Countdown for the animation
death_animation_timer = 0.0 ### NEW: Timer for the death animation ###

# Platform colors
DARK_BLUE = (0.1, 0.1, 0.4)
MID_BLUE = (0.15, 0.15, 0.5)
GRID_CYAN = (0.0, 0.8, 0.8)
DARK_BLUE_SIDE = (DARK_BLUE[0]*0.7, DARK_BLUE[1]*0.7, DARK_BLUE[2]*0.7)
MID_BLUE_SIDE = (MID_BLUE[0]*0.7, MID_BLUE[1]*0.7, MID_BLUE[2]*0.7)
SHADOW_COLOR = (0.0, 0.0, 0.0)
HOLE_COLOR = (1.0, 0.1, 0.1) 
OBSTACLE_COLOR = (1.0, 1.0, 0.0)
MOVING_OBSTACLE_COLOR = (0.7, 0.2, 0.8) # Purple cylinder


# Background Elements Variables (Starfield)
background_elements_distant = []
NUM_BG_ELEMENTS_DISTANT = 300
BG_SCROLL_FACTOR_DISTANT = 0.1

background_elements_mid = []
NUM_BG_ELEMENTS_MID = 100
BG_SCROLL_FACTOR_MID = 0.4

BG_X_RANGE = 1500.0
BG_Y_RANGE = 1000.0
BG_Z_ACTIVE_RANGE = 4000.0

BG_MIN_SIZE = 3.0
BG_MAX_SIZE = 15.0

BG_COLOR_BASE1 = (0.2, 0.0, 0.3)
BG_COLOR_BASE2 = (0.1, 0.1, 0.6)
BACKGROUND_MOVE_SPEED = 100.0

# Key State Tracking System
keys_pressed = {}

# Create a single, reusable quadric object for the ball
ball_quadric = gluNewQuadric()

# Create a single, reusable quadric object for the ball
ball_quadric = gluNewQuadric()

# Create a single, reusable quadric object for the ball
ball_quadric = gluNewQuadric()

# Utility (text)
def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_W, 0, WINDOW_H)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

# ---------- Input ----------
    
def keyboardListener(key, x, y): ### CRITICAL FIX: Double Jump Activation ###
    """
    Records when a key is pressed down. Handles game reset and jump.
    """
    global keys_pressed, is_grounded, fall_velocity_y, game_state
    global has_double_jump_charge # Access has_double_jump_charge

    # --- Handle Game Reset ---
    if key == b'r' and game_state == STATE_GAME_OVER:
        reset_ball()
        return 

    # --- Handle Jump (only in PLAYING state) ---
    if game_state == STATE_PLAYING:
        if key == b' ':
            if is_grounded: # First jump from ground
                is_grounded = False 
                fall_velocity_y = JUMP_STRENGTH 
            elif not is_grounded and has_double_jump_charge: # Second jump while in air
                fall_velocity_y = JUMP_STRENGTH * 0.8 # CRITICAL FIX: Re-apply velocity
                has_double_jump_charge = False # Consume charge
                # is_falling remains True if it was falling
        
    keys_pressed[key] = True

  

def keyboardUpListener(key, x, y):
    global keys_pressed
    keys_pressed[key] = False

def specialKeyListener(key, x, y):
    pass

def mouseListener(button, state, x, y):
    pass

# ---------- Camera ----------
def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, ASPECT, 2.0, 3000.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    bx, by, bz = ball_pos
    cx, cy, cz = bx, by + camera_height, bz + camera_distance
    gluLookAt(cx, cy, cz,  bx, by, bz,  0, 1, 0)


# Helper to get absolute X boundaries for a lane configuration
def get_full_lane_x_coords(num_lanes_block, x_center_offset):
    active_block_width = num_lanes_block * base_lane_width
    x_left_edge = x_center_offset - (active_block_width / 2.0)
    x_right_edge = x_center_offset + (active_block_width / 2.0)
    return x_left_edge, x_right_edge

def generate_platform_tile(last_segment=None): ### CRITICAL FIX: UnboundLocalError and Consolidated Spawning ###
    """
    Generates a new platform segment. Hazards (holes, static obstacles, moving obstacles)
    are now applied based on spacing counters and valid choices,
    with an initial grace period for safe segments.
    """
    global last_platform_tile_z_end, segments_since_last_hole, segments_since_last_obstacle, segments_since_last_moving_obstacle
    global segments_until_hazards_start # Access the global counter
    
    start_z = last_platform_tile_z_end 
    end_z = start_z - platform_segment_length - SEGMENT_GAP 

    if last_segment:
        last_config = last_segment['config']
    else: # Initial segment - always normal, centered, flat
        last_config = [base_num_lanes, 0.0, FLOOR_Y]

    new_config = list(last_config)
    hole_lanes = []
    obstacles = [] # Static cube obstacles
    moving_obstacles = [] # Moving cylinder obstacles
    points = [] 
    
    double_jump_powerups = [] 
    multiplier_pickups = [] 
    boost_pads = [] 
    shields = [] ### NEW ###

    segment_type = SEGMENT_TYPE_NORMAL_FULL_CENTERED

    is_hole_based_hazard = False
    is_static_obstacle_hazard = False
    is_moving_obstacle_hazard = False

    force_no_hazards_this_segment = False
    if segments_until_hazards_start > 0:
        force_no_hazards_this_segment = True
        segments_until_hazards_start -= 1

    current_num_lanes = last_config[CONFIG_NUM_LANES]
    current_x_offset = last_config[CONFIG_X_OFFSET]
    
    shape_choices = ['NORMAL']
    if current_num_lanes == base_num_lanes and current_x_offset == 0.0 and not force_no_hazards_this_segment:
        shape_choices.extend(['NARROW_CENTER', 'NARROW_LEFT', 'NARROW_RIGHT', 'SHIFT_LEFT', 'SHIFT_RIGHT',
                              'SINGLE_LANE_LEFT', 'SINGLE_LANE_RIGHT'])
    elif (current_num_lanes < base_num_lanes or current_x_offset != 0.0) and not force_no_hazards_this_segment:
        shape_choices.append('NORMAL')
    
    chosen_shape = random.choice(shape_choices)
    
    if force_no_hazards_this_segment:
        chosen_shape = 'NORMAL'

    if chosen_shape == 'NORMAL':
        new_config[CONFIG_NUM_LANES] = base_num_lanes
        new_config[CONFIG_X_OFFSET] = 0.0
        segment_type = SEGMENT_TYPE_NORMAL_FULL_CENTERED
    elif chosen_shape == 'NARROW_CENTER':
        new_config[CONFIG_NUM_LANES] = NARROW_LANES_COUNT
        new_config[CONFIG_X_OFFSET] = 0.0
        segment_type = SEGMENT_TYPE_NARROW_CENTERED
    elif chosen_shape == 'NARROW_LEFT':
        new_config[CONFIG_NUM_LANES] = NARROW_ALIGNED_LANES_COUNT
        base_half_width = (base_num_lanes * base_lane_width) / 2.0
        new_half_width = (NARROW_ALIGNED_LANES_COUNT * base_lane_width) / 2.0
        new_config[CONFIG_X_OFFSET] = -base_half_width + new_half_width
        segment_type = SEGMENT_TYPE_NARROW_LEFT_ALIGNED
    elif chosen_shape == 'NARROW_RIGHT':
        new_config[CONFIG_NUM_LANES] = NARROW_ALIGNED_LANES_COUNT
        base_half_width = (base_num_lanes * base_lane_width) / 2.0
        new_half_width = (NARROW_ALIGNED_LANES_COUNT * base_lane_width) / 2.0
        new_config[CONFIG_X_OFFSET] = base_half_width - new_half_width
        segment_type = SEGMENT_TYPE_NARROW_RIGHT_ALIGNED
    elif chosen_shape == 'SHIFT_LEFT':
        new_config[CONFIG_NUM_LANES] = base_num_lanes
        new_config[CONFIG_X_OFFSET] -= PLATFORM_SHIFT_AMOUNT
        segment_type = SEGMENT_TYPE_SHIFT_LEFT
    elif chosen_shape == 'SHIFT_RIGHT':
        new_config[CONFIG_NUM_LANES] = base_num_lanes
        new_config[CONFIG_X_OFFSET] += PLATFORM_SHIFT_AMOUNT
        segment_type = SEGMENT_TYPE_SHIFT_RIGHT
    elif chosen_shape == 'SINGLE_LANE_LEFT':
        new_config[CONFIG_NUM_LANES] = SINGLE_LANE_COUNT
        new_config[CONFIG_X_OFFSET] = -base_platform_total_width / 2.0 + (SINGLE_LANE_COUNT * base_lane_width / 2.0)
        segment_type = SEGMENT_TYPE_SINGLE_LANE_LEFT
    elif chosen_shape == 'SINGLE_LANE_RIGHT':
        new_config[CONFIG_NUM_LANES] = SINGLE_LANE_COUNT
        new_config[CONFIG_X_OFFSET] = base_platform_total_width / 2.0 - (SINGLE_LANE_COUNT * base_lane_width / 2.0)
        segment_type = SEGMENT_TYPE_SINGLE_LANE_RIGHT


    # --- Step 2: If the segment is a standard full-width path, potentially add a HAZARD ---
    
    can_add_hazards = (new_config[CONFIG_NUM_LANES] == base_num_lanes and 
                       new_config[CONFIG_X_OFFSET] == 0.0 and 
                       not force_no_hazards_this_segment)
    
    if can_add_hazards:
        can_have_holes = segments_since_last_hole >= MIN_SEGMENTS_BETWEEN_HOLES
        can_have_static_obstacles = segments_since_last_obstacle >= MIN_SEGMENTS_BETWEEN_OBSTACLES
        can_have_moving_obstacles = segments_since_last_moving_obstacle >= MIN_SEGMENTS_BETWEEN_MOVING_OBSTACLES
        
        hazard_choices = [None] 
        if can_have_holes:
            hazard_choices.extend([
                SEGMENT_TYPE_HOLES, SEGMENT_TYPE_BLOCKADE_INNER_HOLE,
                SEGMENT_TYPE_BLOCKADE_RIGHT_PATH, SEGMENT_TYPE_BLOCKADE_LEFT_PATH,
                SEGMENT_TYPE_STAGGERED_BLOCKS, SEGMENT_TYPE_FUNNEL,
                SEGMENT_TYPE_SAFE_LANE_RANDOM, SEGMENT_TYPE_DEATH_GRID
            ])
        if can_have_static_obstacles:
            hazard_choices.append(SEGMENT_TYPE_STATIC_OBSTACLES) 
        if can_have_moving_obstacles:
            hazard_choices.append(SEGMENT_TYPE_MOVING_OBSTACLES) 
        
        chosen_hazard_key = random.choice(hazard_choices)
        
        if chosen_hazard_key is not None:
            if chosen_hazard_key == SEGMENT_TYPE_STATIC_OBSTACLES: 
                segment_type = SEGMENT_TYPE_STATIC_OBSTACLES 
                is_static_obstacle_hazard = True
                num_obstacles = random.randint(1, 2)
                available_lanes = list(range(new_config[CONFIG_NUM_LANES])) 
                for _ in range(num_obstacles):
                    if not available_lanes: break
                    lane = random.choice(available_lanes)
                    available_lanes.remove(lane)
                    obstacle = {
                        'lane_index': lane,
                        'z_pos_factor': random.uniform(0.2, 0.8),
                        'size': base_lane_width * 0.8,
                        'world_x': 0.0, 'world_y_top': 0.0, 'world_z': 0.0
                    }
                    obstacles.append(obstacle)
                
                for obs_idx, obs in enumerate(obstacles):
                    obs_x_center = new_config[CONFIG_X_OFFSET] - (new_config[CONFIG_NUM_LANES] * base_lane_width / 2.0) + \
                                   (obs['lane_index'] * base_lane_width) + (base_lane_width / 2.0)
                    obs_y_center = FLOOR_Y + obs['size'] / 2.0
                    obs_z_center = start_z + (end_z - start_z) * obs['z_pos_factor']
                    
                    obstacles[obs_idx]['world_x'] = obs_x_center
                    obstacles[obs_idx]['world_y_top'] = obs_y_center + obs['size'] / 2.0
                    obstacles[obs_idx]['world_z'] = obs_z_center
            
            elif chosen_hazard_key == SEGMENT_TYPE_MOVING_OBSTACLES: 
                segment_type = SEGMENT_TYPE_MOVING_OBSTACLES 
                is_moving_obstacle_hazard = True
                initial_x_absolute = random.uniform(-base_platform_total_width/2.0 + MOVING_OBSTACLE_RADIUS,
                                                    base_platform_total_width/2.0 - MOVING_OBSTACLE_RADIUS)
                
                moving_obstacle = {
                    'x_pos_current_absolute': initial_x_absolute,
                    'z_pos_factor': random.uniform(0.2, 0.8), 
                    'direction': random.choice([-1, 1]) 
                }
                moving_obstacles.append(moving_obstacle)

            else: 
                segment_type = chosen_hazard_key 
                is_hole_based_hazard = True
                if chosen_hazard_key == SEGMENT_TYPE_HOLES:
                    max_holes = 2
                    num_holes_to_create = random.randint(1, max_holes)
                    hole_lanes = random.sample(range(new_config[CONFIG_NUM_LANES]), num_holes_to_create)
                elif chosen_hazard_key == SEGMENT_TYPE_BLOCKADE_INNER_HOLE:
                    if new_config[CONFIG_NUM_LANES] >= 3: hole_lanes.append(int(new_config[CONFIG_NUM_LANES] / 2))
                elif chosen_hazard_key == SEGMENT_TYPE_BLOCKADE_RIGHT_PATH:
                    hole_lanes = [i for i in range(new_config[CONFIG_NUM_LANES]) if i < new_config[CONFIG_NUM_LANES] - (base_num_lanes - 2)]
                elif chosen_hazard_key == SEGMENT_TYPE_BLOCKADE_LEFT_PATH:
                    hole_lanes = [i for i in range(new_config[CONFIG_NUM_LANES]) if i >= (base_num_lanes - 2)]
                elif chosen_hazard_key == SEGMENT_TYPE_STAGGERED_BLOCKS:
                    hole_lanes.append(random.choice([0, new_config[CONFIG_NUM_LANES] - 1]))
                elif chosen_hazard_key == SEGMENT_TYPE_FUNNEL:
                    if new_config[CONFIG_NUM_LANES] == 5: hole_lanes.extend([0, 1, 3, 4])
                    else: hole_lanes.extend([0, new_config[CONFIG_NUM_LANES] - 1])
                elif chosen_hazard_key == SEGMENT_TYPE_SAFE_LANE_RANDOM:
                    safe_lane = random.randint(0, new_config[CONFIG_NUM_LANES] - 1)
                    for i in range(new_config[CONFIG_NUM_LANES]):
                        if i != safe_lane: hole_lanes.append(i)
                elif chosen_hazard_key == SEGMENT_TYPE_DEATH_GRID:
                    start_hole = random.randint(0,1)
                    for i in range(new_config[CONFIG_NUM_LANES]):
                        if i % 2 == start_hole: hole_lanes.append(i)
        
    # --- Update Hazard Counters ---
    if is_hole_based_hazard:
        segments_since_last_hole = 0
    else:
        segments_since_last_hole += 1
    
    if is_static_obstacle_hazard:
        segments_since_last_obstacle = 0
    else:
        segments_since_last_obstacle += 1
    
    if is_moving_obstacle_hazard:
        segments_since_last_moving_obstacle = 0
    else:
        segments_since_last_moving_obstacle += 1

    # --- Collectible Spawning (Consolidated for uniqueness) ---
    points = []
    
    can_add_collectibles = True # Flag to control if any collectible can spawn
    if not force_no_hazards_this_segment: # Only spawn collectibles if not in a safe initial segment
        # Get available safe lanes (not holes, not occupied by static obstacles)
        num_lanes_current_seg = new_config[CONFIG_NUM_LANES]
        x_offset_current_seg = new_config[CONFIG_X_OFFSET]
        safe_lanes_for_collectible_placement = [i for i in range(num_lanes_current_seg) if i not in hole_lanes]
        if obstacles: 
            obstacle_lanes = [obs['lane_index'] for obs in obstacles]
            safe_lanes_for_collectible_placement = [lane for lane in safe_lanes_for_collectible_placement if lane not in obstacle_lanes]
        
        # If no safe lanes, no collectibles can spawn
        if not safe_lanes_for_collectible_placement:
            can_add_collectibles = False

        if can_add_collectibles:
            collectible_type_to_spawn = None

            # Decide which type of collectible to spawn (priority: Shield > Boost > Multiplier > DoubleJump > Points)
            if random.random() < SHIELD_SPAWN_PROBABILITY: ### NEW: Shield spawning check ###
                collectible_type_to_spawn = 'SHIELD'
            elif random.random() < BOOST_PAD_SPAWN_PROBABILITY:
                collectible_type_to_spawn = 'BOOST_PAD'
            elif random.random() < MULTIPLIER_SPAWN_PROBABILITY:
                collectible_type_to_spawn = 'MULTIPLIER'
            elif random.random() < DOUBLE_JUMP_SPAWN_PROBABILITY:
                collectible_type_to_spawn = 'DOUBLE_JUMP'
            elif random.random() < POINT_SPAWN_PROBABILITY_PER_SEGMENT:
                collectible_type_to_spawn = 'POINT'
                
            # Now, try to spawn the chosen collectible
            if collectible_type_to_spawn:
                # Common logic to get a spawn lane for tile-based pickups
                chosen_lane_idx = random.choice(safe_lanes_for_collectible_placement)
                playable_x_left = x_offset_current_seg - (num_lanes_current_seg * base_lane_width / 2.0)
                collectible_x = playable_x_left + (chosen_lane_idx * base_lane_width) + (base_lane_width / 2.0)
                z_pos_factor = random.uniform(0.2, 0.8)
                collectible_z = start_z + (end_z - start_z) * z_pos_factor

                if collectible_type_to_spawn == 'POINT':
                    spawn_on_obstacle_chance = True if obstacles and random.choice([True,False]) else False
                    if spawn_on_obstacle_chance:
                        chosen_obstacle = random.choice(obstacles)
                        point = {
                            'x': chosen_obstacle['world_x'],
                            'y': chosen_obstacle['world_y_top'] + POINT_HOVER_HEIGHT,
                            'z': chosen_obstacle['world_z'],
                            'type': POINT_TYPE_OBSTACLE,
                            'color': POINT_COLOR
                        }
                    else: 
                        point = {
                            'x': collectible_x,
                            'y': FLOOR_Y + POINT_HOVER_HEIGHT,
                            'z': collectible_z,
                            'type': POINT_TYPE_TILE,
                            'color': POINT_COLOR
                        }
                    points.append(point)
                
                elif collectible_type_to_spawn == 'DOUBLE_JUMP':
                    powerup = {
                        'x': collectible_x,
                        'y': FLOOR_Y + DOUBLE_JUMP_HOVER_HEIGHT,
                        'z': collectible_z,
                        'color': DOUBLE_JUMP_COLOR
                    }
                    double_jump_powerups.append(powerup)

                elif collectible_type_to_spawn == 'MULTIPLIER':
                    pickup = {
                        'x': collectible_x,
                        'y': FLOOR_Y + MULTIPLIER_HOVER_HEIGHT,
                        'z': collectible_z,
                        'color': MULTIPLIER_COLOR
                    }
                    multiplier_pickups.append(pickup)

                elif collectible_type_to_spawn == 'BOOST_PAD':
                    num_boost_lanes = random.randint(1, min(2, len(safe_lanes_for_collectible_placement)))
                    boost_lanes_for_pad = random.sample(safe_lanes_for_collectible_placement, num_boost_lanes)
                    
                    for lane_idx_for_pad in boost_lanes_for_pad:
                        z_pos_factor_pad = random.uniform(0.2, 0.7)
                        z_center_pad = start_z + (end_z - start_z) * z_pos_factor_pad
                        z_start_pad = z_center_pad - (BOOST_PAD_LENGTH / 2)
                        z_end_pad = z_center_pad + (BOOST_PAD_LENGTH / 2)
                        
                        boost_pad = {
                            'lane_idx': lane_idx_for_pad,
                            'z_start': z_start_pad,
                            'z_end': z_end_pad,
                            'active': True 
                        }
                        boost_pads.append(boost_pad)
                
                elif collectible_type_to_spawn == 'SHIELD':
                    shield_icon = {
                        'x': collectible_x,
                        'y': FLOOR_Y + SHIELD_HOVER_HEIGHT,
                        'z': collectible_z,
                        'color': SHIELD_COLOR
                    }
                    shields.append(shield_icon)
    
    # --- Create the segment dictionary ---
    tile = {
        'start_z': start_z,
        'end_z': end_z,
        'config': new_config,
        'hole_lanes': hole_lanes,
        'obstacles': obstacles,
        'moving_obstacles': moving_obstacles,
        'points': points,
        'double_jump_powerups': double_jump_powerups, ### NEW ###
        'multiplier_pickups': multiplier_pickups, ### NEW ###
        'boost_pads': boost_pads, ### NEW ###
        'shields': shields, ### NEW ###
        'segment_type': segment_type,
        'debug_text': f"T:{segment_type} L:{new_config[CONFIG_NUM_LANES]} O:{new_config[CONFIG_X_OFFSET]:.0f}"
    }
    
    platform_segments.append(tile)
    last_platform_tile_z_end = end_z


def draw_platform_tiled(): ### MODIFIED: Removed glLineWidth ###
    """
    Draws the procedurally generated platform and any obstacles on it.
    Grid lines are drawn over the entire platform area, while solid tiles are drawn individually.
    """
    grid_density_z = 3
    for segment_idx, tile in enumerate(platform_segments):
        num_lanes, x_offset, y_level = tile['config']
        y_bottom = y_level - platform_thickness
        x_left, x_right = get_full_lane_x_coords(num_lanes, x_offset)
        
        # Display debug text for the first segment
        if segment_idx == 0: 
            draw_text(10, WINDOW_H - 90, tile['debug_text'])
        
        # --- Draw Each SOLID Lane Individually (Top, Sides, Bottom) ---
        for lane_idx in range(num_lanes):
            # Skip drawing ANY 3D geometry for hole lanes
            if lane_idx in tile['hole_lanes']:
                continue
                
            # Calculate lane coordinates
            lane_x_left = x_left + (lane_idx * base_lane_width)
            lane_x_right = lane_x_left + base_lane_width
            
            # --- Draw Top Surface with checkerboard pattern ---
            if (segment_idx + lane_idx) % 2 == 0: 
                glColor3f(DARK_BLUE[0], DARK_BLUE[1], DARK_BLUE[2])
            else: 
                glColor3f(MID_BLUE[0], MID_BLUE[1], MID_BLUE[2])
            
            glBegin(GL_QUADS)
            # Top face
            glVertex3f(lane_x_left,  y_level, tile['start_z'])
            glVertex3f(lane_x_right, y_level, tile['start_z'])
            glVertex3f(lane_x_right, y_level, tile['end_z'])
            glVertex3f(lane_x_left,  y_level, tile['end_z'])
            glEnd()
            
            # --- Draw Side Walls and Bottom for THIS solid lane ---
            glColor3f(DARK_BLUE_SIDE[0], DARK_BLUE_SIDE[1], DARK_BLUE_SIDE[2])
            glBegin(GL_QUADS)
            
            # Left side wall (only if this is the leftmost lane or adjacent left lane is a hole)
            if lane_idx == 0 or (lane_idx - 1) in tile['hole_lanes']:
                glVertex3f(lane_x_left, y_level,  tile['start_z'])
                glVertex3f(lane_x_left, y_level,  tile['end_z'])
                glVertex3f(lane_x_left, y_bottom, tile['end_z'])
                glVertex3f(lane_x_left, y_bottom, tile['start_z'])
            
            # Right side wall (only if this is the rightmost lane or adjacent right lane is a hole)
            if lane_idx == num_lanes - 1 or (lane_idx + 1) in tile['hole_lanes']:
                glVertex3f(lane_x_right, y_level,  tile['start_z'])
                glVertex3f(lane_x_right, y_level,  tile['end_z'])
                glVertex3f(lane_x_right, y_bottom, tile['end_z'])
                glVertex3f(lane_x_right, y_bottom, tile['start_z'])
            
            # Front face (always drawn for solid lanes at the segment's start_z)
            glVertex3f(lane_x_left,  y_level,  tile['start_z'])
            glVertex3f(lane_x_right, y_level,  tile['start_z'])
            glVertex3f(lane_x_right, y_bottom, tile['start_z'])
            glVertex3f(lane_x_left,  y_bottom, tile['start_z'])
            
            # Back face (always drawn for solid lanes at the segment's end_z)
            glVertex3f(lane_x_left,  y_level,  tile['end_z'])
            glVertex3f(lane_x_right, y_level,  tile['end_z'])
            glVertex3f(lane_x_right, y_bottom, tile['end_z'])
            glVertex3f(lane_x_left,  y_bottom, tile['end_z'])
            glEnd()
            
            # Bottom face of this lane
            glColor3f(MID_BLUE_SIDE[0], MID_BLUE_SIDE[1], MID_BLUE_SIDE[2])
            glBegin(GL_QUADS)
            glVertex3f(lane_x_left,  y_bottom, tile['start_z'])
            glVertex3f(lane_x_right, y_bottom, tile['start_z'])
            glVertex3f(lane_x_right, y_bottom, tile['end_z'])
            glVertex3f(lane_x_left,  y_bottom, tile['end_z'])
            glEnd()
        
        ### Draw Static Obstacles ###
        if tile.get('obstacles'):
            glColor3f(OBSTACLE_COLOR[0], OBSTACLE_COLOR[1], OBSTACLE_COLOR[2])
            for obstacle_idx, obstacle in enumerate(tile['obstacles']): 
                obs_lane_idx = obstacle['lane_index']
                obs_z_factor = obstacle['z_pos_factor']
                obs_size = obstacle['size']

                obs_x_center = x_left + (obs_lane_idx * base_lane_width) + (base_lane_width / 2.0)
                obs_y_center = y_level + obs_size / 2.0
                obs_z_center = tile['start_z'] + (tile['end_z'] - tile['start_z']) * obs_z_factor
                
                glPushMatrix()
                glTranslatef(obs_x_center, obs_y_center, obs_z_center)
                glutSolidCube(obs_size)
                glPopMatrix()

                obstacle['world_x'] = obs_x_center
                obstacle['world_y_top'] = obs_y_center + obs_size / 2.0
                obstacle['world_z'] = obs_z_center

        ### Draw Moving Obstacles (Cylinders) - Vertical ###
        if tile.get('moving_obstacles'):
            glColor3f(MOVING_OBSTACLE_COLOR[0], MOVING_OBSTACLE_COLOR[1], MOVING_OBSTACLE_COLOR[2])
            
            for mobstacle in tile['moving_obstacles']:
                mob_z_factor = mobstacle['z_pos_factor']
                mob_x_current_absolute = mobstacle['x_pos_current_absolute']

                mob_y_center = y_level + MOVING_OBSTACLE_HEIGHT / 2.0 
                mob_z_center = tile['start_z'] + (tile['end_z'] - tile['start_z']) * mob_z_factor
                
                glPushMatrix()
                glTranslatef(mob_x_current_absolute, mob_y_center - MOVING_OBSTACLE_HEIGHT/2.0, mob_z_center)
                glRotatef(-90, 1, 0, 0) # Corrected rotation to face up
                gluCylinder(ball_quadric, MOVING_OBSTACLE_RADIUS, MOVING_OBSTACLE_RADIUS, MOVING_OBSTACLE_HEIGHT, 16, 1)
                
                glPushMatrix()
                glTranslatef(0, 0, MOVING_OBSTACLE_HEIGHT)
                gluDisk(ball_quadric, 0, MOVING_OBSTACLE_RADIUS, 16, 1)
                glPopMatrix()

                gluDisk(ball_quadric, 0, MOVING_OBSTACLE_RADIUS, 16, 1)
                
                glPopMatrix()

        # --- Draw Grid Lines (always drawn over the full platform area) ---
        glColor3f(GRID_CYAN[0], GRID_CYAN[1], GRID_CYAN[2])
        # REMOVED: glLineWidth(1.0) # Removed for strict compliance
        glBegin(GL_LINES)
        
        # Draw vertical grid lines (lane boundaries)
        for i in range(num_lanes + 1):
            line_x = x_left + (i * base_lane_width)
            glVertex3f(line_x, y_level + 0.1, tile['start_z'])
            glVertex3f(line_x, y_level + 0.1, tile['end_z'])
        
        # Horizontal grid lines
        for i in range(grid_density_z + 1):
            current_z = tile['start_z'] - ((i / grid_density_z) * platform_segment_length)
            glVertex3f(x_left,  y_level + 0.1, current_z)
            glVertex3f(x_right, y_level + 0.1, current_z)
        
        glEnd()

def draw_platform_tiled(): ### MODIFIED: Removed glLineWidth ###
    """
    Draws the procedurally generated platform and any obstacles on it.
    Grid lines are drawn over the entire platform area, while solid tiles are drawn individually.
    """
    grid_density_z = 3
    for segment_idx, tile in enumerate(platform_segments):
        num_lanes, x_offset, y_level = tile['config']
        y_bottom = y_level - platform_thickness
        x_left, x_right = get_full_lane_x_coords(num_lanes, x_offset)
        
        # Display debug text for the first segment
        if segment_idx == 0: 
            draw_text(10, WINDOW_H - 90, tile['debug_text'])
        
        # --- Draw Each SOLID Lane Individually (Top, Sides, Bottom) ---
        for lane_idx in range(num_lanes):
            # Skip drawing ANY 3D geometry for hole lanes
            if lane_idx in tile['hole_lanes']:
                continue
                
            # Calculate lane coordinates
            lane_x_left = x_left + (lane_idx * base_lane_width)
            lane_x_right = lane_x_left + base_lane_width
            
            # --- Draw Top Surface with checkerboard pattern ---
            if (segment_idx + lane_idx) % 2 == 0: 
                glColor3f(DARK_BLUE[0], DARK_BLUE[1], DARK_BLUE[2])
            else: 
                glColor3f(MID_BLUE[0], MID_BLUE[1], MID_BLUE[2])
            
            glBegin(GL_QUADS)
            # Top face
            glVertex3f(lane_x_left,  y_level, tile['start_z'])
            glVertex3f(lane_x_right, y_level, tile['start_z'])
            glVertex3f(lane_x_right, y_level, tile['end_z'])
            glVertex3f(lane_x_left,  y_level, tile['end_z'])
            glEnd()
            
            # --- Draw Side Walls and Bottom for THIS solid lane ---
            glColor3f(DARK_BLUE_SIDE[0], DARK_BLUE_SIDE[1], DARK_BLUE_SIDE[2])
            glBegin(GL_QUADS)
            
            # Left side wall (only if this is the leftmost lane or adjacent left lane is a hole)
            if lane_idx == 0 or (lane_idx - 1) in tile['hole_lanes']:
                glVertex3f(lane_x_left, y_level,  tile['start_z'])
                glVertex3f(lane_x_left, y_level,  tile['end_z'])
                glVertex3f(lane_x_left, y_bottom, tile['end_z'])
                glVertex3f(lane_x_left, y_bottom, tile['start_z'])
            
            # Right side wall (only if this is the rightmost lane or adjacent right lane is a hole)
            if lane_idx == num_lanes - 1 or (lane_idx + 1) in tile['hole_lanes']:
                glVertex3f(lane_x_right, y_level,  tile['start_z'])
                glVertex3f(lane_x_right, y_level,  tile['end_z'])
                glVertex3f(lane_x_right, y_bottom, tile['end_z'])
                glVertex3f(lane_x_right, y_bottom, tile['start_z'])
            
            # Front face (always drawn for solid lanes at the segment's start_z)
            glVertex3f(lane_x_left,  y_level,  tile['start_z'])
            glVertex3f(lane_x_right, y_level,  tile['start_z'])
            glVertex3f(lane_x_right, y_bottom, tile['start_z'])
            glVertex3f(lane_x_left,  y_bottom, tile['start_z'])
            
            # Back face (always drawn for solid lanes at the segment's end_z)
            glVertex3f(lane_x_left,  y_level,  tile['end_z'])
            glVertex3f(lane_x_right, y_level,  tile['end_z'])
            glVertex3f(lane_x_right, y_bottom, tile['end_z'])
            glVertex3f(lane_x_left,  y_bottom, tile['end_z'])
            glEnd()
            
            # Bottom face of this lane
            glColor3f(MID_BLUE_SIDE[0], MID_BLUE_SIDE[1], MID_BLUE_SIDE[2])
            glBegin(GL_QUADS)
            glVertex3f(lane_x_left,  y_bottom, tile['start_z'])
            glVertex3f(lane_x_right, y_bottom, tile['start_z'])
            glVertex3f(lane_x_right, y_bottom, tile['end_z'])
            glVertex3f(lane_x_left,  y_bottom, tile['end_z'])
            glEnd()
        
        ### Draw Static Obstacles ###
        if tile.get('obstacles'):
            glColor3f(OBSTACLE_COLOR[0], OBSTACLE_COLOR[1], OBSTACLE_COLOR[2])
            for obstacle_idx, obstacle in enumerate(tile['obstacles']): 
                obs_lane_idx = obstacle['lane_index']
                obs_z_factor = obstacle['z_pos_factor']
                obs_size = obstacle['size']

                obs_x_center = x_left + (obs_lane_idx * base_lane_width) + (base_lane_width / 2.0)
                obs_y_center = y_level + obs_size / 2.0
                obs_z_center = tile['start_z'] + (tile['end_z'] - tile['start_z']) * obs_z_factor
                
                glPushMatrix()
                glTranslatef(obs_x_center, obs_y_center, obs_z_center)
                glutSolidCube(obs_size)
                glPopMatrix()

                obstacle['world_x'] = obs_x_center
                obstacle['world_y_top'] = obs_y_center + obs_size / 2.0
                obstacle['world_z'] = obs_z_center

        ### Draw Moving Obstacles (Cylinders) - Vertical ###
        if tile.get('moving_obstacles'):
            glColor3f(MOVING_OBSTACLE_COLOR[0], MOVING_OBSTACLE_COLOR[1], MOVING_OBSTACLE_COLOR[2])
            
            for mobstacle in tile['moving_obstacles']:
                mob_z_factor = mobstacle['z_pos_factor']
                mob_x_current_absolute = mobstacle['x_pos_current_absolute']

                mob_y_center = y_level + MOVING_OBSTACLE_HEIGHT / 2.0 
                mob_z_center = tile['start_z'] + (tile['end_z'] - tile['start_z']) * mob_z_factor
                
                glPushMatrix()
                glTranslatef(mob_x_current_absolute, mob_y_center - MOVING_OBSTACLE_HEIGHT/2.0, mob_z_center)
                glRotatef(-90, 1, 0, 0) # Corrected rotation to face up
                gluCylinder(ball_quadric, MOVING_OBSTACLE_RADIUS, MOVING_OBSTACLE_RADIUS, MOVING_OBSTACLE_HEIGHT, 16, 1)
                
                glPushMatrix()
                glTranslatef(0, 0, MOVING_OBSTACLE_HEIGHT)
                gluDisk(ball_quadric, 0, MOVING_OBSTACLE_RADIUS, 16, 1)
                glPopMatrix()

                gluDisk(ball_quadric, 0, MOVING_OBSTACLE_RADIUS, 16, 1)
                
                glPopMatrix()

        # --- Draw Grid Lines (always drawn over the full platform area) ---
        glColor3f(GRID_CYAN[0], GRID_CYAN[1], GRID_CYAN[2])
        # REMOVED: glLineWidth(1.0) # Removed for strict compliance
        glBegin(GL_LINES)
        
        # Vertical grid lines (lane boundaries)
        for i in range(num_lanes + 1):
            line_x = x_left + (i * base_lane_width)
            glVertex3f(line_x, y_level + 0.1, tile['start_z'])
            glVertex3f(line_x, y_level + 0.1, tile['end_z'])
        
        # Horizontal grid lines
        for i in range(grid_density_z + 1):
            current_z = tile['start_z'] - ((i / grid_density_z) * platform_segment_length)
            glVertex3f(x_left,  y_level + 0.1, current_z)
            glVertex3f(x_right, y_level + 0.1, current_z)
        
        glEnd()

def draw_platform_tiled(): ### MODIFIED: Removed glLineWidth ###
    """
    Draws the procedurally generated platform and any obstacles on it.
    Grid lines are drawn over the entire platform area, while solid tiles are drawn individually.
    """
    grid_density_z = 3
    for segment_idx, tile in enumerate(platform_segments):
        num_lanes, x_offset, y_level = tile['config']
        y_bottom = y_level - platform_thickness
        x_left, x_right = get_full_lane_x_coords(num_lanes, x_offset)
        
        # Display debug text for the first segment
        if segment_idx == 0: 
            draw_text(10, WINDOW_H - 90, tile['debug_text'])
        
        # --- Draw Each SOLID Lane Individually (Top, Sides, Bottom) ---
        for lane_idx in range(num_lanes):
            # Skip drawing ANY 3D geometry for hole lanes
            if lane_idx in tile['hole_lanes']:
                continue
                
            # Calculate lane coordinates
            lane_x_left = x_left + (lane_idx * base_lane_width)
            lane_x_right = lane_x_left + base_lane_width
            
            # --- Draw Top Surface with checkerboard pattern ---
            if (segment_idx + lane_idx) % 2 == 0: 
                glColor3f(DARK_BLUE[0], DARK_BLUE[1], DARK_BLUE[2])
            else: 
                glColor3f(MID_BLUE[0], MID_BLUE[1], MID_BLUE[2])
            
            glBegin(GL_QUADS)
            # Top face
            glVertex3f(lane_x_left,  y_level, tile['start_z'])
            glVertex3f(lane_x_right, y_level, tile['start_z'])
            glVertex3f(lane_x_right, y_level, tile['end_z'])
            glVertex3f(lane_x_left,  y_level, tile['end_z'])
            glEnd()
            
            # --- Draw Side Walls and Bottom for THIS solid lane ---
            glColor3f(DARK_BLUE_SIDE[0], DARK_BLUE_SIDE[1], DARK_BLUE_SIDE[2])
            glBegin(GL_QUADS)
            
            # Left side wall (only if this is the leftmost lane or adjacent left lane is a hole)
            if lane_idx == 0 or (lane_idx - 1) in tile['hole_lanes']:
                glVertex3f(lane_x_left, y_level,  tile['start_z'])
                glVertex3f(lane_x_left, y_level,  tile['end_z'])
                glVertex3f(lane_x_left, y_bottom, tile['end_z'])
                glVertex3f(lane_x_left, y_bottom, tile['start_z'])
            
            # Right side wall (only if this is the rightmost lane or adjacent right lane is a hole)
            if lane_idx == num_lanes - 1 or (lane_idx + 1) in tile['hole_lanes']:
                glVertex3f(lane_x_right, y_level,  tile['start_z'])
                glVertex3f(lane_x_right, y_level,  tile['end_z'])
                glVertex3f(lane_x_right, y_bottom, tile['end_z'])
                glVertex3f(lane_x_right, y_bottom, tile['start_z'])
            
            # Front face (always drawn for solid lanes at the segment's start_z)
            glVertex3f(lane_x_left,  y_level,  tile['start_z'])
            glVertex3f(lane_x_right, y_level,  tile['start_z'])
            glVertex3f(lane_x_right, y_bottom, tile['start_z'])
            glVertex3f(lane_x_left,  y_bottom, tile['start_z'])
            
            # Back face (always drawn for solid lanes at the segment's end_z)
            glVertex3f(lane_x_left,  y_level,  tile['end_z'])
            glVertex3f(lane_x_right, y_level,  tile['end_z'])
            glVertex3f(lane_x_right, y_bottom, tile['end_z'])
            glVertex3f(lane_x_left,  y_bottom, tile['end_z'])
            glEnd()
            
            # Bottom face of this lane
            glColor3f(MID_BLUE_SIDE[0], MID_BLUE_SIDE[1], MID_BLUE_SIDE[2])
            glBegin(GL_QUADS)
            glVertex3f(lane_x_left,  y_bottom, tile['start_z'])
            glVertex3f(lane_x_right, y_bottom, tile['start_z'])
            glVertex3f(lane_x_right, y_bottom, tile['end_z'])
            glVertex3f(lane_x_left,  y_bottom, tile['end_z'])
            glEnd()
        
        ### Draw Static Obstacles ###
        if tile.get('obstacles'):
            glColor3f(OBSTACLE_COLOR[0], OBSTACLE_COLOR[1], OBSTACLE_COLOR[2])
            for obstacle_idx, obstacle in enumerate(tile['obstacles']): 
                obs_lane_idx = obstacle['lane_index']
                obs_z_factor = obstacle['z_pos_factor']
                obs_size = obstacle['size']

                obs_x_center = x_left + (obs_lane_idx * base_lane_width) + (base_lane_width / 2.0)
                obs_y_center = y_level + obs_size / 2.0
                obs_z_center = tile['start_z'] + (tile['end_z'] - tile['start_z']) * obs_z_factor
                
                glPushMatrix()
                glTranslatef(obs_x_center, obs_y_center, obs_z_center)
                glutSolidCube(obs_size)
                glPopMatrix()

                obstacle['world_x'] = obs_x_center
                obstacle['world_y_top'] = obs_y_center + obs_size / 2.0
                obstacle['world_z'] = obs_z_center

        ### Draw Moving Obstacles (Cylinders) - Vertical ###
        if tile.get('moving_obstacles'):
            glColor3f(MOVING_OBSTACLE_COLOR[0], MOVING_OBSTACLE_COLOR[1], MOVING_OBSTACLE_COLOR[2])
            
            for mobstacle in tile['moving_obstacles']:
                mob_z_factor = mobstacle['z_pos_factor']
                mob_x_current_absolute = mobstacle['x_pos_current_absolute']

                mob_y_center = y_level + MOVING_OBSTACLE_HEIGHT / 2.0 
                mob_z_center = tile['start_z'] + (tile['end_z'] - tile['start_z']) * mob_z_factor
                
                glPushMatrix()
                glTranslatef(mob_x_current_absolute, mob_y_center - MOVING_OBSTACLE_HEIGHT/2.0, mob_z_center)
                glRotatef(-90, 1, 0, 0)
                gluCylinder(ball_quadric, MOVING_OBSTACLE_RADIUS, MOVING_OBSTACLE_RADIUS, MOVING_OBSTACLE_HEIGHT, 16, 1)
                
                glPushMatrix()
                glTranslatef(0, 0, MOVING_OBSTACLE_HEIGHT)
                gluDisk(ball_quadric, 0, MOVING_OBSTACLE_RADIUS, 16, 1)
                glPopMatrix()

                gluDisk(ball_quadric, 0, MOVING_OBSTACLE_RADIUS, 16, 1)
                
                glPopMatrix()

        # --- Draw Grid Lines (always drawn over the full platform area) ---
        glColor3f(GRID_CYAN[0], GRID_CYAN[1], GRID_CYAN[2])
        # REMOVED: glLineWidth(1.0) # Removed for strict compliance
        glBegin(GL_LINES)
        
        # Vertical grid lines (lane boundaries)
        for i in range(num_lanes + 1):
            line_x = x_left + (i * base_lane_width)
            glVertex3f(line_x, y_level + 0.1, tile['start_z'])
            glVertex3f(line_x, y_level + 0.1, tile['end_z'])
        
        # Horizontal grid lines
        for i in range(grid_density_z + 1):
            current_z = tile['start_z'] - ((i / grid_density_z) * platform_segment_length)
            glVertex3f(x_left,  y_level + 0.1, current_z)
            glVertex3f(x_right, y_level + 0.1, current_z)
        
        glEnd()

# Helper quadric for drawing points
#point_quadric = gluNewQuadric()

# Helper quadric for drawing points
# point_quadric = gluNewQuadric() # This global quadric is not used by glutSolidCube, so it can be removed.

def draw_points(): ### CRITICAL FIX: No glScalef, uses direct size ###
    """
    Draws the diamond-shaped point icons hovering over safe tiles or obstacles, now with pulsation.
    """
    global point_objects, point_pulse_scale # point_quadric is not used here

    # Lighting is already disabled globally for 3D objects in the non-lighting pass
    
    for segment in platform_segments:
        if segment.get('points'):
            for point in segment['points']:
                glPushMatrix()
                
                glColor3f(point['color'][0], point['color'][1], point['color'][2])
                # Hover offset from idle() is used directly
                glTranslatef(point['x'], point['y'] + point_hover_offset, point['z']) 
                
                # --- Apply Pulsation Scale (via direct argument) ---
                current_point_size = POINT_SIZE * point_pulse_scale ### MODIFIED: Calculate final size ###
                
                # REMOVED: glScalef calls
                glRotatef(45, 1, 0, 0) # Rotate for diamond shape (on X-axis)
                glRotatef(45, 0, 1, 0) # Rotate for diamond shape (on Y-axis)
                
                glutSolidCube(current_point_size) ### MODIFIED: Use current_point_size directly ###
                
                glPopMatrix()
    
    # No glDisable(GL_LIGHTING) here as it's not enabled for this pass.



def draw_double_jump_powerups(): ### CRITICAL FIX: Custom Double Chevron Icon (No glScalef) ###
    """
    Draws the double jump power-up icons as double chevron arrows.
    Uses the same pulsation and hover animation as points.
    """
    global point_pulse_scale, point_hover_offset

    for segment in platform_segments:
        if segment.get('double_jump_powerups'):
            for powerup in segment['double_jump_powerups']:
                glPushMatrix()
                glColor3f(powerup['color'][0], powerup['color'][1], powerup['color'][2])  
                glTranslatef(powerup['x'], powerup['y'] + point_hover_offset, powerup['z'])
                
                # --- Apply Pulsation Scale (by adjusting size directly) ---
                current_size = DOUBLE_JUMP_SIZE * point_pulse_scale  
                thickness = current_size / 3.0
                offset = current_size * 0.8  # spacing between chevrons

                # --- Bottom Chevron ---
                glPushMatrix()
                glTranslatef(0, -offset/2, 0)

                glBegin(GL_QUADS)
                glVertex3f(0, 0, 0)
                glVertex3f(-current_size, -current_size, 0)
                glVertex3f(-current_size + thickness, -current_size - thickness, 0)
                glVertex3f(thickness, -thickness, 0)
                
                glVertex3f(0, 0, 0)
                glVertex3f(current_size, -current_size, 0)
                glVertex3f(current_size - thickness, -current_size - thickness, 0)
                glVertex3f(-thickness, -thickness, 0)
                glEnd()

                glPopMatrix()

                # --- Top Chevron ---
                glPushMatrix()
                glTranslatef(0, offset/2, 0)

                glBegin(GL_QUADS)
                glVertex3f(0, 0, 0)
                glVertex3f(-current_size, -current_size, 0)
                glVertex3f(-current_size + thickness, -current_size - thickness, 0)
                glVertex3f(thickness, -thickness, 0)
                
                glVertex3f(0, 0, 0)
                glVertex3f(current_size, -current_size, 0)
                glVertex3f(current_size - thickness, -current_size - thickness, 0)
                glVertex3f(-thickness, -thickness, 0)
                glEnd()

                glPopMatrix()

                glPopMatrix()



def draw_multiplier_pickups(): ### CRITICAL FIX: Bolder "2X" Multiplier Icon ###
    """
    Draws the score multiplier pickup icons (2X symbol) hovering above tiles.
    Uses the same pulsation and hover animation as points, with bolder strokes.
    """
    global point_pulse_scale, point_hover_offset

    for segment in platform_segments:
        if segment.get('multiplier_pickups'):
            for pickup in segment['multiplier_pickups']:
                glPushMatrix()
                glColor3f(pickup['color'][0], pickup['color'][1], pickup['color'][2])
                glTranslatef(pickup['x'], pickup['y'] + point_hover_offset, pickup['z'])
                
                # Apply pulsation scale
                current_size = MULTIPLIER_SIZE * point_pulse_scale
                
                # Calculate half stroke thickness for easier vertex definition
                half_stroke = current_size * MULTIPLIER_STROKE_THICKNESS / 2.0 
                
                # --- Draw "2X" symbol using GL_QUADS ---
                
                # Part 1: The number "2"
                
                # Top horizontal part of '2'
                glBegin(GL_QUADS)
                glVertex3f(-current_size * 0.4 - half_stroke, current_size * 0.5 + half_stroke, 0)
                glVertex3f(current_size * 0.4 + half_stroke, current_size * 0.5 + half_stroke, 0)
                glVertex3f(current_size * 0.4 + half_stroke, current_size * 0.4 - half_stroke, 0)
                glVertex3f(-current_size * 0.4 - half_stroke, current_size * 0.4 - half_stroke, 0)
                glEnd()
                
                # Right vertical part of '2' (top to middle, with curve)
                glBegin(GL_QUADS)
                glVertex3f(current_size * 0.4 + half_stroke, current_size * 0.5, 0)
                glVertex3f(current_size * 0.5 + half_stroke, current_size * 0.4 - half_stroke, 0)
                glVertex3f(current_size * 0.5 + half_stroke, -half_stroke, 0)
                glVertex3f(current_size * 0.4 + half_stroke, current_size * 0.1 + half_stroke, 0) # Adjusted for curve
                glEnd()

                # Middle horizontal part of '2'
                glBegin(GL_QUADS)
                glVertex3f(-current_size * 0.5 - half_stroke, half_stroke, 0)
                glVertex3f(current_size * 0.5 + half_stroke, half_stroke, 0)
                glVertex3f(current_size * 0.5 + half_stroke, -half_stroke, 0)
                glVertex3f(-current_size * 0.5 - half_stroke, -half_stroke, 0)
                glEnd()
                
                # Left vertical part of '2' (middle to bottom)
                glBegin(GL_QUADS)
                glVertex3f(-current_size * 0.5 - half_stroke, half_stroke, 0)
                glVertex3f(-current_size * 0.4 - half_stroke, -half_stroke, 0)
                glVertex3f(-current_size * 0.4 - half_stroke, -current_size * 0.5 + half_stroke, 0)
                glVertex3f(-current_size * 0.5 - half_stroke, -current_size * 0.5 - half_stroke, 0)
                glEnd()
                
                # Bottom horizontal part of '2'
                glBegin(GL_QUADS)
                glVertex3f(-current_size * 0.5 - half_stroke, -current_size * 0.5 + half_stroke, 0)
                glVertex3f(current_size * 0.5 + half_stroke, -current_size * 0.5 + half_stroke, 0)
                glVertex3f(current_size * 0.5 + half_stroke, -current_size * 0.6 - half_stroke, 0)
                glVertex3f(-current_size * 0.5 - half_stroke, -current_size * 0.6 - half_stroke, 0)
                glEnd()

                # Part 2: The letter "X" - shifted right
                glPushMatrix()
                glTranslatef(current_size * 0.8, 0, 0) # Shift X to the right of the '2'
                
                # Diagonal 1 of X
                glBegin(GL_QUADS)
                glVertex3f(-current_size * 0.3 - half_stroke, current_size * 0.4 + half_stroke, 0)
                glVertex3f(-current_size * 0.2 + half_stroke, current_size * 0.5 + half_stroke, 0)
                glVertex3f(current_size * 0.3 + half_stroke, -current_size * 0.4 - half_stroke, 0)
                glVertex3f(current_size * 0.2 - half_stroke, -current_size * 0.5 - half_stroke, 0)
                glEnd()

                # Diagonal 2 of X
                glBegin(GL_QUADS)
                glVertex3f(-current_size * 0.2 - half_stroke, -current_size * 0.5 - half_stroke, 0)
                glVertex3f(-current_size * 0.3 - half_stroke, -current_size * 0.4 - half_stroke, 0)
                glVertex3f(current_size * 0.2 + half_stroke, current_size * 0.5 + half_stroke, 0)
                glVertex3f(current_size * 0.3 + half_stroke, current_size * 0.4 + half_stroke, 0)
                glEnd()
                
                glPopMatrix() # Pop for X
                
                glPopMatrix() # Pop for main pickup


def draw_boost_pads(): ### CRITICAL FIX: Pulsating Boost Pad Color ###
    """
    Draws boost pads as colored tiles on the platform surface, now with pulsation.
    """
    global point_pulse_time # Access for pulsation

    for segment in platform_segments:
        if segment.get('boost_pads'):
            for boost_pad in segment['boost_pads']:
                if not boost_pad['active']: # Only draw if active
                    continue

                num_lanes, x_offset, y_level = segment['config']
                x_left, x_right = get_full_lane_x_coords(num_lanes, x_offset)
                
                lane_x_left = x_left + (boost_pad['lane_idx'] * base_lane_width)
                lane_x_right = lane_x_left + base_lane_width
                pad_z_start = boost_pad['z_start']
                pad_z_end = boost_pad['z_end']
                
                # Add pulsating effect for the MAIN PAD COLOR
                pulse_intensity_main = 0.1 + 0.1 * math.sin(point_pulse_time * 2.5) # Slightly different speed/intensity
                main_pad_color_pulsed = (
                    min(1.0, BOOST_PAD_COLOR[0] + pulse_intensity_main),
                    min(1.0, BOOST_PAD_COLOR[1] + pulse_intensity_main),
                    min(1.0, BOOST_PAD_COLOR[2] + pulse_intensity_main)
                )

                # --- Draw boost pad as a colored tile (MAIN PAD) ---
                glColor3f(main_pad_color_pulsed[0], main_pad_color_pulsed[1], main_pad_color_pulsed[2]) ### CRITICAL FIX: Apply pulsating color here ###
                glBegin(GL_QUADS)
                glVertex3f(lane_x_left, y_level + 0.2, pad_z_start)  # Slightly elevated
                glVertex3f(lane_x_right, y_level + 0.2, pad_z_start)
                glVertex3f(lane_x_right, y_level + 0.2, pad_z_end)
                glVertex3f(lane_x_left, y_level + 0.2, pad_z_end)
                glEnd()
                
                # Add a brighter pulsating center (optional, but good for visual hierarchy)
                pulse_intensity_center = 0.3 + 0.2 * math.sin(point_pulse_time * 2.0)
                bright_center_color = (
                    min(1.0, BOOST_PAD_COLOR[0] + pulse_intensity_center),
                    min(1.0, BOOST_PAD_COLOR[1] + pulse_intensity_center),
                    min(1.0, BOOST_PAD_COLOR[2] + pulse_intensity_center)
                )
                
                # Draw pulsating center
                glColor3f(bright_center_color[0], bright_center_color[1], bright_center_color[2])
                center_x = (lane_x_left + lane_x_right) / 2
                center_z = (pad_z_start + pad_z_end) / 2
                pad_half_width = base_lane_width * 0.4
                pad_half_length = BOOST_PAD_LENGTH * 0.4
                
                glBegin(GL_QUADS)
                glVertex3f(center_x - pad_half_width, y_level + 0.3, center_z - pad_half_length)
                glVertex3f(center_x + pad_half_width, y_level + 0.3, center_z - pad_half_length)
                glVertex3f(center_x + pad_half_width, y_level + 0.3, center_z + pad_half_length)
                glVertex3f(center_x - pad_half_width, y_level + 0.3, center_z + pad_half_length)
                glEnd()



def fill_segment_queue(): ### NEW FUNCTION ###
    """
    Fills the segment queue with a predefined pattern of narrow beams and random segments.
    """
    global segment_queue
    
    # Ensure queue is clear before filling
    segment_queue = []

    # Add narrow beam segments (50% of the cycle)
    narrow_beam_choices = [
        SEGMENT_TYPE_NARROW_BEAM_CENTER,
        SEGMENT_TYPE_NARROW_BEAM_LEFT,
        SEGMENT_TYPE_NARROW_BEAM_RIGHT
    ]
    for _ in range(NARROW_BEAM_COUNT_PER_CYCLE):
        segment_queue.append(random.choice(narrow_beam_choices))
    
    # Add remaining segments as random types
    remaining_random_count = QUEUE_CYCLE_LENGTH - NARROW_BEAM_COUNT_PER_CYCLE
    for _ in range(remaining_random_count):
        # We'll let generate_platform_tile pick a random type when it dequeues a placeholder
        segment_queue.append('RANDOM_TYPE_PLACEHOLDER')

    random.shuffle(segment_queue) # Shuffle to randomize the order

# Create a single, reusable quadric object for the ball
ball_quadric = gluNewQuadric()

def draw_ball(): ### MODIFIED: Draws shield aura if active ###
    """
    The player ball (sphere). Now drawn with flat color and optional shield aura.
    """
    global game_state, is_breaking_animation_active, has_shield_active, point_pulse_scale

    if game_state != STATE_PLAYING:
        return

    glPushMatrix()
    glTranslatef(ball_pos[0], ball_pos[1], ball_pos[2])
    glRotatef(ball_rotation_angle, 1, 0, 0) 
    
    glColor3f(BALL_COLOR_FLAT[0], BALL_COLOR_FLAT[1], BALL_COLOR_FLAT[2]) 
    gluSphere(ball_quadric, ball_radius, 24, 24)
    
    # --- Draw Shield Aura if active ---
    if has_shield_active and shield_charge_count > 0: ### MODIFIED: Only if charges exist ###
        # Simulate pulsation and slight transparency for the aura
        aura_pulse_factor = (math.sin(point_pulse_time * SHIELD_EFFECT_PULSE_SPEED) + 1.0) / 2.0
        aura_radius = ball_radius * (SHIELD_AURA_RADIUS_FACTOR + aura_pulse_factor * 0.1) # Aura pulsates size
        
        # Use a slightly faded version of the aura color (simulating alpha)
        glColor3f(SHIELD_AURA_COLOR[0], SHIELD_AURA_COLOR[1], SHIELD_AURA_COLOR[2]) 
        
        glPushMatrix()
        # Translate slightly out to prevent Z-fighting with the ball's surface
        gluSphere(ball_quadric, aura_radius, 24, 24) ### MODIFIED: Use the pulsating aura_radius ###
        glPopMatrix()

    glPopMatrix()

def draw_ball_shadow():
    global is_falling
    glPushMatrix()
    glTranslatef(ball_pos[0], ball_pos[1] + 0.2, ball_pos[2])
    glColor3f(SHADOW_COLOR[0], SHADOW_COLOR[1], SHADOW_COLOR[2])
    quadric = gluNewQuadric()
    gluDisk(quadric, 0, ball_radius * 0.8, 16, 1)
    gluDeleteQuadric(quadric)
    glPopMatrix()


def idle(): ### CRITICAL FIX: Single Ball Break Animation Trigger ###
    """
    The main game loop logic, now driven by a game_state machine.
    """
    global last_time_ms, ball_pos, is_falling, game_over, is_grounded, game_state
    global fall_velocity_x, fall_velocity_y, last_platform_tile_z_end, death_animation_timer
    global keys_pressed, breaking_particles, player_score, ball_rotation_angle
    global point_pulse_scale, point_pulse_time, point_hover_offset
    global has_double_jump_charge, double_jump_timer, score_multiplier, multiplier_timer, is_boost_active, boost_timer, forward_speed 
    global has_shield_active, shield_charge_count, shield_timer 
    global is_obstacle_breaking_active

    now = glutGet(GLUT_ELAPSED_TIME)
    if last_time_ms is None: last_time_ms = now = glutGet(GLUT_ELAPSED_TIME) # Initialize last_time_ms
    
    dt = (now - last_time_ms) / 1000.0
    last_time_ms = now

    # --- Game State Machine Logic ---
    if game_state == STATE_PLAYING:
        # --- Point Pulsation Update ---
        point_pulse_time += dt * POINT_PULSE_SPEED
        pulse_factor = (math.sin(point_pulse_time) + 1.0) / 2.0 
        point_pulse_scale = POINT_PULSE_MIN_SCALE + (POINT_PULSE_MAX_SCALE - POINT_PULSE_MIN_SCALE) * pulse_factor
        point_hover_offset = math.sin(point_pulse_time * 1.5) * 2.0 

        # --- Update Multiplier Timer ---
        if multiplier_timer > 0:
            multiplier_timer -= dt
            if multiplier_timer <= 0:
                score_multiplier = 1 
        
        # --- Update Boost Timer ---
        if is_boost_active:
            boost_timer -= dt
            if boost_timer <= 0:
                is_boost_active = False
                forward_speed = -500.0 

        # --- Double Jump Timer ---
        if double_jump_timer > 0:
            double_jump_timer -= dt
            if double_jump_timer <= 0:
                has_double_jump_charge = False

        # --- Update Shield Timer ---
        if has_shield_active and shield_charge_count > 0:
            shield_timer -= dt
            if shield_timer <= 0:
                shield_charge_count -= 1 
                if shield_charge_count == 0:
                    has_shield_active = False 
                else: 
                    shield_timer = SHIELD_DURATION

        # --- 1. Apply Physics (Vertical) ---
        if not is_grounded:
            fall_velocity_y += GRAVITY * dt 
        ball_pos[1] += fall_velocity_y * dt
        
        if is_falling: 
            ball_pos[0] += fall_velocity_x * dt    

        # --- 2. Handle Player Input and Forward Motion ---
        if not is_falling: 
            if keys_pressed.get(b'a'): ball_pos[0] -= ball_lateral_speed * dt
            if keys_pressed.get(b'd'): ball_pos[0] += ball_lateral_speed * dt

        ball_pos[2] += forward_speed * dt

        # Update ball rotation angle for rolling effect
        distance_moved = abs(forward_speed * dt)
        circumference = 2 * math.pi * ball_radius
        ball_rotation_angle += (distance_moved / circumference) * 360.0
        ball_rotation_angle %= 360.0

        # --- 3. Continuous Platform Generation ---
        if ball_pos[2] < last_platform_tile_z_end + platform_segment_length * (num_visible_tiles / 2):
            last_segment = platform_segments[-1] if platform_segments else None
            generate_platform_tile(last_segment)
            if platform_segments and platform_segments[0]['start_z'] > ball_pos[2] + camera_distance * 2:
                platform_segments.pop(0)

        # --- 4. Process Moving Obstacles ---
        for segment in platform_segments:
            if segment.get('moving_obstacles'):
                num_lanes_seg, x_offset_seg, y_level_seg = segment['config']
                segment_x_left_boundary, segment_x_right_boundary = get_full_lane_x_coords(num_lanes_seg, x_offset_seg)

                for mobstacle in segment['moving_obstacles']:
                    mob_x_current_absolute = mobstacle['x_pos_current_absolute']
                    mob_direction = mobstacle['direction']

                    mobstacle['x_pos_current_absolute'] += MOVING_OBSTACLE_SPEED * mob_direction * dt

                    mob_actual_x_left_edge = mob_x_current_absolute - MOVING_OBSTACLE_RADIUS
                    mob_actual_x_right_edge = mob_x_current_absolute + MOVING_OBSTACLE_RADIUS

                    if mob_actual_x_left_edge < segment_x_left_boundary or \
                       mob_actual_x_right_edge > segment_x_right_boundary:
                        mobstacle['direction'] *= -1
                        if mob_actual_x_left_edge < segment_x_left_boundary:
                            mobstacle['x_pos_current_absolute'] = segment_x_left_boundary + MOVING_OBSTACLE_RADIUS
                        elif mob_actual_x_right_edge > segment_x_right_boundary:
                            mobstacle['x_pos_current_absolute'] = segment_x_right_boundary - MOVING_OBSTACLE_RADIUS
                            
        # --- 5. Find Current Segment and Determine Grounding/Falling State ---
        is_grounded_this_frame_candidate = False 
        
        current_segment = None
        for segment in platform_segments:
            if segment['end_z'] - 1 < ball_pos[2] <= segment['start_z'] + 1:
                current_segment = segment
                break 
        
        if current_segment:
            target_ball_y_center = FLOOR_Y + ball_radius
            num_lanes, x_offset, _ = current_segment['config']
            playable_x_left, playable_x_right = get_full_lane_x_coords(num_lanes, x_offset)

            is_over_platform_x_solid_ground = (ball_pos[0] >= playable_x_left - ball_radius * 0.5 and 
                                               ball_pos[0] <= playable_x_right + ball_radius * 0.5)

            ball_is_over_hole = False
            if current_segment['hole_lanes']:
                x_relative = ball_pos[0] - playable_x_left
                lane_index = int(x_relative / base_lane_width)
                if 0 <= lane_index < num_lanes and lane_index in current_segment['hole_lanes']:
                    ball_is_over_hole = True
            
            # --- Primary Grounding Condition ---
            if is_over_platform_x_solid_ground and not ball_is_over_hole and ball_pos[1] <= target_ball_y_center + PLATFORM_Y_SNAP_TOLERANCE:
                is_grounded_this_frame_candidate = True
        
        # --- Apply Grounding State & Snap ---
        if is_grounded_this_frame_candidate: 
            if not is_grounded: # Just landed
                is_grounded = True
                is_falling = False 
                fall_velocity_y = 0.0 
                ball_pos[1] = target_ball_y_center 
            else: # Already grounded
                ball_pos[1] = target_ball_y_center 
        else: # Not on solid ground or too high - Ball should be in air (jumping or falling)
            if is_grounded: # Just left ground this frame
                is_grounded = False
                is_falling = True 
                fall_velocity_y = 0.0 
                if current_segment:
                    playable_x_left, playable_x_right = get_full_lane_x_coords(current_segment['config'][CONFIG_NUM_LANES], current_segment['config'][CONFIG_X_OFFSET])
                    if ball_pos[0] < playable_x_left: fall_velocity_x = -100.0
                    elif ball_pos[0] > playable_x_right: fall_velocity_x = 100.0
                    else: fall_velocity_x = 0.0
                else: 
                    fall_velocity_x = 100.0 if ball_pos[0] > 0 else -100.0
            
        # --- Collision Checks (Only if currently grounded) ---
        if is_grounded: 
            # Static Obstacle Collision
            if current_segment.get('obstacles'):
                for obstacle_idx, obstacle in enumerate(current_segment['obstacles']):
                    obs_x_center = obstacle['world_x']
                    obs_y_center = obstacle['world_y_top'] - obstacle['size'] / 2.0
                    obs_z_center = obstacle['world_z']
                    
                    closest_x = max(obs_x_center - obstacle['size'] / 2.0, min(ball_pos[0], obs_x_center + obstacle['size'] / 2.0))
                    closest_y = max(obs_y_center - obstacle['size'] / 2.0, min(ball_pos[1], obs_y_center + obstacle['size'] / 2.0))
                    closest_z = max(obs_z_center - obstacle['size'] / 2.0, min(ball_pos[2], obs_z_center + obstacle['size'] / 2.0))
                    
                    distance_sq = (closest_x - ball_pos[0])**2 + (closest_y - ball_pos[1])**2 + (closest_z - ball_pos[2])**2
                    
                    if distance_sq < (ball_radius**2):
                        # Only trigger animation if shield is NOT active, OR shield is active but has no charges
                        if not (has_shield_active and shield_charge_count > 0): 
                            game_state = STATE_ANIMATING_DEATH
                            death_animation_timer = PARTICLE_LIFETIME
                            breaking_particles = generate_explosion_particles(ball_pos, ball_radius, BALL_COLOR_FLAT)
                            return 
                        else: # Shield active: Obstacle breaks, game continues
                            is_obstacle_breaking_active = True 
                            death_animation_timer = PARTICLE_LIFETIME 
                            obstacle_center_pos = [obs_x_center, obs_y_center, obs_z_center]
                            breaking_particles = generate_explosion_particles(obstacle_center_pos, obstacle['size']/2.0, OBSTACLE_COLOR) 
                            current_segment['obstacles'].pop(obstacle_idx) 
                            return 

            # Moving Obstacle Collision
            if current_segment.get('moving_obstacles'):
                for mobstacle_idx, mobstacle in enumerate(current_segment['moving_obstacles']):
                    mob_z_factor = mobstacle['z_pos_factor']
                    mob_x_center_absolute = mobstacle['x_pos_current_absolute']
                    
                    mob_y_bottom = FLOOR_Y
                    mob_y_top = FLOOR_Y + MOVING_OBSTACLE_HEIGHT
                    mob_z_center = current_segment['start_z'] + (current_segment['end_z'] - current_segment['start_z']) * mob_z_factor

                    closest_x_on_axis = mob_x_center_absolute
                    closest_y_on_axis = max(mob_y_bottom, min(ball_pos[1], mob_y_top))
                    closest_z_on_axis = mob_z_center

                    dist_xz_sq = (ball_pos[0] - closest_x_on_axis)**2 + \
                                 (ball_pos[2] - closest_z_on_axis)**2

                    if dist_xz_sq < (ball_radius + MOVING_OBSTACLE_RADIUS)**2:
                        if ball_pos[1] + ball_radius > mob_y_bottom and ball_pos[1] - ball_radius < mob_y_top:
                            if not (has_shield_active and shield_charge_count > 0): 
                                game_state = STATE_ANIMATING_DEATH
                                death_animation_timer = PARTICLE_LIFETIME
                                breaking_particles = generate_explosion_particles(ball_pos, ball_radius, BALL_COLOR_FLAT)
                                return 
                            else: # Shield active: Obstacle breaks, game continues
                                is_obstacle_breaking_active = True 
                                death_animation_timer = PARTICLE_LIFETIME
                                mobstacle_center_pos = [mob_x_center_absolute, mob_y_bottom + MOVING_OBSTACLE_HEIGHT/2.0, mob_z_center]
                                breaking_particles = generate_explosion_particles(mobstacle_center_pos, MOVING_OBSTACLE_RADIUS, MOVING_OBSTACLE_COLOR)
                                current_segment['moving_obstacles'].pop(mobstacle_idx) 
                                return 
                        
            # Point Collection (only if grounded)
            if current_segment.get('points'):
                for i in range(len(current_segment['points']) -1, -1, -1):
                    point = current_segment['points'][i]
                    point_x, point_y, point_z = point['x'], point['y'], point['z']
                    
                    distance_sq = (point_x - ball_pos[0])**2 + \
                                  (point_y - ball_pos[1])**2 + \
                                  (point_z - ball_pos[2])**2
                    
                    if distance_sq < (ball_radius + POINT_SIZE / 2.0)**2:
                        player_score += score_multiplier
                        current_segment['points'].pop(i)

            # Double Jump Power-up Collection
            if current_segment.get('double_jump_powerups') and not has_double_jump_charge:
                for i in range(len(current_segment['double_jump_powerups']) - 1, -1, -1):
                    powerup = current_segment['double_jump_powerups'][i]
                    dist_sq = (powerup['x'] - ball_pos[0])**2 + \
                              (powerup['y'] + point_hover_offset - ball_pos[1])**2 + \
                              (powerup['z'] - ball_pos[2])**2
                    if dist_sq < (ball_radius + DOUBLE_JUMP_SIZE / 2.0)**2:
                        has_double_jump_charge = True
                        double_jump_timer = DOUBLE_JUMP_DURATION
                        current_segment['double_jump_powerups'].pop(i)
                        break
            
            # Multiplier Pickup Collection
            if current_segment.get('multiplier_pickups'):
                for i in range(len(current_segment['multiplier_pickups']) - 1, -1, -1):
                    pickup = current_segment['multiplier_pickups'][i]
                    dist_sq = (pickup['x'] - ball_pos[0])**2 + \
                              (pickup['y'] + point_hover_offset - ball_pos[1])**2 + \
                              (pickup['z'] - ball_pos[2])**2
                    if dist_sq < (ball_radius + MULTIPLIER_SIZE / 2.0)**2:
                        score_multiplier = MULTIPLIER_FACTOR
                        multiplier_timer = MULTIPLIER_DURATION
                        current_segment['multiplier_pickups'].pop(i)
                        break
            
            # Boost Pad Collision
            if current_segment.get('boost_pads'):
                for boost_pad in current_segment['boost_pads']:
                    if boost_pad['active']:
                        lane_x_left = x_offset - (num_lanes * base_lane_width / 2.0) + (boost_pad['lane_idx'] * base_lane_width)
                        lane_x_right = lane_x_left + base_lane_width
                        
                        is_over_boost_x = (ball_pos[0] >= lane_x_left - ball_radius) and (ball_pos[0] <= lane_x_right + ball_radius)
                        is_over_boost_z = (ball_pos[2] >= boost_pad['z_start'] - ball_radius) and (ball_pos[2] <= boost_pad['z_end'] + ball_radius)
                        
                        if is_over_boost_x and is_over_boost_z:
                            is_boost_active = True
                            forward_speed *= BOOST_PAD_SPEED_BOOST 
                            boost_timer = BOOST_DURATION
                            boost_pad['active'] = False 
                            break 

            # Shield Pickup Collection
            if current_segment.get('shields'):
                for i in range(len(current_segment['shields']) - 1, -1, -1):
                    shield_icon = current_segment['shields'][i]
                    dist_sq = (shield_icon['x'] - ball_pos[0])**2 + \
                              (shield_icon['y'] + point_hover_offset - ball_pos[1])**2 + \
                              (shield_icon['z'] - ball_pos[2])**2
                    if dist_sq < (ball_radius + SHIELD_SIZE / 2.0)**2:
                        has_shield_active = True
                        shield_charge_count += 1
                        shield_timer = SHIELD_DURATION 
                        current_segment['shields'].pop(i)
                        break

        # --- Ultimate Game Over Condition (Falling below defined threshold) ---
        if ball_pos[1] < fall_threshold_y:
            game_state = STATE_ANIMATING_DEATH
            death_animation_timer = PARTICLE_LIFETIME
            breaking_particles = generate_explosion_particles(ball_pos, ball_radius, BALL_COLOR_FLAT)
            return 
        
        glutPostRedisplay()


    # --- State: Animating Death (for ball or obstacles) ---
    elif game_state == STATE_ANIMATING_DEATH:
        death_animation_timer -= dt
        if death_animation_timer <= 0:
            breaking_particles = [] 
            # Check if this animation was for an obstacle break or ball death
            if is_obstacle_breaking_active: ### CRITICAL FIX: Distinguish between ball death and obstacle break ###
                is_obstacle_breaking_active = False # Reset flag
                game_state = STATE_PLAYING # Resume play
                # Important: Ball physics should not be reset, it should continue from current state.
                # If it was falling, it continues falling. If it was grounded, it stays grounded.
            else: # It was the ball's death animation
                game_state = STATE_GAME_OVER 
                game_over = True # True Game Over
        else:
            for particle in breaking_particles:
                particle['vy'] += GRAVITY * dt 
                particle['x'] += particle['vx'] * dt
                particle['y'] += particle['vy'] * dt 
                particle['z'] += particle['vz'] * dt
                particle['lifetime_remaining'] -= dt
        glutPostRedisplay()

    elif game_state == STATE_GAME_OVER:
        glutPostRedisplay()


def draw_shields(): ### CRITICAL COMPLIANCE FIX: Compliant Shield Icon ###
    """Draw collectible hexagonal shields with a glowing orb effect (compliant version)."""
    global point_pulse_scale, point_hover_offset

    for segment in platform_segments:
        if segment.get('shields'):
            for sh in segment['shields']:
                glPushMatrix()
                glColor3f(sh['color'][0], sh['color'][1], sh['color'][2])
                glTranslatef(sh['x'], sh['y'] + point_hover_offset, sh['z'])

                # Pulsating size for the overall shield icon
                current_size = SHIELD_SIZE * point_pulse_scale
                
                # --- Draw compliant hexagon base (using 2 rotated cubes) ---
                # This is a visual approximation of a hexagon using cubes, for compliance.
                glPushMatrix()
                glScalef(1.0, 0.5, 1.0) # Flatten one cube
                glutSolidCube(current_size)
                glPopMatrix()
                
                glPushMatrix()
                glRotatef(60, 0, 1, 0) # Rotate another to form a hexagon approximation
                glScalef(1.0, 0.5, 1.0)
                glutSolidCube(current_size)
                glPopMatrix()

                glPushMatrix()
                glRotatef(-60, 0, 1, 0) # Rotate another
                glScalef(1.0, 0.5, 1.0)
                glutSolidCube(current_size)
                glPopMatrix()


                # --- Draw glowing orb (compliant gluSphere) ---
                glPushMatrix()
                # Use point_pulse_time for rotation effect
                glRotatef(point_pulse_time * 60.0, 0, 1, 0) 
                
                # Simulate multi-layered glow with multiple gluSpheres of different sizes/colors
                # True translucency is not compliant, so we use slightly different colors/sizes
                
                # Innermost bright orb
                glColor3f(0.2, 1.0, 0.8) # Bright cyan-green
                gluSphere(ball_quadric, current_size * 0.4, 16, 16) 
                
                # Outer, slightly larger orb (simulates faded glow)
                glColor3f(0.1, 0.8, 0.6) # Slightly darker
                gluSphere(ball_quadric, current_size * 0.6, 16, 16)

                glPopMatrix()

                glPopMatrix()

def draw_breaking_particles(): ### CRITICAL FIX: Universal particle drawing ###
    """
    Draws the individual particles of *any* breaking animation (ball or obstacle).
    Each particle is drawn with its own isolated transformations.
    """
    global breaking_particles

    # This function will now be called conditionally from showScreen,
    # so its internal check for game_state is removed for cleaner logic.
    if not breaking_particles:
        return

    # Lighting is disabled globally for 3D objects in the non-lighting pass
    
    for particle in breaking_particles:
        glPushMatrix() 
        glColor3f(particle['color'][0], particle['color'][1], particle['color'][2])
        glTranslatef(particle['x'], particle['y'], particle['z'])
        
        current_size = particle['size'] * (particle['lifetime_remaining'] / PARTICLE_LIFETIME)
        if current_size > 0:
            gluSphere(ball_quadric, current_size, 8, 8) 
        
        glPopMatrix() 

def draw_powerup_status(): ### CRITICAL FIX: Top-left positioning for power-up status ###
    """
    Draws the active/inactive status of various power-ups on the HUD in the top-left.
    """
    global has_double_jump_charge, is_boost_active, has_shield_active, shield_charge_count, score_multiplier
    
    # --- Top-left positioning ---
    status_left_x = 10 ### MODIFIED: Use left X for status ###
    status_y_start = WINDOW_H - 150 # Start below other top-left text
    status_line_spacing = 20
    
    # --- Helper to draw status text (MODIFIED to accept positioning args) ---
    def draw_status_left_aligned(x_base, y_pos, label, is_active, value_text=""): ### MODIFIED: Renamed helper for clarity ###
        color = (0.0, 1.0, 0.0) if is_active else (1.0, 0.0, 0.0) # Green for active, Red for inactive
        display_text = f"{label}: {'ACTIVE' if is_active else 'INACTIVE'} {value_text}".strip()
        
        glColor3f(color[0], color[1], color[2])
        # For left alignment, draw text directly at x_base
        draw_text(x_base, y_pos, display_text) ### CRITICAL FIX: Use x_base directly for left alignment ###
        # glColor3f(1,1,1) # No need to reset here, outer call will do it once.

    # Draw statuses (MODIFIED to pass status_left_x to the helper)
    draw_status_left_aligned(status_left_x, status_y_start, "DOUBLE JUMP", has_double_jump_charge)
    draw_status_left_aligned(status_left_x, status_y_start - status_line_spacing, "BOOST", is_boost_active)
    
    shield_status_text = f"({shield_charge_count})" if shield_charge_count > 0 else ""
    draw_status_left_aligned(status_left_x, status_y_start - status_line_spacing * 2, "SHIELD", has_shield_active and shield_charge_count > 0, shield_status_text)
    
    multiplier_label = f"MULTIPLIER: {score_multiplier}X"
    is_multiplier_active = (score_multiplier > 1)
    draw_status_left_aligned(status_left_x, status_y_start - status_line_spacing * 3, "MULTIPLIER", is_multiplier_active, f"{score_multiplier}X" if is_multiplier_active else "1X")
    
    glColor3f(1,1,1) # Final reset color

def generate_explosion_particles(origin_pos, original_radius, color): ### NEW HELPER FUNCTION ###
    """
    Generates a list of particles for a ball breaking explosion.
    """
    particles = []
    for _ in range(NUM_BREAKING_PARTICLES):
        # Random initial velocity components
        vx = random.uniform(-PARTICLE_INITIAL_SPEED_MAX, PARTICLE_INITIAL_SPEED_MAX)
        vy = random.uniform(PARTICLE_INITIAL_SPEED_MAX / 2, PARTICLE_INITIAL_SPEED_MAX) # Prefer upward motion
        vz = random.uniform(-PARTICLE_INITIAL_SPEED_MAX, PARTICLE_INITIAL_SPEED_MAX)

        # Random starting position slightly offset from the ball's center
        offset_x = random.uniform(-original_radius / 2, original_radius / 2)
        offset_y = random.uniform(-original_radius / 2, original_radius / 2)
        offset_z = random.uniform(-original_radius / 2, original_radius / 2)
        
        particle_size = random.uniform(PARTICLE_SIZE_MAX_FACTOR * original_radius / 2, PARTICLE_SIZE_MAX_FACTOR * original_radius)

        particles.append({
            'x': origin_pos[0] + offset_x,
            'y': origin_pos[1] + offset_y,
            'z': origin_pos[2] + offset_z,
            'vx': vx,
            'vy': vy,
            'vz': vz,
            'size': particle_size,
            'color': color,
            'lifetime_remaining': PARTICLE_LIFETIME
        })
    return particles

    
def draw_background(): ### MODIFIED: Removed gluDeleteQuadric ###
    """
    Draws the procedurally generated background elements (stars/nebula particles).
    """
    glDisable(GL_LIGHTING)
    
    quad = gluNewQuadric() 

    # Draw distant elements first
    for el in background_elements_distant:
        glPushMatrix()
        glTranslatef(el['x'], el['y'], el['z'])
        glColor3f(el['color'][0], el['color'][1], el['color'][2])
        gluSphere(quad, el['size'], 8, 8)
        glPopMatrix()

    # Then draw mid-ground elements
    for el in background_elements_mid:
        glPushMatrix()
        glTranslatef(el['x'], el['y'], el['z'])
        glColor3f(el['color'][0], el['color'][1], el['color'][2])
        gluSphere(quad, el['size'], 8, 8)
        glPopMatrix()
    
    # REMOVED: gluDeleteQuadric(quad) # Removed for strict compliance

def idle(): ### CRITICAL, COMPREHENSIVE FIX: Obstacle Animation, Physics, State Flow ###
    """
    The main game loop logic, now driven by a game_state machine.
    """
    global last_time_ms, ball_pos, is_falling, game_over, is_grounded, game_state
    global fall_velocity_x, fall_velocity_y, last_platform_tile_z_end, death_animation_timer
    global keys_pressed, breaking_particles, player_score, ball_rotation_angle
    global point_pulse_scale, point_pulse_time, point_hover_offset
    global has_double_jump_charge, double_jump_timer, score_multiplier, multiplier_timer, is_boost_active, boost_timer, forward_speed 
    global has_shield_active, shield_charge_count, shield_timer 
    global is_obstacle_breaking_active # Access the global flag for obstacle animation

    now = glutGet(GLUT_ELAPSED_TIME)
    if last_time_ms is None: last_time_ms = now
    
    dt = (now - last_time_ms) / 1000.0
    last_time_ms = now

    # --- Game State Machine Logic ---
    if game_state == STATE_PLAYING:
        # --- Point Pulsation Update ---
        point_pulse_time += dt * POINT_PULSE_SPEED
        pulse_factor = (math.sin(point_pulse_time) + 1.0) / 2.0 
        point_pulse_scale = POINT_PULSE_MIN_SCALE + (POINT_PULSE_MAX_SCALE - POINT_PULSE_MIN_SCALE) * pulse_factor
        point_hover_offset = math.sin(point_pulse_time * 1.5) * 2.0 

        # --- Update Multiplier Timer ---
        if multiplier_timer > 0:
            multiplier_timer -= dt
            if multiplier_timer <= 0:
                score_multiplier = 1 
        
        # --- Update Boost Timer ---
        if is_boost_active:
            boost_timer -= dt
            if boost_timer <= 0:
                is_boost_active = False
                forward_speed = -500.0 

        # --- Double Jump Timer ---
        if double_jump_timer > 0:
            double_jump_timer -= dt
            if double_jump_timer <= 0:
                has_double_jump_charge = False

        # --- Update Shield Timer ---
        if has_shield_active and shield_charge_count > 0:
            shield_timer -= dt
            if shield_timer <= 0:
                shield_charge_count -= 1 
                if shield_charge_count == 0:
                    has_shield_active = False 
                else: 
                    shield_timer = SHIELD_DURATION

        # --- 1. Apply Physics (Vertical) ---
        # Gravity always applies if not grounded
        if not is_grounded:
            fall_velocity_y += GRAVITY * dt 
        ball_pos[1] += fall_velocity_y * dt
        
        # Apply sideways drift only if ball is actively falling off an edge/hole
        if is_falling: 
            ball_pos[0] += fall_velocity_x * dt    

        # --- 2. Handle Player Input and Forward Motion ---
        if not is_falling: # Only allow input/movement if not actively falling due to edge/hole
            if keys_pressed.get(b'a'): ball_pos[0] -= ball_lateral_speed * dt
            if keys_pressed.get(b'd'): ball_pos[0] += ball_lateral_speed * dt

        ball_pos[2] += forward_speed * dt

        # Update ball rotation angle for rolling effect
        distance_moved = abs(forward_speed * dt)
        circumference = 2 * math.pi * ball_radius
        ball_rotation_angle += (distance_moved / circumference) * 360.0
        ball_rotation_angle %= 360.0

        # --- 3. Continuous Platform Generation ---
        if ball_pos[2] < last_platform_tile_z_end + platform_segment_length * (num_visible_tiles / 2):
            last_segment = platform_segments[-1] if platform_segments else None
            generate_platform_tile(last_segment)
            if platform_segments and platform_segments[0]['start_z'] > ball_pos[2] + camera_distance * 2:
                platform_segments.pop(0)

        # --- 4. Process Moving Obstacles ---
        for segment in platform_segments:
            if segment.get('moving_obstacles'):
                num_lanes_seg, x_offset_seg, y_level_seg = segment['config']
                segment_x_left_boundary, segment_x_right_boundary = get_full_lane_x_coords(num_lanes_seg, x_offset_seg)

                for mobstacle in segment['moving_obstacles']:
                    mob_x_current_absolute = mobstacle['x_pos_current_absolute']
                    mob_direction = mobstacle['direction']

                    mobstacle['x_pos_current_absolute'] += MOVING_OBSTACLE_SPEED * mob_direction * dt

                    mob_actual_x_left_edge = mob_x_current_absolute - MOVING_OBSTACLE_RADIUS
                    mob_actual_x_right_edge = mob_x_current_absolute + MOVING_OBSTACLE_RADIUS

                    if mob_actual_x_left_edge < segment_x_left_boundary or \
                       mob_actual_x_right_edge > segment_x_right_boundary:
                        mobstacle['direction'] *= -1
                        if mob_actual_x_left_edge < segment_x_left_boundary:
                            mobstacle['x_pos_current_absolute'] = segment_x_left_boundary + MOVING_OBSTACLE_RADIUS
                        elif mob_actual_x_right_edge > segment_x_right_boundary:
                            mobstacle['x_pos_current_absolute'] = segment_x_right_boundary - MOVING_OBSTACLE_RADIUS
                            
        # --- 5. Find Current Segment and Determine Grounding/Falling State ---
        is_grounded_this_frame_candidate = False 
        
        current_segment = None
        for segment in platform_segments:
            if segment['end_z'] - 1 < ball_pos[2] <= segment['start_z'] + 1:
                current_segment = segment
                break 
        
        # --- Determine `is_grounded` and `is_falling` status ---
        if current_segment:
            target_ball_y_center = FLOOR_Y + ball_radius
            num_lanes, x_offset, _ = current_segment['config']
            playable_x_left, playable_x_right = get_full_lane_x_coords(num_lanes, x_offset)

            is_over_platform_x_solid_ground = (ball_pos[0] >= playable_x_left - ball_radius * 0.5 and 
                                               ball_pos[0] <= playable_x_right + ball_radius * 0.5)

            ball_is_over_hole = False
            if current_segment['hole_lanes']:
                x_relative = ball_pos[0] - playable_x_left
                lane_index = int(x_relative / base_lane_width)
                if 0 <= lane_index < num_lanes and lane_index in current_segment['hole_lanes']:
                    ball_is_over_hole = True
            
            # --- Primary Grounding Condition ---
            # Ball is over solid ground, NOT a hole, AND its Y is at or below the platform's top surface.
            if is_over_platform_x_solid_ground and not ball_is_over_hole and ball_pos[1] <= target_ball_y_center + PLATFORM_Y_SNAP_TOLERANCE:
                is_grounded_this_frame_candidate = True
        
        # --- Apply Grounding State & Snap ---
        if is_grounded_this_frame_candidate: 
            if not is_grounded: # Just landed
                is_grounded = True
                is_falling = False 
                fall_velocity_y = 0.0 
                ball_pos[1] = target_ball_y_center 
            else: # Already grounded
                ball_pos[1] = target_ball_y_center 
        else: # Not on solid ground or too high - Ball should be in air (jumping or falling)
            if is_grounded: # Just left ground this frame
                is_grounded = False
                is_falling = True 
                fall_velocity_y = 0.0 
                if current_segment:
                    playable_x_left, playable_x_right = get_full_lane_x_coords(current_segment['config'][CONFIG_NUM_LANES], current_segment['config'][CONFIG_X_OFFSET])
                    if ball_pos[0] < playable_x_left: fall_velocity_x = -100.0
                    elif ball_pos[0] > playable_x_right: fall_velocity_x = 100.0
                    else: fall_velocity_x = 0.0
                else: 
                    fall_velocity_x = 100.0 if ball_pos[0] > 0 else -100.0
            
        # --- Collision Checks (Only if currently grounded) ---
        if is_grounded: 
            # Static Obstacle Collision
            if current_segment.get('obstacles'):
                for obstacle_idx, obstacle in enumerate(current_segment['obstacles']):
                    obs_x_center = obstacle['world_x']
                    obs_y_center = obstacle['world_y_top'] - obstacle['size'] / 2.0
                    obs_z_center = obstacle['world_z']
                    
                    closest_x = max(obs_x_center - obstacle['size'] / 2.0, min(ball_pos[0], obs_x_center + obstacle['size'] / 2.0))
                    closest_y = max(obs_y_center - obstacle['size'] / 2.0, min(ball_pos[1], obs_y_center + obstacle['size'] / 2.0))
                    closest_z = max(obs_z_center - obstacle['size'] / 2.0, min(ball_pos[2], obs_z_center + obstacle['size'] / 2.0))
                    
                    distance_sq = (closest_x - ball_pos[0])**2 + (closest_y - ball_pos[1])**2 + (closest_z - ball_pos[2])**2
                    
                    if distance_sq < (ball_radius**2):
                        if has_shield_active and shield_charge_count > 0:
                            is_obstacle_breaking_active = True 
                            death_animation_timer = PARTICLE_LIFETIME 
                            obstacle_center_pos = [obs_x_center, obs_y_center, obs_z_center]
                            breaking_particles = generate_explosion_particles(obstacle_center_pos, obstacle['size']/2.0, OBSTACLE_COLOR) 
                            current_segment['obstacles'].pop(obstacle_idx) 
                            return 
                        else: # No shield: Ball breaks, Game Over
                            game_state = STATE_ANIMATING_DEATH
                            death_animation_timer = PARTICLE_LIFETIME
                            breaking_particles = generate_explosion_particles(ball_pos, ball_radius, BALL_COLOR_FLAT)
                            return 

            # Moving Obstacle Collision
            if current_segment.get('moving_obstacles'):
                for mobstacle_idx, mobstacle in enumerate(current_segment['moving_obstacles']):
                    mob_z_factor = mobstacle['z_pos_factor']
                    mob_x_center_absolute = mobstacle['x_pos_current_absolute']
                    
                    mob_y_bottom = FLOOR_Y
                    mob_y_top = FLOOR_Y + MOVING_OBSTACLE_HEIGHT
                    mob_z_center = current_segment['start_z'] + (current_segment['end_z'] - current_segment['start_z']) * mob_z_factor

                    closest_x_on_axis = mob_x_center_absolute
                    closest_y_on_axis = max(mob_y_bottom, min(ball_pos[1], mob_y_top))
                    closest_z_on_axis = mob_z_center

                    dist_xz_sq = (ball_pos[0] - closest_x_on_axis)**2 + \
                                 (ball_pos[2] - closest_z_on_axis)**2

                    if dist_xz_sq < (ball_radius + MOVING_OBSTACLE_RADIUS)**2:
                        if ball_pos[1] + ball_radius > mob_y_bottom and ball_pos[1] - ball_radius < mob_y_top:
                            if not (has_shield_active and shield_charge_count > 0): 
                                game_state = STATE_ANIMATING_DEATH
                                death_animation_timer = PARTICLE_LIFETIME
                                breaking_particles = generate_explosion_particles(ball_pos, ball_radius, BALL_COLOR_FLAT)
                                return 
                            else: # Shield active: Obstacle breaks, game continues
                                is_obstacle_breaking_active = True 
                                death_animation_timer = PARTICLE_LIFETIME
                                mobstacle_center_pos = [mob_x_center_absolute, mob_y_bottom + MOVING_OBSTACLE_HEIGHT/2.0, mob_z_center]
                                breaking_particles = generate_explosion_particles(mobstacle_center_pos, MOVING_OBSTACLE_RADIUS, MOVING_OBSTACLE_COLOR)
                                current_segment['moving_obstacles'].pop(mobstacle_idx) 
                                return 
                        
            # Point Collection (only if grounded)
            if current_segment.get('points'):
                for i in range(len(current_segment['points']) -1, -1, -1):
                    point = current_segment['points'][i]
                    point_x, point_y, point_z = point['x'], point['y'], point['z']
                    
                    distance_sq = (point_x - ball_pos[0])**2 + \
                                  (point_y - ball_pos[1])**2 + \
                                  (point_z - ball_pos[2])**2
                    
                    if distance_sq < (ball_radius + POINT_SIZE / 2.0)**2:
                        player_score += score_multiplier
                        current_segment['points'].pop(i)

            # Double Jump Power-up Collection
            if current_segment.get('double_jump_powerups') and not has_double_jump_charge:
                for i in range(len(current_segment['double_jump_powerups']) - 1, -1, -1):
                    powerup = current_segment['double_jump_powerups'][i]
                    dist_sq = (powerup['x'] - ball_pos[0])**2 + \
                              (powerup['y'] + point_hover_offset - ball_pos[1])**2 + \
                              (powerup['z'] - ball_pos[2])**2
                    if dist_sq < (ball_radius + DOUBLE_JUMP_SIZE / 2.0)**2:
                        has_double_jump_charge = True
                        double_jump_timer = DOUBLE_JUMP_DURATION
                        current_segment['double_jump_powerups'].pop(i)
                        break
            
            # Multiplier Pickup Collection
            if current_segment.get('multiplier_pickups'):
                for i in range(len(current_segment['multiplier_pickups']) - 1, -1, -1):
                    pickup = current_segment['multiplier_pickups'][i]
                    dist_sq = (pickup['x'] - ball_pos[0])**2 + \
                              (pickup['y'] + point_hover_offset - ball_pos[1])**2 + \
                              (pickup['z'] - ball_pos[2])**2
                    if dist_sq < (ball_radius + MULTIPLIER_SIZE / 2.0)**2:
                        score_multiplier = MULTIPLIER_FACTOR
                        multiplier_timer = MULTIPLIER_DURATION
                        current_segment['multiplier_pickups'].pop(i)
                        break
            
            # Boost Pad Collision
            if current_segment.get('boost_pads'):
                for boost_pad in current_segment['boost_pads']:
                    if boost_pad['active']:
                        lane_x_left = x_offset - (num_lanes * base_lane_width / 2.0) + (boost_pad['lane_idx'] * base_lane_width)
                        lane_x_right = lane_x_left + base_lane_width
                        
                        is_over_boost_x = (ball_pos[0] >= lane_x_left - ball_radius) and (ball_pos[0] <= lane_x_right + ball_radius)
                        is_over_boost_z = (ball_pos[2] >= boost_pad['z_start'] - ball_radius) and (ball_pos[2] <= boost_pad['z_end'] + ball_radius)
                        
                        if is_over_boost_x and is_over_boost_z:
                            is_boost_active = True
                            forward_speed *= BOOST_PAD_SPEED_BOOST 
                            boost_timer = BOOST_DURATION
                            boost_pad['active'] = False 
                            break 

            # Shield Pickup Collection
            if current_segment.get('shields'):
                for i in range(len(current_segment['shields']) - 1, -1, -1):
                    shield_icon = current_segment['shields'][i]
                    dist_sq = (shield_icon['x'] - ball_pos[0])**2 + \
                              (shield_icon['y'] + point_hover_offset - ball_pos[1])**2 + \
                              (shield_icon['z'] - ball_pos[2])**2
                    if dist_sq < (ball_radius + SHIELD_SIZE / 2.0)**2:
                        has_shield_active = True
                        shield_charge_count += 1
                        shield_timer = SHIELD_DURATION 
                        current_segment['shields'].pop(i)
                        break

        # --- Ultimate Game Over Condition (Falling below defined threshold) ---
        if ball_pos[1] < fall_threshold_y:
            game_state = STATE_ANIMATING_DEATH
            death_animation_timer = PARTICLE_LIFETIME
            breaking_particles = generate_explosion_particles(ball_pos, ball_radius, BALL_COLOR_FLAT)
            return 
        
        glutPostRedisplay()


    elif game_state == STATE_ANIMATING_DEATH:
        death_animation_timer -= dt
        if death_animation_timer <= 0:
            breaking_particles = [] 
            # Check if this animation was for an obstacle break or ball death
            if is_obstacle_breaking_active: # If it was an obstacle breaking, resume play
                is_obstacle_breaking_active = False # Reset flag
                game_state = STATE_PLAYING # Resume playing
            else: # It was the ball's death animation
                game_state = STATE_GAME_OVER 
                game_over = True 
        else:
            for particle in breaking_particles:
                particle['vy'] += GRAVITY * dt 
                particle['x'] += particle['vx'] * dt
                particle['y'] += particle['vy'] * dt 
                particle['z'] += particle['vz'] * dt
                particle['lifetime_remaining'] -= dt
        glutPostRedisplay()

    elif game_state == STATE_GAME_OVER:
        glutPostRedisplay()


# ---------- Render ----------



# Background Starfield Generation Helper
def generate_background_elements():
    global background_elements_distant, background_elements_mid
    start_z_offset = ball_pos[2] - camera_distance - BG_Z_ACTIVE_RANGE / 2 
    background_elements_distant = []
    for _ in range(NUM_BG_ELEMENTS_DISTANT):
        x = random.uniform(-BG_X_RANGE / 2, BG_X_RANGE / 2)
        y = random.uniform(FLOOR_Y + platform_thickness, FLOOR_Y + BG_Y_RANGE)
        z = random.uniform(start_z_offset, start_z_offset + BG_Z_ACTIVE_RANGE)
        size = random.uniform(BG_MIN_SIZE, BG_MIN_SIZE * 2)
        t = random.random()
        color = (
            BG_COLOR_BASE1[0] * (1-t) + BG_COLOR_BASE2[0] * t,
            BG_COLOR_BASE1[1] * (1-t) + BG_COLOR_BASE2[1] * t,
            BG_COLOR_BASE1[2] * (1-t) + BG_COLOR_BASE2[2] * t
        )
        background_elements_distant.append({'x': x, 'y': y, 'z': z, 'size': size, 'color': color})
    background_elements_mid = []
    for _ in range(NUM_BG_ELEMENTS_MID):
        x = random.uniform(-BG_X_RANGE / 2, BG_X_RANGE / 2)
        y = random.uniform(FLOOR_Y + platform_thickness, FLOOR_Y + BG_Y_RANGE)
        z = random.uniform(start_z_offset, start_z_offset + BG_Z_ACTIVE_RANGE)
        size = random.uniform(BG_MIN_SIZE * 1.5, BG_MAX_SIZE)
        t = random.random()
        color = (
            BG_COLOR_BASE1[0] * (1-t) + BG_COLOR_BASE2[0] * t,
            BG_COLOR_BASE1[1] * (1-t) + BG_COLOR_BASE2[1] * t,
            BG_COLOR_BASE1[2] * (1-t) + BG_COLOR_BASE2[2] * t
        )
        background_elements_mid.append({'x': x, 'y': y, 'z': z, 'size': size, 'color': color})

def showScreen(): ### CRITICAL FIX: Obstacle Animation Drawing and Clean HUD ###
    """Display function to render the game scene with robust state management."""
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluPerspective(fovY, ASPECT, 2.0, 3000.0)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    setupCamera()
    
    glEnable(GL_DEPTH_TEST)

    draw_background()
    draw_platform_tiled()
    
    draw_points()
    draw_double_jump_powerups()
    draw_multiplier_pickups()
    draw_boost_pads() 
    draw_shields()

    # --- CRITICAL FIX: Draw ball and / or particles based on state ---
    if game_state == STATE_PLAYING: 
        draw_ball_shadow() 
        draw_ball()
        # If an obstacle is currently breaking *during playing*, draw its particles
        if is_obstacle_breaking_active and breaking_particles:
            draw_breaking_particles()
    elif game_state == STATE_ANIMATING_DEATH: # This means the ball is breaking OR an obstacle finished breaking and we're about to resume
        draw_breaking_particles() 
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    # --- 2D HUD Rendering Pass ---
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_W, 0, WINDOW_H)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    
    # --- HUD Text Drawing ---
    hud_left_x = 10
    hud_line_spacing = 30 
    
    draw_text(hud_left_x, WINDOW_H - hud_line_spacing, 
              f"Ball: x={ball_pos[0]:.1f}, y={ball_pos[1]:.1f}, z={ball_pos[2]:.1f}")
              
    draw_text(hud_left_x, WINDOW_H - hud_line_spacing * 2, 
              "Controls: A/D = steer, SPACE = Jump , R = Reset")
    
    score_text = f"Score: {player_score}"
    score_text_width_approx = len(score_text) * 10 
    draw_text(WINDOW_W - score_text_width_approx - hud_left_x, WINDOW_H - hud_line_spacing, 
              score_text)
    
    # REMOVED: Debug text (platform_segments[0]['debug_text']) - as per request
    # No, it was requested to KEEP the debug text, but remove the duplicate.
    # The previous code correctly places it at hud_line_spacing * 4
    # Re-adding if statement for debug text based on your previous valid code.
    if platform_segments:
        draw_text(hud_left_x, WINDOW_H - hud_line_spacing * 4, 
                  platform_segments[0]['debug_text'])

    # NEW: Draw power-up status
    draw_powerup_status()

    if game_state == STATE_GAME_OVER: 
        game_over_text = "GAME OVER!"
        restart_text = "Press 'R' to Restart"
        
        game_over_width = sum(glutBitmapWidth(GLUT_BITMAP_HELVETICA_18, ord(c)) for c in game_over_text)
        restart_text_width = sum(glutBitmapWidth(GLUT_BITMAP_HELVETICA_18, ord(c)) for c in restart_text)
        
        # Center game over text horizontally and vertically
        draw_text(WINDOW_W/2 - (game_over_width/2), WINDOW_H/2, 
                  game_over_text, font=GLUT_BITMAP_HELVETICA_18)
        # Center restart text horizontally and offset vertically below game over text
        draw_text(WINDOW_W/2 - (restart_text_width/2), WINDOW_H/2 - 30, 
                  restart_text)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    glutSwapBuffers()

# ---------- Helpers ----------
def reset_ball(): ### MODIFIED: Reset Shield State ###
    global ball_pos, is_falling, game_over, is_grounded, game_state
    global fall_velocity_x, fall_velocity_y, platform_segments, last_platform_tile_z_end
    global keys_pressed, segments_since_last_hole, segments_since_last_obstacle, segments_since_last_moving_obstacle
    global segments_until_hazards_start, breaking_particles, death_animation_timer, player_score
    global has_double_jump_charge, double_jump_timer, score_multiplier, multiplier_timer, is_boost_active, boost_timer
    global has_shield_active, shield_charge_count, shield_timer, forward_speed # All power-up globals here
    global is_obstacle_breaking_active # CRITICAL FIX: Reset obstacle breaking flag

    ball_pos = [0.0, FLOOR_Y + ball_radius, -100.0]
    
    is_falling = False 
    game_over = False 
    is_grounded  = True 
    game_state = STATE_PLAYING 
    is_obstacle_breaking_active = False # CRITICAL FIX: Initialize obstacle breaking flag
    
    fall_velocity_x, fall_velocity_y = 0.0, 0.0

    platform_segments = []
    breaking_particles = [] 
    death_animation_timer = 0.0 
    player_score = 0 

    # --- Reset Power-up/Boost States (CRITICAL FIX) ---
    has_double_jump_charge = False
    double_jump_timer = 0.0
    score_multiplier = 1
    multiplier_timer = 0.0
    is_boost_active = False
    boost_timer = 0.0
    forward_speed = -500.0 
    has_shield_active = False ### NEW: Reset shield state ###
    shield_charge_count = 0 ### NEW: Reset shield charges ###
    shield_timer = 0.0 ### NEW: Reset shield timer ###

    last_platform_tile_z_end = ball_pos[2] 
    
    segments_since_last_hole = MIN_SEGMENTS_BETWEEN_HOLES
    segments_since_last_obstacle = MIN_SEGMENTS_BETWEEN_OBSTACLES
    segments_since_last_moving_obstacle = MIN_SEGMENTS_BETWEEN_MOVING_OBSTACLES
    
    segments_until_hazards_start = INITIAL_SAFE_SEGMENTS_COUNT 

    for _ in range(num_visible_tiles): 
        last_gen_segment = platform_segments[-1] if platform_segments else None
        generate_platform_tile(last_gen_segment)
    
    generate_background_elements()
    keys_pressed = {}

# ---------- Main ----------
def main(): ### MODIFIED: Removed glShadeModel for compliance ###
    global last_time_ms
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_W, WINDOW_H)
    glutInitWindowPosition(100, 50)
    glutCreateWindow(b"Slopey+ Platformer")
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glClearDepth(1.0)
    glClearColor(0.05, 0.05, 0.08, 1.0)
    # REMOVED: glShadeModel(GL_SMOOTH) # Not allowed by template rules

    # Hooks
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutKeyboardUpFunc(keyboardUpListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    
    reset_ball()
    glutMainLoop()

if __name__ == "__main__":
    main()