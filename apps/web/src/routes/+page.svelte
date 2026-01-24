<script lang="ts">
	import MultimodalRecorder from '$lib/components/MultimodalRecorder.svelte';
	import DiaryCard from '$lib/components/DiaryCard.svelte';
	import { fade, fly } from 'svelte/transition';

	let generatedDiary: { imageSrc: string; text: string } | null = $state(null);

	function handleComplete(data: { imageSrc: string; text: string }) {
		generatedDiary = data;
	}

	function reset() {
		generatedDiary = null;
	}
</script>

<div class="flex min-h-[60vh] w-full max-w-4xl flex-col items-center justify-center">
	{#if !generatedDiary}
		<div class="flex w-full flex-col items-center" out:fade>
			<div class="mb-12 text-center">
				<h2
					class="mb-4 bg-linear-to-br from-gray-700 to-gray-500 bg-clip-text text-4xl leading-tight font-extrabold text-transparent sm:text-5xl"
				>
					あなたの今日を、<br />絵日記にしませんか？
				</h2>
				<p class="text-lg text-gray-500">AIとお話しするだけで、素敵な思い出として記録します。</p>
			</div>
			<MultimodalRecorder oncomplete={handleComplete} />
		</div>
	{:else}
		<div class="flex flex-col items-center gap-8" in:fly={{ y: 50, duration: 800, delay: 200 }}>
			<DiaryCard imageSrc={generatedDiary.imageSrc} text={generatedDiary.text} />
			<button
				class="font-semibold text-blue-500 underline decoration-blue-500/30 underline-offset-4 opacity-80 transition-all hover:decoration-blue-500 hover:opacity-100"
				onclick={reset}
			>
				もう一度記録する
			</button>
		</div>
	{/if}
</div>
