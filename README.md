# Project Instructions

This project contains two main components:
- **imageEditor**: A simple image editing tool.
- **game**: A tank-based game.

Follow the steps below to set up and run each component.

---

## Prerequisites

- Python 3.8 or higher
- Recommended: Create and activate a virtual environment
- Install required packages:

```bash
pip install -r requirements.txt
```

---

## 1. Running the Image Editor

1. Open a terminal and navigate to the `imageEditor` directory:
   ```bash
   cd imageEditor
   ```
2. Run the image editor script:
   ```bash
   python imageEditor.py
   ```
3. The editor will open and allow you to edit `image.png` or other images as per the script's functionality.

**Note:**
- Edited images may be saved as `cropped_image.png` or other output files, depending on the script.
- Ensure `image.png` exists in the `imageEditor` folder.

---

## 2. Running the Game

1. Open a terminal and navigate to the `game` directory:
   ```bash
   cd game
   ```
2. Run the main game script:
   ```bash
   python main.py
   ```
3. The game window will launch. Follow on-screen instructions to play.

**Notes:**
- Game assets (images, high score file) are located in the `assets` subfolders. Do not move or delete these files.
- High scores are saved in `assets/files/high_score.txt`.

---

## Troubleshooting

- If you encounter missing module errors, ensure all dependencies are installed with `pip install -r requirements.txt`.
- For issues with images or assets, verify the folder structure matches the repository.

---

## Project Structure

```
README.md
requirements.txt
imageEditor/
    imageEditor.py
    image.png
    cropped_image.png
...
game/
    main.py
    assets/
        images/
        files/
            high_score.txt
...
```
