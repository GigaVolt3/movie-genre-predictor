// Tab functionality
function showTab(tabName) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Deactivate all tab buttons
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.remove('active');
    });
    
    // Activate the selected tab
    document.getElementById(`${tabName}-tab`).classList.add('active');
    event.currentTarget.classList.add('active');
}

document.addEventListener('DOMContentLoaded', function() {
    const predictBtn = document.getElementById('predict-btn');
    const budgetInput = document.getElementById('budget');
    const durationInput = document.getElementById('duration');
    const directorSelect = document.getElementById('director');
    const predictionElement = document.getElementById('prediction');
    const confidenceElement = document.getElementById('confidence');
    const neighborsBody = document.getElementById('neighbors-body');
    const distributionBody = document.getElementById('distribution-body');
    
    // Add event listener to the predict button
    predictBtn.addEventListener('click', predictGenre);
    
    // Also allow form submission when pressing Enter in any input field
    [budgetInput, durationInput].forEach(input => {
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                predictGenre();
            }
        });
    });
    
    // Handle Enter key in Select2 search
    $(document).on('keypress', '.select2-search__field', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            predictGenre();
        }
    });
    
    function predictGenre() {
        // Get form values
        const budget = budgetInput.value.trim();
        const duration = durationInput.value.trim();
        const director = directorSelect.value;
        
        // Simple validation
        if (!budget || !duration || !director) {
            showError('Please fill in all fields');
            return;
        }
        
        // Disable button and show loading state
        predictBtn.disabled = true;
        predictBtn.innerHTML = '<span class="loading"></span> Predicting...';
        
        // Clear previous results
        neighborsBody.innerHTML = '';
        distributionBody.innerHTML = '';
        
        // Prepare request data
        const requestData = {
            budget: parseFloat(budget), // Send budget in crores as entered by user
            duration: parseInt(duration),
            director: director
        };
        
        // Make API request
        fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Display prediction
            displayPredictionResults(data);
            
            // Scroll to result
            document.getElementById('result').scrollIntoView({ behavior: 'smooth' });
        })
        .catch(error => {
            console.error('Error:', error);
            showError('Failed to get prediction. Please try again.');
        })
        .finally(() => {
            // Re-enable button and reset text
            predictBtn.disabled = false;
            predictBtn.textContent = 'Predict Genre';
        });
    }
    
    function displayPredictionResults(data) {
        // Display main prediction
        predictionElement.textContent = data.predicted_genre || 'Unknown';
        
        // Calculate and display confidence
        const totalVotes = data.total_neighbors;
        const genreVotes = data.genre_distribution[data.predicted_genre] || 0;
        const confidence = Math.round((genreVotes / totalVotes) * 100);
        confidenceElement.textContent = `${confidence}% (${genreVotes}/${totalVotes} votes)`;
        
        // Display nearest neighbors
        displayNeighborsTable(data.neighbors, data.predicted_genre);
        
        // Display genre distribution
        displayGenreDistribution(data.genre_distribution, totalVotes, data.predicted_genre);
    }
    
    function displayNeighborsTable(neighbors, predictedGenre) {
        neighborsBody.innerHTML = '';
        
        neighbors.forEach((neighbor, index) => {
            const row = document.createElement('tr');
            if (neighbor.genre === predictedGenre) {
                row.classList.add('predicted-genre');
            }
            
            // Format budget with 2 decimal places
            const formattedBudget = parseFloat(neighbor.budget).toFixed(2);
            
            row.innerHTML = `
                <td>${index + 1}</td>
                <td>${escapeHtml(neighbor.title)}</td>
                <td>${escapeHtml(neighbor.genre)}</td>
                <td>${escapeHtml(neighbor.director)}</td>
                <td>${formattedBudget} Cr</td>
                <td>${neighbor.duration}</td>
                <td>${neighbor.distance.toFixed(4)}</td>
            `;
            
            neighborsBody.appendChild(row);
        });
    }
    
    function displayGenreDistribution(genreDistribution, totalVotes, predictedGenre) {
        distributionBody.innerHTML = '';
        
        // Convert to array and sort by count (descending)
        const sortedGenres = Object.entries(genreDistribution)
            .map(([genre, count]) => ({
                genre,
                count,
                percentage: (count / totalVotes) * 100
            }))
            .sort((a, b) => b.count - a.count);
        
        sortedGenres.forEach(item => {
            const row = document.createElement('tr');
            if (item.genre === predictedGenre) {
                row.classList.add('predicted-genre');
            }
            
            row.innerHTML = `
                <td>${escapeHtml(item.genre)}</td>
                <td>${item.count}</td>
                <td>${item.percentage.toFixed(1)}%</td>
                <td>
                    <div class="vote-bar">
                        <div class="vote-fill" style="width: ${item.percentage}%"></div>
                    </div>
                </td>
            `;
            
            distributionBody.appendChild(row);
        });
    }
    
    function showError(message) {
        predictionElement.textContent = message;
        predictionElement.style.color = '#dc3545'; // Error color
        confidenceElement.textContent = '-';
        document.getElementById('result').scrollIntoView({ behavior: 'smooth' });
    }
    
    // Helper function to escape HTML to prevent XSS
    function escapeHtml(unsafe) {
        if (typeof unsafe !== 'string') return '';
        return unsafe
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }
    
    // Add input validation and formatting for budget
    budgetInput.addEventListener('input', function(e) {
        // Remove any non-numeric characters except decimal point
        let value = e.target.value.replace(/[^0-9.]/g, '');
        
        // Ensure only one decimal point
        const decimalCount = value.split('.').length - 1;
        if (decimalCount > 1) {
            value = value.substring(0, value.lastIndexOf('.'));
        }
        
        // Ensure value is non-negative
        if (value < 0) {
            value = '0';
        }
        
        // Update the input value
        if (e.target.value !== value) {
            e.target.value = value;
        }
        
        // Add tooltip with conversion to actual amount
        if (value && !isNaN(parseFloat(value))) {
            const amountInCrores = parseFloat(value);
            const actualAmount = new Intl.NumberFormat('en-IN', {
                style: 'currency',
                currency: 'INR',
                minimumFractionDigits: 0,
                maximumFractionDigits: 0
            }).format(amountInCrores * 10000000);
            
            budgetInput.title = `Approx. ${actualAmount} (${amountInCrores} crores)`;
        } else {
            budgetInput.title = 'Enter budget in crores (e.g., 100 for 100 crores)';
        }
    });
    
    durationInput.addEventListener('input', function(e) {
        // Ensure positive integers only
        if (e.target.value < 1) {
            e.target.value = 1;
        }
    });
});