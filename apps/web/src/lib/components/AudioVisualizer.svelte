<script lang="ts">
  export let mode: 'idle' | 'listening' | 'thinking' | 'speaking' = 'idle';
</script>

<div class="flex h-[200px] w-full flex-col items-center justify-center gap-4 transition-all duration-300" data-mode={mode}>
  <div class="flex h-[60px] items-center justify-center gap-[6px]">
    {#each Array(5) as _, i}
      <div 
        class="w-2 rounded-full transition-all duration-200"
        class:bg-gray-300={mode === 'idle'}
        class:h-2.5={mode === 'idle'}
        
        class:bg-blue-500={mode === 'listening'}
        class:animate-wave={mode === 'listening'}
        
        class:bg-green-500={mode === 'speaking'}
        class:animate-wave-fast={mode === 'speaking'}
        
        class:bg-yellow-400={mode === 'thinking'}
        class:animate-pulse={mode === 'thinking'}
        
        style="animation-delay: {i * 0.1}s"
      ></div>
    {/each}
  </div>
  <div class="font-display text-base font-medium text-gray-600">
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
  /* Custom animations that are hard to express purely in utility classes without config */
  @keyframes wave {
    0%, 100% { height: 10px; }
    50% { height: 50px; }
  }
  
  .animate-wave {
    animation: wave 1s infinite ease-in-out;
  }
  
  .animate-wave-fast {
    animation: wave 0.5s infinite ease-in-out;
  }
</style>
