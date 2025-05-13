from ultralytics import YOLO
import yaml
from pathlib import Path

def create_dataset_yaml(data_dir, train_dir, val_dir, classes):
    """Create YAML configuration file for the dataset"""
    yaml_data = {
        'path': str(data_dir),
        'train': str(train_dir),
        'val': str(val_dir),
        'names': {i: name for i, name in enumerate(classes)}
    }
    
    yaml_path = data_dir / 'dataset.yaml'
    with open(yaml_path, 'w') as f:
        yaml.dump(yaml_data, f)
    
    return yaml_path

def train_model(data_yaml, epochs=100, batch_size=16, img_size=640):
    """Train YOLOv8 model on custom dataset"""
    # Initialize model
    model = YOLO('yolov8n.pt')  # Load pretrained model
    
    # Train the model
    results = model.train(
        data=str(data_yaml),
        epochs=epochs,
        batch=batch_size,
        imgsz=img_size,
        patience=50,  # Early stopping patience
        save=True,    # Save best model
        device='0'    # Use GPU if available
    )
    
    return model

if __name__ == "__main__":
    # Define your dataset structure
    data_dir = Path('dataset')
    train_dir = data_dir / 'train'
    val_dir = data_dir / 'val'
    
    # Define your classes
    classes = [
        'chair', 'table', 'bed', 'sofa', 'tv', 'lamp', 'desk',
        'bookshelf', 'plant', 'clock', 'picture', 'window', 'door'
    ]
    
    # Create dataset YAML
    yaml_path = create_dataset_yaml(data_dir, train_dir, val_dir, classes)
    
    # Train model
    model = train_model(yaml_path)
    
    # Save the trained model
    model.save('room_detector.pt') 