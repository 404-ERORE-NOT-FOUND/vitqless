document.addEventListener('DOMContentLoaded', () => {

    // --- Logic for the Admin Page ---
    const adminContainer = document.querySelector('.admin-container');
    if (adminContainer) {
        // Event listeners for admin serve buttons
        document.querySelectorAll('.serve-next-btn').forEach(button => {
            button.addEventListener('click', async (e) => {
                const queueId = e.target.dataset.queueId;
                
                try {
                    const response = await fetch(`/api/queues/serve_next/${queueId}`, {
                        method: 'POST'
                    });
                    const data = await response.json();
                    
                    if (response.ok) {
                        const currentTokenSpan = document.getElementById(`current-${queueId}`);
                        currentTokenSpan.innerText = parseInt(currentTokenSpan.innerText) + 1;
                        console.log(data.message);
                    } else {
                        console.error('Failed to serve next:', data.error);
                    }
                } catch (error) {
                    console.error("Serve next error:", error);
                }
            });
        });

        // Event listeners for admin set tokens forms
        document.querySelectorAll('.set-tokens-form').forEach(form => {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                const queueId = e.target.closest('.queue-card').dataset.queueId;
                const currentToken = e.target.querySelector('.current-token-input').value;
                const lastToken = e.target.querySelector('.last-token-input').value;

                try {
                    const response = await fetch(`/api/queues/set_tokens/${queueId}`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            current_token: currentToken,
                            last_token: lastToken
                        })
                    });
                    const data = await response.json();

                    if (response.ok) {
                        document.getElementById(`current-${queueId}`).innerText = currentToken;
                        document.getElementById(`last-${queueId}`).innerText = lastToken;
                        alert('Tokens updated successfully!');
                    } else {
                        alert('Failed to set tokens: ' + data.error);
                    }
                } catch (error) {
                    console.error("Set tokens error:", error);
                    alert('An error occurred while setting tokens.');
                }
            });
        });
    }

    // --- Logic for the User Dashboard ---
    const queueListContainer = document.querySelector('.queue-list-container');
    if (queueListContainer) {
        fetchQueues();
    }

    async function fetchQueues() {
        try {
            const response = await fetch('/api/queues');
            const queues = await response.json();
            
            queueListContainer.innerHTML = '';
            
            queues.forEach(queue => {
                const card = document.createElement('div');
                card.classList.add('card', 'queue-card');
                card.innerHTML = `
                    <div class="queue-card-content">
                        <div class="queue-header">
                            <span class="material-icons">chevron_right</span>
                        </div>
                        <h4>${queue.name}</h4>
                        <p>Currently Serving: #${queue.current_token}</p>
                        <button class="join-queue-btn" data-queue-id="${queue.id}">Join Queue</button>
                    </div>
                `;
                queueListContainer.appendChild(card);
            });

            document.querySelectorAll('.join-queue-btn').forEach(button => {
                button.addEventListener('click', async (e) => {
                    const queueId = e.target.dataset.queueId;
                    
                    try {
                        const joinResponse = await fetch(`/api/queues/join/${queueId}`);
                        const joinData = await joinResponse.json();
                        
                        if (joinData.token) {
                            alert(`You have successfully joined the queue for ${joinData.queue_name}. Your token number is #${joinData.token}.`);
                        } else {
                            alert(`Failed to join queue: ${joinData.error}`);
                        }
                    } catch (error) {
                        console.error("Join queue error:", error);
                        alert("An error occurred while joining the queue.");
                    }
                });
            });

        } catch (error) {
            console.error("Could not fetch queues:", error);
        }
    }
});