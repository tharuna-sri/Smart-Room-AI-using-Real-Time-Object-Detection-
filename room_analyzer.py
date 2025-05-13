from collections import defaultdict
import time

class RoomAnalyzer:
    def __init__(self):
        self.safety_items = {
            'fire extinguisher': 'Safety',
            'smoke detector': 'Safety',
            'first aid kit': 'Safety',
            'emergency exit': 'Safety'
        }
        
        # Enhanced room scenarios with more indoor objects
        self.room_scenarios = {
            'bedroom': {
                'required': ['bed'],
                'optional': ['lamp', 'tv', 'chair', 'desk', 'window', 'dresser', 'mirror', 'nightstand', 'wardrobe'],
                'suggestions': {
                    'default': "I notice this is a bedroom. Would you like me to adjust the lighting for a more relaxing atmosphere?",
                    'with_tv': "Perfect setup for a movie night! Would you like some movie recommendations?",
                    'with_desk': "This looks like a great workspace. I can help you optimize the lighting for productivity.",
                    'with_window': "I can help you control the natural light based on the time of day.",
                    'with_mirror': "I notice you have a mirror. Would you like some lighting suggestions for getting ready?"
                }
            },
            'living_room': {
                'required': ['couch'],
                'optional': ['tv', 'coffee table', 'lamp', 'plant', 'window', 'bookshelf', 'rug', 'armchair', 'fireplace'],
                'suggestions': {
                    'default': "This looks like a cozy living room. Would you like some ambient lighting suggestions?",
                    'with_plant': "Your plants might need some care. Would you like watering reminders?",
                    'entertainment': "Perfect for entertainment! I can suggest some activities based on the time of day.",
                    'with_bookshelf': "I see you have a bookshelf. Would you like some reading recommendations?",
                    'with_fireplace': "I notice you have a fireplace. Would you like some cozy atmosphere suggestions?"
                }
            },
            'kitchen': {
                'required': ['sink'],
                'optional': ['oven', 'refrigerator', 'microwave', 'table', 'stove', 'dishwasher', 'cabinet', 'counter', 'toaster'],
                'suggestions': {
                    'default': "I see you're in the kitchen. Would you like some recipe suggestions?",
                    'cooking': "I can help you set the perfect cooking environment. Need any assistance?",
                    'safety': "Let me check if all safety features are properly set up.",
                    'with_appliances': "I notice you have several appliances. Would you like some energy-saving tips?"
                }
            },
            'office': {
                'required': ['desk'],
                'optional': ['chair', 'computer', 'lamp', 'window', 'bookshelf', 'printer', 'filing cabinet', 'whiteboard'],
                'suggestions': {
                    'default': "This looks like a productive workspace. Would you like some focus-enhancing suggestions?",
                    'ergonomic': "I can help you optimize your workspace for better ergonomics.",
                    'lighting': "Let me adjust the lighting for optimal productivity.",
                    'with_bookshelf': "I see you have a bookshelf. Would you like some organization tips?"
                }
            }
        }
        
        self.interaction_history = []
        self.last_suggestion_time = defaultdict(float)
        self.suggestion_cooldown = 300  # 5 minutes between similar suggestions
        
    def analyze_room(self, detected_objects, confidence_scores=None):
        """Analyze the room and generate personalized suggestions"""
        current_time = time.time()
        suggestions = []
        warnings = []
        
        # Check for safety items
        missing_safety = self._check_safety_items(detected_objects)
        if missing_safety:
            warnings.append(f"I notice some important safety items might be missing: {', '.join(missing_safety)}")
        
        # Determine room type and generate suggestions
        room_type = self._determine_room_type(detected_objects)
        if room_type:
            room_suggestions = self._generate_room_suggestions(room_type, detected_objects)
            suggestions.extend(room_suggestions)
        
        # Add time-based suggestions
        time_suggestions = self._get_time_based_suggestions(detected_objects)
        if time_suggestions:
            suggestions.extend(time_suggestions)
        
        # Record interaction
        self._record_interaction(detected_objects, suggestions, warnings)
        
        return {
            'room_type': room_type,
            'suggestions': suggestions,
            'warnings': warnings,
            'detected_objects': detected_objects
        }
    
    def _check_safety_items(self, detected_objects):
        """Check for missing safety items"""
        return [item for item in self.safety_items if item not in detected_objects]
    
    def _determine_room_type(self, detected_objects):
        """Determine the type of room based on detected objects"""
        room_scores = defaultdict(int)
        
        for room_type, criteria in self.room_scenarios.items():
            # Check required items
            if all(item in detected_objects for item in criteria['required']):
                room_scores[room_type] += 2
            # Check optional items
            room_scores[room_type] += sum(1 for item in criteria['optional'] if item in detected_objects)
        
        if room_scores:
            return max(room_scores.items(), key=lambda x: x[1])[0]
        return None
    
    def _generate_room_suggestions(self, room_type, detected_objects):
        """Generate suggestions based on room type and detected objects"""
        suggestions = []
        room_info = self.room_scenarios[room_type]
        
        # Add default suggestion
        suggestions.append(room_info['suggestions']['default'])
        
        # Add specific suggestions based on detected objects
        if room_type == 'bedroom':
            if 'tv' in detected_objects:
                suggestions.append(room_info['suggestions']['with_tv'])
            if 'desk' in detected_objects:
                suggestions.append(room_info['suggestions']['with_desk'])
            if 'mirror' in detected_objects:
                suggestions.append(room_info['suggestions']['with_mirror'])
        elif room_type == 'living_room':
            if 'plant' in detected_objects:
                suggestions.append(room_info['suggestions']['with_plant'])
            if 'bookshelf' in detected_objects:
                suggestions.append(room_info['suggestions']['with_bookshelf'])
            if 'fireplace' in detected_objects:
                suggestions.append(room_info['suggestions']['with_fireplace'])
        elif room_type == 'kitchen':
            if any(item in detected_objects for item in ['oven', 'microwave', 'stove']):
                suggestions.append(room_info['suggestions']['cooking'])
            if any(item in detected_objects for item in ['oven', 'refrigerator', 'dishwasher']):
                suggestions.append(room_info['suggestions']['with_appliances'])
        elif room_type == 'office':
            if 'bookshelf' in detected_objects:
                suggestions.append(room_info['suggestions']['with_bookshelf'])
        
        return suggestions
    
    def _get_time_based_suggestions(self, detected_objects):
        """Generate time-based suggestions"""
        suggestions = []
        current_hour = time.localtime().tm_hour
        
        if 6 <= current_hour < 12:
            if 'bed' in detected_objects:
                suggestions.append("Good morning! Would you like me to help you start your day with some energizing lighting?")
        elif 12 <= current_hour < 18:
            if 'desk' in detected_objects:
                suggestions.append("It's a great time for productivity. Would you like some focus-enhancing suggestions?")
        elif 18 <= current_hour < 22:
            if 'tv' in detected_objects or 'couch' in detected_objects:
                suggestions.append("Perfect time for relaxation. Would you like some entertainment suggestions?")
        else:
            if 'bed' in detected_objects:
                suggestions.append("It's getting late. Would you like me to help you create a sleep-friendly environment?")
        
        return suggestions
    
    def _record_interaction(self, detected_objects, suggestions, warnings):
        """Record the interaction for future reference"""
        self.interaction_history.append({
            'timestamp': time.time(),
            'detected_objects': detected_objects,
            'suggestions': suggestions,
            'warnings': warnings
        })
        
        # Keep only last 100 interactions
        if len(self.interaction_history) > 100:
            self.interaction_history.pop(0)

# Example usage
if __name__ == "__main__":
    analyzer = RoomAnalyzer()
    
    # Test with different scenarios
    test_objects = ["bed", "tv", "lamp", "window", "dresser", "mirror"]
    analysis = analyzer.analyze_room(test_objects)
    
    print("\nRoom Analysis:")
    print(f"Room Type: {analysis['room_type']}")
    print("\nSuggestions:")
    for suggestion in analysis['suggestions']:
        print(f"- {suggestion}")
    if analysis['warnings']:
        print("\nWarnings:")
        for warning in analysis['warnings']:
            print(f"- {warning}") 