# 🍌 PlantWatch - Banana Ripeness Detection System

**Authors:**
- Wan Zafirzan Bin Wan Tarmizan (A22MJ8003)
- Safuan Hakim Bin Shani (A22MJ8014)

**Group:** Group 2 - PlantWatch

---

## Project Description

An AI-powered web application that uses **YOLOv8 deep learning** to detect banana ripeness levels in real-time through a webcam. The system classifies bananas into four categories (Unripe, Ripe, Overripe, Rotten) and provides harvestability recommendations to help farmers and consumers assess fruit quality.

### Features
- 📷 Real-time camera detection with front/back camera switching
- 🎯 Ripeness classification (Unripe, Ripe, Overripe, Rotten)
- 📊 Confidence score display
- 🌿 Harvestability recommendations

---

## How to Run

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the Application
```bash
python main.py
```

### Step 3: Open in Browser
Navigate to: **http://127.0.0.1:5000**

Click on **"Fruit Detection"** to start the camera and detect banana ripeness.

---

## Expected Output

1. **Terminal Output:**
```
============================================================
PlantWatch - Banana Ripeness Detection System
Authors: A22MJ8003 & A22MJ8014 | Group 2 - PlantWatch
============================================================

Downloading model weights...
Model downloaded successfully!
Starting server...
Open http://127.0.0.1:5000 in your browser
Navigate to 'Fruit Detection' to use the camera

 * Running on http://127.0.0.1:5000
```

2. **Browser Output:**
   - Home page with project information
   - Fruit Detection page with live camera feed
   - Real-time bounding boxes around detected bananas
   - Ripeness classification with confidence percentage
   - Harvestability status and recommendations

### Ripeness Categories

| Status | Recommendation |
|--------|----------------|
| 🟢 **Ripe** | Harvestable - Ready for consumption |
| 🟡 **Unripe** | Not Ready - Wait 3-5 days |
| 🔴 **Overripe** | Past Optimal - Use for baking |
| ⚫ **Rotten** | Not Consumable - Discard |

---

## Technology Stack

- **Deep Learning:** YOLOv8 (Ultralytics)
- **Backend:** Flask (Python)
- **Frontend:** HTML5, CSS3, JavaScript
- **Computer Vision:** OpenCV

---

## Notes

- The model weights (~6MB) are automatically downloaded on first run
- Requires a webcam for real-time detection
- Works on both desktop and mobile browsers (camera permission required)
