import csv
import random

# Sample data for generation
directors = [
    'S.S. Rajamouli', 'Rajkumar Hirani', 'Rohit Shetty', 'Lokesh Kanagaraj', 'Prashanth Neel',
    'Sandeep Reddy Vanga', 'Ayan Mukerji', 'S.S. Rajamouli', 'Atlee', 'Karan Johar',
    'Sanjay Leela Bhansali', 'Anurag Kashyap', 'Zoya Akhtar', 'Imtiaz Ali', 'Anurag Basu',
    'Kabir Khan', 'Shoojit Sircar', 'Vishal Bhardwaj', 'Sriram Raghavan', 'Mani Ratnam'
]

genres = [
    'Action', 'Drama', 'Comedy', 'Thriller', 'Romance',
    'Sci-Fi', 'Horror', 'Crime', 'Adventure', 'Fantasy',
    'Romantic Comedy', 'Historical', 'Biography', 'Musical', 'Animation'
]

def generate_movie():

    
    # Generate random duration between 90 and 180 minutes
    duration = random.randint(90, 180)
    
    # Generate budget between 20 to 500 crores
    budget = round(random.uniform(20, 500), 2)
    
    # Select random director and genre
    director = random.choice(directors)
    genre = random.choice(genres)
    
    return {
        'Director': director,
        'Duration (mins)': duration,
        'Budget (INR Crores)': budget,
        'Genre': genre,
    }

def generate_dataset(num_entries=5000):
    # Generate dataset with specified number of entries
    dataset = [generate_movie() for _ in range(num_entries)]
    
    
    # Write to CSV
    with open('boxoffice.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Director', 'Duration (mins)', 'Budget (INR Crores)', 'Genre']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for movie in dataset:
            writer.writerow(movie)

if __name__ == "__main__":
    # Generate 10000 entries (well under the 10,000 limit)
    generate_dataset(10000)
    print("boxoffice.csv has been generated with 10000 entries.")
