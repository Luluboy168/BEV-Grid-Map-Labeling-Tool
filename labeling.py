import pygame
import os
import json

# Config
GRID_SIZE = 5
GRID_CELL = 200  # Grid cell size
image_height = GRID_CELL * GRID_SIZE
image_width = int(image_height * 16 / 9)  # 16:9 image

LABEL_COLORS = {0: (255, 255, 255), 1: (255, 0, 0)}  # 0: empty, 1: vehicle

IMAGE_FOLDER = 'images'
PANOPTIC_FOLDER = 'panoptic'
LABEL_FOLDER = 'labels'
os.makedirs(LABEL_FOLDER, exist_ok=True)

def load_images(folder):
    return sorted(f for f in os.listdir(folder) if f.lower().endswith(('.png', '.jpg', '.jpeg')))

def save_label(image_name, grid):
    path = os.path.join(LABEL_FOLDER, os.path.splitext(image_name)[0] + ".json")
    with open(path, "w") as f:
        json.dump(grid, f)
    print(f"Saved: {path}")

def load_label(image_name):
    path = os.path.join(LABEL_FOLDER, os.path.splitext(image_name)[0] + ".json")
    if os.path.exists(path):
        with open(path, "r") as f:
            grid = json.load(f)
        print(f"Loaded label: {path}")
        return grid
    else:
        return [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

def draw_grid(screen, grid, offset_x):
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            color = LABEL_COLORS[grid[row][col]]
            rect = pygame.Rect(offset_x + col * GRID_CELL, row * GRID_CELL, GRID_CELL - 2, GRID_CELL - 2)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (0, 0, 0), rect, 1)

def main():
    pygame.init()
    images = load_images(IMAGE_FOLDER)
    index = 0
    running = True

    while running and 0 <= index < len(images):
        filename = images[index]
        name_stem = os.path.splitext(filename)[0]

        # Load raw images (do NOT convert yet)
        image_path = os.path.join(IMAGE_FOLDER, filename)
        image_raw = pygame.image.load(image_path)

        panoptic_path = os.path.join(PANOPTIC_FOLDER, name_stem + ".png")
        panoptic_raw = pygame.image.load(panoptic_path) if os.path.exists(panoptic_path) else None

        # Prepare display
        image_size = GRID_CELL * GRID_SIZE
        window_width = image_width + image_height  # left: image (16:9), right: grid (square)
        window_height = image_height
        screen = pygame.display.set_mode((window_width, window_height))
        pygame.display.set_caption(f"Labeling: {filename}")

        image = pygame.transform.scale(image_raw.convert(), (image_width, image_height))
        if panoptic_raw:
            panoptic = pygame.transform.scale(panoptic_raw.convert_alpha(), (image_width, image_height))
            panoptic.set_alpha(128)  # semi-transparent
            blended = image.copy()
            blended.blit(panoptic, (0, 0))  # overlay panoptic mask
        else:
            blended = image
            print(f"Warning: Panoptic mask not found for {filename}")

        # Load grid.jpg
        grid_path = "grid.png"
        if os.path.exists(grid_path):
            grid_image = pygame.image.load(grid_path).convert()
            # grid_image = pygame.transform.scale(grid_image, (image_size, image_size))
            grid_image = pygame.transform.scale(grid_image, (image_width, image_height))
            grid_image.set_colorkey((255, 255, 255))  # Treat white as transparent
            blended.blit(grid_image, (0, 0))  # Overlay grid
        else:
            print("Warning: grid.jpg not found, skipping grid overlay.")

        # Load existing label if exists
        grid = load_label(filename)
        next_image = False

        while not next_image and running:
            screen.fill((0, 0, 0))
            screen.blit(blended, (0, 0))  # Left: blended image
            draw_grid(screen, grid, offset_x=image_width)  # Right: grid
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

                    elif event.key == pygame.K_s:
                        save_label(filename, grid)
                        index += 1
                        next_image = True

                    elif event.key == pygame.K_a:  # ← previous image
                        index = max(0, index - 1)
                        next_image = True

                    elif event.key == pygame.K_d:  # → next image (without saving)
                        index = min(len(images) - 1, index + 1)
                        next_image = True
                    
                    elif event.key == pygame.K_x:
                        os.remove(os.path.join(IMAGE_FOLDER, filename))
                        print(f"Deleted: {filename}")
                        images.pop(index)
                        if index >= len(images):
                            index = len(images) - 1
                        next_image = True

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    x, y = pygame.mouse.get_pos()
                    if x >= image_width:
                        col = (x - image_width) // GRID_CELL
                        row = y // GRID_CELL
                        if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
                            grid[row][col] ^= 1  # toggle 0 <-> 1

    pygame.quit()

if __name__ == "__main__":
    main()
