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
		const { region, accessToken } = this.config;

		// Vertex AI WebSocket URL with access token as query parameter
		// Browser WebSocket API cannot set Authorization headers
		// Documentation: https://cloud.google.com/vertex-ai/generative-ai/docs/live-api/get-started-websocket?hl=ja
		const url = `wss://${region}-aiplatform.googleapis.com/ws/google.cloud.aiplatform.v1.LlmBidiService/BidiGenerateContent?access_token=${encodeURIComponent(accessToken)}`;

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
				model: `projects/${projectId}/locations/${region}/publishers/google/models/gemini-live-2.5-flash-preview-native-audio-09-2025`,
				generation_config: {
					response_modalities: ['AUDIO'],
					speech_config: {
						voice_config: {
							prebuilt_voice_config: {
								voice_name: 'Aoede'
							}
						}
					}
				},
				system_instruction: {
					parts: [
						{
							text: `あなたはユーザーの「今日一日の出来事」を聞き出す、優しくて親しみやすいインタビュアーです。
目的は、後でこの会話を元に「ぼくの夏休み」風の絵日記を作ることです。
ただし、実際のユーザーは大人です。大人がクスッと笑えるような絵日記を作りたいので、ジョークのネタになる情報も聞き出してください。

## 聞き出したい情報
- いつ、どこで、誰と、何をした、どう思った（基本情報）
- ジョークのネタになりそうな情報（例: 「何時に起きた？」「何歩歩いた？」「何個食べた？」「明日仕事？」など）

## ルール
1. 一度にたくさんの質問をせず、ひとつずつ聞いてください。
2. ユーザーが答えたら、ポジティブに反応してください（「それは楽しそうだね！」「すごいね！」など）。
3. 大人向けジョークのネタになりそうなことをさりげなく聞いてください:
   - 「ちなみに今日は何時に起きたの？」
   - 「いっぱい食べた？カロリーは気にしない派？」
   - 「明日も休み？それとも仕事？」
   - 「何歩くらい歩いた？」
4. 話が一段落したら、「report_diary_event」ツールを呼び出して終了してください。
5. 常に日本語で話してください。`
						}
					]
				},
				tools: [
					{
						function_declarations: [
							{
								name: 'report_diary_event',
								description: '絵日記に必要な情報が集まったら呼び出す。会話を終了する。',
								parameters: {
									type: 'OBJECT',
									properties: {
										date: { type: 'STRING', description: '出来事の日付 (例: 2024-01-01)' },
										location: { type: 'STRING', description: '場所' },
										activity: { type: 'STRING', description: '何をしたか' },
										feeling: { type: 'STRING', description: '感想' },
										summary: { type: 'STRING', description: '会話の要約（絵日記の本文用）' },
										joke_hint: {
											type: 'STRING',
											description:
												'大人向けジョークのヒント（起床時間、歩数、食べた量、カロリー、明日の予定など）'
										}
									},
									required: ['activity', 'feeling', 'summary']
								}
							}
						]
					}
				]
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
		if (data.toolCall) {
			console.log('Tool Call received:', data.toolCall);
			this.dispatchEvent(
				new CustomEvent('toolCall', {
					detail: data.toolCall
				})
			);
		}

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
