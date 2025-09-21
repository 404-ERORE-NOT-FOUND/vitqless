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

document.addEventListener('DOMContentLoaded', () => {

    const queues = [
        { name: 'Q Block Paid Mess', count: 158, id: 'q-block-mess' },
        { name: 'G D Block Paid Mess', count: 121, id: 'gd-block-mess' },
        { name: 'Admin Office', count: 25, id: 'admin-office' },
        { name: 'Proctor Cabins', count: 10, id: 'hod-rooms' },
        { name: 'Sports Courts', count: 50, id: 'sports-courts' },
        { name: 'Gyms', count: 35, id: 'gyms' },
    ];

    const container = document.querySelector('.queue-list-container');

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
        card.addEventListener('click', () => {
            window.location.href = `/queue/${queue.id}`;
        });
        container.appendChild(card);
    });

    // --- New Logic for Profile Pop-up ---
    const profileIcon = document.querySelector('a[href="{{ url_for(\'profile\') }}"]');
    const profileModal = document.getElementById('profile-modal');
    const closeModalBtn = document.querySelector('.close-btn');

    profileIcon.addEventListener('click', (e) => {
        e.preventDefault(); // Prevent the default redirect
        
        fetch('/api/profile')
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error('Error fetching profile:', data.error);
                    return;
                }
                
                // Populate the modal with the data
                document.getElementById('profile-name-modal').innerText = data.name;
                document.getElementById('profile-email-modal').innerText = data.email;
                document.getElementById('profile-reg-no-modal').innerText = data.reg_no;
                
                // Show the modal
                profileModal.style.display = 'block';
            })
            .catch(error => {
                console.error('Failed to fetch profile data:', error);
            });
    });

    closeModalBtn.addEventListener('click', () => {
        profileModal.style.display = 'none';
    });

    window.addEventListener('click', (e) => {
        if (e.target === profileModal) {
            profileModal.style.display = 'none';
        }
    });

});