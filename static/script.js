document.addEventListener('DOMContentLoaded', function() {
    // Cache DOM elements
    const directorInput = document.getElementById('director');
    const directorList = document.getElementById('directorList');
    let allDirectors = [];
    
    // Fetch all directors from the API
    async function fetchDirectors() {
        try {
            directorInput.classList.add('loading');
            const response = await fetch('/api/directors');
            if (!response.ok) throw new Error('Failed to fetch directors');
            allDirectors = await response.json();
            updateDirectorList('');
        } catch (error) {
            console.error('Error fetching directors:', error);
            // Show error to user
            const errorMsg = document.createElement('div');
            errorMsg.className = 'alert alert-warning mt-2';
            errorMsg.textContent = 'Failed to load director list. You can still type the director name manually.';
            directorInput.parentNode.insertBefore(errorMsg, directorInput.nextSibling);
            
            // Remove error after 5 seconds
            setTimeout(() => {
                errorMsg.remove();
            }, 5000);
        } finally {
            directorInput.classList.remove('loading');
        }
    }
    
    // Update the datalist with filtered directors
    function updateDirectorList(query) {
        // Clear existing options
        directorList.innerHTML = '';
        
        // Filter directors based on query
        const filteredDirectors = allDirectors.filter(director => 
            director.toLowerCase().includes(query.toLowerCase())
        );
        
        // Add filtered options to datalist
        filteredDirectors.forEach(director => {
            const option = document.createElement('option');
            option.value = director;
            directorList.appendChild(option);
        });
    }
    
    // Initialize director list
    fetchDirectors();
    
    // Add input event listener for filtering
    let filterTimeout;
    directorInput.addEventListener('input', function() {
        // Debounce the filtering to improve performance
        clearTimeout(filterTimeout);
        filterTimeout = setTimeout(() => {
            updateDirectorList(this.value);
        }, 300);
    });
    
    // Prevent form submission when selecting from datalist with Enter
    directorInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && this.value) {
            e.preventDefault();
            // Find if the current input matches any director
            const match = allDirectors.find(d => 
                d.toLowerCase() === this.value.toLowerCase()
            );
            if (match) {
                this.value = match; // Normalize the case
            }
        }
    });
    
    // Rest of your existing code
    // Rest of your existing code
    const form = document.getElementById('predictionForm');
    const resultDiv = document.getElementById('result');
    const predictedGenreSpan = document.getElementById('predictedGenre');
    const modelAccuracySpan = document.getElementById('modelAccuracy');
    const topPredictionsDiv = document.getElementById('topPredictions');
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Show loading state
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalBtnText = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Predicting...';
        
        try {
            // Get form data
            const formData = {
                director: document.getElementById('director').value.trim(),
                budget: document.getElementById('budget').value,
                duration: document.getElementById('duration').value
            };
            
            // Send prediction request
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                // Update UI with prediction results
                predictedGenreSpan.textContent = data.prediction;
                modelAccuracySpan.textContent = data.model_accuracy;
                
                // Clear previous predictions
                topPredictionsDiv.innerHTML = '';
                
                // Add prediction items
                data.top_predictions.forEach((pred, index) => {
                    const predictionItem = document.createElement('div');
                    predictionItem.className = `list-group-item d-flex justify-content-between align-items-center ${index === 0 ? 'active' : ''}`;
                    predictionItem.innerHTML = `
                        <span>${pred.genre}</span>
                        <span class="badge bg-primary rounded-pill">${pred.confidence}%</span>
                    `;
                    topPredictionsDiv.appendChild(predictionItem);
                });
                
                // Show results
                resultDiv.style.display = 'block';
                resultDiv.scrollIntoView({ behavior: 'smooth' });
            } else {
                throw new Error(data.message || 'Error making prediction');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error making prediction: ' + error.message);
        } finally {
            // Reset button state
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalBtnText;
        }
    });
});