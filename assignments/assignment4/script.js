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
let imageInput, selectedFilesDiv, stitchBtn, clearBtn, loadingIndicator, errorMessage, resultContainer, panoramaResult, downloadBtn;

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', () => {
  initializePanoramaStitching();
});

function initializePanoramaStitching() {
  // Get all DOM elements
  imageInput = document.getElementById('imageInput');
  selectedFilesDiv = document.getElementById('selectedFiles');
  stitchBtn = document.getElementById('stitchBtn');
  clearBtn = document.getElementById('clearBtn');
  loadingIndicator = document.getElementById('loadingIndicator');
  errorMessage = document.getElementById('errorMessage');
  resultContainer = document.getElementById('resultContainer');
  panoramaResult = document.getElementById('panoramaResult');
  downloadBtn = document.getElementById('downloadBtn');

  // Check if elements exist (in case we're not on the Task 1 page)
  if (!imageInput || !stitchBtn) {
    console.log('Panorama stitching elements not found on this page');
    return;
  }

  // Setup file input change handler
  imageInput.addEventListener('change', handleFileSelection);
  
  // Setup file input click handlers - support both label and button
  const fileLabel = document.querySelector('label[for="imageInput"]');
  const selectBtn = document.getElementById('selectImagesBtn');
  
  if (fileLabel) {
    fileLabel.addEventListener('click', (e) => {
      e.preventDefault();
      if (imageInput) {
        imageInput.click();
      }
    });
  }
  
  if (selectBtn) {
    selectBtn.addEventListener('click', () => {
      if (imageInput) {
        imageInput.click();
      }
    });
  }

  if (stitchBtn) stitchBtn.addEventListener('click', handleStitch);
  if (clearBtn) clearBtn.addEventListener('click', handleClear);
  if (downloadBtn) downloadBtn.addEventListener('click', handleDownload);
  
  console.log('Panorama stitching initialized successfully');
}

// Handle file selection
function handleFileSelection(e) {
  const files = e.target.files;
  if (!files || files.length === 0) {
    selectedFiles = [];
    updateSelectedFilesDisplay();
    updateButtons();
    return;
  }
  
  selectedFiles = Array.from(files);
  console.log(`Selected ${selectedFiles.length} file(s)`);
  updateSelectedFilesDisplay();
  updateButtons();
}

// Update selected files display
function updateSelectedFilesDisplay() {
  if (!selectedFilesDiv) return;
  
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
  if (!stitchBtn || !clearBtn) return;
  
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
function handleClear() {
  selectedFiles = [];
  if (imageInput) {
    imageInput.value = '';
  }
  updateSelectedFilesDisplay();
  updateButtons();
  if (resultContainer) resultContainer.style.display = 'none';
  if (errorMessage) errorMessage.style.display = 'none';
}

// Stitch panorama
async function handleStitch() {
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
    
  if (loadingIndicator) loadingIndicator.style.display = 'none';
  if (stitchBtn) stitchBtn.disabled = false;
  
  if (!response.ok || !data.success) {
    showError(data.error || 'Failed to stitch panorama. Please try again.');
    return;
  }
  
  // Display result
  if (panoramaResult && data.panorama) {
    panoramaResult.src = data.panorama;
    panoramaResult.onload = () => {
      if (resultContainer) {
        resultContainer.style.display = 'block';
        resultContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    };
    
    // Store panorama data for download
    panoramaResult.dataset.panoramaData = data.panorama;
  }
    
  } catch (error) {
    loadingIndicator.style.display = 'none';
    stitchBtn.disabled = false;
    showError('Network error: ' + error.message);
    console.error('Stitching error:', error);
  }
});

// Download panorama
function handleDownload() {
  if (!panoramaResult) return;
  const panoramaData = panoramaResult.dataset.panoramaData;
  if (!panoramaData) return;
  
  const link = document.createElement('a');
  link.href = panoramaData;
  link.download = `panorama_${Date.now()}.jpg`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

// Show error message
function showError(message) {
  if (!errorMessage) {
    console.error('Error:', message);
    alert('Error: ' + message);
    return;
  }
  errorMessage.textContent = `❌ Error: ${message}`;
  errorMessage.style.display = 'block';
  errorMessage.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

