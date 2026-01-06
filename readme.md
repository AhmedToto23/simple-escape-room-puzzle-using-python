🧩 Simple Escape Room Puzzle Using Python

A 3D first-person escape room puzzle game built with Python + OpenGL, where the player solves board-based riddles to progress through multiple levels and unlock the final ending.


🎮 Game Overview

This project is a simple escape room experience featuring:

First-person camera movement

Interactive puzzle boards instead of doors

Text-based riddles with real-time input

Multiple levels with different questions

UI panels rendered with OpenGL

Final fullscreen image before game exit

The goal is to solve all puzzles correctly to complete the game.


🧠 Gameplay Flow

Player spawns inside a room

A board appears on the wall

Player looks at the board and clicks it

A UI puzzle panel appears

Player types the answer

✅ Correct → Next level
❌ Wrong → Error message

Final level displays an image for 5 seconds, then exits


🏗️ Project Structure

C:.
│   main.py                # Main game logic and loop
│   camera.py              # First-person camera
│   mesh.py                # Cube mesh (used for all objects)
│   shader.py              # Shader loader and manager
│   texture.py             # Texture loading utilities
│   text_renderer.py       # Font and text rendering
│   ui_text.py             # UI text helpers
│
├── assets
│   └── textures
│       ├── floor.jpg
│       ├── wall.jpg
│       ├── door.jpg
│       └── final_image.jpg
│
├── fonts
│   └── about_font.TTF
│
├── shaders
│   ├── vertex.glsl
│   ├── fragment.glsl
│   ├── text_vertex.glsl
│   ├── text_fragment.glsl
│   ├── image_vertex.glsl
│   ├── image_fragment.glsl
│   ├── ui_vertex.glsl
│   └── ui_fragment.glsl


🧩 Levels & Puzzles
Level	Question	Answer
1	What is 5 + 7?	12
2	Who lives in the sea and is loved by people?	SpongeBob SquarePants
3	Who is the best doctor ever?	hataba

🎉 After Level 3, a final image appears and the game closes automatically.

🛠️ Technologies Used

Python 3.10+

OpenGL (PyOpenGL)

GLFW

GLM

Pillow (PIL)

FreeType

🚀 How to Run

1️⃣ Install Dependencies

pip install glfw PyOpenGL PyOpenGL_accelerate Pillow freetype-py PyGLM numpy


2️⃣ Run the Game

python main.py


⚠️ The game runs in fullscreen mode.


🎮 Controls
Action	Control
Move	W A S D
Look around	Mouse
Interact	Left Mouse Button
Type answer	Keyboard
Submit answer	Enter
Delete	Backspace


✨ Features

✔ First-person 3D environment
✔ Interactive puzzle boards
✔ Custom OpenGL UI system
✔ Smooth text rendering
✔ Multiple levels
✔ Final cinematic ending


📌 Future Improvements

Sound effects & background music

Animated boards

More puzzle types

Save system

Menu screen

Timed challenges


👤 Author

Ahmed Toto
