<script lang="ts">
  export let imageSrc: string;
  export let text: string;
  export let date: string = new Date().toLocaleDateString('ja-JP', { year: 'numeric', month: 'long', day: 'numeric' });
</script>

<div class="diary-card">
  <div class="image-container">
    {#if imageSrc}
      <img src={imageSrc} alt="Generated Diary" />
    {:else}
      <div class="placeholder">No Image</div>
    {/if}
  </div>
  <div class="content">
    <div class="date">{date}</div>
    <p class="text">{text}</p>
  </div>
</div>

<style>
  .diary-card {
    background: white;
    border-radius: 1px;
    padding: 1rem 1rem 3rem 1rem; /* Polaroid bottom padding */
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    max-width: 400px;
    width: 100%;
    margin: 0 auto;
    transform: rotate(-1deg);
    transition: transform 0.3s ease;
  }

  .diary-card:hover {
    transform: rotate(0deg) scale(1.02);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  }

  .image-container {
    width: 100%;
    aspect-ratio: 1 / 1;
    background-color: #f0f0f0;
    margin-bottom: 1.5rem;
    overflow: hidden;
    border: 1px solid #ddd;
  }

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .placeholder {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #999;
  }

  .content {
    text-align: center;
  }

  .date {
    font-family: 'Courier New', monospace;
    font-size: 0.9rem;
    color: #888;
    margin-bottom: 0.5rem;
  }

  .text {
    font-family: 'Zen Kurenaido', sans-serif; /* Fallback to sans-serif if not available */
    font-size: 1.2rem;
    line-height: 1.6;
    color: #333;
    white-space: pre-wrap;
  }
</style>
