<script lang="ts">
  export let mode: 'idle' | 'listening' | 'thinking' | 'speaking' = 'idle';

  // Simple mock visualization logic
  // In a real app, this would use Web Audio API to analyze frequency data
</script>

<div class="visualizer-container" data-mode={mode}>
  <div class="bars">
    {#each Array(5) as _, i}
      <div class="bar" style="animation-delay: {i * 0.1}s"></div>
    {/each}
  </div>
  <div class="status-text">
    {#if mode === 'idle'}
      Start Conversation
    {:else if mode === 'listening'}
      Listening...
    {:else if mode === 'thinking'}
      Thinking...
    {:else if mode === 'speaking'}
      Speaking...
    {/if}
  </div>
</div>

<style>
  .visualizer-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    height: 200px;
    width: 100%;
    transition: all 0.3s ease;
  }

  .bars {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    height: 60px;
  }

  .bar {
    width: 8px;
    background-color: #333;
    border-radius: 4px;
    height: 10px;
    transition: all 0.2s ease;
  }

  /* Animations for different modes */
  [data-mode="listening"] .bar {
    background-color: #4285f4; /* Google Blue */
    animation: wave 1s infinite ease-in-out;
  }

  [data-mode="speaking"] .bar {
    background-color: #34a853; /* Google Green */
    animation: wave 0.5s infinite ease-in-out;
  }

  [data-mode="thinking"] .bar {
    background-color: #fbbc05; /* Google Yellow */
    animation: pulse 1.5s infinite ease-in-out;
  }

  [data-mode="idle"] .bar {
    height: 10px;
    background-color: #ccc;
  }

  .status-text {
    font-family: 'Inter', sans-serif;
    font-size: 1rem;
    font-weight: 500;
    color: #555;
  }

  @keyframes wave {
    0%, 100% { height: 10px; }
    50% { height: 50px; }
  }

  @keyframes pulse {
    0%, 100% { opacity: 0.5; transform: scale(0.9); }
    50% { opacity: 1; transform: scale(1.1); }
  }
</style>
