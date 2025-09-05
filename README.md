# Slopey+ Platformer

## Description

Slopey+ Platformer is a fast-paced 3D arcade-style game developed using Python and OpenGL (GLUT/GLU). Players control a dynamic ball as it auto-rolls forward on an endlessly generated, abstract platform filled with various hazards and collectible power-ups. The goal is to navigate through challenging segments, collect points, avoid obstacles, and survive for as long as possible!

## Features

This game boasts a wide array of dynamic features designed to provide a challenging and visually engaging experience:

### Core Gameplay Mechanics

*   **Player Ball:** A visually striking blue 3D ball that auto-rolls forward.
*   **Physics Engine:** Implements realistic gravity for jumping and falling, with accurate collision detection.
*   **Responsive Controls:** Smooth left/right movement via 'A'/'D' keys, and precise jumping with the 'SPACE' bar.
*   **Dynamic Game States:** Transitions seamlessly between PLAYING, ANIMATING_DEATH (explosion sequence), and GAME_OVER states.

### Procedural Platform Generation

*   **Endless Path:** Platforms are procedurally generated to provide a unique experience every time, creating an infinitely scrolling track.
*   **3D Segments:** Each platform piece has a distinct 3D thickness, adding depth to the environment.
*   **90-Degree Transitions:** All platform width and offset changes are abrupt, 90-degree "steps," creating clear and challenging geometry.
*   **Variety of Segments (Approx. 20+ Types):**
    *   **Normal Paths:** Standard 5-lane centered track.
    *   **Hazardous Tiles:** Full-width paths with random "hole" (background-colored) tiles.
    *   **Shifted Paths:** Entire platforms shifted sharply to the left or right.
    *   **Narrow Paths:** Platforms that reduce to a narrower 3-lane path in the center, or 2-lane paths aligned to the left/right.
    *   **Blockades:** Full-width paths with strategically placed large "hole" sections (e.g., center blockade, left-path/right-path blockades, staggered blocks, funnels, death grids) forcing players into specific narrow passages.

### Interactive Elements

*   **Collectible Points:** Bright yellow, pulsating diamond-shaped icons that hover over safe tiles or static obstacles. Collecting them increases the player's score.
*   **Static Cube Obstacles:** Yellow 3D cubes placed on the platform lanes; collision triggers a destruction animation for the obstacle.
*   **Moving Cylinder Obstacles:** Purple 3D cylinders that move continuously left-to-right across the entire platform width. Collision triggers a destruction animation for the obstacle.
*   **Double Jump Power-up:** Collectible green double-chevron icon. Grants the ability to perform a second jump mid-air for a limited duration.
*   **Score Multiplier Power-up:** Collectible orange "2X" icon. Temporarily doubles the points gained for collected points.
*   **Boost Pad:** Magenta-colored tiles embedded in the platform. Rolling over them provides a temporary burst of forward speed.
*   **Shield Power-up:** Collectible blue icon. Provides a temporary protective aura around the ball.

### Visual & Audio Feedback (Visual Only for Compliance)

*   **Rolling Ball Animation:** The player ball rotates dynamically to simulate realistic rolling motion.
*   **Explosion Animations:** Collision with obstacles (when shielded) or the player ball (when unshielded) triggers a vibrant particle explosion effect.
*   **Power-up Auras/Pulsation:** Collectible points, double jump, multiplier, and shield icons visually pulsate and hover to attract attention. The shield also displays a translucent aura around the ball when active.
*   **Dynamic HUD:** Displays real-time game information:
    *   Ball's current X, Y, Z coordinates.
    *   Current score.
    *   Control instructions.
    *   Detailed status of Double Jump, Boost, Shield, and Multiplier power-ups (ACTIVE/INACTIVE, green/red text).
    *   Debug information for the current platform segment.
*   **Scrolling Starfield Background:** A dynamic background with distant and mid-ground stars/nebula elements that scroll at different speeds, enhancing the sense of depth and motion.

## How to Run

1.  **Ensure Python is installed:** This project requires Python 3.x.
2.  **Install PyOpenGL:**
    ```bash
    pip install PyOpenGL PyOpenGL_accelerate
    ```
3.  **Save the code:** Save the entire Python script (that we've developed) as `main.py` (or any `.py` file).
4.  **Run from terminal:** Navigate to the directory where you saved the file and run:
    ```bash
    python main.py
    ```

### Troubleshooting NameError or rendering issues:

*   **Graphics Drivers:** Ensure your graphics drivers are up to date. Outdated drivers can cause OpenGL issues.
*   **Virtual Machines:** If running in a VM, ensure 3D acceleration is enabled in your VM settings.
*   **Strict Compliance:** If you encounter `NameError` related to OpenGL functions, it's possible a non-compliant function slipped through. Refer to the compliance disclaimer below.

## Controls

*   **A Key:** Move ball left
*   **D Key:** Move ball right
*   **SPACE Key:** Jump (can double jump if power-up is active)
*   **R Key:** Restart Game (only available on "GAME OVER!" screen)