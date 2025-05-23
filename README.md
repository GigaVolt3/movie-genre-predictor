# Movie Genre Predictor

A web application that predicts movie genres based on budget, duration, and director using the K-Nearest Neighbors (KNN) algorithm.

## Features
- Predict movie genres based on budget, duration, and director
- View top K nearest neighbors
- Responsive and user-friendly interface
- Built with Flask and pandas

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/movie-genre-predictor.git
   cd movie-genre-predictor
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Add your dataset:
   - Place your `movie.csv` file in the project root directory
   - The CSV should contain at least these columns: 'budget', 'runtime', 'director', 'genre'

5. Run the application:
   ```bash
   python app.py
   ```

6. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## Deployment

### Deploy to Render (Recommended)

1. Push your code to a GitHub repository
2. Create a new Web Service on [Render](https://render.com/)
3. Connect your GitHub repository
4. Use the following settings:
   - Name: `movie-genre-predictor` (or your preferred name)
   - Region: Choose the one closest to you
   - Branch: `main`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
5. Click "Advanced" and add the following environment variable:
   - Key: `DATASET_URL`
   - Value: The URL where your `movie.csv` is hosted (you can upload it to GitHub as a release asset or use a service like Google Drive or Dropbox with a direct download link)
6. Click "Create Web Service"

### Deploy to PythonAnywhere
1. Create a new Web App
2. Choose "Manual Configuration" (Python 3.8+)
3. In the console:
   ```bash
   git clone https://github.com/yourusername/movie-genre-predictor.git
   cd movie-genre-predictor
   mkvirtualenv --python=/usr/bin/python3.8 venv
   pip install -r requirements.txt
   ```
4. Configure your web app to use the WSGI file
5. Add the path to your `movie.csv` file in the WSGI configuration

## Project Structure

```
movie-genre-predictor/
├── app.py                # Main Flask application
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── .gitignore           # Git ignore file
└── templates/
    └── index.html      # Frontend template
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
