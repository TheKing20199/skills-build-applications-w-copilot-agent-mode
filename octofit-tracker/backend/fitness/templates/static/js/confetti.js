// CDN load
import('https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js').then(() => {
  console.log("Confetti is ready! 🥳");
});

// Use this in any template with: <script>launchConfetti()</script>
function launchConfetti() {
  confetti({
    particleCount: 100,
    spread: 70,
    origin: { y: 0.6 },
  });
}

function launchFloatingEmojis() {
    const emojis = ['🎉', '🏆', '✨', '🎊'];
    const emojiContainer = document.createElement('div');
    emojiContainer.className = 'emoji-container';
    document.body.appendChild(emojiContainer);

    for (let i = 0; i < 20; i++) {
        const emoji = document.createElement('div');
        emoji.className = 'floating-emoji';
        emoji.textContent = emojis[Math.floor(Math.random() * emojis.length)];
        emoji.style.left = Math.random() * 100 + 'vw';
        emoji.style.animationDelay = Math.random() * 2 + 's';
        emojiContainer.appendChild(emoji);
    }

    setTimeout(() => {
        emojiContainer.remove();
    }, 5000);
}

// Show loading spinner and typing animation
function showLoadingSpinner() {
    const spinner = document.createElement('div');
    spinner.className = 'loading-spinner';
    spinner.textContent = 'Thinking...';
    document.getElementById('octocoach-messages').appendChild(spinner);
    return spinner;
}

function removeLoadingSpinner(spinner) {
    if (spinner) {
        spinner.remove();
    }
}

function addTypingAnimation(messageElement) {
    let dots = 0;
    const interval = setInterval(() => {
        dots = (dots + 1) % 4;
        messageElement.textContent = '🤖 Typing' + '.'.repeat(dots);
    }, 500);
    return interval;
}

function getCSRFToken() {
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Connect the chat form input to the interpretUserInput function
document.getElementById('octocoach-send').addEventListener('click', () => {
    const userInput = document.getElementById('octocoach-input').value;
    if (userInput.trim()) {
        const userBubble = document.createElement('div');
        userBubble.className = 'user-message';
        userBubble.textContent = userInput;
        document.getElementById('octocoach-messages').appendChild(userBubble);

        // Show loading spinner
        const spinner = showLoadingSpinner();
        
        // Start typing animation
        const typingElement = document.createElement('div');
        typingElement.className = 'coach-message typing';
        document.getElementById('octocoach-messages').appendChild(typingElement);
        const typingInterval = addTypingAnimation(typingElement);

        // Send the message to the backend
        fetch('https://orange-space-cod-jqxwv4gxjrp3qp4j-8000.app.github.dev/api/octocoach/ask/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({ message: userInput })
        })
        .then(response => {
            console.log('Fetch response status:', response.status);
            return response.json().then(data => {
                console.log('Fetch response body:', data);
                return { status: response.status, data };
            });
        })
        .then(({ status, data }) => {
            removeLoadingSpinner(spinner);
            clearInterval(typingInterval);
            typingElement.remove();

            if (data.error) {
                const errorBubble = document.createElement('div');
                errorBubble.className = 'error-message';
                errorBubble.textContent = 'Error: ' + data.error + ' (Status: ' + status + ')';
                document.getElementById('octocoach-messages').appendChild(errorBubble);
                return;
            }

            const coachBubble = document.createElement('div');
            coachBubble.className = 'coach-message';
            coachBubble.textContent = data.response;
            document.getElementById('octocoach-messages').appendChild(coachBubble);

            // If the response indicates success or achievement, show confetti
            if (data.showConfetti) {
                launchConfetti();
            }
            // If the response indicates floating emojis should be shown
            if (data.showEmojis) {
                launchFloatingEmojis();
            }
        })
        .catch(error => {
            removeLoadingSpinner(spinner);
            clearInterval(typingInterval);
            typingElement.remove();

            const errorBubble = document.createElement('div');
            errorBubble.className = 'error-message';
            errorBubble.textContent = 'Something went wrong: ' + error.message;
            document.getElementById('octocoach-messages').appendChild(errorBubble);
            console.error('Fetch error:', error);
        });

        document.getElementById('octocoach-input').value = '';
    }
});