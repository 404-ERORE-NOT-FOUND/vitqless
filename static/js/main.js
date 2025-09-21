document.addEventListener('DOMContentLoaded', () => {

    // Function to fetch live queue data from the Flask API
    async function fetchQueues() {
        try {
            const response = await fetch('/api/queues');
            const queues = await response.json();
            
            const container = document.querySelector('.queue-list-container');
            container.innerHTML = ''; // Clear previous content

            queues.forEach(queue => {
                const card = document.createElement('div');
                card.classList.add('card', 'queue-card');
                card.innerHTML = `
                    <div class="queue-card-content">
                        <div class="queue-header">
                            <span class="material-icons">chevron_right</span>
                        </div>
                        <h4>${queue.name}</h4>
                        <p>1 in Queue - ${queue.count} people</p>
                    </div>
                `;
                // Add a click event listener to navigate to the specific queue page
                card.addEventListener('click', () => {
                    window.location.href = `/queue/${queue.id}`;
                });
                container.appendChild(card);
            });
        } catch (error) {
            console.error("Could not fetch queues:", error);
        }
    }

    // Function to fetch active tokens and featured message
    async function fetchLiveData() {
        try {
            const response = await fetch('/api/live_data');
            const data = await response.json();
            
            document.getElementById('active-token-number').innerText = `#${data.active_token_number}`;
            document.getElementById('active-token-service').innerText = data.active_token_service;
            document.getElementById('featured-message').innerText = data.featured_message;

        } catch (error) {
            console.error("Could not fetch live data:", error);
        }
    }

    // Call the functions to load initial data when the page loads
    fetchQueues();
    fetchLiveData();

});