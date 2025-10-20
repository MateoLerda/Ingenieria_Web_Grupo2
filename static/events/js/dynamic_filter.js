document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("filtersForm");

  if (!form) return;

  // Handle toggle button
  const checkbox = form.querySelector("input[type='checkbox'][name='only_available']");
  const toggleLabel = document.getElementById("toggleLabel");
  
  if (checkbox && toggleLabel) {
    // Toggle on label click (handled by the for attribute)
    toggleLabel.addEventListener("click", (e) => {
      // The checkbox will be automatically toggled by the label's for attribute
      // We just need to update the visual state after a brief delay
      setTimeout(() => {
        if (checkbox.checked) {
          toggleLabel.classList.add("active");
        } else {
          toggleLabel.classList.remove("active");
        }
      }, 0);
    });
    
    // Auto-submit form when checkbox changes
    checkbox.addEventListener("change", () => {
      form.submit();
    });
  }

});