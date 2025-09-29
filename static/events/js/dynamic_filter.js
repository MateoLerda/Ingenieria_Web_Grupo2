document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("filtersForm");

  if (!form) return;


  const checkbox = form.querySelector("input[name='only_available']");
  if (checkbox) {
    checkbox.addEventListener("change", () => form.submit());
  }
});