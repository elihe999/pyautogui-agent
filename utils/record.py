import pyaudio
import webrtcvad
import wave
import time
import logging
from plyer import notification

# notification.notify(
#     title="test",					#标题
#     message="aaaa",			#内容
#     app_icon="None",		#图标
#     timeout=1,					#通知持续时间
# )

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def record_until_silence(
    output_filename="output.wav",
    silence_threshold=0.5,  # 静音持续时间（秒）
    chunk_duration_ms=30,  # 每块音频时长（必须是10/20/30ms）
    sample_rate=16000,
    channels=1,
    format=pyaudio.paInt16,
):

    vad = webrtcvad.Vad(3)  # 敏感度：0~3，3最敏感（更容易判为语音）
    p = pyaudio.PyAudio()

    stream = p.open(
        format=format,
        channels=channels,
        rate=sample_rate,
        input=True,
        frames_per_buffer=int(sample_rate * chunk_duration_ms / 1000),
    )

    logging.info("🎤 开始录音，请说话...")

    frames = []
    silent_chunks = 0
    speech_chunks = 0
    max_silent_chunks = int(silence_threshold / (chunk_duration_ms / 1000))
    min_speech_chunks = int(0.3 / (chunk_duration_ms / 1000))  # 至少说0.3秒才算有效

    while True:
        data = stream.read(int(sample_rate * chunk_duration_ms / 1000))
        frames.append(data)

        # 判断当前块是否为语音
        is_speech = vad.is_speech(data, sample_rate)

        if is_speech:
            silent_chunks = 0
            speech_chunks += 1
        else:
            silent_chunks += 1

        # 如果已经说过话，且连续静音超过阈值，就停止
        if speech_chunks > min_speech_chunks and silent_chunks > max_silent_chunks:
            logging.info("🔇 检测到静音，停止录音")
            break

    # 停止并保存
    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(output_filename, "wb")
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(format))
    wf.setframerate(sample_rate)
    wf.writeframes(b"".join(frames))
    wf.close()

    logging.info(f"✅ 录音已保存为 {output_filename}")
    notification.notify(
        title="录音完成",
        message=f"录音已保存为 {output_filename}",
        timeout=1,
    )


if __name__ == "__main__":
    # 使用
    record_until_silence("my_speech.wav")
