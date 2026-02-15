<script lang="ts">
	import MultimodalRecorder from '$lib/components/MultimodalRecorder.svelte';
	import DiaryCard from '$lib/components/DiaryCard.svelte';
	import { fade, fly } from 'svelte/transition';
	import { onMount, onDestroy } from 'svelte';
	import { checkAuthStatus, getVertexAIToken } from '$lib/api';
	import { doc, onSnapshot, setLogLevel, type Firestore } from 'firebase/firestore';
	import { getFirebase, googleProvider } from '$lib/firebase';
	import { signInWithPopup, type User } from 'firebase/auth';

	let db: Firestore | null = null;
	let user: User | null = $state(null);
	let isLoaded = $state(false);

	// Discord Webhook 設定
	let showWebhookModal = $state(false);
	let webhookUrlInput = $state('');
	let savedWebhookUrl = $state('');

	onMount(async () => {
		isLoaded = true;
		const { auth, db: firestore } = getFirebase();
		db = firestore;
		setLogLevel('debug');

		auth.onAuthStateChanged((u) => {
			user = u;
		});

		// localStorage から Webhook URL を復元
		const stored = localStorage.getItem('discord_webhook_url');
		if (stored) {
			savedWebhookUrl = stored;
			webhookUrlInput = stored;
		}
	});

	async function login() {
		const { auth } = getFirebase();
		try {
			await signInWithPopup(auth, googleProvider);
		} catch (err) {
			console.error('Login error:', err);
			error = 'ログインに失敗しました';
		}
	}

	// Webhook 設定
	function openWebhookModal() {
		webhookUrlInput = savedWebhookUrl;
		showWebhookModal = true;
	}

	function saveWebhookUrl() {
		const url = webhookUrlInput.trim();
		if (url && !url.startsWith('https://discord.com/api/webhooks/')) {
			alert(
				'Discord Webhook URL の形式が正しくありません。\nhttps://discord.com/api/webhooks/... の形式で入力してください。'
			);
			return;
		}
		if (url) {
			localStorage.setItem('discord_webhook_url', url);
			savedWebhookUrl = url;
		} else {
			localStorage.removeItem('discord_webhook_url');
			savedWebhookUrl = '';
		}
		showWebhookModal = false;
	}

	function removeWebhookUrl() {
		localStorage.removeItem('discord_webhook_url');
		savedWebhookUrl = '';
		webhookUrlInput = '';
		showWebhookModal = false;
	}

	// Generate snow particles
	const snowParticles = Array.from({ length: 50 }, (_, i) => ({
		id: i,
		left: Math.random() * 100,
		delay: Math.random() * 5,
		duration: 5 + Math.random() * 5
	}));

	let diaryId: string | null = $state(null);
	let diaryStatus: 'pending' | 'processing' | 'completed' | 'failed' | null = $state(null);
	let generatedDiary: { imageSrc: string; text: string } | null = $state(null);
	let error: string | null = $state(null);
	let unsubscribe: (() => void) | null = null;

	function handleComplete(data: { diaryId: string }) {
		if (!db) {
			console.error('Firebase not initialized');
			error = 'Firebase が初期化されていません';
			diaryStatus = 'failed';
			return;
		}

		diaryId = data.diaryId;
		diaryStatus = 'pending';
		console.log('Start watching diary:', diaryId);

		unsubscribe = onSnapshot(
			doc(db, 'diaries', diaryId),
			(docSnapshot) => {
				if (docSnapshot.exists()) {
					const data = docSnapshot.data();
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
			},
			(err) => {
				console.error('Firestore subscription error:', err);
				diaryStatus = 'failed';
				error = err.message;
			}
		);
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

<!-- Hero Section with Background -->
<section class="relative min-h-screen overflow-hidden">
	<!-- Background Image -->
	<div class="absolute inset-0">
		<img src="/images/winter-hero.jpg" alt="冬の風景" class="h-full w-full object-cover" />
		<!-- Overlay for better readability -->
		<div
			class="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-background/90"
		></div>
	</div>

	<!-- Snow Animation -->
	<div class="pointer-events-none absolute inset-0 overflow-hidden">
		{#each snowParticles as particle (particle.id)}
			<div
				class="animate-snow absolute h-2 w-2 rounded-full bg-white/80"
				style="left: {particle.left}%; animation-delay: {particle.delay}s; animation-duration: {particle.duration}s;"
			></div>
		{/each}
	</div>

	<!-- Content -->
	<div class="relative z-10 flex min-h-screen flex-col items-center justify-center px-4 pt-16">
		{#if !diaryId}
			<!-- 初期画面: レコーダー表示 -->
			<div class="flex w-full flex-col items-center" out:fade>
				<!-- Title Box -->
				<div
					class="mb-8 transform rounded-lg border-4 border-primary bg-card/95 p-8 shadow-2xl backdrop-blur-sm transition-all duration-1000 md:p-12 {isLoaded
						? 'translate-y-0 opacity-100'
						: 'translate-y-10 opacity-0'}"
				>
					<div class="text-center">
						<!-- Pixel-style subtitle -->
						<p class="mb-4 font-pixel text-sm tracking-[0.3em] text-muted-foreground md:text-base">
							ぼくの
						</p>

						<!-- Main Title -->
						<h1 class="mb-2 text-5xl font-bold tracking-tight text-primary md:text-7xl lg:text-8xl">
							<span class="text-accent">絵</span>日記
						</h1>

						<!-- English subtitle -->
						<p class="mt-4 text-xs tracking-[0.5em] text-muted-foreground uppercase md:text-sm">
							My Picture Diary
						</p>
					</div>
				</div>

				<!-- Tagline -->
				<div
					class="mb-8 transition-all delay-500 duration-1000 {isLoaded
						? 'translate-y-0 opacity-100'
						: 'translate-y-10 opacity-0'}"
				>
					<p
						class="rounded-full bg-card/80 px-6 py-3 text-sm text-card-foreground/90 backdrop-blur-sm md:text-base"
					>
						AIとお話しするだけで、素敵な思い出を記録します
					</p>
				</div>

				<!-- Recorder / Login -->
				<div
					class="w-full max-w-2xl rounded-2xl bg-card/90 p-6 shadow-xl backdrop-blur-sm transition-all delay-700 duration-1000 {isLoaded
						? 'translate-y-0 opacity-100'
						: 'translate-y-10 opacity-0'}"
				>
					{#if user}
						<!-- 通知設定ボタン -->
						<div class="mb-4 flex justify-end">
							<button
								id="webhook-settings-btn"
								class="inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs transition-all {savedWebhookUrl
									? 'bg-accent/15 text-accent hover:bg-accent/25'
									: 'text-muted-foreground hover:bg-muted hover:text-foreground'}"
								onclick={openWebhookModal}
							>
								{#if savedWebhookUrl}
									<span>🔔</span> 通知ON
								{:else}
									<span>🔕</span> 通知設定
								{/if}
							</button>
						</div>
						<MultimodalRecorder oncomplete={handleComplete} />
					{:else}
						<div class="py-8 text-center">
							<button
								class="inline-flex items-center gap-2 rounded-full bg-primary px-8 py-4 font-bold text-primary-foreground transition-all hover:scale-105 active:scale-95"
								onclick={login}
							>
								<svg class="h-5 w-5" viewBox="0 0 24 24">
									<path
										fill="currentColor"
										d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
									/>
									<path
										fill="currentColor"
										d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
									/>
									<path
										fill="currentColor"
										d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z"
									/>
									<path
										fill="currentColor"
										d="M12 5.38c1.62 0 3.06.56 4.21 1.66l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
									/>
								</svg>
								Google でログインしてはじめる
							</button>
							<p class="mt-4 text-xs text-muted-foreground">
								※有効な Google アカウントのみ利用可能です
							</p>
						</div>
					{/if}
				</div>
			</div>
		{:else if diaryStatus === 'pending' || diaryStatus === 'processing'}
			<!-- 生成中画面 -->
			<div
				class="flex flex-col items-center gap-6 rounded-2xl bg-card/95 p-12 shadow-2xl backdrop-blur-sm"
				in:fade
			>
				<div class="relative flex h-32 w-32 items-center justify-center">
					<div class="absolute inset-0 animate-ping rounded-full bg-accent/30 opacity-75"></div>
					<div
						class="relative flex h-24 w-24 items-center justify-center rounded-full bg-accent/20"
					>
						<svg
							xmlns="http://www.w3.org/2000/svg"
							class="h-12 w-12 animate-bounce text-accent"
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
					<h3 class="text-2xl font-bold text-foreground">
						{#if diaryStatus === 'pending'}
							日記の準備をしています...
						{:else}
							絵を描いています...
						{/if}
					</h3>
					<p class="mt-2 text-muted-foreground">少し時間がかかります。そのままお待ちください。</p>
				</div>
			</div>
		{:else if diaryStatus === 'completed' && generatedDiary}
			<!-- 完了画面 -->
			<div class="flex flex-col items-center gap-8" in:fly={{ y: 50, duration: 800, delay: 200 }}>
				<DiaryCard imageSrc={generatedDiary.imageSrc} text={generatedDiary.text} />
				<button
					class="font-semibold text-accent underline decoration-accent/30 underline-offset-4 opacity-80 transition-all hover:decoration-accent hover:opacity-100"
					onclick={reset}
				>
					もう一度記録する
				</button>
			</div>
		{:else if diaryStatus === 'failed'}
			<!-- エラー画面 -->
			<div
				class="flex flex-col items-center gap-6 rounded-2xl bg-card/95 p-12 text-center shadow-2xl backdrop-blur-sm"
				in:fade
			>
				<div
					class="flex h-24 w-24 items-center justify-center rounded-full bg-destructive/20 text-destructive"
				>
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
					<h3 class="text-xl font-bold text-foreground">エラーが発生しました</h3>
					<p class="mt-2 text-muted-foreground">{error}</p>
				</div>
				<button
					class="rounded-full bg-muted px-6 py-2 font-bold text-foreground hover:bg-muted/80"
					onclick={reset}
				>
					最初に戻る
				</button>
			</div>
		{/if}
	</div>
</section>

<!-- Webhook 設定モーダル -->
{#if showWebhookModal}
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<div
		class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
		transition:fade={{ duration: 150 }}
		onkeydown={(e) => {
			if (e.key === 'Escape') showWebhookModal = false;
		}}
		onclick={(e) => {
			if (e.target === e.currentTarget) showWebhookModal = false;
		}}
	>
		<div
			class="mx-4 w-full max-w-md rounded-2xl bg-card p-6 shadow-2xl"
			in:fly={{ y: 20, duration: 200 }}
		>
			<h3 class="mb-1 text-lg font-bold text-foreground">🔔 Discord 通知設定</h3>
			<p class="mb-4 text-xs text-muted-foreground">
				絵日記の生成完了時に Discord チャンネルへ通知を送信します。
			</p>

			<label for="webhook-url-input" class="mb-1 block text-sm font-medium text-foreground">
				Webhook URL
			</label>
			<input
				id="webhook-url-input"
				type="url"
				bind:value={webhookUrlInput}
				placeholder="https://discord.com/api/webhooks/..."
				class="w-full rounded-lg border border-border bg-input px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:ring-2 focus:ring-ring focus:outline-none"
			/>
			<p class="mt-1 mb-4 text-[11px] text-muted-foreground">
				Discordのチャンネル設定 → 連携サービス → ウェブフック から取得できます
			</p>

			<div class="flex items-center justify-between gap-2">
				<div>
					{#if savedWebhookUrl}
						<button
							class="rounded-lg px-3 py-2 text-sm text-destructive hover:bg-destructive/10"
							onclick={removeWebhookUrl}
						>
							削除する
						</button>
					{/if}
				</div>
				<div class="flex gap-2">
					<button
						class="rounded-lg px-4 py-2 text-sm text-muted-foreground hover:bg-muted"
						onclick={() => (showWebhookModal = false)}
					>
						キャンセル
					</button>
					<button
						class="rounded-lg bg-primary px-4 py-2 text-sm font-bold text-primary-foreground hover:opacity-90"
						onclick={saveWebhookUrl}
					>
						保存
					</button>
				</div>
			</div>
		</div>
	</div>
{/if}
