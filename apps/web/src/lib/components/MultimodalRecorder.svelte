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

	// 会話履歴を蓄積
	type ConversationEntry = {
		role: 'user' | 'ai';
		text: string;
		timestamp: string;
	};
	let conversationHistory: ConversationEntry[] = $state([]);
	let currentAiText = $state(''); // AIの応答テキストを一時的に蓄積
	let turnCount = $state(0); // ユーザー発話のターン数

	// 最低ターン数と終了ボタンの有効化
	const MIN_TURNS = 3;
	let canEndConversation = $derived(turnCount >= MIN_TURNS);

	let client: LiveClient | null = null;
	let recorder: AudioRecorder | null = null;
	let player: AudioPlayer | null = null;

	async function startConversation() {
		status = 'connecting';
		// 会話履歴をリセット
		conversationHistory = [];
		currentAiText = '';
		turnCount = 0;

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

			// テキストイベント: AIの応答テキストを蓄積
			client.addEventListener('text', ((e: CustomEvent) => {
				currentAiText += e.detail;
			}) as EventListener);

			client.addEventListener('turnComplete', () => {
				// AIのターンが完了したら、蓄積したテキストを会話履歴に追加
				if (currentAiText.trim()) {
					conversationHistory = [
						...conversationHistory,
						{
							role: 'ai',
							text: currentAiText.trim(),
							timestamp: new Date().toISOString()
						}
					];
					console.log('AI response added to history:', currentAiText.trim().substring(0, 50) + '...');
					currentAiText = '';
				}
				status = 'listening';
				// リスニング開始 = ユーザーのターン開始
				turnCount++;
				console.log(`Turn count: ${turnCount}`);
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

					// 会話履歴をJSON文字列に変換
					const transcriptJson = JSON.stringify(conversationHistory);
					console.log('Conversation transcript:', transcriptJson);

					// Send log to backend
						createDiary({
							date: args.date || new Date().toISOString().split('T')[0],
							conversation_transcript: transcriptJson
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
		if (!canEndConversation) {
			alert(`まだ会話が短いです。もう少しお話ししてください（現在: ${turnCount}ターン、最低: ${MIN_TURNS}ターン）`);
			return;
		}
		stop();
		// 手動終了の場合、会話ログのみで日記を作成
		const transcriptJson = JSON.stringify(conversationHistory);
		console.log('Manual end - Conversation transcript:', transcriptJson);

		createDiary({
			date: new Date().toISOString().split('T')[0],
			conversation_transcript: transcriptJson
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
				class="rounded-full border-2 px-8 py-4 text-lg font-bold transition-all duration-200 {canEndConversation
					? 'border-border bg-card text-foreground hover:bg-muted'
					: 'cursor-not-allowed border-muted bg-muted/50 text-muted-foreground'}"
				onclick={endConversation}
				disabled={!canEndConversation}
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
