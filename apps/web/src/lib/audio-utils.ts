/**
 * AudioRecorder: マイク入力を PCM 16kHz Base64 で出力
 */
export class AudioRecorder extends EventTarget {
	private stream: MediaStream | null = null;
	private audioContext: AudioContext | null = null;
	private source: MediaStreamAudioSourceNode | null = null;
	private processor: ScriptProcessorNode | null = null;

	async start() {
		this.stream = await navigator.mediaDevices.getUserMedia({ audio: true });
		this.audioContext = new AudioContext({ sampleRate: 16000 });
		this.source = this.audioContext.createMediaStreamSource(this.stream);

		this.processor = this.audioContext.createScriptProcessor(4096, 1, 1);

		this.processor.onaudioprocess = (e) => {
			const inputData = e.inputBuffer.getChannelData(0);
			const pcm16 = float32ToPcm16(inputData);
			const base64 = arrayBufferToBase64(pcm16);
			this.dispatchEvent(new CustomEvent('data', { detail: base64 }));
		};

		this.source.connect(this.processor);
		this.processor.connect(this.audioContext.destination);
	}

	stop() {
		this.processor?.disconnect();
		this.source?.disconnect();
		this.audioContext?.close();
		this.stream?.getTracks().forEach((track) => track.stop());
		this.stream = null;
		this.audioContext = null;
		this.source = null;
		this.processor = null;
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

function float32ToPcm16(float32Arr: Float32Array): ArrayBuffer {
	const buffer = new ArrayBuffer(float32Arr.length * 2);
	const view = new DataView(buffer);
	for (let i = 0; i < float32Arr.length; i++) {
		let s = Math.max(-1, Math.min(1, float32Arr[i]));
		s = s < 0 ? s * 0x8000 : s * 0x7fff;
		view.setInt16(i * 2, s, true);
	}
	return buffer;
}

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
