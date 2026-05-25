from fastapi import APIRouter, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from core.rag_engine import RAGEngine
import json

router = APIRouter()
rag = RAGEngine()

class ChatRequest(BaseModel):
    query: str
    history: list = []

@router.post("/chat")
async def chat(request: ChatRequest):
    """普通文字对话接口"""
    response = rag.chat(request.query, request.history)
    return {"response": response}

@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """流式文字对话接口 (SSE格式 - 前端打字机效果)"""
    def event_generator():
        for chunk in rag.chat_stream(request.query, request.history):
            yield f"data: {json.dumps({'chunk': chunk})}\n\n"
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.post("/voice_chat")
async def voice_chat(audio_file: UploadFile):
    """语音对话接口"""
    # 1. ASR 语音转文字
    # text = asr.transcribe(audio_file)
    text = "模拟语音转文字结果"
    # 2. RAG 生成回答
    response = rag.chat(text)
    # 3. TTS 文字转语音
    # audio_url = tts.synthesize(response)
    audio_url = "http://example.com/audio.mp3"
    return {"text": response, "audio_url": audio_url}
