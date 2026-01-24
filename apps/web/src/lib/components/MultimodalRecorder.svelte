<script lang="ts">
	import AudioVisualizer from './AudioVisualizer.svelte';

	let { oncomplete }: { oncomplete: (data: { imageSrc: string; text: string }) => void } = $props();

	let status: 'idle' | 'connecting' | 'connected' | 'listening' | 'thinking' | 'speaking' =
		$state('idle');
	let conversationCount = $state(0);

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
			oncomplete({
				imageSrc:
					'https://images.unsplash.com/photo-1516934024742-b461fba47600?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTB8fHN1bW1lciUyMHZpYmV8ZW58MHx8MHx8fDA%3D',
				text: '今日はとても良い天気でした。近くの公園まで散歩に行きました。セミの声がたくさん聞こえて、夏を感じました。お昼には冷たいそうめんを食べました。'
			});
			status = 'idle';
			conversationCount = 0;
		}, 2000);
	}
</script>

<div class="mx-auto flex w-full max-w-2xl flex-col items-center gap-8">
	<div class="flex w-full justify-center">
		<AudioVisualizer
			mode={status === 'listening'
				? 'listening'
				: status === 'speaking'
					? 'speaking'
					: status === 'thinking'
						? 'thinking'
						: 'idle'}
		/>
	</div>

	<div class="flex gap-4">
		{#if status === 'idle'}
			<button
				class="rounded-full bg-linear-to-br from-blue-500 to-green-500 px-8 py-4 text-lg font-bold text-white shadow-lg transition-all duration-200 hover:-translate-y-0.5 hover:shadow-blue-500/40"
				onclick={startConversation}
			>
				話しかける
			</button>
		{:else}
			<button
				class="rounded-full border border-gray-300 bg-gray-100 px-8 py-4 text-lg font-bold text-gray-800 transition-all duration-200 hover:bg-gray-200"
				onclick={endConversation}
			>
				日記にする
			</button>
		{/if}
	</div>
</div>
