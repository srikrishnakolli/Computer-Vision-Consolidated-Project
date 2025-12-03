document.querySelectorAll("[data-scroll]").forEach((button) => {
  button.addEventListener("click", () => {
    const target = document.querySelector(button.dataset.scroll);
    if (target) {
      target.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  });
});

document.querySelectorAll("[data-copy]").forEach((button) => {
  button.addEventListener("click", async () => {
    const selector = button.dataset.copy;
    const el = document.querySelector(selector);
    if (!el) return;
    const text = el.innerText.trim();
    try {
      await navigator.clipboard.writeText(text);
      button.textContent = "Copied!";
      setTimeout(() => (button.textContent = "Copy"), 1600);
    } catch (err) {
      console.error("Clipboard error:", err);
    }
  });
});

