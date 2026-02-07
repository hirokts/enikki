<script lang="ts">
	let {
		imageSrc,
		text,
		date = new Date().toLocaleDateString('ja-JP', {
			year: 'numeric',
			month: 'long',
			day: 'numeric'
		})
	}: {
		imageSrc: string;
		text: string;
		date?: string;
	} = $props();
</script>

<div
	class="group mx-auto w-full max-w-[400px] -rotate-1 rounded-lg border-4 border-border bg-card p-4 pb-12 shadow-lg transition-transform duration-300 hover:scale-[1.02] hover:rotate-0 hover:shadow-2xl"
>
	<div class="mb-6 aspect-square w-full overflow-hidden rounded-md border border-border bg-muted">
		{#if imageSrc}
			<img src={imageSrc} alt="Generated Diary" class="h-full w-full object-cover" />
		{:else}
			<div class="flex h-full w-full items-center justify-center text-muted-foreground">
				No Image
			</div>
		{/if}
	</div>
	<div class="text-center">
		<div class="mb-2 font-pixel text-sm text-muted-foreground">{date}</div>
		<p class="text-lg leading-relaxed whitespace-pre-wrap text-foreground">{text}</p>
	</div>
</div>
