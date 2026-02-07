class AudioProcessor extends AudioWorkletProcessor {
    process(inputs, outputs, parameters) {
        const input = inputs[0];
        if (input.length > 0) {
            const float32Arr = input[0];
            const pcm16 = this.float32ToPcm16(float32Arr);
            this.port.postMessage(pcm16);
        }
        return true;
    }

    float32ToPcm16(float32Arr) {
        const buffer = new Int16Array(float32Arr.length);
        for (let i = 0; i < float32Arr.length; i++) {
            let s = Math.max(-1, Math.min(1, float32Arr[i]));
            s = s < 0 ? s * 0x8000 : s * 0x7FFF;
            buffer[i] = s;
        }
        return buffer.buffer;
    }
}

registerProcessor('audio-processor', AudioProcessor);
