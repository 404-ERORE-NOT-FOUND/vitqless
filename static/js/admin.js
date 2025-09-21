document.addEventListener('DOMContentLoaded', () => {

    const adminContainer = document.querySelector('.admin-container');
    if (adminContainer) {
        // --- Admin Queue Detail Page Logic ---
        const userList = document.getElementById('user-list');
        if (userList) {
            fetchUserDetails();
        }

        async function fetchUserDetails() {
            const userItems = userList.querySelectorAll('li[data-uid]');
            for (const item of userItems) {
                const uid = item.dataset.uid;
                try {
                    const response = await fetch(`/api/users/${uid}`);
                    const user = await response.json();
                    
                    if (response.ok) {
                        const token = item.querySelector('strong').innerText;
                        item.innerText = `${token}: ${user.reg_no} - ${user.name}`;
                    } else {
                        item.innerText = `${token}: User not found`;
                    }
                } catch (error) {
                    console.error("Failed to fetch user details:", error);
                    item.innerText = "Error loading user details";
                }
            }
        }

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