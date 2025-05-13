from flask import Flask, render_template, Response, jsonify
from flask_cors import CORS
import cv2
import numpy as np
from room_detector import RoomDetector
import threading
import time
import json
from flask_socketio import SocketIO, emit

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Global detector instance
detector = None
detector_thread = None
is_running = False

def generate_frames():
    """Generate video frames for streaming"""
    global detector, is_running
    
    while is_running:
        if detector and detector.cap is not None:
            ret, frame = detector.cap.read()
            if not ret:
                break
                
            # Process frame
            detections = detector.process_frame(frame)
            frame = detector.draw_detections(frame, detections)
            
            # Convert frame to JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
        time.sleep(0.01)  # Small delay to prevent CPU overload

def emit_room_analysis():
    """Emit room analysis updates via WebSocket"""
    global detector, is_running
    
    while is_running:
        if detector:
            analysis = detector.get_room_analysis()
            socketio.emit('room_analysis', analysis)
        time.sleep(1)  # Update every second

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_detection')
def start_detection():
    """Start the room detection"""
    global detector, detector_thread, is_running
    
    if not is_running:
        detector = RoomDetector(device='auto')
        is_running = True
        
        # Start detection thread
        detector_thread = threading.Thread(target=detector.run)
        detector_thread.start()
        
        # Start analysis emission thread
        analysis_thread = threading.Thread(target=emit_room_analysis)
        analysis_thread.daemon = True
        analysis_thread.start()
        
        return jsonify({'status': 'success', 'message': 'Detection started'})
    return jsonify({'status': 'error', 'message': 'Detection already running'})

@app.route('/stop_detection')
def stop_detection():
    """Stop the room detection"""
    global detector, is_running
    
    if is_running:
        is_running = False
        if detector:
            detector.is_running = False
            if detector.cap is not None:
                detector.cap.release()
        return jsonify({'status': 'success', 'message': 'Detection stopped'})
    return jsonify({'status': 'error', 'message': 'Detection not running'})

@app.route('/get_metrics')
def get_metrics():
    """Get current performance metrics"""
    global detector
    if detector:
        return jsonify(detector.get_performance_metrics())
    return jsonify({'status': 'error', 'message': 'Detector not initialized'})

@app.route('/get_room_analysis')
def get_room_analysis():
    """Get current room analysis"""
    global detector
    if detector:
        return jsonify(detector.get_room_analysis())
    return jsonify({'status': 'error', 'message': 'Detector not initialized'})

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    emit('connection_response', {'data': 'Connected'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000) 