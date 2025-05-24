import csv
import math
import random
from collections import defaultdict, Counter
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Global variable to store our movie data
movies = []
genres = set()

def load_data():
    global movies, genres, directors
    directors = set()  # Store unique directors
    try:
        import os
        
        # Path to local CSV file
        csv_path = os.path.join(os.path.dirname(__file__), 'dmdw.csv')
        
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found at: {csv_path}")
            
        print(f"Loading data from: {csv_path}")
        
        # Read the local CSV file
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            print(f"CSV columns: {reader.fieldnames}")  # Debug: Print column names
            
            # Read all rows while the file is still open
            rows = list(reader)
        
        # Process the rows after the file is closed
        for i, row in enumerate(rows, 1):
            try:
                # Debug: Print first few rows
                if i <= 5:
                    print(f"Row {i}: {row}")
                    
                # Clean and map the row data
                try:
                    # Parse budget - handle potential commas and convert to float
                    budget_str = row.get('Budget (INR Crores)', '0').strip().replace(',', '')
                    movie = {
                        'title': row.get('Title', '').strip() or f"{row.get('Director', '').strip()}'s Movie {i}",
                        'budget': float(budget_str) * 10000000,  # Convert crores to actual amount
                        'duration': int(float(row.get('Duration (mins)', '0').strip())),
                        'director': row.get('Director', '').strip(),
                        'genre': row.get('Genre', 'Unknown').strip()
                    }
                except (ValueError, AttributeError) as e:
                    print(f"Error parsing row {i}: {e}")
                    continue
                
                # Only add if we have valid budget and duration
                if movie['budget'] > 0 and movie['duration'] > 0:
                    movies.append(movie)
                    genres.add(movie['genre'])
                    if movie['director']:  # Only add non-empty director names
                        directors.add(movie['director'])
                else:
                    print(f"Skipping row {i} - invalid budget or duration values")
                    
            except (ValueError, KeyError) as e:
                print(f"Error processing row {i}: {e}")
                continue
        
        if not movies:
            raise ValueError("No valid movie data was loaded from the CSV file.")
            
        # Convert genres to list for consistent ordering
        genres = sorted(list(genres))
        print(f"Loaded {len(movies)} movies with {len(genres)} unique genres.")
        print(f"Sample movie: {movies[0]}")
        print(f"Available genres: {genres}")
        
    except Exception as e:
        raise Exception(f"Error loading data: {str(e)}")
    finally:
        # Ensure we have a valid reader before proceeding
        if 'reader' not in locals():
            raise Exception("Failed to initialize CSV reader. No data source available.")

def calculate_target_encoding():
    # Calculate target encoding for directors
    director_genres = defaultdict(list)
    
    # Group movies by director
    for movie in movies:
        director_genres[movie['director']].append(movie['genre'])
    
    # Calculate genre distribution for each director
    director_encoding = {}
    for director, genre_list in director_genres.items():
        total = len(genre_list)
        genre_count = Counter(genre_list)
        director_encoding[director] = {genre: genre_count.get(genre, 0) / total for genre in genres}
    
    return director_encoding

def normalize_features():
    if not movies:
        raise ValueError("No movies available for feature normalization.")
    
    # Find min and max for normalization
    budgets = [movie['budget'] for movie in movies]
    durations = [movie['duration'] for movie in movies]
    
    if not budgets or not durations:
        raise ValueError("No valid budget or duration data available for normalization.")
    
    min_budget, max_budget = min(budgets), max(budgets)
    min_duration, max_duration = min(durations), max(durations)
    
    print(f"Budget range: {min_budget} - {max_budget}")
    print(f"Duration range: {min_duration} - {max_duration}")
    
    # Handle case where all values are the same (to avoid division by zero)
    budget_range = max_budget - min_budget
    duration_range = max_duration - min_duration
    
    if budget_range == 0:
        print("Warning: All budget values are the same.")
        budget_range = 1
    if duration_range == 0:
        print("Warning: All duration values are the same.")
        duration_range = 1
    
    # Normalize features
    for movie in movies:
        movie['norm_budget'] = (movie['budget'] - min_budget) / budget_range
        movie['norm_duration'] = (movie['duration'] - min_duration) / duration_range
    
    print(f"Normalization complete. Sample normalized values:")
    for i, movie in enumerate(movies[:3], 1):
        print(f"  Movie {i}: budget={movie['norm_budget']:.4f}, duration={movie['norm_duration']:.4f}")
    
    return min_budget, max_budget, min_duration, max_duration

def euclidean_distance(movie1, movie2, director_encoding):
    # Calculate distance for numerical features
    budget_diff = movie1['norm_budget'] - movie2['norm_budget']
    duration_diff = movie1['norm_duration'] - movie2['norm_duration']
    
    # Calculate distance for director (using target encoding)
    dir1 = director_encoding[movie1['director']]
    dir2 = director_encoding[movie2['director']]
    
    dir_distance = 0
    for genre in genres:
        dir_distance += (dir1.get(genre, 0) - dir2.get(genre, 0)) ** 2
    
    # Combine all distances
    return math.sqrt(budget_diff**2 + duration_diff**2 + dir_distance)

def knn_predict(k, test_movie, director_encoding):
    distances = []
    
    for movie in movies:
        if movie == test_movie:  # Skip the test movie itself
            continue
            
        dist = euclidean_distance(test_movie, movie, director_encoding)
        distances.append({
            'distance': dist,
            'genre': movie['genre'],
            'title': movie['title'],
            'budget': movie['budget'] / 10000000,  # Convert back to crores
            'duration': movie['duration'],
            'director': movie['director']
        })
    
    # Sort by distance and get k nearest neighbors
    distances.sort(key=lambda x: x['distance'])
    k_nearest = distances[:k]
    
    # Perform majority voting
    genre_votes = Counter(neighbor['genre'] for neighbor in k_nearest)
    predicted_genre = genre_votes.most_common(1)[0][0]
    
    return {
        'predicted_genre': predicted_genre,
        'neighbors': k_nearest,
        'genre_distribution': genre_votes,
        'total_neighbors': k
    }

@app.route('/')
def home():
    try:
        # Get unique directors from movies, ensuring we have valid director names
        unique_directors = sorted(list(set(movie['director'] for movie in movies if movie.get('director', '').strip())))
        
        if not unique_directors:
            print("Warning: No directors found in the dataset")
            unique_directors = ["Unknown Director"]
            
        print(f"Rendering template with {len(unique_directors)} directors")
        return render_template('index.html', directors=unique_directors, genres=sorted(genres))
    except Exception as e:
        print(f"Error in home route: {str(e)}")
        # Return default values in case of error
        return render_template('index.html', directors=["Unknown Director"], genres=[])

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    print(f"Received prediction request: {data}")
    
    # Generate test movie
    try:
        director = data.get('director', '').strip()
        if not director:
            return jsonify({'error': 'Director name is required'}), 400
            
        test_movie = {
            'budget': float(data.get('budget', 0)) * 10000000,  # Convert from crores to actual amount
            'duration': int(float(data.get('duration', 0))),
            'director': director,
            'title': 'Your Movie'  # Placeholder for the test movie
        }
        print(f"Created test movie: {test_movie}")
    except (ValueError, TypeError) as e:
        return jsonify({'error': f'Invalid input data: {str(e)}'}), 400
    
    # Normalize features
    min_budget, max_budget, min_duration, max_duration = normalize_features()
    test_movie['norm_budget'] = (test_movie['budget'] - min_budget) / (max_budget - min_budget + 1e-10)
    test_movie['norm_duration'] = (test_movie['duration'] - min_duration) / (max_duration - min_duration + 1e-10)
    
    # Get prediction with k=5
    k = 5
    result = knn_predict(k, test_movie, director_encoding)
    
    # Prepare response
    response = {
        'predicted_genre': result['predicted_genre'],
        'neighbors': result['neighbors'],
        'genre_distribution': result['genre_distribution'],
        'total_neighbors': k,
        'test_movie': {
            'title': test_movie['title'],
            'budget': test_movie['budget'] / 10000000,  # Convert back to crores
            'duration': test_movie['duration'],
            'director': test_movie['director']
        }
    }
    
    return jsonify(response)

if __name__ == '__main__':
    # Load and preprocess data
    load_data()
    director_encoding = calculate_target_encoding()
    normalize_features()
    
    # Get list of directors for the dropdown
    directors = sorted(list(set(movie['director'] for movie in movies)))
    
    # Add directors to app context
    app.directors = directors
    
    app.run(debug=True)
