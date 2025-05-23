import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

# Load and preprocess the data
def load_and_preprocess_data():
    # Load the dataset
    df = pd.read_csv('boxoffice.csv')
    
    # Frequency encoding for Director column
    director_freq = df['Director'].value_counts().to_dict()
    df['Director_Freq'] = df['Director'].map(director_freq)
    
    # Prepare features and target
    X = df[['Budget (INR Crores)', 'Duration (mins)', 'Director_Freq']]
    y = df['Genre']
    
    # Scale the features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    return X_scaled, y, scaler, director_freq, df

# Train the KNN model
def train_knn(X, y, n_neighbors=5):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    knn = KNeighborsClassifier(n_neighbors=n_neighbors)
    knn.fit(X_train, y_train)
    
    # Evaluate the model
    y_pred = knn.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True)
    
    return knn, accuracy, report

# Load data and train model
X, y, scaler, director_freq, df = load_and_preprocess_data()
knn_model, accuracy, report = train_knn(X, y)

@app.route('/')
def index():
    # Get unique genres and directors for the dropdowns
    genres = sorted(df['Genre'].unique())
    directors = sorted(df['Director'].unique())
    return render_template('index.html', genres=genres, directors=directors)

@app.route('/api/directors')
def get_directors():
    # Return JSON list of all unique directors
    directors = sorted(df['Director'].unique().tolist())
    return jsonify(directors)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        
        # Get director frequency (default to 1 if not in training data)
        director_freq_val = director_freq.get(data['director'], 1)
        
        # Prepare input features
        input_data = np.array([[
            float(data['budget']),
            float(data['duration']),
            director_freq_val
        ]])
        
        # Scale the input
        input_scaled = scaler.transform(input_data)
        
        # Make prediction
        prediction = knn_model.predict(input_scaled)[0]
        
        # Get prediction probabilities
        probas = knn_model.predict_proba(input_scaled)[0]
        classes = knn_model.classes_
        confidence_scores = {}
        
        # Calculate confidence for each class
        for i, class_name in enumerate(classes):
            confidence_scores[class_name] = round(probas[i] * 100, 2)
        
        # Sort by confidence
        confidence_scores = dict(sorted(confidence_scores.items(), key=lambda x: x[1], reverse=True))
        
        # Get top 3 predictions
        top_predictions = [
            {'genre': genre, 'confidence': conf}
            for genre, conf in list(confidence_scores.items())[:3]
        ]
        
        return jsonify({
            'status': 'success',
            'prediction': prediction,
            'confidence_scores': confidence_scores,
            'top_predictions': top_predictions,
            'model_accuracy': round(accuracy * 100, 2)
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)