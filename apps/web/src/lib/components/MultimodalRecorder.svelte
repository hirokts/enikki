<script lang="ts">
	import { onDestroy } from 'svelte';
	import AudioVisualizer from './AudioVisualizer.svelte';
	import { AudioRecorder, AudioPlayer } from '$lib/audio-utils';
	import { LiveClient } from '$lib/live-client';
	import { getVertexAIToken, createDiary } from '$lib/api';

	let { oncomplete }: { oncomplete: (data: { diaryId: string }) => void } = $props();

	let status: 'idle' | 'connecting' | 'connected' | 'listening' | 'speaking' | 'error' =
		$state('idle');
	let isFirstListening = $state(true);

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
				isFirstListening = false; // AIが話し始めたので初回フラグをオフ
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
					console.log('Diary event reported (conversation end signal)');

					// transcript を取得してから stop() する
					const transcript = client?.getTranscript() ?? [];
					console.log('Transcript entries:', transcript.length);

					stop();

					// date はブラウザから取得、内容は transcript から抽出
					createDiary({
						date: new Date().toISOString().split('T')[0],
						transcript
					})
						.then((response) => {
							console.log('Diary created:', response);
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
		// transcript を取得してから stop() する
		const transcript = client?.getTranscript() ?? [];
		console.log('End conversation - Transcript entries:', transcript.length);

		if (transcript.length === 0) {
			stop();
			alert('会話が短すぎます。もう少しお話ししてください。');
			return;
		}

		stop();

		// transcript から日記を生成（ツールコールなしで手動終了した場合）
		createDiary({
			date: new Date().toISOString().split('T')[0],
			transcript
		})
			.then((response) => {
				console.log('Diary created from transcript:', response);
				oncomplete({
					diaryId: response.id
				});
			})
			.catch((err) => {
				console.error('Failed to create diary:', err);
				alert('日記の保存に失敗しました。');
			});
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

	{#if status === 'connecting'}
		<p class="animate-pulse text-center text-muted-foreground">接続中...</p>
	{:else if (status === 'connected' || status === 'listening') && isFirstListening}
		<p class="text-center text-foreground">
			<span class="text-lg">🎤</span> 「こんにちは」と話しかけてみてください
		</p>
	{:else if status === 'error'}
		<div class="rounded-lg bg-destructive/20 px-4 py-2 text-destructive">
			エラーが発生しました。コンソールを確認してください。
		</div>
	{/if}

	<div class="flex gap-4">
		{#if status === 'idle' || status === 'error'}
			<button
				class="rounded-full bg-gradient-to-br from-primary to-accent px-8 py-4 text-lg font-bold text-primary-foreground shadow-lg transition-all duration-200 hover:-translate-y-0.5 hover:shadow-accent/40"
				onclick={startConversation}
			>
				話しかける
			</button>
		{:else}
			<button
				class="rounded-full border-2 border-border bg-card px-8 py-4 text-lg font-bold text-foreground transition-all duration-200 hover:bg-muted"
				onclick={endConversation}
			>
				日記にする
			</button>
		{/if}
	</div>

	{#if status !== 'idle'}
		<button class="mt-4 text-xs text-muted-foreground underline" onclick={stop}>
			強制終了 (Debug)
		</button>
	{/if}
</div>
