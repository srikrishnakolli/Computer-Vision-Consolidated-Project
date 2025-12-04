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
let panoramaDataUrl = null;

const imageUpload = document.getElementById('image-upload');
const selectedImagesContainer = document.getElementById('selected-images');
const stitchBtn = document.getElementById('stitch-btn');
const resultSection = document.getElementById('result-section');
const panoramaContainer = document.getElementById('panorama-container');
const downloadBtn = document.getElementById('download-btn');
const errorMessage = document.getElementById('error-message');
const loadingDiv = document.getElementById('loading');

if (imageUpload) {
  imageUpload.addEventListener('change', (e) => {
    selectedFiles = Array.from(e.target.files);
    displaySelectedImages();
    updateStitchButton();
  });
}

function displaySelectedImages() {
  selectedImagesContainer.innerHTML = '';
  
  if (selectedFiles.length === 0) {
    return;
  }
  
  const previewGrid = document.createElement('div');
  previewGrid.className = 'preview-grid';
  
  selectedFiles.forEach((file, index) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const imgWrapper = document.createElement('div');
      imgWrapper.className = 'preview-item';
      
      const img = document.createElement('img');
      img.src = e.target.result;
      img.alt = file.name;
      
      const removeBtn = document.createElement('button');
      removeBtn.className = 'remove-btn';
      removeBtn.innerHTML = '×';
      removeBtn.onclick = () => {
        selectedFiles.splice(index, 1);
        displaySelectedImages();
        updateStitchButton();
        // Update file input
        const dt = new DataTransfer();
        selectedFiles.forEach(f => dt.items.add(f));
        imageUpload.files = dt.files;
      };
      
      imgWrapper.appendChild(img);
      imgWrapper.appendChild(removeBtn);
      previewGrid.appendChild(imgWrapper);
    };
    reader.readAsDataURL(file);
  });
  
  selectedImagesContainer.appendChild(previewGrid);
}

function updateStitchButton() {
  stitchBtn.disabled = selectedFiles.length < 2;
}

if (stitchBtn) {
  stitchBtn.addEventListener('click', async () => {
    if (selectedFiles.length < 2) {
      showError('Please select at least 2 images');
      return;
    }
    
    // Hide previous results and errors
    resultSection.style.display = 'none';
    errorMessage.style.display = 'none';
    loadingDiv.style.display = 'block';
    stitchBtn.disabled = true;
    stitchBtn.textContent = 'Stitching...';
    
    try {
      const formData = new FormData();
      selectedFiles.forEach(file => {
        formData.append('images', file);
      });
      
      const apiUrl = window.location.origin + '/api/stitch_panorama';
      const response = await fetch(apiUrl, {
        method: 'POST',
        body: formData
      });
      
      const data = await response.json();
      
      if (!response.ok || !data.success) {
        throw new Error(data.error || 'Stitching failed');
      }
      
      // Display result
      panoramaDataUrl = data.panorama;
      panoramaContainer.innerHTML = `<img src="${data.panorama}" alt="Stitched Panorama" style="width: 100%; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);" />`;
      resultSection.style.display = 'block';
      
      // Scroll to result
      resultSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      
    } catch (error) {
      console.error('Stitching error:', error);
      showError(error.message || 'Failed to stitch images. Please ensure images have sufficient overlap (40-60%).');
    } finally {
      loadingDiv.style.display = 'none';
      stitchBtn.disabled = false;
      stitchBtn.textContent = 'Stitch Images';
    }
  });
}

if (downloadBtn) {
  downloadBtn.addEventListener('click', () => {
    if (!panoramaDataUrl) return;
    
    const link = document.createElement('a');
    link.href = panoramaDataUrl;
    link.download = 'panorama_' + Date.now() + '.jpg';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  });
}

function showError(message) {
  errorMessage.textContent = message;
  errorMessage.style.display = 'block';
  setTimeout(() => {
    errorMessage.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }, 100);
}

