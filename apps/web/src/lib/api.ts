const API_BASE_URL = 'http://localhost:8000';

/**
 * API Key を取得（localStorage から）
 */
function getApiKey(): string | null {
	if (typeof window === 'undefined') return null;
	return localStorage.getItem('apiKey');
}

/**
 * API リクエストを送信（X-API-Key ヘッダー付き）
 */
export async function fetchWithAuth(path: string, options: RequestInit = {}): Promise<Response> {
	const apiKey = getApiKey();

	const headers = new Headers(options.headers);
	if (apiKey) {
		headers.set('X-API-Key', apiKey);
	}

	return fetch(`${API_BASE_URL}${path}`, {
		...options,
		headers
	});
}

/**
 * Vertex AI トークンを取得
 */
export async function getVertexAIToken(): Promise<{
	accessToken: string;
	expiresIn: number;
	projectId: string;
	region: string;
}> {
	const response = await fetchWithAuth('/auth/token', { method: 'POST' });

	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.detail || 'Failed to get token');
	}

	return response.json();
}

/**
 * 日記作成 API を呼び出す
 */
export async function createDiary(log: {
	date: string;
	conversation_transcript: string; // 会話の全文（JSON形式）
	activity?: string;
	feeling?: string;
	location?: string;
}): Promise<{ id: string; status: string }> {
	const response = await fetchWithAuth('/diaries', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(log)
	});

	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.detail || 'Failed to create diary');
	}

	return response.json();
}

/**
 * Ephemeral Token を取得（Gemini Live API 用）
 */
export async function getEphemeralToken(): Promise<{
	token: string;
	expiresIn: number;
}> {
	const response = await fetchWithAuth('/auth/ephemeral-token', { method: 'POST' });

	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.detail || 'Failed to get ephemeral token');
	}

	return response.json();
}

/**
 * API Key の設定状況をチェックして console.log に出力
 * ページ読み込み時に自動実行される
 */
export async function checkApiKeyStatus(): Promise<boolean> {
	const apiKey = getApiKey();

	if (!apiKey) {
		console.log('🔑 API Key が設定されていません');
		console.log('💡 設定方法: localStorage.setItem("apiKey", "your-api-key")');
		return false;
	}

	try {
		const token = await getVertexAIToken();
		console.log('✅ API Key 認証成功!');
		console.log(`   Project: ${token.projectId}`);
		console.log(`   Region: ${token.region}`);
		return true;
	} catch (error) {
		console.log('❌ API Key 認証失敗:', error instanceof Error ? error.message : error);
		return false;
	}
}
