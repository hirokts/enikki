/**
 * AudioRecorder: マイク入力を PCM 16kHz Base64 で出力
 */
export class AudioRecorder extends EventTarget {
	private stream: MediaStream | null = null;
	private audioContext: AudioContext | null = null;
	private source: MediaStreamAudioSourceNode | null = null;
	private workletNode: AudioWorkletNode | null = null;

	async start() {
		this.stream = await navigator.mediaDevices.getUserMedia({ audio: true });
		this.audioContext = new AudioContext({ sampleRate: 16000 });

		try {
			// AudioWorklet モジュールの読み込み
			// static/audio-processor.js に配置されたファイルを読み込む
			await this.audioContext.audioWorklet.addModule('/audio-processor.js');

			this.source = this.audioContext.createMediaStreamSource(this.stream);
			this.workletNode = new AudioWorkletNode(this.audioContext, 'audio-processor');

			this.workletNode.port.onmessage = (event) => {
				// AudioProcessor から受信したデータ（PCM16 ArrayBuffer）を Base64 に変換
				const base64 = arrayBufferToBase64(event.data);
				this.dispatchEvent(new CustomEvent('data', { detail: base64 }));
			};

			this.source.connect(this.workletNode);
			this.workletNode.connect(this.audioContext.destination);
		} catch (error) {
			console.error('Errors loading audio processor:', error);
			throw error;
		}
	}

	stop() {
		this.workletNode?.disconnect();
		this.source?.disconnect();
		this.audioContext?.close();
		this.stream?.getTracks().forEach((track) => track.stop());
		this.stream = null;
		this.audioContext = null;
		this.source = null;
		this.workletNode = null;
	}
}

/**
 * AudioPlayer: PCM 16bit 24kHz Base64 データを再生
 */
export class AudioPlayer {
	private audioContext: AudioContext;
	private nextStartTime: number = 0;

	constructor(sampleRate: number = 24000) {
		this.audioContext = new AudioContext({ sampleRate });
	}

	play(base64Data: string) {
		const pcmData = base64ToArrayBuffer(base64Data);
		const float32Data = pcm16ToFloat32(pcmData);

		const buffer = this.audioContext.createBuffer(
			1,
			float32Data.length,
			this.audioContext.sampleRate
		);
		buffer.getChannelData(0).set(float32Data);

		const source = this.audioContext.createBufferSource();
		source.buffer = buffer;
		source.connect(this.audioContext.destination);

		const currentTime = this.audioContext.currentTime;
		if (this.nextStartTime < currentTime) {
			this.nextStartTime = currentTime;
		}

		source.start(this.nextStartTime);
		this.nextStartTime += buffer.duration;
	}

	reset() {
		this.nextStartTime = 0;
	}
}

// --- Utilities ---

function pcm16ToFloat32(arrayBuffer: ArrayBuffer): Float32Array {
	const view = new DataView(arrayBuffer);
	const float32Arr = new Float32Array(arrayBuffer.byteLength / 2);
	for (let i = 0; i < float32Arr.length; i++) {
		const s = view.getInt16(i * 2, true);
		float32Arr[i] = s / 32768;
	}
	return float32Arr;
}

function arrayBufferToBase64(buffer: ArrayBuffer): string {
	let binary = '';
	const bytes = new Uint8Array(buffer);
	for (let i = 0; i < bytes.byteLength; i++) {
		binary += String.fromCharCode(bytes[i]);
	}
	return btoa(binary);
}

function base64ToArrayBuffer(base64: string): ArrayBuffer {
	const binary = atob(base64);
	const bytes = new Uint8Array(binary.length);
	for (let i = 0; i < binary.length; i++) {
		bytes[i] = binary.charCodeAt(i);
	}
	return bytes.buffer;
}
