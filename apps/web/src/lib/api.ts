import { getFirebase } from './firebase';

// API URL (from environment variable or default to localhost)
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Firebase ID Token を取得
 */
async function getIdToken(): Promise<string | null> {
	if (typeof window === 'undefined') return null;
	const { auth } = getFirebase();
	const user = auth.currentUser;
	if (!user) return null;
	return user.getIdToken();
}

/**
 * API リクエストを送信（X-Firebase-Token ヘッダー付き）
 */
export async function fetchWithAuth(path: string, options: RequestInit = {}): Promise<Response> {
	const token = await getIdToken();

	const headers = new Headers(options.headers);
	if (token) {
		headers.set('X-Firebase-Token', token);
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
	activity: string;
	feeling: string;
	summary: string;
	location?: string;
	joke_hint?: string;
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
 * ログイン状態をチェックして console.log に出力
 */
export async function checkAuthStatus(): Promise<boolean> {
	const { auth } = getFirebase();

	return new Promise((resolve) => {
		const unsubscribe = auth.onAuthStateChanged(async (user) => {
			unsubscribe();
			if (user) {
				console.log('✅ ログイン済み:', user.email);
				try {
					const token = await getVertexAIToken();
					console.log('✅ Vertex AI トークン取得成功');
					console.log(`   Project: ${token.projectId}`);
					resolve(true);
				} catch (error) {
					console.log('❌ トークン取得失敗:', error instanceof Error ? error.message : error);
					resolve(false);
				}
			} else {
				console.log('🔑 ログインされていません');
				resolve(false);
			}
		});
	});
}
