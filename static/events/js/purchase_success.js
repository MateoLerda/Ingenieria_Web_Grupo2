document.addEventListener("DOMContentLoaded", function () {
  // Countdown timer
  let seconds = 5;
  const countdownElement = document.getElementById("countdown");

  const countdownInterval = setInterval(() => {
    seconds--;
    if (countdownElement) {
      countdownElement.textContent = seconds;
    }
    
    if (seconds <= 0) {
      clearInterval(countdownInterval);
      window.location.href = "/";
    }
  }, 1000);

  // Confetti effect
  createConfetti();
});

function createConfetti() {
  const confettiContainer = document.getElementById("confetti");
  if (!confettiContainer) return;

  const colors = ["#4CAF50", "#4A4E69", "#22223B", "#F72585", "#7209B7", "#3A0CA3", "#4CC9F0"];
  const confettiCount = 50;

  for (let i = 0; i < confettiCount; i++) {
    setTimeout(() => {
      const confetti = document.createElement("div");
      confetti.className = "confetti";
      confetti.style.left = Math.random() * 100 + "%";
      confetti.style.background = colors[Math.floor(Math.random() * colors.length)];
      confetti.style.animationDelay = Math.random() * 0.5 + "s";
      confetti.style.animationDuration = (Math.random() * 2 + 2) + "s";
      
      // Randomize shape
      if (Math.random() > 0.5) {
        confetti.style.borderRadius = "50%";
      }
      
      confettiContainer.appendChild(confetti);
      
      // Remove confetti after animation
      setTimeout(() => {
        confetti.remove();
      }, 3500);
    }, i * 30);
  }
}