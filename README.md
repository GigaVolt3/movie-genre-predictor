# Movie Genre Predictor

A web application that predicts movie genres based on director, budget, and duration using the K-Nearest Neighbors (KNN) algorithm.

## Features

- Predicts movie genres using three key features:
  - Director (using frequency encoding)
  - Budget (in INR Crores)
  - Duration (in minutes)
- Displays top 3 predicted genres with confidence scores
- Responsive web interface with modern UI
- Model performance metrics

## Live Demo

Check out the live demo: [Movie Genre Predictor](https://movie-genre-predictor.onrender.com)


The application expects a CSV file named `boxoffice.csv` with the following columns:
- `Director`: Name of the movie director
- `Duration (mins)`: Movie duration in minutes
- `Budget (INR Crores)`: Movie budget in Indian Rupees (Crores)
- `Genre`: Movie genre (target variable)

## Model Details

- **Algorithm**: K-Nearest Neighbors (KNN)
- **Features**:
  - Director (frequency encoded)
  - Budget (scaled)
  - Duration (scaled)
- **Evaluation**: Model accuracy is displayed in the web interface

## Project Structure

```
├── app.py                # Main Flask application
├── requirements.txt      # Python dependencies
├── boxoffice.csv         # Dataset
├── static/
│   ├── script.js        # Frontend JavaScript
│   └── styles.css       # Custom styles
└── templates/
    └── index.html      # Main HTML template
```

