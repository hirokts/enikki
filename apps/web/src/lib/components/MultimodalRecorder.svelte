<script lang="ts">
	import { onDestroy } from 'svelte';
	import AudioVisualizer from './AudioVisualizer.svelte';
	import { AudioRecorder, AudioPlayer } from '$lib/audio-utils';
	import { LiveClient } from '$lib/live-client';
	import { getVertexAIToken, createDiary } from '$lib/api';

	let { oncomplete }: { oncomplete: (data: { diaryId: string }) => void } = $props();

	let status: 'idle' | 'connecting' | 'connected' | 'listening' | 'speaking' | 'error' =
		$state('idle');

	let client: LiveClient | null = null;
	let recorder: AudioRecorder | null = null;
	let player: AudioPlayer | null = null;

	async function startConversation() {
		status = 'connecting';
		try {
			// 1. Get Access Token from backend
			const token = await getVertexAIToken();
			console.log('Got token for project:', token.projectId);

			// 2. Initialize WebSocket Client
			client = new LiveClient({
				projectId: token.projectId,
				region: token.region,
				accessToken: token.accessToken
			});

			// 3. Initialize Audio
			recorder = new AudioRecorder();
			player = new AudioPlayer();

			// 4. Setup Events
			client.addEventListener('open', () => {
				console.log('Connected to Vertex AI Live API');
			});

			client.addEventListener('setupComplete', async () => {
				status = 'connected';
				await startListening();
			});

			client.addEventListener('audio', ((e: CustomEvent) => {
				status = 'speaking';
				player?.play(e.detail);
			}) as EventListener);

			client.addEventListener('turnComplete', () => {
				status = 'listening';
			});

			client.addEventListener('close', () => {
				console.log('Disconnected');
				if (status !== 'idle') {
					stop();
				}
			});

			client.addEventListener('toolCall', ((e: CustomEvent) => {
				const toolCall = e.detail;
				const functionCall = toolCall.functionCalls[0];

				if (functionCall.name === 'report_diary_event') {
					console.log('Diary event reported:', functionCall.args);

					stop();

					// args are already an object
					const args = functionCall.args;

					// Send log to backend
					createDiary({
						date: args.date || new Date().toISOString().split('T')[0],
						location: args.location,
						activity: args.activity,
						feeling: args.feeling,
						summary: args.summary,
						joke_hint: args.joke_hint
					})
						.then((response) => {
							console.log('Diary created:', response);
							// Complete the conversation with structured data
							oncomplete({
								diaryId: response.id
							});
						})
						.catch((err) => {
							console.error('Failed to create diary:', err);
							alert('日記の保存に失敗しました。');
						});
				}
			}) as EventListener);

			client.addEventListener('error', ((e: CustomEvent) => {
				console.error('Live API error:', e.detail);
				status = 'error';
			}) as EventListener);

			// 5. Connect
			client.connect();
		} catch (e) {
			console.error('Failed to start conversation', e);
			status = 'error';
		}
	}

	async function startListening() {
		if (!recorder || !client) return;

		await recorder.start();
		status = 'listening';

		recorder.addEventListener('data', ((e: CustomEvent) => {
			client?.sendAudio(e.detail);
		}) as EventListener);
	}

	function endConversation() {
		stop();
		// TODO: 会話ログから絵日記を生成（後続issue）
         // For now, we don't have a diary ID in this stub implementation
		// oncomplete({
		// 	diaryId: 'stub-id'
		// });
        alert("会話が短すぎます。もう少しお話ししてください。");
	}

	function stop() {
		recorder?.stop();
		client?.disconnect();
		status = 'idle';
		recorder = null;
		client = null;
		player = null;
	}

	onDestroy(() => {
		stop();
	});
</script>

<div class="mx-auto flex w-full max-w-2xl flex-col items-center gap-8">
	<div class="flex w-full justify-center">
		<AudioVisualizer
			mode={status === 'speaking' ? 'speaking' : status === 'listening' ? 'listening' : 'idle'}
		/>
	</div>

	{#if status === 'error'}
		<div class="text-red-500">エラーが発生しました。コンソールを確認してください。</div>
	{/if}

	<div class="flex gap-4">
		{#if status === 'idle' || status === 'error'}
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

	{#if status !== 'idle'}
		<button class="mt-4 text-xs text-gray-400 underline" onclick={stop}> 強制終了 (Debug) </button>
	{/if}
</div>
