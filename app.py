from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
import math
import requests
from io import StringIO
import sys

app = Flask(__name__)

MOVIES_CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'movie.csv')

def load_and_preprocess_data():
    print("Starting data loading process...", file=sys.stderr)
    
    # Check if we should load from URL
    dataset_url = os.environ.get('DATASET_URL')
    
    try:
        if dataset_url:
            print(f"Attempting to load dataset from URL: {dataset_url}", file=sys.stderr)
            try:
                # Try to download the dataset from URL
                response = requests.get(dataset_url, timeout=30)
                response.raise_for_status()
                df = pd.read_csv(StringIO(response.text))
                print("Successfully loaded dataset from URL", file=sys.stderr)
            except Exception as e:
                print(f"Error loading dataset from URL: {e}", file=sys.stderr)
                raise
        else:
            print(f"Loading dataset from local file: {MOVIES_CSV_PATH}", file=sys.stderr)
            try:
                df = pd.read_csv(MOVIES_CSV_PATH)
            except Exception as e:
                print(f"Error loading local dataset: {e}", file=sys.stderr)
                raise

        # Data validation and preprocessing
        print("Validating data...", file=sys.stderr)
        required_columns = ['budget', 'runtime', 'director', 'genre']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            error_msg = f"CSV is missing required columns: {', '.join(missing_columns)}"
            print(error_msg, file=sys.stderr)
            raise ValueError(error_msg)

        # Clean the data
        print("Cleaning data...", file=sys.stderr)
        df = df.dropna(subset=required_columns).reset_index(drop=True)
        df['budget'] = pd.to_numeric(df['budget'], errors='coerce')
        df['runtime'] = pd.to_numeric(df['runtime'], errors='coerce')
        df = df.dropna(subset=['budget', 'runtime'])

        # Check if we have enough data
        if len(df) == 0:
            error_msg = "No valid data available after cleaning"
            print(error_msg, file=sys.stderr)
            raise ValueError(error_msg)

        # Normalize numerical features
        print("Normalizing features...", file=sys.stderr)
        df['budget_norm'] = (df['budget'] - df['budget'].min()) / (df['budget'].max() - df['budget'].min())
        df['runtime_norm'] = (df['runtime'] - df['runtime'].min()) / (df['runtime'].max() - df['runtime'].min())

        print(f"Successfully loaded and preprocessed {len(df)} records", file=sys.stderr)
        return df
        
    except Exception as e:
        print(f"Critical error in load_and_preprocess_data: {str(e)}", file=sys.stderr)
        print(f"Error type: {type(e).__name__}", file=sys.stderr)
        raise

def calculate_distances(df, input_budget_norm, input_runtime_norm):
    distances = []
    for idx, row in df.iterrows():
        budget_diff = (input_budget_norm - row['budget_norm']) ** 2
        runtime_diff = (input_runtime_norm - row['runtime_norm']) ** 2
        distance = math.sqrt(budget_diff + runtime_diff)
        distances.append((distance, idx))
    return distances

def get_k_nearest_neighbors(distances, k):
    distances.sort(key=lambda x: x[0])
    return distances[:k]

def predict_genre(df, neighbors):
    genre_votes = {}
    for _, idx in neighbors:
        genre = df.iloc[idx]['genre']
        genre_votes[genre] = genre_votes.get(genre, 0) + 1
    return max(genre_votes.items(), key=lambda x: x[1])[0]

df = load_and_preprocess_data()

# Define K value at the module level for easy access
K_VALUE = 79

@app.route('/')
def home():
    directors = sorted(df['director'].dropna().unique())
    return render_template('index.html', directors=directors, k_value=K_VALUE)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        budget = float(data['budget'])
        duration = float(data['duration'])

        budget_norm = (budget - df['budget'].min()) / (df['budget'].max() - df['budget'].min())
        runtime_norm = (duration - df['runtime'].min()) / (df['runtime'].max() - df['runtime'].min())

        distances = calculate_distances(df, budget_norm, runtime_norm)
        k_nearest = get_k_nearest_neighbors(distances, K_VALUE)  # Use the module-level K_VALUE
        all_distances = distances[:1000]

        prediction = predict_genre(df, k_nearest)

        k_nearest_data = []
        for i, (dist, idx) in enumerate(k_nearest):
            movie = df.iloc[idx]
            k_nearest_data.append({
                'rank': i + 1,
                'distance': round(dist, 4),
                'budget': float(movie['budget']),
                'runtime': float(movie['runtime']),
                'director': movie['director'],
                'genre': movie['genre']
            })

        all_distances_data = []
        for i, (dist, idx) in enumerate(all_distances):
            movie = df.iloc[idx]
            all_distances_data.append({
                'rank': i + 1,
                'distance': round(dist, 4),
                'budget': float(movie['budget']),
                'runtime': float(movie['runtime']),
                'director': movie['director'],
                'genre': movie['genre']
            })
            if len(all_distances_data) >= 1000:
                break

        return jsonify({
            'status': 'success',
            'prediction': prediction,
            'best_k': k,
            'k_nearest': k_nearest_data,
            'all_distances': all_distances_data
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

if __name__ == '__main__':
    # Get port from environment variable or use default 5000
    port = int(os.environ.get('PORT', 5000))
    # Run the app
    app.run(host='0.0.0.0', port=port, debug=False)
