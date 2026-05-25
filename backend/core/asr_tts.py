"""语音识别 + 语音合成（稳定版）"""
from funasr import AutoModel
import subprocess, os

class ASRService:
    def __init__(self):
        print("⏳ 加载 ASR...")
        self.model = AutoModel(
            model="iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch",
            device="cpu", disable_update=True
        )
        print("✅ ASR 就绪")
    
    def transcribe(self, audio_path):
        try:
            result = self.model.generate(input=audio_path)
            return result[0].get('text', '') if result else ""
        except:
            return ""

class TTSService:
    def set_voice(self, voice_id: str):
        """动态设置音色"""
        from core.config import validate_voice
        self.current_voice = validate_voice(voice_id)
        self.voice = self.current_voice  # 更新实际使用的音色

    def __init__(self):
        self.voice = "zh-CN-XiaoxiaoNeural"  # 默认音色
        self.current_voice = "zh-CN-XiaoxiaoNeural"  # 当前使用的音色
        print("✅ Edge TTS 就绪 (Xiaoxiao)")
    
    def synthesize(self, text, output_path="output.wav"):
        # 确保输出路径是绝对路径，避免相对路径问题
        if not os.path.isabs(output_path):
            output_path = os.path.join(os.getcwd(), output_path)
        # 确保目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        try:
            subprocess.run([
                'edge-tts',
                '--voice', self.voice,
                '--text', text,
                '--write-media', output_path
            ], check=True, capture_output=True)
        except Exception as e:
            print(f"⚠️ Edge TTS 失败: {e}")
            # 降级：生成静默 WAV 文件，避免 404
            import wave, struct
            with wave.open(output_path, 'w') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(16000)
                wf.writeframes(struct.pack('<h', 0) * 16000)
        
        return output_path
