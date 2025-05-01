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