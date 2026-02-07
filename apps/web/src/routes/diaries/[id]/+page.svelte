<script lang="ts">
	import DiaryCard from '$lib/components/DiaryCard.svelte';
	import { fade, fly } from 'svelte/transition';
	import { onMount, onDestroy } from 'svelte';
	import { page } from '$app/stores';
	import { getVertexAIToken } from '$lib/api';
	import { doc, getDoc, onSnapshot, type Firestore } from 'firebase/firestore';
	import { initializeFirebase } from '$lib/firebase';

	let db: Firestore | null = null;
	let diaryId: string = $derived($page.params.id);

	let diaryStatus: 'pending' | 'processing' | 'completed' | 'failed' | null = $state(null);
	let generatedDiary: { imageSrc: string; text: string; date?: string } | null = $state(null);
	let error: string | null = $state(null);
	let loading: boolean = $state(true);
	let unsubscribe: (() => void) | null = null;

	onMount(async () => {
		try {
			// Initialize Firebase with project ID from backend
			const token = await getVertexAIToken();
			db = initializeFirebase(token.projectId);

			// Start watching the diary document
			watchDiary();
		} catch (e) {
			console.error('Failed to initialize:', e);
			error = '初期化に失敗しました';
			loading = false;
		}
	});

	function watchDiary() {
		if (!db || !diaryId) {
			loading = false;
			error = '日記IDが見つかりません';
			return;
		}

		const docRef = doc(db, 'diaries', diaryId);

		// First, try to get the document once
		getDoc(docRef)
			.then((docSnapshot) => {
				if (!docSnapshot.exists()) {
					loading = false;
					error = '日記が見つかりません';
					return;
				}

				// Document exists, start real-time listener
				unsubscribe = onSnapshot(
					docRef,
					(docSnapshot) => {
						loading = false;
						if (docSnapshot.exists()) {
							const data = docSnapshot.data();
							diaryStatus = data.status;
							console.log('Diary status:', diaryStatus);

							if (data.status === 'completed') {
								generatedDiary = {
									imageSrc: data.imageUrl,
									text: data.diaryText,
									date: data.conversationLog?.date || undefined
								};
							} else if (data.status === 'failed') {
								error = data.error || '生成に失敗しました';
							}
						}
					},
					(err) => {
						console.error('Firestore subscription error:', err);
						loading = false;
						error = err.message;
					}
				);
			})
			.catch((err) => {
				console.error('Failed to get document:', err);
				loading = false;
				error = err.message;
			});
	}

	onDestroy(() => {
		if (unsubscribe) {
			unsubscribe();
		}
	});
</script>

<svelte:head>
	<title>絵日記 - Enikki</title>
</svelte:head>

<div class="flex min-h-[60vh] w-full max-w-4xl flex-col items-center justify-center">
	{#if loading}
		<!-- ローディング画面 -->
		<div class="flex flex-col items-center gap-4" in:fade>
			<div
				class="h-8 w-8 animate-spin rounded-full border-4 border-blue-500 border-t-transparent"
			></div>
			<p class="text-gray-500">読み込み中...</p>
		</div>
	{:else if error}
		<!-- エラー画面 -->
		<div class="flex flex-col items-center gap-6 text-center" in:fade>
			<div class="flex h-24 w-24 items-center justify-center rounded-full bg-red-100 text-red-500">
				<svg
					xmlns="http://www.w3.org/2000/svg"
					class="h-12 w-12"
					fill="none"
					viewBox="0 0 24 24"
					stroke="currentColor"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
					/>
				</svg>
			</div>
			<div>
				<h3 class="text-xl font-bold text-gray-800">エラーが発生しました</h3>
				<p class="mt-2 text-gray-500">{error}</p>
			</div>
			<a
				href="/"
				class="rounded-full bg-gray-200 px-6 py-2 font-bold text-gray-700 hover:bg-gray-300"
			>
				トップに戻る
			</a>
		</div>
	{:else if diaryStatus === 'pending' || diaryStatus === 'processing'}
		<!-- 生成中画面 -->
		<div class="flex flex-col items-center gap-6" in:fade>
			<div class="relative flex h-32 w-32 items-center justify-center">
				<div class="absolute inset-0 animate-ping rounded-full bg-blue-100 opacity-75"></div>
				<div class="relative flex h-24 w-24 items-center justify-center rounded-full bg-blue-50">
					<svg
						xmlns="http://www.w3.org/2000/svg"
						class="h-12 w-12 animate-bounce text-blue-500"
						fill="none"
						viewBox="0 0 24 24"
						stroke="currentColor"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"
						/>
					</svg>
				</div>
			</div>
			<div class="text-center">
				<h3 class="text-2xl font-bold text-gray-800">
					{#if diaryStatus === 'pending'}
						日記の準備をしています...
					{:else}
						絵を描いています...
					{/if}
				</h3>
				<p class="mt-2 text-gray-500">少し時間がかかります。そのままお待ちください。</p>
			</div>
		</div>
	{:else if diaryStatus === 'completed' && generatedDiary}
		<!-- 完了画面 -->
		<div class="flex flex-col items-center gap-8" in:fly={{ y: 50, duration: 800, delay: 200 }}>
			<DiaryCard
				imageSrc={generatedDiary.imageSrc}
				text={generatedDiary.text}
				date={generatedDiary.date}
			/>
			<a
				href="/"
				class="font-semibold text-blue-500 underline decoration-blue-500/30 underline-offset-4 opacity-80 transition-all hover:decoration-blue-500 hover:opacity-100"
			>
				新しい絵日記を作る
			</a>
		</div>
	{:else}
		<!-- 不明な状態 -->
		<div class="flex flex-col items-center gap-4 text-center" in:fade>
			<p class="text-gray-500">日記を読み込んでいます...</p>
			<p class="font-mono text-xs text-gray-400">ID: {diaryId}</p>
		</div>
	{/if}
</div>
