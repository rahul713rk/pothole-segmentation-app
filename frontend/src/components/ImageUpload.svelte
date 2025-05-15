<!-- src/components/ImageUpload.svelte -->
<script>
  import { createEventDispatcher } from 'svelte';
  
  const dispatch = createEventDispatcher();
  
  let selectedFile = null;
  let previewUrl = null;
  let fileInput;
  
  // API endpoint for predictions
  const API_URL = 'https://pothole-segmentation-app.onrender.com/predict';
  
  // Handle file selection
  const handleFileChange = (event) => {
    const file = event.target.files[0];
    
    if (file && file.type.startsWith('image/')) {
      selectedFile = file;
      
      // Create preview URL
      previewUrl = URL.createObjectURL(file);
    } else {
      resetFileInput();
      if (file) {
        alert('Please select a valid image file.');
      }
    }
  };
  
  // Reset file input and preview
  const resetFileInput = () => {
    selectedFile = null;
    previewUrl = null;
    if (fileInput) {
      fileInput.value = '';
    }
  };
  
  // Handle predict button click
  const handlePredict = async () => {
    if (!selectedFile) {
      alert('Please select an image first.');
      return;
    }
    
    dispatch('loading', true);
    
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      
      const response = await fetch(API_URL, {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to process image');
      }
      
      const resultData = await response.json();
      dispatch('predictionResult', resultData);
      
    } catch (error) {
      console.error('Error making prediction:', error);
      dispatch('error', error.message);
    }
  };
</script>

<div class="image-upload">
  <div class="upload-area">
    <label for="file-input">
      {#if previewUrl}
        <img src={previewUrl} alt="Preview" class="preview-image"/>
      {:else}
        <div class="upload-placeholder">
          <span class="upload-icon">📁</span>
          <span>Click to upload image</span>
        </div>
      {/if}
    </label>
    
    <input
      id="file-input"
      type="file"
      accept="image/*"
      on:change={handleFileChange}
      bind:this={fileInput}
    />
  </div>
  
  <div class="button-group">
    <button class="predict-button" on:click={handlePredict} disabled={!selectedFile}>
      Predict
    </button>
    
    {#if selectedFile}
      <button class="reset-button" on:click={resetFileInput}>
        Clear
      </button>
    {/if}
  </div>
</div>

<style>
  .image-upload {
    margin: 2rem 0;
  }
  
  .upload-area {
    border: 2px dashed #ccc;
    border-radius: 5px;
    padding: 1rem;
    text-align: center;
    margin-bottom: 1rem;
    cursor: pointer;
    transition: border-color 0.3s ease;
  }
  
  .upload-area:hover {
    border-color: #3498db;
  }
  
  .upload-placeholder {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 200px;
    color: #666;
  }
  
  .upload-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
  }
  
  .preview-image {
    max-width: 100%;
    max-height: 300px;
    display: block;
    margin: 0 auto;
  }
  
  input[type="file"] {
    display: none;
  }
  
  .button-group {
    display: flex;
    gap: 1rem;
    justify-content: center;
  }
  
  button {
    padding: 0.75rem 1.5rem;
    font-size: 1rem;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }
  
  .predict-button {
    background-color: #3498db;
    color: white;
  }
  
  .predict-button:hover {
    background-color: #2980b9;
  }
  
  .predict-button:disabled {
    background-color: #95a5a6;
    cursor: not-allowed;
  }
  
  .reset-button {
    background-color: #e74c3c;
    color: white;
  }
  
  .reset-button:hover {
    background-color: #c0392b;
  }
</style>