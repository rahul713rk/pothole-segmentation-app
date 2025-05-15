<!-- src/components/PredictionDisplay.svelte -->
<script>
  export let data;
  
  // Extract data from props
  $: segmentationImage = data?.segmentation_image || '';
  $: predictedLabels = data?.predicted_labels || [];
  $: hasPotholes = predictedLabels.includes('Pothole');
</script>

<div class="prediction-display">
  <h2>Segmentation Result</h2>
  
  {#if segmentationImage}
    <div class="result-image">
      <img src={segmentationImage} alt="Segmentation Result" />
    </div>
  {/if}
  
  <div class="prediction-labels">
    <h3>Predicted Labels</h3>
    
    {#if hasPotholes}
      <div class="detection-result detected">
        <span class="icon">⚠️</span>
        <span class="label">Pothole Detected</span>
      </div>
    {:else}
      <div class="detection-result not-detected">
        <span class="icon">✓</span>
        <span class="label">No Potholes Detected</span>
      </div>
    {/if}
  </div>
</div>

<style>
  .prediction-display {
    margin-top: 2rem;
    padding: 1rem;
    border: 1px solid #e0e0e0;
    border-radius: 5px;
    background-color: #f9f9f9;
  }
  
  h2 {
    color: #333;
    margin-top: 0;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #e0e0e0;
  }
  
  .result-image {
    text-align: center;
    margin-bottom: 1.5rem;
  }
  
  .result-image img {
    max-width: 100%;
    max-height: 400px;
    border-radius: 4px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  }
  
  .prediction-labels {
    background-color: white;
    padding: 1rem;
    border-radius: 4px;
  }
  
  h3 {
    color: #333;
    margin-top: 0;
    margin-bottom: 1rem;
  }
  
  .detection-result {
    display: flex;
    align-items: center;
    padding: 1rem;
    border-radius: 4px;
    font-weight: bold;
  }
  
  .detected {
    background-color: #ffebee;
    color: #c62828;
  }
  
  .not-detected {
    background-color: #e8f5e9;
    color: #2e7d32;
  }
  
  .icon {
    font-size: 1.5rem;
    margin-right: 0.75rem;
  }
  
  .label {
    font-size: 1.2rem;
  }
</style>