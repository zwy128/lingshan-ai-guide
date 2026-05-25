from fastapi import APIRouter, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from core.rag_engine import RAGEngine
from core.asr_tts import asr, tts
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
            yield f"data: {json.dumps({'chunk': chunk}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post("/voice_chat")
async def voice_chat(audio_file: UploadFile = File(...)):
    """语音对话接口"""
    # 1. ASR 语音转文字
    text = await asr.transcribe(audio_file)
    # 2. RAG 生成回答
    response = rag.chat(text)
    # 3. TTS 文字转语音
    audio_url = await tts.synthesize(response)
    return {"text": response, "audio_url": audio_url}
