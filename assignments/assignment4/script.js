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

// Panorama Stitching Functionality
let selectedFiles = [];

const imageInput = document.getElementById('imageInput');
const selectedFilesDiv = document.getElementById('selectedFiles');
const stitchBtn = document.getElementById('stitchBtn');
const clearBtn = document.getElementById('clearBtn');
const loadingIndicator = document.getElementById('loadingIndicator');
const errorMessage = document.getElementById('errorMessage');
const resultContainer = document.getElementById('resultContainer');
const panoramaResult = document.getElementById('panoramaResult');
const downloadBtn = document.getElementById('downloadBtn');

// Handle file selection
imageInput.addEventListener('change', (e) => {
  selectedFiles = Array.from(e.target.files);
  updateSelectedFilesDisplay();
  updateButtons();
});

// Update selected files display
function updateSelectedFilesDisplay() {
  if (selectedFiles.length === 0) {
    selectedFilesDiv.innerHTML = '';
    return;
  }
  
  const filesList = selectedFiles.map((file, index) => 
    `<div class="file-item">
      <span>${index + 1}. ${file.name}</span>
      <span class="file-size">(${(file.size / 1024 / 1024).toFixed(2)} MB)</span>
    </div>`
  ).join('');
  
  selectedFilesDiv.innerHTML = `
    <div class="selected-files-header">
      <strong>Selected ${selectedFiles.length} image(s):</strong>
    </div>
    <div class="files-list">${filesList}</div>
  `;
}

// Update button states
function updateButtons() {
  const hasFiles = selectedFiles.length >= 2;
  stitchBtn.disabled = !hasFiles;
  clearBtn.disabled = selectedFiles.length === 0;
  
  if (hasFiles) {
    stitchBtn.style.opacity = '1';
    stitchBtn.style.cursor = 'pointer';
  } else {
    stitchBtn.style.opacity = '0.5';
    stitchBtn.style.cursor = 'not-allowed';
  }
}

// Clear selection
clearBtn.addEventListener('click', () => {
  selectedFiles = [];
  imageInput.value = '';
  updateSelectedFilesDisplay();
  updateButtons();
  resultContainer.style.display = 'none';
  errorMessage.style.display = 'none';
});

// Stitch panorama
stitchBtn.addEventListener('click', async () => {
  if (selectedFiles.length < 2) {
    showError('Please select at least 2 images to stitch.');
    return;
  }
  
  // Hide previous results and errors
  resultContainer.style.display = 'none';
  errorMessage.style.display = 'none';
  loadingIndicator.style.display = 'block';
  stitchBtn.disabled = true;
  
  try {
    // Prepare form data
    const formData = new FormData();
    selectedFiles.forEach(file => {
      formData.append('images', file);
    });
    formData.append('max_width', '2000'); // Optional: limit image width
    
    // Call API
    const response = await fetch('/api/stitch_panorama', {
      method: 'POST',
      body: formData
    });
    
    const data = await response.json();
    
    loadingIndicator.style.display = 'none';
    stitchBtn.disabled = false;
    
    if (!response.ok || !data.success) {
      showError(data.error || 'Failed to stitch panorama. Please try again.');
      return;
    }
    
    // Display result
    panoramaResult.src = data.panorama;
    panoramaResult.onload = () => {
      resultContainer.style.display = 'block';
      resultContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    };
    
    // Store panorama data for download
    panoramaResult.dataset.panoramaData = data.panorama;
    
  } catch (error) {
    loadingIndicator.style.display = 'none';
    stitchBtn.disabled = false;
    showError('Network error: ' + error.message);
    console.error('Stitching error:', error);
  }
});

// Download panorama
downloadBtn.addEventListener('click', () => {
  const panoramaData = panoramaResult.dataset.panoramaData;
  if (!panoramaData) return;
  
  const link = document.createElement('a');
  link.href = panoramaData;
  link.download = `panorama_${Date.now()}.jpg`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
});

// Show error message
function showError(message) {
  errorMessage.textContent = `❌ Error: ${message}`;
  errorMessage.style.display = 'block';
  errorMessage.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

