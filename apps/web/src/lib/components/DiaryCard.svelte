<script lang="ts">
  export let imageSrc: string;
  export let text: string;
  export let date: string = new Date().toLocaleDateString('ja-JP', { year: 'numeric', month: 'long', day: 'numeric' });
</script>

<div class="group mx-auto w-full max-w-[400px] -rotate-1 bg-white p-4 pb-12 shadow-md transition-transform duration-300 hover:rotate-0 hover:scale-[1.02] hover:shadow-xl">
  <div class="mb-6 aspect-square w-full overflow-hidden border border-gray-200 bg-gray-100">
    {#if imageSrc}
      <img src={imageSrc} alt="Generated Diary" class="h-full w-full object-cover" />
    {:else}
      <div class="flex h-full w-full items-center justify-center text-gray-400">No Image</div>
    {/if}
  </div>
  <div class="text-center">
    <div class="mb-2 font-mono text-sm text-gray-500">{date}</div>
    <p class="font-handwriting whitespace-pre-wrap text-lg leading-relaxed text-gray-800">{text}</p>
  </div>
</div>
