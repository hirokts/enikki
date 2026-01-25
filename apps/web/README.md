# sv

Everything you need to build a Svelte project, powered by [`sv`](https://github.com/sveltejs/cli).

## Creating a project

If you're seeing this, you've probably already done this step. Congrats!

```sh
# create a new project
npx sv create my-app
```

To recreate this project with the same configuration:

```sh
# recreate this project
pnpm dlx sv create --template minimal --types ts --add prettier eslint vitest="usages:unit,component" playwright tailwindcss="plugins:typography,forms" sveltekit-adapter="adapter:static" devtools-json mcp="ide:claude-code,other+setup:local" --install pnpm web
```

## Developing

Once you've created a project and installed dependencies with `npm install` (or `pnpm install` or `yarn`), start a development server:

```sh
npm run dev

# or start the server and open the app in a new browser tab
npm run dev -- --open
```

## API Key Setup

An API Key is required to access the backend API (`/auth/token`).

Run the following in your browser's Developer Tools (Console):

```js
localStorage.setItem('apiKey', 'YOUR_API_KEY')
```

Reload the page, and the authentication status will be displayed in the console:
- ✅ Success: `API Key 認証成功!`
- ❌ Failure: `API Key 認証失敗: Invalid API Key`


## Building

To create a production version of your app:

```sh
npm run build
```

You can preview the production build with `npm run preview`.

> To deploy your app, you may need to install an [adapter](https://svelte.dev/docs/kit/adapters) for your target environment.
