<script lang="ts">
	import MultimodalRecorder from '$lib/components/MultimodalRecorder.svelte';
	import DiaryCard from '$lib/components/DiaryCard.svelte';
	import { fade, fly } from 'svelte/transition';
	import { onMount, onDestroy } from 'svelte';
	import { checkApiKeyStatus } from '$lib/api';
	import { doc, onSnapshot } from 'firebase/firestore';
	import { db } from '$lib/firebase';

	onMount(() => {
		checkApiKeyStatus();
	});

	let diaryId: string | null = $state(null);
	let diaryStatus: 'pending' | 'processing' | 'completed' | 'failed' | null = $state(null);
	let generatedDiary: { imageSrc: string; text: string } | null = $state(null);
	let error: string | null = $state(null);
	let unsubscribe: (() => void) | null = null;

	function handleComplete(data: { diaryId: string }) {
		diaryId = data.diaryId;
		diaryStatus = 'pending';

		unsubscribe = onSnapshot(doc(db, 'diaries', diaryId), (doc) => {
			if (doc.exists()) {
				const data = doc.data();
				diaryStatus = data.status;
				console.log('Diary status updated:', diaryStatus);

				if (data.status === 'completed') {
					generatedDiary = {
						imageSrc: data.imageUrl,
						text: data.diaryText
					};
				} else if (data.status === 'failed') {
					error = data.error || '生成に失敗しました';
				}
			} else {
				console.log('Document does not exist yet');
			}
		}, (err) => {
			console.error("Firestore subscription error:", err);
			diaryStatus = 'failed';
			error = err.message;
		});
	}

	function reset() {
		if (unsubscribe) {
			unsubscribe();
			unsubscribe = null;
		}
		diaryId = null;
		diaryStatus = null;
		generatedDiary = null;
		error = null;
	}

	onDestroy(() => {
		if (unsubscribe) {
			unsubscribe();
		}
	});
</script>

<div class="flex min-h-[60vh] w-full max-w-4xl flex-col items-center justify-center">
	{#if !diaryId}
		<!-- 初期画面: レコーダー表示 -->
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
			<DiaryCard imageSrc={generatedDiary.imageSrc} text={generatedDiary.text} />
			<button
				class="font-semibold text-blue-500 underline decoration-blue-500/30 underline-offset-4 opacity-80 transition-all hover:decoration-blue-500 hover:opacity-100"
				onclick={reset}
			>
				もう一度記録する
			</button>
		</div>
	{:else if diaryStatus === 'failed'}
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
			<button
				class="rounded-full bg-gray-200 px-6 py-2 font-bold text-gray-700 hover:bg-gray-300"
				onclick={reset}
			>
				最初に戻る
			</button>
		</div>
	{/if}
</div>
