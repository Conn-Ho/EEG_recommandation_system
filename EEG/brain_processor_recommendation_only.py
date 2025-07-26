#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
EEG Brain Wave Data Processor Service - Recommendation Only Version
脑波数据处理服务 - 仅推荐版本

负责：
1. 连接Emotiv EEG设备获取脑波数据
2. 实时分析情绪状态
3. 仅向推荐服务发送情绪数据（不包含音频服务）
"""

import math
import logging
import requests
import time
from cortex import Cortex
from typing import Dict, Any, List
import json

# ========================================================================================
# 全局配置与日志 (Global Configuration & Logging)
# ========================================================================================

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- 凭证配置 ---
# Emotiv App Credentials
YOUR_APP_CLIENT_ID = '6OV53rWuPZiJo6419CHi4ppabSdqKpTgfYCU5mvV'
YOUR_APP_CLIENT_SECRET = 'XMWhqlpRTnQfe8a0b363jYFD976u7Ar17mQw2IWJT6eS2Z5LllaMckJbfbrSEqJYZ2LBpru6cvusWDapvjPSPutglsUwgNXYUzzcLKZqIhYOV52Rcy0YilZDJwoaQWnE'

# --- 服务配置 ---
RECOMMENDATION_SERVICE_URL = 'http://localhost:8081'
EMOTION_UPDATE_ENDPOINT = '/update_emotion'

# ========================================================================================
# 情绪识别模块 (Emotion Recognition Module)
# ========================================================================================

EMOTION_MAP = {
    "Happy": "Happy (开心)",
    "Excited": "Excited (激动)",
    "Surprised": "Surprised (惊喜)",
    "Fear": "Fear (恐惧)",
    "Angry": "Angry (愤怒)",
    "Contempt": "Contempt (轻蔑)",
    "Disgust": "Disgust (厌恶)",
    "Miserable": "Miserable (痛苦)",
    "Sad": "Sad (悲伤)",
    "Depressed": "Depressed (沮丧)",
    "Bored": "Bored (无聊)",
    "Tired": "Tired (疲倦)",
    "Sleepy": "Sleepy (困倦)",
    "Relaxed": "Relaxed (放松)",
    "Pleased": "Pleased (平静)",
    "Neutral": "Neutral (中性)" 
}

API_METRIC_ORDER = ['eng', 'exc', 'lex', 'str', 'rel', 'int']
METRIC_RANGES = {
    'eng': (0, 1), 'exc': (0, 1), 'lex': (0, 1), 'str': (0, 1),
    'rel': (0, 1), 'int': (0, 1)
}
WEIGHTS = {
    'arousal': {'exc': 0.4, 'str': 0.3, 'lex': 0.2, 'int': 0.15, 'eng': 0.1, 'rel': -0.4},
    'valence': {'rel': 0.35, 'int': 0.25, 'eng': 0.2, 'lex': 0.2, 'exc': 0.1, 'str': -0.5}
}

def normalize_to_neg_one_to_one(value, min_val, max_val):
    if max_val == min_val: 
        return 0
    return 2 * ((value - min_val) / (max_val - min_val)) - 1

def calculate_emotion_scores(metrics, weights):
    arousal = sum(weights['arousal'][key] * metrics[key] for key in API_METRIC_ORDER)
    valence = sum(weights['valence'][key] * metrics[key] for key in API_METRIC_ORDER)
    return max(-1, min(1, valence)), max(-1, min(1, arousal))

def get_precise_emotion(valence, arousal, neutral_threshold=0.1):
    intensity_raw = math.sqrt(valence**2 + arousal**2)
    
    # 原始强度归一化到0-100范围
    intensity_normalized = min(100, (intensity_raw / math.sqrt(2)) * 100)
    
    # 数学运算：归一化到0-1 -> 开平方 -> 乘10 -> 回到0-100范围
    intensity_0_to_1 = intensity_normalized / 100.0
    intensity_sqrt = math.sqrt(intensity_0_to_1)
    intensity_amplified = intensity_sqrt * 10
    intensity_final = min(100, intensity_amplified * 10)
    
    if intensity_raw < neutral_threshold:
        return "Neutral (中性)", intensity_final
        
    angle = math.degrees(math.atan2(arousal, valence))
    if angle < 0: 
        angle += 360
    
    emotion_label = "Neutral"

    if intensity_raw >= neutral_threshold:
        if 0 <= angle < 30: emotion_label = "Happy"
        elif 30 <= angle < 60: emotion_label = "Excited"
        elif 60 <= angle < 90: emotion_label = "Surprised"
        elif 90 <= angle < 112.5: emotion_label = "Fear"
        elif 112.5 <= angle < 135: emotion_label = "Angry"
        elif 135 <= angle < 157.5: emotion_label = "Contempt"
        elif 157.5 <= angle < 180: emotion_label = "Disgust"
        elif 180 <= angle < 198: emotion_label = "Miserable"
        elif 198 <= angle < 216: emotion_label = "Sad"
        elif 216 <= angle < 234: emotion_label = "Depressed"
        elif 234 <= angle < 252: emotion_label = "Bored"
        elif 252 <= angle < 270: emotion_label = "Tired"
        elif 270 <= angle < 300: emotion_label = "Sleepy"
        elif 300 <= angle < 330: emotion_label = "Relaxed"
        elif 330 <= angle < 360: emotion_label = "Pleased"
    
    return EMOTION_MAP.get(emotion_label, emotion_label), intensity_final

def analyze_emotion_from_sample(sample_list):
    raw_data = dict(zip(API_METRIC_ORDER, sample_list))
    normalized_metrics = {k: normalize_to_neg_one_to_one(v, *METRIC_RANGES[k]) for k, v in raw_data.items()}
    v, a = calculate_emotion_scores(normalized_metrics, WEIGHTS)
    emotion, intensity = get_precise_emotion(v, a)
    
    return emotion, intensity, v, a

# ========================================================================================
# 推荐服务通信模块 (Recommendation Service Communication Module)
# ========================================================================================

class RecommendationServiceClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.last_emotion_time = 0
        self.recommendation_service_available = False
        
    def check_service_health(self) -> bool:
        """检查推荐服务健康状态"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=2)
            self.recommendation_service_available = response.status_code == 200
            return self.recommendation_service_available
        except:
            self.recommendation_service_available = False
            return False
    
    def send_emotion_update(self, emotion: str, intensity: float, valence: float, arousal: float, user_id: str = "default_user") -> bool:
        """向推荐服务发送情绪更新"""
        current_time = time.time()
        
        emotion_data = {
            'emotion': emotion,
            'intensity': intensity,
            'valence': valence,
            'arousal': arousal,
            'timestamp': current_time,
            'user_id': user_id
        }
        
        # 检查服务状态
        if not self.check_service_health():
            logger.warning("🔌 推荐服务: 连接失败")
            return False
        
        try:
            response = self.session.post(
                f"{self.base_url}{EMOTION_UPDATE_ENDPOINT}",
                json=emotion_data,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    # 检查是否生成了新推荐
                    if result.get('recommendation_generated', False):
                        recommendations = result.get('recommendations', [])
                        logger.info(f"🎯 推荐服务: 生成了 {len(recommendations)} 个新推荐")
                        
                        # 显示推荐摘要
                        if recommendations:
                            for i, video in enumerate(recommendations[:3], 1):  # 显示前3个
                                logger.info(f"   {i}. {video['title']} (分数: {video['recommendation_score']:.2f})")
                    else:
                        logger.info("✅ 推荐服务: 情绪数据已更新，暂未生成新推荐")
                    
                    return True
                else:
                    logger.warning(f"❌ 推荐服务: {result.get('message', '未知错误')}")
            else:
                logger.warning(f"❌ 推荐服务: HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            logger.warning(f"⏰ 推荐服务: 请求超时")
        except requests.exceptions.ConnectionError:
            logger.warning(f"🔌 推荐服务: 连接失败")
        except Exception as e:
            logger.warning(f"❌ 推荐服务: {str(e)}")
        
        self.last_emotion_time = current_time
        return False

# ========================================================================================
# EEG数据处理器 (EEG Data Processor)
# ========================================================================================

class RecommendationOnlyEEGProcessor:
    def __init__(self, app_client_id: str, app_client_secret: str, rec_client: RecommendationServiceClient):
        logger.info("初始化EEG数据处理器（仅推荐模式）...")
        
        self.rec_client = rec_client
        self.streams = []
        self.is_connected = False
        self.last_emotion_data = {}
        self.output_interval = 5.0  # 5秒输出间隔
        self.last_output_time = 0
        
        # 初始化Cortex客户端
        self.cortex_client = Cortex(app_client_id, app_client_secret, debug_mode=False)
        self.cortex_client.bind(new_met_data=self.on_new_met_data)
        self.cortex_client.bind(inform_error=self.on_inform_error)
        self.cortex_client.bind(create_session_done=self.on_create_session_done)
        
        logger.info("EEG数据处理器初始化完成")
    
    def start(self, streams: List[str], headset_id: str = ''):
        """启动EEG数据采集"""
        self.streams = streams
        if headset_id:
            self.cortex_client.set_wanted_headset(headset_id)
        
        logger.info("启动Cortex连接...")
        self.cortex_client.open()
    
    def subscribe_streams(self, streams: List[str]):
        """订阅数据流"""
        logger.info(f"订阅数据流: {streams}")
        self.cortex_client.sub_request(streams)
    
    def on_new_met_data(self, *args, **kwargs):
        """处理新的EEG数据"""
        if not self.is_connected:
            return
        
        try:
            met_values = kwargs.get('data')['met']
            
            # 提取数值
            numerical_values = [
                met_values[1], met_values[3], met_values[5], met_values[7],
                met_values[9], met_values[11]  # 注意：这里是6个值，不是7个
            ]
            
            # 情绪分析
            emotion, intensity, valence, arousal = analyze_emotion_from_sample(numerical_values)
            
            # 更新最新数据
            self.last_emotion_data = {
                'emotion': emotion,
                'intensity': intensity,
                'valence': valence,
                'arousal': arousal,
                'timestamp': time.time()
            }
            
            # 控制输出频率
            current_time = time.time()
            if (current_time - self.last_output_time) >= self.output_interval:
                # 输出情绪状态
                logger.info(f"[EEG] 当前情绪: {emotion} | 强度: {intensity:.1f}/100 | (V: {valence:.2f}, A: {arousal:.2f})")
                
                # 发送到推荐服务
                success = self.rec_client.send_emotion_update(emotion, intensity, valence, arousal)
                if success:
                    logger.info(f"📡 情绪数据已发送到推荐服务")
                else:
                    logger.warning(f"📡 情绪数据发送失败")
                
                self.last_output_time = current_time
            
        except IndexError as e:
            logger.error(f"EEG数据格式错误: {e}")
        except Exception as e:
            logger.error(f"处理EEG数据时发生错误: {e}")
    
    def get_current_emotion_summary(self) -> str:
        """获取当前情绪摘要"""
        if self.last_emotion_data:
            data = self.last_emotion_data
            time_since_last = time.time() - data['timestamp']
            return f"最新情绪: {data['emotion']} | 强度: {data['intensity']:.1f}% | 更新于 {time_since_last:.1f}秒前"
        else:
            return "暂无情绪数据"
    
    def on_create_session_done(self, *args, **kwargs):
        """Cortex会话创建完成回调"""
        logger.info("Cortex 会话创建成功, 准备订阅数据。")
        logger.info(f"情绪数据将每 {self.output_interval} 秒输出一次并发送到推荐服务")
        self.is_connected = True
        self.subscribe_streams(self.streams)
    
    def on_inform_error(self, *args, **kwargs):
        """Cortex错误回调"""
        logger.error(f"Cortex 错误: {kwargs.get('error_data')}")
        self.is_connected = False

# ========================================================================================
# 主程序入口 (Main Application Entry Point)
# ========================================================================================

def main():
    """主程序入口"""
    logger.info("启动EEG脑波数据处理服务（仅推荐模式）...")
    
    # 检查凭证配置
    if YOUR_APP_CLIENT_ID == '你的Client ID' or YOUR_APP_CLIENT_SECRET == '你的Client Secret':
        logger.error("错误：请在代码中填入你的 Emotiv App Client ID 和 Client Secret!")
        return
    
    # 初始化推荐服务客户端
    rec_client = RecommendationServiceClient(RECOMMENDATION_SERVICE_URL)
    
    # 检查推荐服务连接
    logger.info("检查推荐服务连接状态...")
    max_retries = 30  # 最多等待30秒
    retry_count = 0
    
    while retry_count < max_retries:
        if rec_client.check_service_health():
            logger.info("✅ 推荐服务连接成功!")
            break
        else:
            logger.info(f"等待推荐服务启动... ({retry_count + 1}/{max_retries})")
            time.sleep(1)
            retry_count += 1
    
    if retry_count >= max_retries:
        logger.error("❌ 无法连接到推荐服务，请确保推荐服务已启动!")
        return
    
    # 初始化EEG数据处理器
    eeg_processor = RecommendationOnlyEEGProcessor(
        YOUR_APP_CLIENT_ID, 
        YOUR_APP_CLIENT_SECRET,
        rec_client
    )
    
    # 启动EEG数据采集
    logger.info("启动EEG数据采集...")
    logger.info("请戴上你的Emotiv设备并确保Cortex服务正在运行。")
    logger.info("💡 系统将每5秒输出一次情绪状态并发送到推荐服务")
    logger.info("🎯 专注于视频推荐，不包含音频生成功能")
    
    try:
        eeg_processor.start(['met'])
        
        # 保持程序运行
        logger.info("EEG脑波数据处理服务正在运行...")
        logger.info("📊 实时数据采集中，专注于视频内容推荐")
        logger.info("🔄 每5秒汇总输出一次情绪状态并推送到推荐服务")
        logger.info("按Ctrl+C停止服务")
        
        # 定期检查服务状态
        last_service_check = 0
        service_check_interval = 60  # 每60秒检查一次服务状态
        
        while True:
            time.sleep(1)
            
            current_time = time.time()
            if (current_time - last_service_check) >= service_check_interval:
                service_ok = rec_client.check_service_health()
                logger.info(f"🔍 服务状态检查: 推荐服务={'正常' if service_ok else '异常'}")
                last_service_check = current_time
            
            if not eeg_processor.is_connected:
                logger.warning("EEG设备连接丢失，尝试重新连接...")
                
    except KeyboardInterrupt:
        logger.info("接收到停止信号，正在关闭服务...")
    except Exception as e:
        logger.error(f"程序运行出错: {e}")
    finally:
        logger.info("EEG脑波数据处理服务已退出。")

if __name__ == "__main__":
    main()
