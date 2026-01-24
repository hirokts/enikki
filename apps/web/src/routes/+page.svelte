<script lang="ts">
  import MultimodalRecorder from '$lib/components/MultimodalRecorder.svelte';
  import DiaryCard from '$lib/components/DiaryCard.svelte';
  import { fade, fly } from 'svelte/transition';

  let generatedDiary: { imageSrc: string; text: string } | null = null;

  function handleComplete(event: CustomEvent) {
    generatedDiary = event.detail;
  }

  function reset() {
    generatedDiary = null;
  }
</script>

<div class="page-content">
  {#if !generatedDiary}
    <div class="recorder-section" out:fade>
      <div class="hero-text">
        <h2>あなたの今日を、<br/>絵日記にしませんか？</h2>
        <p>AIとお話しするだけで、素敵な思い出として記録します。</p>
      </div>
      <MultimodalRecorder on:complete={handleComplete} />
    </div>
  {:else}
    <div class="result-section" in:fly={{ y: 50, duration: 800, delay: 200 }}>
      <DiaryCard imageSrc={generatedDiary.imageSrc} text={generatedDiary.text} />
      <button class="reset-btn" on:click={reset}>もう一度記録する</button>
    </div>
  {/if}
</div>

<style>
  .page-content {
    width: 100%;
    max-width: 800px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 60vh;
  }

  .hero-text {
    text-align: center;
    margin-bottom: 3rem;
  }

  h2 {
    font-size: 2.5rem;
    font-weight: 800;
    line-height: 1.2;
    margin-bottom: 1rem;
    background: linear-gradient(135deg, #333, #666);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  p {
    font-size: 1.1rem;
    color: #666;
  }

  .recorder-section {
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .result-section {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2rem;
  }

  .reset-btn {
    background: none;
    border: none;
    color: #4285f4;
    font-weight: 600;
    cursor: pointer;
    text-decoration: underline;
    opacity: 0.8;
    transition: opacity 0.2s;
  }

  .reset-btn:hover {
    opacity: 1;
  }
</style>
