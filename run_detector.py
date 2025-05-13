from room_detector import RoomDetector
import time
import sys

def print_analysis(analysis):
    """Print room analysis in a formatted way"""
    print("\n" + "="*50)
    print("Room Analysis Update")
    print("="*50)
    
    print(f"\nRoom Type: {analysis['room_type'].title() if analysis['room_type'] else 'Unknown'}")
    
    print("\nDetected Objects:")
    for obj in analysis['detected_objects']:
        print(f"- {obj}")
    
    print("\nSuggestions:")
    for suggestion in analysis['suggestions']:
        print(f"- {suggestion}")
    
    if analysis['warnings']:
        print("\nWarnings:")
        for warning in analysis['warnings']:
            print(f"- {warning}")
    
    print("\n" + "="*50)

def main():
    print("Starting Room Detection System...")
    print("Press 'q' to quit")
    print("Initializing camera...")
    
    try:
        detector = RoomDetector()
        detector.start_detection(callback=print_analysis)
        
        while True:
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nStopping detection...")
        detector.stop_detection()
        print("Detection stopped.")
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 