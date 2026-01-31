/**
 * LiveClient: Vertex AI Multimodal Live API への WebSocket 接続を管理
 * ブラウザ標準の EventTarget を継承
 */

type LiveClientConfig = {
	projectId: string;
	region: string;
	accessToken: string;
};

export class LiveClient extends EventTarget {
	private ws: WebSocket | null = null;
	private config: LiveClientConfig;

	constructor(config: LiveClientConfig) {
		super();
		this.config = config;
	}

	connect() {
		const { projectId, region, accessToken } = this.config;

		// Vertex AI WebSocket URL with access token as query parameter
		// Browser WebSocket API cannot set Authorization headers
		const url = `wss://${region}-aiplatform.googleapis.com/ws/google.cloud.aiplatform.v1beta1.LlmBidiService/BidiGenerateContent?access_token=${encodeURIComponent(accessToken)}`;

		this.ws = new WebSocket(url);

		this.ws.onopen = () => {
			console.log('WebSocket connected');
			this.sendSetupMessage();
			this.dispatchEvent(new Event('open'));
		};

		this.ws.onmessage = async (event) => {
			await this.handleMessage(event);
		};

		this.ws.onerror = (error) => {
			console.error('WebSocket Error:', error);
			this.dispatchEvent(new CustomEvent('error', { detail: error }));
		};

		this.ws.onclose = (event) => {
			console.log('WebSocket Closed:', event.code, event.reason);
			this.dispatchEvent(new Event('close'));
		};
	}

	private sendSetupMessage() {
		const { projectId, region } = this.config;

		const setupMessage = {
			setup: {
				model: `projects/${projectId}/locations/${region}/publishers/google/models/gemini-2.0-flash-exp`,
				generation_config: {
					response_modalities: ['AUDIO']
				}
			}
		};

		this.sendJSON(setupMessage);
	}

	sendAudio(base64Data: string) {
		const message = {
			realtime_input: {
				media_chunks: [
					{
						mime_type: 'audio/pcm;rate=16000',
						data: base64Data
					}
				]
			}
		};
		this.sendJSON(message);
	}

	private sendJSON(data: object) {
		if (this.ws && this.ws.readyState === WebSocket.OPEN) {
			this.ws.send(JSON.stringify(data));
		}
	}

	private async handleMessage(event: MessageEvent) {
		let data;
		try {
			if (event.data instanceof Blob) {
				const text = await event.data.text();
				data = JSON.parse(text);
			} else {
				data = JSON.parse(event.data);
			}
		} catch (e) {
			console.error('Failed to parse message', e);
			return;
		}

		// Handle server content
		if (data.serverContent) {
			if (data.serverContent.modelTurn?.parts) {
				for (const part of data.serverContent.modelTurn.parts) {
					if (part.inlineData?.mimeType?.startsWith('audio/')) {
						this.dispatchEvent(
							new CustomEvent('audio', {
								detail: part.inlineData.data
							})
						);
					}
				}
			}

			if (data.serverContent.turnComplete) {
				this.dispatchEvent(new Event('turnComplete'));
			}
		}

		// Handle setup complete
		if (data.setupComplete) {
			console.log('Setup complete');
			this.dispatchEvent(new Event('setupComplete'));
		}
	}

	disconnect() {
		if (this.ws) {
			this.ws.close();
			this.ws = null;
		}
	}
}
