import cv2
import numpy as np
from ultralytics import YOLO
import torch
import time
import threading
from collections import defaultdict, deque
import logging
from room_analyzer import RoomAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RoomDetector:
    def __init__(self, model_path='yolov8n.pt', confidence_threshold=0.5):
        # Initialize YOLO model
        self.model = YOLO(model_path)
        self.confidence_threshold = confidence_threshold
        
        # COCO dataset classes for indoor objects
        self.indoor_classes = {
            0: 'person', 1: 'bicycle', 2: 'car', 3: 'motorcycle', 4: 'airplane',
            5: 'bus', 6: 'train', 7: 'truck', 8: 'boat', 9: 'traffic light',
            10: 'fire hydrant', 11: 'stop sign', 12: 'parking meter', 13: 'bench',
            14: 'bird', 15: 'cat', 16: 'dog', 17: 'horse', 18: 'sheep',
            19: 'cow', 20: 'elephant', 21: 'bear', 22: 'zebra', 23: 'giraffe',
            24: 'backpack', 25: 'umbrella', 26: 'handbag', 27: 'tie', 28: 'suitcase',
            29: 'frisbee', 30: 'skis', 31: 'snowboard', 32: 'sports ball',
            33: 'kite', 34: 'baseball bat', 35: 'baseball glove', 36: 'skateboard',
            37: 'surfboard', 38: 'tennis racket', 39: 'bottle', 40: 'wine glass',
            41: 'cup', 42: 'fork', 43: 'knife', 44: 'spoon', 45: 'bowl',
            46: 'banana', 47: 'apple', 48: 'sandwich', 49: 'orange', 50: 'broccoli',
            51: 'carrot', 52: 'hot dog', 53: 'pizza', 54: 'donut', 55: 'cake',
            56: 'chair', 57: 'couch', 58: 'potted plant', 59: 'bed', 60: 'dining table',
            61: 'toilet', 62: 'tv', 63: 'laptop', 64: 'mouse', 65: 'remote',
            66: 'keyboard', 67: 'cell phone', 68: 'microwave', 69: 'oven',
            70: 'toaster', 71: 'sink', 72: 'refrigerator', 73: 'book', 74: 'clock',
            75: 'vase', 76: 'scissors', 77: 'teddy bear', 78: 'hair drier', 79: 'toothbrush'
        }
        
        # Indoor-specific object mappings
        self.indoor_mappings = {
            'dining table': 'table',
            'potted plant': 'plant',
            'hair drier': 'hairdryer',
            'cell phone': 'phone',
            'remote': 'remote control',
            'toilet': 'bathroom',
            'toothbrush': 'bathroom item',
            'hair drier': 'bathroom item',
            'sink': 'bathroom sink',
            'oven': 'stove',
            'microwave': 'microwave oven',
            'refrigerator': 'fridge',
            'tv': 'television',
            'laptop': 'computer',
            'mouse': 'computer mouse',
            'keyboard': 'computer keyboard',
            'book': 'books',
            'clock': 'wall clock',
            'vase': 'decoration',
            'teddy bear': 'toy',
            'scissors': 'office item',
            'bottle': 'water bottle',
            'cup': 'drinking glass',
            'wine glass': 'glass',
            'bowl': 'dish',
            'fork': 'utensil',
            'knife': 'utensil',
            'spoon': 'utensil'
        }
        
        self.detection_thread = None
        self.is_running = False
        self.frame_buffer = deque(maxlen=30)  # 1 second buffer at 30 FPS
        self.last_analysis_time = 0
        self.analysis_interval = 5  # seconds between analyses
        self.room_analyzer = RoomAnalyzer()
        self.current_analysis = None
        self.callback = None
        
        # Performance metrics
        self.fps = 0
        self.frame_count = 0
        self.start_time = time.time()
        
    def start_detection(self, video_source=0, callback=None):
        """Start the detection thread"""
        if self.is_running:
            return
            
        self.is_running = True
        self.callback = callback
        self.detection_thread = threading.Thread(target=self._detection_loop, args=(video_source,))
        self.detection_thread.daemon = True
        self.detection_thread.start()
        
    def stop_detection(self):
        """Stop the detection thread"""
        self.is_running = False
        if self.detection_thread:
            self.detection_thread.join()
            
    def _detection_loop(self, video_source):
        """Main detection loop"""
        cap = cv2.VideoCapture(video_source)
        
        while self.is_running:
            ret, frame = cap.read()
            if not ret:
                break
                
            # Run detection
            results = self.model(frame, conf=self.confidence_threshold)[0]
            
            # Process detections
            detected_objects = []
            confidence_scores = {}
            
            for box in results.boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                class_name = results.names[class_id]
                
                # Map class name to indoor-specific name if available
                mapped_name = self.indoor_mappings.get(class_name, class_name)
                
                detected_objects.append(mapped_name)
                confidence_scores[mapped_name] = confidence
                
                # Draw bounding box
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{mapped_name} {confidence:.2f}", 
                          (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Update FPS
            self.frame_count += 1
            if time.time() - self.start_time > 1:
                self.fps = self.frame_count
                self.frame_count = 0
                self.start_time = time.time()
            
            # Add frame to buffer
            self.frame_buffer.append(frame)
            
            # Analyze room periodically
            current_time = time.time()
            if current_time - self.last_analysis_time >= self.analysis_interval:
                self.current_analysis = self.room_analyzer.analyze_room(detected_objects, confidence_scores)
                self.last_analysis_time = current_time
                
                if self.callback:
                    self.callback(self.current_analysis)
            
            # Display frame with FPS
            cv2.putText(frame, f"FPS: {self.fps}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow('Room Detection', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        cap.release()
        cv2.destroyAllWindows()
        
    def get_current_analysis(self):
        """Get the current room analysis"""
        return self.current_analysis
        
    def get_latest_frame(self):
        """Get the latest frame from the buffer"""
        return self.frame_buffer[-1] if self.frame_buffer else None

# Example usage
if __name__ == "__main__":
    def analysis_callback(analysis):
        print("\nRoom Analysis Update:")
        print(f"Room Type: {analysis['room_type']}")
        print("\nSuggestions:")
        for suggestion in analysis['suggestions']:
            print(f"- {suggestion}")
        if analysis['warnings']:
            print("\nWarnings:")
            for warning in analysis['warnings']:
                print(f"- {warning}")
    
    detector = RoomDetector()
    detector.start_detection(callback=analysis_callback)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        detector.stop_detection() 