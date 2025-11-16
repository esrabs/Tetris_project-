# Tetris Game – Python Academic Project

## Description
This project was developed as part of a university programming assignment. It is a complete implementation of the classic Tetris game written in Python, using a custom graphical interface (interface.py) provided by the instructor. No external libraries such as Pygame are used; all rendering is performed through a constrained grid-based API. The goal of the project is to reproduce the core mechanics of Tetris while respecting strict limitations on rendering, input handling, and data structures.

## Main Features
- Standard 10×20 Tetris playfield  
- Movement controls: left, right, rotation, soft drop  
- Rotation system with wall-kick behavior  
- Collision detection with borders and placed blocks  
- Line clearing system supporting 1 to 4 simultaneous clears  
- Official scoring system:  
  - 1 line: +40  
  - 2 lines: +200  
  - 3 lines: +300  
  - 4 lines: +1200  
- Next tetromino preview panel  
- Dual-piece mode after clearing 2 or more lines  
  - Switch between pieces using the space bar  
  - Horizontal pushing allowed  
- Clean and refined user interface with thin borders

## Technologies Used
- Python 3  
- Custom interface module (interface.py) for:  
  - Grid rendering  
  - Colored cell drawing  
  - Keyboard input  
  - Cursor positioning  
- No external dependencies

## Installation
1. Clone the repository using your GitHub link.  
2. Ensure tetris.py and interface.py are in the same directory.  
3. Run the game using:  
   python tetris.py

## Usage
- Left / Right arrows: move horizontally  
- Up arrow: rotate  
- Down arrow: soft drop  
- Space bar: switch between active pieces (dual-piece mode only)  

The right panel shows the score and the next tetromino.

## Demonstration
You may add screenshots or a GIF of the gameplay here.

## Authors
Project developed by Your Name  
Part of the University Informatics curriculum.
