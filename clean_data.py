import csv
import os

def clean_and_convert_budget(budget_str):
    """Convert budget string to float and convert USD to INR (assuming 1 USD = 83 INR)"""
    if not budget_str or budget_str.strip() == '':
        return 0.0
    try:
        # Remove any commas and convert to float
        budget_usd = float(budget_str.replace(',', ''))
        # Convert USD to INR (1 USD = 83 INR) and then to crores (1 crore = 10,000,000)
        budget_inr_crores = (budget_usd * 83) / 10000000
        return round(budget_inr_crores, 2)  # Round to 2 decimal places
    except (ValueError, TypeError):
        return 0.0

def clean_runtime(runtime_str):
    """Convert runtime string to minutes (integer)"""
    if not runtime_str or runtime_str.strip() == '':
        return 0
    try:
        # Extract numbers from the runtime string (e.g., "146 min" -> 146)
        if ' ' in runtime_str:
            minutes = int(runtime_str.split()[0])
        else:
            minutes = int(runtime_str)
        return minutes if minutes > 0 else 0
    except (ValueError, TypeError):
        return 0

def clean_genre(genre_str):
    """Clean and standardize genre names"""
    if not genre_str:
        return "Unknown"
    # Take the first genre if multiple genres are listed (e.g., "Action,Adventure" -> "Action")
    return genre_str.split(',')[0].strip()

def clean_director(director_str):
    """Clean director names"""
    if not director_str:
        return "Unknown"
    return director_str.strip()

def clean_data():
    input_file = 'movie.csv'
    output_file = 'dmdw.csv'
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found!")
        return
    
    try:
        # Read the entire file as binary first
        with open(input_file, 'rb') as f:
            content = f.read()
        
        # Try to decode with different encodings
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        
        for encoding in encodings:
            try:
                # Try to decode with current encoding
                decoded = content.decode(encoding)
                # If successful, write to a temporary string
                import io
                temp_file = io.StringIO(decoded)
                # Test reading as CSV
                csv.DictReader(temp_file)
                temp_file.seek(0)
                break
            except (UnicodeDecodeError, csv.Error):
                continue
        else:
            print("Warning: Could not determine file encoding. Using 'latin-1' with error handling.")
            encoding = 'latin-1'
            decoded = content.decode(encoding, errors='replace')
            temp_file = io.StringIO(decoded)
        
        print(f"Using encoding: {encoding}")
        
        # Now process the file
        with temp_file as infile, \
             open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            
            reader = csv.DictReader(infile)
            
            # Define output fieldnames
            fieldnames = ['Title', 'Director', 'Budget (INR Crores)', 'Duration (mins)', 'Genre']
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in reader:
                # Clean and transform each field
                cleaned_row = {
                    'Title': row.get('name', '').strip(),
                    'Director': clean_director(row.get('director', '')),
                    'Budget (INR Crores)': clean_and_convert_budget(row.get('budget', '')),
                    'Duration (mins)': clean_runtime(row.get('runtime', '')),
                    'Genre': clean_genre(row.get('genre', ''))
                }
                
                # Only write rows with valid data
                if (cleaned_row['Director'] != 'Unknown' and 
                    cleaned_row['Budget (INR Crores)'] > 0 and 
                    cleaned_row['Duration (mins)'] > 0):
                    writer.writerow(cleaned_row)
        
        print(f"Data cleaned and saved to {output_file}")
        print(f"Total movies processed: {sum(1 for _ in open(input_file)) - 1}")
        print(f"Total valid movies saved: {sum(1 for _ in open(output_file)) - 1}")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    clean_data()
