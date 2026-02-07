<script lang="ts">
	import '../app.css';
	import { onMount } from 'svelte';
	import type { Snippet } from 'svelte';

	let { children }: { children: Snippet } = $props();
	let isScrolled = $state(false);

	onMount(() => {
		const handleScroll = () => {
			isScrolled = window.scrollY > 50;
		};
		window.addEventListener('scroll', handleScroll);
		return () => window.removeEventListener('scroll', handleScroll);
	});
</script>

<div class="flex min-h-screen flex-col bg-background font-sans text-foreground">
	<header
		class="fixed top-0 right-0 left-0 z-50 transition-all duration-300 {isScrolled
			? 'bg-card/95 shadow-md backdrop-blur-sm'
			: 'bg-transparent'}"
	>
		<nav class="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
			<a
				href="/"
				class="text-xl font-bold transition-colors {isScrolled ? 'text-primary' : 'text-card'}"
			>
				<span class="text-accent">絵</span>日記
			</a>
		</nav>
	</header>

	<main class="flex flex-1 flex-col">
		{@render children()}
	</main>

	<footer class="bg-card/80 p-8 text-center text-xs text-muted-foreground backdrop-blur-sm">
		<p>&copy; 2025 絵日記プロジェクト</p>
	</footer>
</div>
