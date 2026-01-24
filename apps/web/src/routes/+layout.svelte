<script lang="ts">
  import '../app.css';
</script>

<div class="flex min-h-screen flex-col bg-gray-50 text-gray-800 font-body">
  <header class="flex justify-center p-6">
    <h1 class="bg-linear-to-br from-blue-500 to-red-500 bg-clip-text text-2xl font-extrabold tracking-tight text-transparent">
      Enikki
    </h1>
  </header>

  <main class="flex flex-1 flex-col items-center px-8 py-8">
    <slot />
  </main>

  <footer class="p-8 text-center text-xs text-gray-400">
    <p>&copy; 2025 Enikki Project</p>
  </footer>
</div>
