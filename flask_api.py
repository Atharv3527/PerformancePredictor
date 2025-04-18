from flask import Flask, request, jsonify, render_template, send_from_directory
import pandas as pd
import numpy as np
import os
from sklearn.ensemble import RandomForestRegressor
from flask_cors import CORS
import json

app = Flask(__name__, 
    static_folder='static',
    template_folder='templates')
CORS(app)  # Enable CORS for all routes

# File path for permanent data storage
DATA_FILE = 'student_data.json'

# Initialize student data store
students = []

# Load existing data if file exists
def load_data():
    global students
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as file:
                students = json.load(file)
                print(f"Loaded {len(students)} students from {DATA_FILE}")
        except Exception as e:
            print(f"Error loading data: {e}")
            students = []
    else:
        print(f"Data file {DATA_FILE} not found. Starting with empty dataset.")
        students = []
        # Add sample data if no data exists
        add_sample_data()
        # Save sample data
        save_data()

# Save data to file
def save_data():
    try:
        with open(DATA_FILE, 'w') as file:
            json.dump(students, file, indent=4)
        print(f"Data saved to {DATA_FILE}")
    except Exception as e:
        print(f"Error saving data: {e}")

# Add sample data if no data exists
def add_sample_data():
    global students
    if not students:
        students.append({
            'name': 'John Smith',
            'study_hours': 6, 
            'attendance': 85,
            'previous_grades': 78,
            'participation_score': 7,
            'socio_economic_status': 'Middle',
            'extracurricular': 'Medium',
            'learning_style': 'Visual',
            'gender': 'Male',
            'parents_education': 'Graduate',
            'study_environment': 'Quiet',
            'parent_meeting_freq': 'Sometimes',
            'home_support': 'Moderate',
            'sleep_duration': 7.5,
            'stress_level': 'Moderate',
            'physical_activity': 'Moderate',
            'peer_group_quality': 'Good',
            'submission_timeliness': 'Good',
            'performance': 82
        })
        students.append({
            'name': 'Emma Johnson',
            'study_hours': 8, 
            'attendance': 92,
            'previous_grades': 88,
            'participation_score': 9,
            'socio_economic_status': 'High',
            'extracurricular': 'High',
            'learning_style': 'Reading/Writing',
            'gender': 'Female',
            'parents_education': 'Post-Graduate',
            'study_environment': 'Quiet',
            'parent_meeting_freq': 'Frequently',
            'home_support': 'High',
            'sleep_duration': 8,
            'stress_level': 'Low',
            'physical_activity': 'High',
            'peer_group_quality': 'Excellent',
            'submission_timeliness': 'Excellent',
            'performance': 90
        })
        students.append({
            'name': 'Michael Brown',
            'study_hours': 4, 
            'attendance': 70,
            'previous_grades': 65,
            'participation_score': 6,
            'socio_economic_status': 'Low',
            'extracurricular': 'Low',
            'learning_style': 'Kinesthetic',
            'gender': 'Male',
            'parents_education': 'Secondary',
            'study_environment': 'Noisy',
            'parent_meeting_freq': 'Rarely',
            'home_support': 'Low',
            'sleep_duration': 6,
            'stress_level': 'High',
            'physical_activity': 'Low',
            'peer_group_quality': 'Average',
            'submission_timeliness': 'Average',
            'performance': 68
        })

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/api/students', methods=['GET'])
def get_students():
    return jsonify(students)

@app.route('/api/students/<int:student_index>', methods=['DELETE'])
def delete_student(student_index):
    try:
        if 0 <= student_index < len(students):
            deleted_student = students.pop(student_index)
            save_data()  # Save changes to file
            return jsonify({
                "message": "Student deleted successfully",
                "deleted_student": deleted_student
            }), 200
        else:
            return jsonify({"error": "Student not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/students', methods=['POST'])
def add_student():
    student_data = request.json
    
    # If performance is not provided, calculate it
    if 'performance' not in student_data:
        prediction_result = make_prediction(student_data)
        student_data['performance'] = prediction_result['prediction']
    
    students.append(student_data)
    save_data()  # Save changes to file
    return jsonify({"message": "Student added successfully", "student": student_data}), 201

@app.route('/api/predict', methods=['POST'])
def predict():
    student_data = request.json
    prediction_result = make_prediction(student_data)
    return jsonify(prediction_result)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    return jsonify(calculate_stats())

def make_prediction(data):
    """Makes a prediction based on student data and returns prediction with suggestions"""
    # Create a more sophisticated prediction model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    
    # Sample training data - expanded with additional features
    # Format: [study_hours, attendance, previous_grades, participation_score, 
    #          socio_economic, extracurricular, learning_style, gender, parents_edu, study_env,
    #          parent_meeting_freq, home_support, sleep_duration, stress_level, physical_activity,
    #          peer_group_quality, submission_timeliness]
    
    # Encoding explanation:
    # For socio_economic: 0=Low, 1=Middle, 2=High
    # For extracurricular: 0=None, 1=Low, 2=Medium, 3=High
    # For learning_style: 0=Visual, 1=Auditory, 2=Reading/Writing, 3=Kinesthetic
    # For gender: 0=Male, 1=Female, 2=Other
    # For parents_education: 0=Primary, 1=Secondary, 2=Higher, 3=Graduate, 4=Post-Graduate
    # For study_environment: 0=Quiet, 1=Moderate, 2=Noisy
    # For parent_meeting_freq: 0=Never, 1=Rarely, 2=Sometimes, 3=Frequently
    # For home_support: 0=Low, 1=Moderate, 2=High
    # For stress_level: 0=Low, 1=Moderate, 2=High, 3=Very High
    # For physical_activity: 0=None, 1=Low, 2=Moderate, 3=High
    # For peer_group_quality: 0=Poor, 1=Average, 2=Good, 3=Excellent
    # For submission_timeliness: 0=Poor, 1=Average, 2=Good, 3=Excellent
    
    X_train = np.array([
        [5, 90, 80, 8, 1, 2, 0, 0, 3, 0, 2, 2, 7, 1, 2, 2, 2],  # Male, parents: Graduate, quiet environment
        [3, 70, 65, 6, 0, 1, 1, 1, 1, 1, 1, 0, 6, 2, 1, 1, 1],  # Female, parents: Secondary, moderate environment
        [7, 95, 85, 9, 2, 3, 2, 0, 4, 0, 3, 2, 8, 0, 3, 3, 3],  # Male, parents: Post-Graduate, quiet environment
        [4, 80, 75, 7, 1, 1, 3, 1, 2, 1, 2, 1, 7, 1, 2, 2, 2],  # Female, parents: Higher, moderate environment
        [6, 85, 80, 8, 1, 2, 0, 0, 3, 0, 2, 2, 8, 1, 2, 2, 3],  # Male, parents: Graduate, quiet environment
        [2, 60, 55, 5, 0, 0, 1, 1, 0, 2, 0, 0, 5, 3, 0, 0, 0],  # Female, parents: Primary, noisy environment
        [8, 98, 90, 9, 2, 3, 2, 0, 4, 0, 3, 2, 8, 0, 3, 3, 3],  # Male, parents: Post-Graduate, quiet environment
        [5, 75, 70, 7, 1, 2, 3, 1, 2, 1, 2, 1, 6, 2, 1, 1, 1],  # Female, parents: Higher, moderate environment
    ])
    
    # Target values (student performance)
    y_train = np.array([85, 65, 90, 75, 82, 60, 95, 78])
    
    # Fit the model
    model.fit(X_train, y_train)
    
    # Convert categorical data to numerical for prediction
    socio_economic_map = {'Low': 0, 'Middle': 1, 'High': 2}
    extracurricular_map = {'None': 0, 'Low': 1, 'Medium': 2, 'High': 3}
    learning_style_map = {'Visual': 0, 'Auditory': 1, 'Reading/Writing': 2, 'Kinesthetic': 3}
    gender_map = {'Male': 0, 'Female': 1, 'Other': 2}
    parents_education_map = {'Primary': 0, 'Secondary': 1, 'Higher': 2, 'Graduate': 3, 'Post-Graduate': 4}
    study_environment_map = {'Quiet': 0, 'Moderate': 1, 'Noisy': 2}
    parent_meeting_freq_map = {'Never': 0, 'Rarely': 1, 'Sometimes': 2, 'Frequently': 3}
    home_support_map = {'Low': 0, 'Moderate': 1, 'High': 2}
    stress_level_map = {'Low': 0, 'Moderate': 1, 'High': 2, 'Very High': 3}
    physical_activity_map = {'None': 0, 'Low': 1, 'Moderate': 2, 'High': 3}
    peer_group_quality_map = {'Poor': 0, 'Average': 1, 'Good': 2, 'Excellent': 3}
    submission_timeliness_map = {'Poor': 0, 'Average': 1, 'Good': 2, 'Excellent': 3}
    
    # Get values from data with defaults if not provided
    socio_economic = socio_economic_map.get(data.get('socio_economic_status', 'Middle'), 1)
    extracurricular = extracurricular_map.get(data.get('extracurricular', 'Medium'), 2)
    learning_style = learning_style_map.get(data.get('learning_style', 'Visual'), 0)
    gender = gender_map.get(data.get('gender', 'Male'), 0)
    parents_education = parents_education_map.get(data.get('parents_education', 'Secondary'), 1)
    study_environment = study_environment_map.get(data.get('study_environment', 'Moderate'), 1)
    parent_meeting_freq = parent_meeting_freq_map.get(data.get('parent_meeting_freq', 'Sometimes'), 2)
    home_support = home_support_map.get(data.get('home_support', 'Moderate'), 1)
    sleep_duration = float(data.get('sleep_duration', 7))
    stress_level = stress_level_map.get(data.get('stress_level', 'Moderate'), 1)
    physical_activity = physical_activity_map.get(data.get('physical_activity', 'Moderate'), 2)
    peer_group_quality = peer_group_quality_map.get(data.get('peer_group_quality', 'Average'), 1)
    submission_timeliness = submission_timeliness_map.get(data.get('submission_timeliness', 'Good'), 2)
    
    # Make prediction with the new features
    X_test = np.array([[
        float(data['study_hours']),
        float(data['attendance']),
        float(data['previous_grades']),
        float(data['participation_score']),
        socio_economic,
        extracurricular,
        learning_style,
        gender,
        parents_education,
        study_environment,
        parent_meeting_freq,
        home_support,
        sleep_duration,
        stress_level,
        physical_activity,
        peer_group_quality,
        submission_timeliness
    ]])
    
    prediction = model.predict(X_test)[0]
    
    # Get feature importance for advanced visualization
    feature_names = [
        'study_hours', 'attendance', 'previous_grades', 'participation', 
        'socio_economic', 'extracurricular', 'learning_style', 'gender', 
        'parents_education', 'study_environment', 'parent_meeting_freq', 
        'home_support', 'sleep_duration', 'stress_level', 'physical_activity',
        'peer_group_quality', 'submission_timeliness'
    ]
    
    feature_importance = {
        name: float(importance) for name, importance in zip(feature_names, model.feature_importances_)
    }
    
    # Round the prediction to one decimal place
    prediction = round(prediction, 1)
    
    # Generate personalized suggestions based on prediction and input values
    suggestions = []
    
    # Find the student's weakest areas based on feature importance
    features_with_importance = []
    for feature, importance in feature_importance.items():
        features_with_importance.append((feature, importance))
    
    # Sort by importance (highest first)
    features_with_importance.sort(key=lambda x: x[1], reverse=True)
    
    # Get top features
    top_features = [feature for feature, _ in features_with_importance[:5]]
    
    # Base suggestions on the student's performance and key features
    if prediction < 70:
        # For students needing improvement
        if 'study_hours' in top_features and float(data['study_hours']) < 6:
            suggestions.append("Increase daily study hours to at least 6 hours for better performance")
        
        if 'attendance' in top_features and float(data['attendance']) < 85:
            suggestions.append("Improve class attendance to above 85% to ensure you don't miss critical content")
        
        if 'participation' in top_features and float(data['participation_score']) < 7:
            suggestions.append("Increase active participation in class discussions and activities")
        
        if 'sleep_duration' in top_features and sleep_duration < 7:
            suggestions.append("Aim for 7-8 hours of sleep daily to improve cognitive function and learning retention")
        
        if 'stress_level' in top_features and data.get('stress_level', 'Moderate') in ['High', 'Very High']:
            suggestions.append("Consider stress-reduction techniques like meditation, deep breathing, or counseling services")
        
        if 'physical_activity' in top_features and data.get('physical_activity', 'Moderate') in ['None', 'Low']:
            suggestions.append("Introduce regular physical activity (20-30 minutes daily) to improve concentration and reduce stress")
        
        if 'peer_group_quality' in top_features and data.get('peer_group_quality', 'Average') in ['Poor', 'Average']:
            suggestions.append("Join study groups with high-performing peers to benefit from collaborative learning")
        
        if 'submission_timeliness' in top_features and data.get('submission_timeliness', 'Good') in ['Poor', 'Average']:
            suggestions.append("Improve assignment submission timeliness by creating a submission schedule and calendar reminders")
        
        if 'home_support' in top_features and data.get('home_support', 'Moderate') == 'Low':
            suggestions.append("Seek additional academic support through tutoring or mentoring programs")
        
        if 'parent_meeting_freq' in top_features and data.get('parent_meeting_freq', 'Sometimes') in ['Never', 'Rarely']:
            suggestions.append("Encourage increased parental involvement through regular parent-teacher meetings")
    else:
        # For students already doing well
        suggestions.append("Maintain your current study routine of " + str(data['study_hours']) + " hours daily")
        suggestions.append("Continue your excellent attendance record to stay on top of course material")
        
        if 'learning_style' in top_features:
            learning_style_text = data.get('learning_style', 'Visual')
            suggestions.append(f"Continue leveraging your {learning_style_text} learning style with appropriate study techniques")
        
        if sleep_duration < 7:
            suggestions.append("Consider increasing sleep duration to 7-8 hours for optimal cognitive performance")
        
        if data.get('physical_activity', 'Moderate') in ['None', 'Low']:
            suggestions.append("Incorporate more physical activity for better stress management and overall wellbeing")
    
    # Ensure we have at least 8 suggestions
    general_suggestions = [
        "Develop a structured study plan with specific goals for each session",
        "Use the Pomodoro technique (25-minute focused sessions followed by 5-minute breaks)",
        "Practice retrieval-based studying rather than passive re-reading",
        "Create concept maps to visualize connections between different topics",
        "Teach concepts to others to solidify your understanding",
        "Review material regularly rather than cramming before exams",
        "Take practice tests to improve recall and identify knowledge gaps",
        "Maintain a balanced lifestyle with time for academics, activities, and rest"
    ]
    
    # Add general suggestions if we need more
    while len(suggestions) < 8:
        if not general_suggestions:
            break
        suggestions.append(general_suggestions.pop(0))
    
    # Return prediction result with suggestions
    return {
        "prediction": prediction,
        "performance_category": get_performance_category(prediction),
        "suggestions": suggestions,
        "feature_importance": feature_importance,
        "top_factors": top_features[:3]  # Return top 3 factors
    }

def get_performance_category(score):
    """Convert numerical score to category"""
    if score >= 85:
        return "Excellent"
    elif score >= 70:
        return "Good"
    elif score >= 60:
        return "Average"
    else:
        return "Needs Improvement"

def calculate_stats():
    """Calculate student statistics"""
    if not students:
        return {
            "total_students": 0,
            "average_performance": 0,
            "performance_distribution": {
                "Excellent": 0,
                "Good": 0, 
                "Average": 0,
                "Needs Improvement": 0
            }
        }
    
    # Calculate average performance
    total_students = len(students)
    performances = [s.get('performance', 0) for s in students]
    average_performance = sum(performances) / total_students if total_students > 0 else 0
    average_performance = round(average_performance, 1)
    
    # Calculate performance distribution
    performance_distribution = {
        "Excellent": 0,
        "Good": 0,
        "Average": 0,
        "Needs Improvement": 0
    }
    
    for p in performances:
        category = get_performance_category(p)
        performance_distribution[category] += 1
    
    return {
        "total_students": total_students,
        "average_performance": average_performance,
        "performance_distribution": performance_distribution
    }

# Load data when the application starts
load_data()

if __name__ == '__main__':
    # Create static folder if it doesn't exist
    if not os.path.exists('static'):
        os.makedirs('static')
    
    # Create static/css folder if it doesn't exist
    if not os.path.exists('static/css'):
        os.makedirs('static/css')
    
    # Create static/js folder if it doesn't exist 
    if not os.path.exists('static/js'):
        os.makedirs('static/js')
    
    app.run(debug=True, port=5000) 