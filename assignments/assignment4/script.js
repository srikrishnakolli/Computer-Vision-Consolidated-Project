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
// Global storage for Task 1 images (accessible by Task 2)
window.task1Images = [];
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

// ========== Task 2: SIFT + RANSAC Functionality ==========
let siftImageA = null;
let siftImageB = null;

// Update Task 2 image selector with Task 1 images
function updateTask2ImageSelector() {
  const selectorDiv = document.getElementById('task1ImagesSelector');
  const listDiv = document.getElementById('task1ImagesList');
  
  if (!selectorDiv || !listDiv) return;
  
  if (!window.task1Images || window.task1Images.length < 2) {
    selectorDiv.style.display = 'none';
    return;
  }
  
  selectorDiv.style.display = 'block';
  listDiv.innerHTML = '';
  
  window.task1Images.forEach((file, index) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'btn ghost';
      btn.style.cssText = 'padding: 0.5rem; display: flex; flex-direction: column; align-items: center; gap: 0.25rem;';
      btn.innerHTML = `
        <img src="${e.target.result}" style="width: 80px; height: 80px; object-fit: cover; border-radius: 8px; border: 2px solid var(--border);" />
        <span style="font-size: 0.75rem;">Image ${index + 1}</span>
      `;
      btn.onclick = () => selectTask1ImageForSIFT(index, 'A');
      listDiv.appendChild(btn);
      
      const btnB = btn.cloneNode(true);
      btnB.innerHTML = `
        <img src="${e.target.result}" style="width: 80px; height: 80px; object-fit: cover; border-radius: 8px; border: 2px solid var(--border);" />
        <span style="font-size: 0.75rem;">Image ${index + 1}</span>
      `;
      btnB.onclick = () => selectTask1ImageForSIFT(index, 'B');
      listDiv.appendChild(btnB);
    };
    reader.readAsDataURL(file);
  });
}

function selectTask1ImageForSIFT(index, letter) {
  if (!window.task1Images || index >= window.task1Images.length) return;
  
  const file = window.task1Images[index];
  if (letter === 'A') {
    siftImageA = file;
    updateSiftImageDisplay('A', file, selectedImageADiv);
  } else {
    siftImageB = file;
    updateSiftImageDisplay('B', file, selectedImageBDiv);
  }
  updateSiftButtons();
}

const siftImageAInput = document.getElementById('siftImageA');
const siftImageBInput = document.getElementById('siftImageB');
const selectedImageADiv = document.getElementById('selectedImageA');
const selectedImageBDiv = document.getElementById('selectedImageB');
const siftProcessBtn = document.getElementById('siftProcessBtn');
const siftClearBtn = document.getElementById('siftClearBtn');
const siftLoadingIndicator = document.getElementById('siftLoadingIndicator');
const siftErrorMessage = document.getElementById('siftErrorMessage');
const siftResultContainer = document.getElementById('siftResultContainer');
const customSiftImage = document.getElementById('customSiftImage');
const opencvSiftImage = document.getElementById('opencvSiftImage');
const customSiftStats = document.getElementById('customSiftStats');
const opencvSiftStats = document.getElementById('opencvSiftStats');

// Initialize SIFT handlers if elements exist
if (siftImageAInput && siftImageBInput) {
  siftImageAInput.addEventListener('change', (e) => {
    siftImageA = e.target.files[0];
    updateSiftImageDisplay('A', siftImageA, selectedImageADiv);
    updateSiftButtons();
  });

  siftImageBInput.addEventListener('change', (e) => {
    siftImageB = e.target.files[0];
    updateSiftImageDisplay('B', siftImageB, selectedImageBDiv);
    updateSiftButtons();
  });

  if (siftProcessBtn) {
    siftProcessBtn.addEventListener('click', handleSiftProcess);
  }

  if (siftClearBtn) {
    siftClearBtn.addEventListener('click', handleSiftClear);
  }
}

function updateSiftImageDisplay(letter, file, container) {
  if (!container) return;
  
  if (!file) {
    container.innerHTML = '';
    container.style.display = 'none';
    return;
  }
  
  const reader = new FileReader();
  reader.onload = (e) => {
    container.innerHTML = `
      <div class="sift-image-preview">
        <div class="image-preview-large">
          <img src="${e.target.result}" alt="Image ${letter}" />
        </div>
        <div class="file-info">
          <span class="file-name">Image ${letter}: ${file.name}</span>
          <span class="file-size">(${(file.size / 1024 / 1024).toFixed(2)} MB)</span>
        </div>
      </div>
    `;
    container.style.display = 'block';
  };
  reader.onerror = () => {
    container.innerHTML = `
      <div class="file-item">
        <span>Image ${letter}: ${file.name}</span>
        <span class="file-size">(${(file.size / 1024 / 1024).toFixed(2)} MB)</span>
      </div>
    `;
    container.style.display = 'block';
  };
  reader.readAsDataURL(file);
}

function updateSiftButtons() {
  if (!siftProcessBtn || !siftClearBtn) return;
  
  const hasBoth = siftImageA && siftImageB;
  siftProcessBtn.disabled = !hasBoth;
  siftClearBtn.disabled = !siftImageA && !siftImageB;
  
  if (hasBoth) {
    siftProcessBtn.style.opacity = '1';
    siftProcessBtn.style.cursor = 'pointer';
  } else {
    siftProcessBtn.style.opacity = '0.5';
    siftProcessBtn.style.cursor = 'not-allowed';
  }
}

function handleSiftClear() {
  siftImageA = null;
  siftImageB = null;
  if (siftImageAInput) siftImageAInput.value = '';
  if (siftImageBInput) siftImageBInput.value = '';
  updateSiftImageDisplay('A', null, selectedImageADiv);
  updateSiftImageDisplay('B', null, selectedImageBDiv);
  updateSiftButtons();
  if (siftResultContainer) siftResultContainer.style.display = 'none';
  if (siftErrorMessage) siftErrorMessage.style.display = 'none';
}

async function handleSiftProcess() {
  if (!siftImageA || !siftImageB) {
    showSiftError('Please select both Image A and Image B');
    return;
  }
  
  // Hide previous results and errors
  if (siftResultContainer) siftResultContainer.style.display = 'none';
  if (siftErrorMessage) siftErrorMessage.style.display = 'none';
  if (siftLoadingIndicator) siftLoadingIndicator.style.display = 'block';
  if (siftProcessBtn) siftProcessBtn.disabled = true;
  
  try {
    // Prepare form data
    const formData = new FormData();
    formData.append('image_a', siftImageA);
    formData.append('image_b', siftImageB);
    formData.append('resize_width', '960');
    formData.append('octaves', '4');
    formData.append('scales', '3');
    formData.append('ratio_test', '0.75');
    formData.append('ransac_iters', '2000');
    formData.append('ransac_threshold', '3.0');
    
    // Call API
    const response = await fetch('/api/sift_ransac', {
      method: 'POST',
      body: formData
    });
    
    const data = await response.json();
    
    if (siftLoadingIndicator) siftLoadingIndicator.style.display = 'none';
    if (siftProcessBtn) siftProcessBtn.disabled = false;
    
    if (!response.ok || !data.success) {
      showSiftError(data.error || 'Failed to process SIFT + RANSAC. Please try again.');
      return;
    }
    
    // Display results
    if (data.custom && data.custom.matches_image && customSiftImage) {
      customSiftImage.src = data.custom.matches_image;
      
      if (customSiftStats) {
        customSiftStats.innerHTML = `
          <div class="sift-stats-content">
            <p><strong>Keypoints A:</strong> ${data.custom.keypoints_a}</p>
            <p><strong>Keypoints B:</strong> ${data.custom.keypoints_b}</p>
            <p><strong>Matches:</strong> ${data.custom.matches}</p>
            <p><strong>RANSAC Inliers:</strong> ${data.custom.inliers}</p>
          </div>
        `;
      }
    }
    
    if (data.opencv && data.opencv.matches_image && opencvSiftImage) {
      opencvSiftImage.src = data.opencv.matches_image;
      
      if (opencvSiftStats) {
        opencvSiftStats.innerHTML = `
          <div class="sift-stats-content">
            <p><strong>Keypoints A:</strong> ${data.opencv.keypoints_a}</p>
            <p><strong>Keypoints B:</strong> ${data.opencv.keypoints_b}</p>
            <p><strong>Matches:</strong> ${data.opencv.matches}</p>
            <p><strong>RANSAC Inliers:</strong> ${data.opencv.inliers}</p>
          </div>
        `;
      }
    }
    
    if (siftResultContainer) {
      siftResultContainer.style.display = 'block';
      siftResultContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    
  } catch (error) {
    if (siftLoadingIndicator) siftLoadingIndicator.style.display = 'none';
    if (siftProcessBtn) siftProcessBtn.disabled = false;
    showSiftError('Network error: ' + error.message);
    console.error('SIFT processing error:', error);
  }
}

function showSiftError(message) {
  if (!siftErrorMessage) {
    console.error('Error:', message);
    alert('Error: ' + message);
    return;
  }
  siftErrorMessage.textContent = `❌ Error: ${message}`;
  siftErrorMessage.style.display = 'block';
  siftErrorMessage.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

