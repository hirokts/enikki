<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import AudioVisualizer from './AudioVisualizer.svelte';

  const dispatch = createEventDispatcher();

  let status: 'idle' | 'connecting' | 'connected' | 'listening' | 'thinking' | 'speaking' = 'idle';
  let conversationCount = 0;

  function startConversation() {
    status = 'connecting';
    setTimeout(() => {
        status = 'connected';
        startListening();
    }, 1000);
  }

  function startListening() {
    status = 'listening';
    // Mock user speaking for 3 seconds
    setTimeout(() => {
        status = 'thinking';
        // Mock AI thinking for 2 seconds
        setTimeout(() => {
            status = 'speaking';
            // Mock AI speaking for 3 seconds
            setTimeout(() => {
                conversationCount++;
                if (conversationCount >= 2) {
                    // After 2 turns, let user decide to continue or stop
                    status = 'listening'; // Go back to listening
                } else {
                    startListening();
                }
            }, 3000);
        }, 2000);
    }, 3000);
  }

  function endConversation() {
    status = 'thinking'; // Simulate final processing
    setTimeout(() => {
        // Dispatch mock result
        dispatch('complete', {
            imageSrc: 'https://images.unsplash.com/photo-1516934024742-b461fba47600?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTB8fHN1bW1lciUyMHZpYmV8ZW58MHx8MHx8fDA%3D',
            text: '今日はとても良い天気でした。近くの公園まで散歩に行きました。セミの声がたくさん聞こえて、夏を感じました。お昼には冷たいそうめんを食べました。'
        });
        status = 'idle';
        conversationCount = 0;
    }, 2000);
  }
</script>

<div class="recorder-container">
  <div class="visualizer-wrapper">
    <AudioVisualizer mode={status === 'listening' ? 'listening' : status === 'speaking' ? 'speaking' : status === 'thinking' ? 'thinking' : 'idle'} />
  </div>

  <div class="controls">
    {#if status === 'idle'}
      <button class="btn-primary" on:click={startConversation}>
        話しかける
      </button>
    {:else}
      <button class="btn-secondary" on:click={endConversation}>
        日記にする
      </button>
    {/if}
  </div>
</div>

<style>
  .recorder-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2rem;
    width: 100%;
    max-width: 600px;
    margin: 0 auto;
  }

  .visualizer-wrapper {
    width: 100%;
    display: flex;
    justify-content: center;
  }

  .controls {
    display: flex;
    gap: 1rem;
  }

  button {
    padding: 1rem 2rem;
    border-radius: 9999px;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    border: none;
    outline: none;
  }

  .btn-primary {
    background: linear-gradient(135deg, #4285f4, #34a853);
    color: white;
    box-shadow: 0 4px 15px rgba(66, 133, 244, 0.3);
  }

  .btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(66, 133, 244, 0.4);
  }

  .btn-secondary {
    background: #f1f3f4;
    color: #333;
    border: 1px solid #ddd;
  }

  .btn-secondary:hover {
    background: #e8eaed;
  }
</style>
