# Bird’s Eye View Grid Labeling Tool

This toolset allows you to generate panoptic segmentation masks and manually label 5×5 bird’s-eye-view (BEV) grids on road scene images. It’s designed for creating datasets suitable for training spatial understanding models in autonomous driving or risk prediction systems.

## Folder Structure
```
project/
├── images/ # Input images (JPEG/PNG)
├── panoptic/ # Output masks from panoptic segmentation
├── labels/ # Saved grid labels (JSON)
├── grid.png # (Optional) Overlay grid image
├── data_panoptic.py
├── labeling.py
└── README.md
```

## Requirements

- Python ≥ 3.8
- `torch`
- `transformers`
- `opencv-python`
- `pygame`
- `tqdm`
- CUDA (optional, for faster Mask2Former inference)

Install dependencies:
```bash
pip install torch torchvision transformers opencv-python pygame tqdm
```

## Step-by-Step Usage
### Step 1: Generate Panoptic Masks

Run the following script to perform panoptic segmentation on all images in the images/ folder using Mask2Former (COCO):

```
python data_panoptic.py
```

This will save binary masks (car, bus, truck) to the panoptic/ folder.
You can change CATEGORY_IDS in data_panoptic.py to use other categories if needed.

### Step 2: Manually Label BEV Grids

Launch the interactive labeling tool:

```
python labeling.py
```

Left panel: original image with optional overlays (panoptic + grid.png)
Right panel: a 5×5 grid where each cell can be toggled (white = empty, red = vehicle)

## Controls
| Key        | Action                                |
|------------|----------------------------------------|
| `Left Click` | Toggle grid cell (0 ⇄ 1)             |
| `S`        | Save label and go to next image        |
| `A`        | Go to previous image                   |
| `D`        | Go to next image (without saving)      |
| `X`        | Delete current image                   |
| `Esc`      | Exit the tool                          |

## Output Format

Each labeled sample will save a JSON file (same filename as the image) in the labels/ folder. Example:
```
[
  [0, 0, 1, 0, 0],
  [0, 0, 1, 0, 0],
  [0, 0, 1, 0, 0],
  [0, 0, 0, 0, 0],
  [0, 0, 0, 0, 0]
]
```
>[!NOTE]  
>All input images must be placed in the images/ folder.  
>Panoptic masks must share the same base name as the image (e.g., scene001.jpg → scene001.png  inpanoptic/).
>Including grid.png will add a transparent grid overlay to help visual alignment.

## License

MIT License – free to use, modify, and share.