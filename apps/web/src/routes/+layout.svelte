<script lang="ts">
  // import '../app.css';
  import './layout.css';
</script>

<div class="app-layout">
  <header>
    <h1>Enikki</h1>
  </header>

  <main>
    <slot />
  </main>

  <footer>
    <p>&copy; 2025 Enikki Project</p>
  </footer>
</div>

<style>
  :global(body) {
    margin: 0;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    background-color: #f8f9fa;
    color: #333;
  }

  .app-layout {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
  }

  header {
    padding: 1.5rem 2rem;
    display: flex;
    justify-content: center;
  }

  h1 {
    font-size: 1.5rem;
    font-weight: 800;
    margin: 0;
    background: linear-gradient(135deg, #4285f4, #ea4335);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.05em;
  }

  main {
    flex: 1;
    padding: 2rem;
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  footer {
    padding: 2rem;
    text-align: center;
    color: #888;
    font-size: 0.8rem;
  }
</style>
