"""模型与声音动态配置"""
from dataclasses import dataclass
from typing import List

@dataclass
class VoiceOption:
    id: str
    name: str
    gender: str
    style: str

@dataclass  
class ModelOption:
    id: str
    name: str
    desc: str
    speed: str
    context_length: str
    input_price: str
    output_price: str

# 支持的模型列表（基于搜索结果<span data-allow-html class='source-item source-aggregated' data-group-key='source-group-0' data-url='https://www.aliyunbaike.com/tag/%e9%98%bf%e9%87%8c%e4%ba%91%e9%80%9a%e4%b9%89%e5%8d%83%e9%97%ae/feed/' data-id='turn0search0'><span data-allow-html class='source-item-num' data-group-key='source-group-0' data-id='turn0search0' data-url='https://www.aliyunbaike.com/tag/%e9%98%bf%e9%87%8c%e4%ba%91%e9%80%9a%e4%b9%89%e5%8d%83%e9%97%ae/feed/'><span class='source-item-num-name' data-allow-html>aliyunbaike.com</span><span data-allow-html class='source-item-num-count'>+2</span></span></span>）
MODELS: List[ModelOption] = [
    ModelOption("qwen-turbo", "通义千问-Turbo", "极速响应，适合简单问答", "快", "1M tokens", "0.3元/百万", "0.6元/百万"),
    ModelOption("qwen-plus", "通义千问-Plus", "均衡之选，推荐使用", "中", "1M tokens", "0.8元/百万", "2元/百万"),
    ModelOption("qwen-max", "通义千问-Max", "最强推理，复杂问题首选", "慢", "32K tokens", "2.4元/百万", "9.6元/百万"),
]

# 支持的音色列表（基于搜索结果<span data-allow-html class='source-item source-aggregated' data-group-key='source-group-1' data-url='https://zhuanlan.zhihu.com/p/619612276' data-id='turn0search1'><span data-allow-html class='source-item-num' data-group-key='source-group-1' data-id='turn0search1' data-url='https://zhuanlan.zhihu.com/p/619612276'><span class='source-item-num-name' data-allow-html>zhihu.com</span><span data-allow-html class='source-item-num-count'>+1</span></span></span>）
VOICES: List[VoiceOption] = [
    VoiceOption("zh-CN-XiaoxiaoNeural", "晓晓", "female", "温柔亲切"),
    VoiceOption("zh-CN-XiaoyiNeural", "晓伊", "female", "活泼可爱"),
    VoiceOption("zh-CN-YunjianNeural", "云健", "male", "磁性沉稳"),
    VoiceOption("zh-CN-YunxiNeural", "云希", "male", "阳光清新"),
    VoiceOption("zh-CN-YunxiaNeural", "云夏", "male", "少年清朗"),
    VoiceOption("zh-CN-XiaochenNeural", "晓辰", "female", "知性大方"),
    VoiceOption("zh-CN-XiaohanNeural", "晓涵", "female", "温暖治愈"),
    VoiceOption("zh-CN-XiaomengNeural", "晓梦", "female", "甜美灵动"),
    VoiceOption("zh-CN-XiaomoNeural", "晓墨", "female", "优雅文艺"),
    VoiceOption("zh-CN-XiaoruiNeural", "晓瑞", "female", "沉稳干练"),
    VoiceOption("zh-CN-XiaoshuangNeural", "晓双", "female", "童声天真"),
    VoiceOption("zh-CN-XiaoxuanNeural", "晓萱", "female", "柔美细腻"),
    VoiceOption("zh-CN-XiaozhenNeural", "晓甄", "female", "自然舒适"),
]

def get_model_list():
    return [
        {
            "id": m.id, 
            "name": m.name, 
            "desc": m.desc, 
            "speed": m.speed,
            "context_length": m.context_length,
            "input_price": m.input_price,
            "output_price": m.output_price
        } for m in MODELS
    ]

def get_voice_list():
    return [
        {
            "id": v.id, 
            "name": v.name, 
            "gender": v.gender, 
            "style": v.style
        } for v in VOICES
    ]

def validate_model(model_id: str) -> str:
    """验证模型ID，无效则返回默认"""
    valid_ids = [m.id for m in MODELS]
    return model_id if model_id in valid_ids else "qwen-plus"

def validate_voice(voice_id: str) -> str:
    """验证音色ID，无效则返回默认"""
    valid_ids = [v.id for v in VOICES]
    return voice_id if voice_id in valid_ids else "zh-CN-XiaoxiaoNeural"
