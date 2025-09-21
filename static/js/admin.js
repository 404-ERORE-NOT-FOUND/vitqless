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
                const queueId = e.target.closest('.set-tokens-form').dataset.queueId;
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
        
        // Event listener for the Reset Queue button
        document.querySelectorAll('.reset-queue-btn').forEach(button => {
            button.addEventListener('click', async (e) => {
                const queueId = e.target.dataset.queueId;
                if(confirm("Are you sure you want to reset this queue? This will kick all users out.")) {
                    try {
                        const response = await fetch(`/api/queues/reset/${queueId}`, {
                            method: 'POST'
                        });
                        const data = await response.json();
                        
                        if (response.ok) {
                            alert(data.message);
                            // Refresh the page to show the new state
                            window.location.reload();
                        } else {
                            alert('Failed to reset queue: ' + data.error);
                        }
                    } catch (error) {
                        console.error("Reset queue error:", error);
                        alert('An error occurred while resetting the queue.');
                    }
                }
            });
        });
    }

});