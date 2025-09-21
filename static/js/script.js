document.addEventListener('DOMContentLoaded', () => {

    // --- Logic for the User Dashboard ---
    const queueListContainer = document.querySelector('.queue-list-container');
    if (queueListContainer) {
        fetchQueues();
    }

    async function fetchQueues() {
        try {
            const response = await fetch('/api/queues');
            const queues = await response.json();
            
            queueListContainer.innerHTML = ''; // Clear previous content
            
            queues.forEach(queue => {
                const card = document.createElement('a');
                card.classList.add('card', 'queue-card');
                card.href = `/queue/${queue.id}`;
                card.innerHTML = `
                    <div class="queue-card-content">
                        <div class="queue-header">
                            <span class="material-icons">chevron_right</span>
                        </div>
                        <h4>${queue.name}</h4>
                        <p>Currently Serving: #${queue.current_token}</p>
                    </div>
                `;
                queueListContainer.appendChild(card);
            });

        } catch (error) {
            console.error("Could not fetch queues:", error);
        }
    }
});