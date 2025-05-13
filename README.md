# Real-Time Room Object Detection System

This project implements a real-time room and object detection system using YOLOv8 and OpenCV. It can detect common room objects and provide real-time feedback through your webcam.

## Features

- Real-time object detection using YOLOv8
- Support for 80+ common objects (COCO dataset)
- Custom training capability for room-specific objects
- FPS counter and confidence scores
- Optimized for low-resource environments

## Requirements

- Python 3.8+
- Webcam
- CUDA-capable GPU (optional, but recommended for better performance)

## Installation

1. Install the required packages:
```bash
pip install -r requirements.txt
```

2. Download the YOLOv8 pretrained model (automatically done on first run)

## Usage

### Real-time Detection

Run the detection script:
```bash
python room_detector.py
```

- Press 'q' to quit the application
- The system will show bounding boxes around detected objects with their labels and confidence scores
- FPS counter is displayed in the top-left corner

### Training on Custom Dataset

1. Prepare your dataset in the following structure:
```
dataset/
├── train/
│   ├── images/
│   └── labels/
└── val/
    ├── images/
    └── labels/
```

2. Run the training script:
```bash
python train_model.py
```

The script will:
- Create a dataset configuration file
- Train the model on your custom dataset
- Save the trained model as 'room_detector.pt'

## Dataset Preparation

For custom training, you'll need to:

1. Collect images of rooms and objects
2. Label the images using a tool like [LabelImg](https://github.com/tzutalin/labelImg)
3. Convert labels to YOLO format
4. Organize the dataset in the structure shown above

## Performance Optimization

The system is optimized for real-time performance:

- Uses the smallest YOLOv8 model (YOLOv8n) by default
- Implements efficient frame processing
- Supports GPU acceleration
- Configurable confidence threshold

## Customization

You can customize the system by:

1. Modifying the confidence threshold in `room_detector.py`
2. Adding new classes in the training script
3. Adjusting the model size (YOLOv8n, YOLOv8s, YOLOv8m, YOLOv8l, YOLOv8x)
4. Changing the input resolution

## License

MIT License 