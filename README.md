# Movie Genre Predictor

A web application that predicts movie genres based on director, budget, and duration using a custom implementation of the K-Nearest Neighbors (KNN) algorithm.

## Features

- Predicts movie genres using three key features:
  - Director (using target encoding)
  - Budget (in USD)
  - Duration (in minutes)
- Custom implementation of KNN algorithm from scratch
- Responsive web interface with modern UI
- Real-time prediction

## How to Run

1. Make sure you have Python 3.7+ installed
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Place your `boxoffice.csv` file in the project root directory with the following columns:
   - `director`: Name of the movie director
   - `duration`: Movie duration in minutes
   - `budget`: Movie budget in USD
   - `genre`: Movie genre (target variable)
4. Run the application:
   ```
   python app.py
   ```
5. Open your browser and navigate to `http://localhost:5000`

## Model Details

- **Algorithm**: Custom K-Nearest Neighbors (KNN) with k=5
- **Features**:
  - Director (target encoded)
  - Budget (min-max scaled)
  - Duration (min-max scaled)
- **Distance Metric**: Euclidean distance

## Project Structure

```
├── app.py                # Main Flask application
├── requirements.txt      # Python dependencies
├── boxoffice.csv         # Dataset (not included in repo)
├── static/
│   ├── script.js        # Frontend JavaScript
│   └── styles.css       # Custom styles
└── templates/
    └── index.html      # Main HTML template
```

## Implementation Notes

- The KNN algorithm is implemented from scratch without using scikit-learn
- Target encoding is used for the director feature to convert categorical data to numerical values
- All numerical features are normalized using min-max scaling
- The web interface is built with vanilla JavaScript and CSS (no additional frameworks)

