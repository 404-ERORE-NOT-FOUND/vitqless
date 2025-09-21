document.addEventListener('DOMContentLoaded', () => {

    const joinBtn = document.getElementById('join-queue-btn');
    const leaveBtn = document.getElementById('leave-queue-btn');
    
    // Logic for joining a queue
    if (joinBtn) {
        joinBtn.addEventListener('click', async (e) => {
            const queueId = e.target.dataset.queueId;
            try {
                const response = await fetch(`/api/queues/join/${queueId}`);
                const data = await response.json();
                
                if (response.ok) {
                    window.location.reload();
                } else {
                    alert(`Failed to join queue: ${data.error}`);
                }
            } catch (error) {
                console.error("Join queue error:", error);
                alert("An error occurred while joining the queue.");
            }
        });
    }

    // Logic for leaving a queue
    if (leaveBtn) {
        leaveBtn.addEventListener('click', async (e) => {
            const queueId = e.target.dataset.queueId;
            try {
                const response = await fetch(`/api/queues/leave/${queueId}`, {
                    method: 'POST'
                });
                const data = await response.json();
                
                if (response.ok) {
                    window.location.href = `/`;
                } else {
                    alert(`Failed to leave queue: ${data.error}`);
                }
            } catch (error) {
                console.error("Leave queue error:", error);
                alert("An error occurred while leaving the queue.");
            }
        });
    }

    // --- Real-time updates for current token ---
    const currentTokenElement = document.getElementById('current-token');
    if (currentTokenElement) {
        const pathSegments = window.location.pathname.split('/');
        const queueId = pathSegments[pathSegments.length - 1];

        async function fetchCurrentToken() {
            try {
                const response = await fetch(`/api/queues/status/${queueId}`);
                const data = await response.json();
                
                if (response.ok) {
                    currentTokenElement.innerText = data.current_token;
                } else {
                    console.error('Failed to fetch current token:', data.error);
                }
            } catch (error) {
                console.error('API call failed:', error);
            }
        }
        
        fetchCurrentToken();
        setInterval(fetchCurrentToken, 5000);
    }
});