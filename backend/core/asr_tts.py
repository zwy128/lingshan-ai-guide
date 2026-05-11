"""语音识别 + 语音合成"""
from funasr import AutoModel
import subprocess, os, asyncio

class ASRService:
    def __init__(self):
        print("⏳ 加载 ASR...")
        self.model = AutoModel(
            model="iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch",
            device="cuda:0", disable_update=True
        )
        print("✅ ASR 就绪")
    
    def transcribe(self, audio_path):
        result = self.model.generate(input=audio_path)
        if result and len(result) > 0:
            return result[0].get('text', '')
        return ""

class TTSService:
    def __init__(self):
        self.voice = "zh-CN-XiaoxiaoNeural"  # 温柔女声
        print("✅ Edge TTS 就绪 (Xiaoxiao)")
    
    def synthesize(self, text, output_path="output.wav"):
        # edge-tts 是异步的，用 subprocess 同步调用
        result = subprocess.run([
            'edge-tts',
            '--voice', self.voice,
            '--text', text,
            '--write-media', output_path
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"⚠️ Edge TTS 失败: {result.stderr[:200]}")
            # 降级到 espeak
            subprocess.run([
                'espeak', '-v', 'zh', '-s', '150',
                '-w', output_path, text
            ], capture_output=True)
        
        filesize = os.path.getsize(output_path) if os.path.exists(output_path) else 0
        print(f"✅ TTS: {filesize} bytes → {os.path.basename(output_path)}")
        return output_path
