<!-- src/App.svelte -->
<script>
  import ImageUpload from './components/ImageUpload.svelte';
  import PredictionDisplay from './components/PredictionDisplay.svelte';
  
  let resultData = null;
  let isLoading = false;
  let error = null;

  // Handle the prediction result from ImageUpload component
  const handlePredictionResult = (event) => {
    resultData = event.detail;
    isLoading = false;
  };

  const handleLoading = (event) => {
    isLoading = event.detail;
    if (isLoading) {
      resultData = null;
      error = null;
    }
  };

  const handleError = (event) => {
    error = event.detail;
    isLoading = false;
  };
</script>

<main>
  <div class="App">
    <h1>Image Segmentation App for Pothole Detection</h1>
    
    <ImageUpload 
      on:predictionResult={handlePredictionResult}
      on:loading={handleLoading}
      on:error={handleError}
    />
    
    {#if isLoading}
      <div class="loading">
        <p>Processing image...</p>
        <div class="spinner"></div>
      </div>
    {:else if error}
      <div class="error">
        <p>Error: {error}</p>
      </div>
    {:else if resultData}
      <PredictionDisplay data={resultData} />
    {/if}
  </div>
</main>

<style>
  .App {
    max-width: 800px;
    margin: 0 auto;
    padding: 2rem;
    font-family: Arial, sans-serif;
  }
  
  h1 {
    color: #333;
    text-align: center;
    margin-bottom: 2rem;
  }
  
  .loading {
    text-align: center;
    margin-top: 2rem;
  }
  
  .spinner {
    border: 4px solid #f3f3f3;
    border-top: 4px solid #3498db;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 2s linear infinite;
    margin: 0 auto;
  }
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
  
  .error {
    background-color: #ffebee;
    color: #c62828;
    padding: 1rem;
    border-radius: 4px;
    margin-top: 2rem;
  }
</style>