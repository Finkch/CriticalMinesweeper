# Shows board state using Pygame
import pygame

# Window size
WS = 500

# Grid cells visible in a row/column
ZOOM = 20
OOB = ZOOM // 2

CELL_SIZE = WS // ZOOM

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (200, 50, 50)
BLUE = (50, 50, 200)
DGREY = (75, 75, 75)
LGREY = (150, 150, 150)

pygame.init()
screen = pygame.display.set_mode((WS, WS))
pygame.display.set_caption("Critical Minesweeper")

font = pygame.font.Font(None, 18)  # None for default font, 36 for size


def see(minesweeper, index):

    grid = minesweeper.grids[index]
    cell = minesweeper.cells[index]

    if len(minesweeper.torqs) > 0:
        neighbours = minesweeper.torqs[index]

    # Clear the screen
    screen.fill(BLACK)

    # Draw the grid
    for pos in grid:
        draw(grid, pos)

    # Draws the revealed cell
    draw(grid, cell, RED)

    # Draws new adjacent cells
    if len(minesweeper.torqs) > 0:
        for npos in neighbours:
            draw(grid, npos, BLUE)

    # Update the display
    pygame.display.flip()


# Draws a cell
def draw(grid, pos, colour = None):
    x, y = pos[0], pos[1]

    # Only draws if cell is on screen
    if not (x < -OOB or x > OOB or y < -OOB or y > OOB):

        if not colour:
            if grid[pos] & 4:
                colour = LGREY
            elif grid[pos] & 2:
                colour = DGREY
            else:
                colour = WHITE


        pygame.draw.rect(
            screen,
            colour,
            (x * CELL_SIZE + OOB * CELL_SIZE, y * CELL_SIZE + OOB * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        )
        
        # Draws a border around the cell
        pygame.draw.rect(
                screen,
                BLACK,
                (x * CELL_SIZE + OOB * CELL_SIZE, y * CELL_SIZE + OOB * CELL_SIZE, CELL_SIZE, CELL_SIZE),
                1  # Border thickness
            )
        
        # Draws cell value
        text_surface = font.render(str(grid[pos]), True, BLACK)
        text_rect = text_surface.get_rect(center=(
            x * CELL_SIZE + CELL_SIZE // 2 + OOB * CELL_SIZE,
            y * CELL_SIZE + CELL_SIZE // 2 + OOB * CELL_SIZE
        ))
        screen.blit(text_surface, text_rect)


# Shows user the board and iterates between board states
def visualise(minesweeper):
    
    # Main loop
    running = True
    index = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False


            index = keys(event, len(minesweeper.cells), index)

        see(minesweeper, index)
        #pygame.display.flip()  # Update the display

# Function to handle navigation
def keys(event, length, index):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_RIGHT:  # Go forward
            return (index + 1) % length  # Loop back to start
        elif event.key == pygame.K_LEFT:  # Go backward
            return (index - 1) % length  # Loop to the end
    return index
     


        