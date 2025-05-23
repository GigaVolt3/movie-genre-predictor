from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
import math
import requests
from io import StringIO

app = Flask(__name__)

MOVIES_CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'movie.csv')

def load_and_preprocess_data():
    # Check if we should load from URL
    dataset_url = os.environ.get('DATASET_URL')
    
    if dataset_url:
        try:
            # Try to download the dataset from URL
            response = requests.get(dataset_url)
            response.raise_for_status()
            df = pd.read_csv(StringIO(response.text))
        except Exception as e:
            print(f"Error loading dataset from URL, falling back to local file: {e}")
            df = pd.read_csv(MOVIES_CSV_PATH)
    else:
        # Load from local file
        df = pd.read_csv(MOVIES_CSV_PATH)

    # Data validation and preprocessing
    required_columns = ['budget', 'runtime', 'director', 'genre']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"CSV is missing required columns: {', '.join(missing_columns)}")

    # Clean the data
    df = df.dropna(subset=required_columns).reset_index(drop=True)
    df['budget'] = pd.to_numeric(df['budget'], errors='coerce')
    df['runtime'] = pd.to_numeric(df['runtime'], errors='coerce')
    df = df.dropna(subset=['budget', 'runtime'])

    # Normalize numerical features
    df['budget_norm'] = (df['budget'] - df['budget'].min()) / (df['budget'].max() - df['budget'].min())
    df['runtime_norm'] = (df['runtime'] - df['runtime'].min()) / (df['runtime'].max() - df['runtime'].min())

    return df

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

@app.route('/')
def home():
    directors = sorted(df['director'].dropna().unique())
    return render_template('index.html', directors=directors)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        budget = float(data['budget'])
        duration = float(data['duration'])

        budget_norm = (budget - df['budget'].min()) / (df['budget'].max() - df['budget'].min())
        runtime_norm = (duration - df['runtime'].min()) / (df['runtime'].max() - df['runtime'].min())

        distances = calculate_distances(df, budget_norm, runtime_norm)
        k = 5
        k_nearest = get_k_nearest_neighbors(distances, k)
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
    app.run(debug=True)
