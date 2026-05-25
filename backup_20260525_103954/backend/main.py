
import re

def clean_text_for_tts(text):
    """移除文本中的emoji和特殊图标，防止TTS读出乱码"""
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642"
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"
        u"\u3030"
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text).strip()

from datetime import date, timedelta
import io, csv
import os, sys, uuid, subprocess, re, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, UploadFile, File, Form
from api.monitoring import router as monitoring_router
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import Response, HTMLResponse, StreamingResponse
from pydantic import BaseModel

from core.rag_engine import RAGEngine
from core.asr_tts import ASRService, TTSService
from core.logger import InteractionLogger
from core.config import get_model_list, get_voice_list, validate_model, validate_voice
from core.cache import cache_response, cache_manager

app = FastAPI()
# 添加Gzip压缩中间件
app.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=4)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

rag = RAGEngine()
asr = ASRService()
tts = TTSService()
logger = InteractionLogger()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def remove_emoji(text):
    emoji_pattern = re.compile(
        "[\\U0001F600-\\U0001F64F]"
        "[\\U0001F300-\\U0001F5FF]"
        "[\\U0001F680-\\U0001F6FF]"
        "[\\U0001F1E0-\\U0001F1FF]"
        "[\\U00002702-\\U000027B0]"
        "[\\U000024C2-\\U0001F251]"
        "[\\U0001F900-\\U0001F9FF]"
        "[\\U0001FA00-\\U0001FA6F]"
        "[\\U0001FA70-\\U0001FAFF]"
        "[\\U00002600-\\U000026FF]"
        "[\\U0000FE00-\\U0000FE0F]"
        "+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

# 预设回答（无需调用大模型）
PRESET_REPLIES = {
    '你是谁': '我是小灵，灵山胜境的AI数字导游。我可以为您讲解灵山大佛、梵宫等景点，推荐游览路线，解答各类景区问题。随时问我吧！',
    '介绍自己': '我叫小灵，是灵山胜境景区的专属AI导游。我熟悉这里的每一个景点和每一段故事，希望能带您领略千年佛国的魅力。',
    '你好': '您好！我是小灵，灵山胜境的AI导游。有什么可以帮您的吗？',
    '嗨': '嗨！我是小灵，很高兴为您服务。关于灵山胜境的任何问题，尽管问我哦。',
}

def get_preset_reply(text):
    for key, reply in PRESET_REPLIES.items():
        if key in text:
            return reply
    return None

class FeedbackRequest(BaseModel):
    rating: str

class ChatRequest(BaseModel):
    text: str
    voice: str = None

@app.get("/", response_class=HTMLResponse)
async def index():
    with open(os.path.join(BASE_DIR, 'static', 'index.html'), 'r', encoding='utf-8') as f:
        return f.read()

@app.post("/api/chat/tts")
async def text_to_speech(req: ChatRequest):
    start = time.time()
    preset = get_preset_reply(req.text)
    if preset:
        reply_audio = f"../data/processed/reply_{uuid.uuid4().hex[:8]}.wav"
        tts.synthesize(preset, reply_audio)
        return {"question": req.text, "answer": preset, "audio_url": f"/api/audio/{os.path.basename(reply_audio)}"}
    result = rag.answer(req.text)
    clean_answer = remove_emoji(result['answer'])
    reply_audio = f"../data/processed/reply_{uuid.uuid4().hex[:8]}.wav"
    tts.synthesize(clean_answer, reply_audio, voice=req.voice)
    duration = time.time() - start
    logger.add(req.text, clean_answer, duration=duration, source="tts")
    return {
        "question": result['question'],
        "answer": clean_answer,
        "audio_url": f"/api/audio/{os.path.basename(reply_audio)}"
    }

@app.post("/api/chat/text")
async def text_chat(req: ChatRequest):
    start = time.time()
    preset = get_preset_reply(req.text)
    if preset:
        return {"question": req.text, "answer": preset, "sources": []}
    result = rag.answer(req.text)
    clean_answer = remove_emoji(result['answer'])
    duration = time.time() - start
    logger.add(req.text, clean_answer, duration=duration, source="text")
    return {
        "question": result['question'],
        "answer": clean_answer,
        "sources": result['sources']
    }

@app.post("/api/chat/voice")
async def voice_chat(file: UploadFile = File(...)):
    start = time.time()
    raw = f"../data/processed/{uuid.uuid4().hex[:8]}.webm"
    wav = raw.replace('.webm', '.wav')
    with open(raw, "wb") as f: f.write(await file.read())
    subprocess.run(['ffmpeg', '-y', '-i', raw, '-ar', '16000', '-ac', '1', wav], capture_output=True)
    user_text = asr.transcribe(wav) or "未识别"
    preset = get_preset_reply(user_text)
    if preset:
        reply_audio = f"../data/processed/reply_{uuid.uuid4().hex[:8]}.wav"
        tts.synthesize(preset, reply_audio)
        return {"user_text": user_text, "reply_text": preset, "audio_url": f"/api/audio/{os.path.basename(reply_audio)}"}
    result = rag.answer(user_text)
    clean_answer = remove_emoji(result['answer'])
    reply_audio = f"../data/processed/reply_{uuid.uuid4().hex[:8]}.wav"
    tts.synthesize(clean_answer, reply_audio, voice=None)
    duration = time.time() - start
    logger.add(user_text, clean_answer, duration=duration, source="voice")
    return {
        "user_text": user_text,
        "reply_text": clean_answer,
        "audio_url": f"/api/audio/{os.path.basename(reply_audio)}"
    }

@app.get("/api/audio/{filename}")
async def get_audio(filename: str):
    path = f"../data/processed/{filename}"
    if not os.path.exists(path): return Response(status_code=404)
    with open(path, 'rb') as f: content = f.read()
    return Response(content=content, media_type="audio/wav")


@app.post("/api/chat/image")
async def image_chat(text: str = Form(""), file: UploadFile = File(...)):
    """支持图片提问：用户上传照片并提问，调用 DashScope 多模态大模型"""
    # 保存上传的图片
    img_bytes = await file.read()
    img_path = f"../data/processed/img_{uuid.uuid4().hex[:8]}.jpg"
    with open(img_path, "wb") as f:
        f.write(img_bytes)
    
    # 调用 DashScope 多模态 API（qwen-vl-plus 支持图片理解）
    try:
        import dashscope
        from dashscope import MultiModalConversation
        
        messages = [{
            "role": "system",
            "content": [{"text": "你是灵山胜境景区的AI导游小灵，请根据图片和问题，结合景区知识回答。"}]
        }, {
            "role": "user",
            "content": [
                {"image": f"file://{os.path.abspath(img_path)}"},
                {"text": text or "请描述这张图片"}
            ]
        }]
        
        response = MultiModalConversation.call(
            model="qwen-vl-plus",
            messages=messages,
            api_key=os.getenv("DASHSCOPE_API_KEY")
        )
        
        if response.status_code == 200:
            answer = response.output.choices[0].message.content[0]["text"]
        else:
            answer = "抱歉，小灵无法理解这张图片"
    except Exception as e:
        print(f"多模态API调用失败: {e}")
        answer = rag.answer(text)['answer'] if text else "请提供问题描述"
    
    # 合成语音
    clean_answer = remove_emoji(answer)
    tts_audio = f"../data/processed/reply_{uuid.uuid4().hex[:8]}.wav"
    tts.synthesize(clean_answer, tts_audio)
    logger.add(text or "图片提问", clean_answer, source="image")
    
    return {
        "answer": clean_answer,
        "audio_url": f"/api/audio/{os.path.basename(tts_audio)}"
    }


@app.post("/api/chat/clear")
async def clear():
    return rag.clear_history()

@app.get("/api/admin/dashboard")
async def dashboard():
    return logger.get_stats()

@app.get("/api/admin/recent")
async def recent(limit: int = 20):
    return logger.get_recent(limit)

@app.get("/admin", response_class=HTMLResponse)
async def admin():
    with open(os.path.join(BASE_DIR, 'static', 'admin.html'), 'r', encoding='utf-8') as f:
        return f.read()

@app.get("/settings.html", response_class=HTMLResponse)
async def settings():
    with open(os.path.join(BASE_DIR, 'static', 'settings.html'), 'r', encoding='utf-8') as f:
        return f.read()

@app.get("/avatar-manage.html", response_class=HTMLResponse)
async def avatar_manage():
    with open(os.path.join(BASE_DIR, 'static', 'avatar-manage.html'), 'r', encoding='utf-8') as f:
        return f.read()


from pydantic import BaseModel

class FeedbackRequest(BaseModel):
    rating: str  # good, neutral, bad

@app.post("/api/feedback")
async def feedback(req: FeedbackRequest):
    if req.rating not in ("good", "neutral", "bad"):
        return {"status": "error", "message": "无效的评分"}
    logger.add_feedback(req.rating)
    return {"status": "ok"}



# ========== 数字人形象管理 ==========
from fastapi import UploadFile
import shutil

AVATAR_DIR = os.path.join(BASE_DIR, "static", "avatars")
os.makedirs(AVATAR_DIR, exist_ok=True)

@app.post("/api/admin/upload-avatar")
async def upload_avatar(file: UploadFile = File(...)):
    if file.content_type not in ("image/png", "image/jpeg", "image/gif"):
        return {"error": "仅支持 PNG/JPG/GIF 图片"}
    filename = f"{uuid.uuid4().hex}_{file.filename}"
    filepath = os.path.join(AVATAR_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(await file.read())
    return {"url": f"/static/avatars/{filename}", "name": file.filename}

@app.get("/api/admin/avatars")
async def list_avatars():
    avatars = [{"id": "default", "name": "默认导游", "type": "svg", "url": ""}]
    if os.path.exists(AVATAR_DIR):
        for fname in sorted(os.listdir(AVATAR_DIR)):
            if fname.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                avatars.append({
                    "id": fname,
                    "name": fname.split("_", 1)[-1],
                    "type": "image",
                    "url": f"/static/avatars/{fname}"
                })
    return avatars

@app.delete("/api/admin/avatars/{filename}")
async def delete_avatar(filename: str):
    filepath = os.path.join(AVATAR_DIR, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        return {"status": "ok"}
    return {"error": "文件不存在"}



@app.get("/api/admin/export")
async def export_data(format: str = "json"):
    logs = logger._read(logger.log_path)
    if format == "csv":
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["timestamp","date","question","answer","duration","source"])
        writer.writeheader()
        writer.writerows(logs)
        return StreamingResponse(iter([output.getvalue()]), media_type="text/csv",
                                 headers={"Content-Disposition": "attachment; filename=interaction_log.csv"})
    else:
        return logs

@app.get("/api/admin/feedbacks")
async def get_feedbacks():
    return logger._read(logger.feedback_path)

@app.get("/api/admin/stats/daily")
async def daily_stats():
    logs = logger._read(logger.log_path)
    daily = {}
    for l in logs:
        day = l["date"]
        daily[day] = daily.get(day, 0) + 1
    today = date.today()
    result = []
    for i in range(6, -1, -1):
        d = str(today - timedelta(days=i))
        result.append({"date": d, "count": daily.get(d, 0)})
    return result

@app.get("/api/admin/documents")
async def list_documents():
    doc_dir = os.path.join(BASE_DIR, "..", "data", "raw")
    files = os.listdir(doc_dir) if os.path.exists(doc_dir) else []
    return [{"name": f} for f in files if not f.startswith('.')]

@app.post("/api/admin/upload-document")
async def upload_document(file: UploadFile = File(...)):
    save_dir = os.path.join(BASE_DIR, "..", "data", "raw")
    os.makedirs(save_dir, exist_ok=True)
    filepath = os.path.join(save_dir, file.filename)
    with open(filepath, "wb") as f:
        f.write(await file.read())
    # 重建向量库（可选，这里不自动重建，由用户手动触发）
    return {"status": "ok", "filename": file.filename}



@app.post("/api/admin/rebuild-index")
async def rebuild_index():
    try:
        rag.kb.build_vector_store()
        return {"status": "ok", "message": "向量库已重建"}
    except Exception as e:
        return {"status": "error", "message": str(e)}



# ========== 数字人模型管理 ==========
import shutil
MODEL_DIR = os.path.join(BASE_DIR, "static", "models")
os.makedirs(MODEL_DIR, exist_ok=True)

@app.post("/api/admin/models/upload")
async def upload_model(file: UploadFile = File(...)):
    if file.content_type not in ("image/png", "image/jpeg", "image/gif"):
        return {"error": "仅支持 PNG/JPG/GIF 图片"}
    filename = f"{uuid.uuid4().hex}_{file.filename}"
    filepath = os.path.join(MODEL_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(await file.read())
    return {"url": f"/static/models/{filename}", "name": file.filename}

@app.get("/api/admin/models")
async def list_models():
    models = [{"id": "default", "name": "默认导游小灵", "type": "svg", "url": ""},
             {"id": "shizuku", "name": "雫·清风", "type": "live2d", "url": "/static/models/shizuku/shizuku.model.json"},
             {"id": "koharu", "name": "小春·春日问候", "type": "live2d", "url": "/static/models/koharu/koharu.model.json"},
             {"id": "hijiki", "name": "小黑·活力满满", "type": "live2d", "url": "/static/models/hijiki/hijiki.model.json"},
             {"id": "tororo", "name": "多罗罗·慵懒时光", "type": "live2d", "url": "/static/models/tororo/tororo.model.json"},
             {"id": "haruto", "name": "晴斗·阳光少年", "type": "live2d", "url": "/static/models/haruto/haruto.model.json"},
             {"id": "miku", "name": "初音·未来歌姬", "type": "live2d", "url": "/static/models/miku/miku.model.json"}]
    if os.path.exists(MODEL_DIR):
        for fname in sorted(os.listdir(MODEL_DIR)):
            if fname.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                models.append({
                    "id": fname,
                    "name": fname.split("_", 1)[-1],
                    "type": "image",
                    "url": f"/static/models/{fname}"
                })
    return models

@app.delete("/api/admin/models/{filename}")
async def delete_model(filename: str):
    filepath = os.path.join(MODEL_DIR, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        return {"status": "ok"}
    return {"error": "文件不存在"}




# ========== 模型与音色配置接口 ==========
@cache_response("model_list")
@app.get("/api/config/models")
async def list_models():
    """获取可用模型列表"""
    return {"models": get_model_list()}

@cache_response("voice_list")
@app.get("/api/config/voices")
async def list_voices():
    """获取可用音色列表"""
    return {"voices": get_voice_list()}

@app.post("/api/config/set-model")
async def set_model(model_id: str):
    """设置当前模型"""
    valid_model = validate_model(model_id)
    rag.set_model(valid_model)
    return {"status": "ok", "current_model": valid_model}

@app.post("/api/config/set-voice")
async def set_voice(voice_id: str):
    """设置当前音色"""
    valid_voice = validate_voice(voice_id)
    tts.set_voice(valid_voice)
    return {"status": "ok", "current_voice": valid_voice}

@cache_response("current_config")
@app.get("/api/config/current")
async def get_current_config():
    """获取当前配置"""
    return {
        "current_model": rag.current_model,
        "current_voice": tts.current_voice
    }
@app.get("/health")
async def health():
    return {"status": "ok", "uptime": time.time()}

if __name__ == "__main__":
    import uvicorn
    print("🚀 http://localhost:8000 | 管理: http://localhost:8000/admin")
    uvicorn.run(app, host="0.0.0.0", port=8000)
