#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
EEG情绪驱动的视频推荐服务
Video Recommendation Service Driven by EEG Emotion Data

接收来自EEG脑波处理服务的情绪数据，实时生成个性化视频推荐
"""

import time
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from typing import Dict, List, Any

from recommendation_engine import EmotionBasedRecommendationEngine
from user_learning import UserLearningSystem
from emotion_video_mapping import VIDEO_CATEGORIES

# ========================================================================================
# 全局配置 (Global Configuration)
# ========================================================================================

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# 服务配置
RECOMMENDATION_SERVICE_PORT = 8081
UPDATE_THRESHOLD = 3.0  # 3秒内的情绪变化不重复推荐

# ========================================================================================
# 推荐服务类 (Recommendation Service Class)
# ========================================================================================

class EEGRecommendationService:
    def __init__(self):
        """初始化推荐服务"""
        logger.info("初始化EEG情绪推荐服务...")
        
        # 初始化推荐引擎和学习系统
        self.recommendation_engine = EmotionBasedRecommendationEngine()
        self.learning_system = UserLearningSystem()
        
        # 服务状态
        self.current_emotion_data = None
        self.last_recommendation_time = 0
        self.recommendation_history = []
        self.active_users = set()
        
        logger.info("推荐服务初始化完成")
    
    def process_emotion_update(self, emotion_data: Dict[str, Any], user_id: str = "default_user") -> Dict[str, Any]:
        """处理情绪更新并生成推荐"""
        try:
            # 解析情绪数据
            emotion = emotion_data.get('emotion', '')
            intensity = emotion_data.get('intensity', 0.0)
            valence = emotion_data.get('valence', 0.0)
            arousal = emotion_data.get('arousal', 0.0)
            timestamp = emotion_data.get('timestamp', time.time())
            
            # 更新当前情绪状态
            self.current_emotion_data = {
                "user_id": user_id,
                "emotion": emotion,
                "intensity": intensity,
                "valence": valence,
                "arousal": arousal,
                "timestamp": timestamp,
                "datetime": datetime.fromtimestamp(timestamp)
            }
            
            # 添加活跃用户
            self.active_users.add(user_id)
            
            logger.info(f"[{user_id}] 收到情绪数据: {emotion} | 强度: {intensity:.1f}% | V: {valence:.2f} | A: {arousal:.2f}")
            
            # 判断是否需要生成新推荐
            should_recommend = self._should_generate_recommendation()
            
            result = {
                "status": "success",
                "emotion_received": True,
                "current_emotion": self.current_emotion_data,
                "recommendation_generated": False,
                "recommendations": []
            }
            
            if should_recommend:
                recommendations = self._generate_recommendations(user_id)
                result["recommendation_generated"] = True
                result["recommendations"] = recommendations
                
                logger.info(f"[{user_id}] 生成了 {len(recommendations)} 个推荐")
            else:
                logger.info(f"[{user_id}] 情绪数据已更新，暂不生成新推荐")
            
            return result
            
        except Exception as e:
            logger.error(f"处理情绪数据时发生错误: {e}")
            return {
                "status": "error",
                "message": str(e),
                "emotion_received": False,
                "recommendation_generated": False
            }
    
    def _should_generate_recommendation(self) -> bool:
        """判断是否应该生成推荐"""
        if not self.current_emotion_data:
            logger.debug("无情绪数据，不生成推荐")
            return False
        
        current_time = time.time()
        time_since_last = current_time - self.last_recommendation_time
        
        # 检查时间间隔
        if time_since_last < UPDATE_THRESHOLD:
            logger.debug(f"时间间隔太短 ({time_since_last:.1f}s < {UPDATE_THRESHOLD}s)，不生成推荐")
            return False
        
        # 检查情绪强度（降低阈值）
        intensity = self.current_emotion_data.get("intensity", 0)
        current_emotion = self.current_emotion_data.get("emotion", "")
        
        # 强度阈值降低到25
        if intensity > 25:  # 降低强度阈值
            logger.info(f"强度足够 ({intensity:.1f} > 25)，生成推荐")
            return True
        
        # 检查情绪变化（情绪有明显变化时推荐）
        if self.recommendation_history:
            last_emotion = self.recommendation_history[-1]["emotion_context"]["emotion"]
            if last_emotion != current_emotion:
                logger.info(f"情绪变化 ({last_emotion} -> {current_emotion})，生成推荐")
                return True
        else:
            # 首次推荐，降低阈值
            if intensity > 15:  # 首次推荐阈值更低
                logger.info(f"首次推荐，强度足够 ({intensity:.1f} > 15)，生成推荐")
                return True
        
        logger.info(f"不满足推荐条件: 强度={intensity:.1f}, 情绪={current_emotion}, 历史={len(self.recommendation_history)}")
        return False
    
    def _generate_recommendations(self, user_id: str) -> List[Dict[str, Any]]:
        """生成推荐列表"""
        try:
            # 使用推荐引擎生成推荐
            recommendations = self.recommendation_engine.recommend_videos(
                emotion=self.current_emotion_data["emotion"],
                intensity=self.current_emotion_data["intensity"],
                valence=self.current_emotion_data["valence"],
                arousal=self.current_emotion_data["arousal"],
                user_id=user_id,
                num_recommendations=5
            )
            
            # 应用用户学习优化
            optimized_recommendations = self.learning_system.get_adaptive_recommendations(
                user_id, recommendations
            )
            
            # 为每个推荐添加解释
            for video in optimized_recommendations:
                video["explanation"] = self.recommendation_engine.get_recommendation_explanation(video)
                video["category_cn"] = VIDEO_CATEGORIES.get(video.get("category", ""), video.get("category", ""))
            
            # 记录推荐历史
            recommendation_record = {
                "timestamp": time.time(),
                "datetime": datetime.now(),
                "user_id": user_id,
                "emotion_context": self.current_emotion_data.copy(),
                "recommendations": optimized_recommendations,
                "num_recommendations": len(optimized_recommendations)
            }
            
            self.recommendation_history.append(recommendation_record)
            self.last_recommendation_time = time.time()
            
            # 限制历史记录长度
            if len(self.recommendation_history) > 100:
                self.recommendation_history = self.recommendation_history[-50:]
            
            return optimized_recommendations
            
        except Exception as e:
            logger.error(f"生成推荐时发生错误: {e}")
            return []
    
    def get_service_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        return {
            "service": "EEG Video Recommendation Service",
            "status": "running",
            "active_users": len(self.active_users),
            "total_recommendations": len(self.recommendation_history),
            "current_emotion": self.current_emotion_data,
            "last_recommendation_time": self.last_recommendation_time,
            "uptime": time.time()
        }
    
    def record_user_feedback(self, user_id: str, video_index: int, feedback_type: str) -> Dict[str, Any]:
        """记录用户反馈"""
        try:
            # 查找最近的推荐记录
            user_recommendations = [r for r in self.recommendation_history if r["user_id"] == user_id]
            
            if not user_recommendations:
                return {"status": "error", "message": "没有找到用户的推荐历史"}
            
            last_recommendation = user_recommendations[-1]
            recommendations = last_recommendation["recommendations"]
            
            if video_index < 1 or video_index > len(recommendations):
                return {"status": "error", "message": f"无效的视频序号，应在1-{len(recommendations)}之间"}
            
            # 获取目标视频
            target_video = recommendations[video_index - 1]
            
            # 记录反馈到学习系统
            self.learning_system.record_user_feedback(
                user_id=user_id,
                video_id=target_video["video_id"],
                feedback_type=feedback_type,
                emotion_context=last_recommendation["emotion_context"]
            )
            
            logger.info(f"[{user_id}] 记录反馈: {target_video['title']} -> {feedback_type}")
            
            return {
                "status": "success",
                "message": "反馈已记录",
                "video_title": target_video["title"],
                "feedback_type": feedback_type
            }
            
        except Exception as e:
            logger.error(f"记录用户反馈时发生错误: {e}")
            return {"status": "error", "message": str(e)}

# ========================================================================================
# Flask API 路由 (Flask API Routes)
# ========================================================================================

# 全局推荐服务实例
recommendation_service = EEGRecommendationService()

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "status": "healthy",
        "service": "EEG Video Recommendation Service",
        "timestamp": time.time()
    })

@app.route('/update_emotion', methods=['POST'])
def update_emotion():
    """接收EEG情绪数据更新"""
    try:
        emotion_data = request.get_json()
        user_id = emotion_data.get('user_id', 'default_user')
        
        if not emotion_data:
            return jsonify({"status": "error", "message": "没有接收到情绪数据"}), 400
        
        result = recommendation_service.process_emotion_update(emotion_data, user_id)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"处理情绪更新请求时发生错误: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/status', methods=['GET'])
def get_status():
    """获取服务状态"""
    try:
        status = recommendation_service.get_service_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/recommendations/<user_id>', methods=['GET'])
def get_user_recommendations(user_id):
    """获取用户的推荐历史"""
    try:
        user_history = [
            r for r in recommendation_service.recommendation_history 
            if r["user_id"] == user_id
        ]
        
        # 只返回最近的推荐
        recent_history = user_history[-10:] if user_history else []
        
        return jsonify({
            "status": "success",
            "user_id": user_id,
            "total_recommendations": len(user_history),
            "recent_recommendations": recent_history
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/feedback', methods=['POST'])
def record_feedback():
    """记录用户反馈"""
    try:
        feedback_data = request.get_json()
        user_id = feedback_data.get('user_id', 'default_user')
        video_index = feedback_data.get('video_index')
        feedback_type = feedback_data.get('feedback_type')
        
        if not all([video_index, feedback_type]):
            return jsonify({"status": "error", "message": "缺少必要参数"}), 400
        
        result = recommendation_service.record_user_feedback(user_id, video_index, feedback_type)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/user_profile/<user_id>', methods=['GET'])
def get_user_profile(user_id):
    """获取用户画像"""
    try:
        profile = recommendation_service.learning_system.get_user_profile(user_id)
        return jsonify({
            "status": "success",
            "user_id": user_id,
            "profile": profile
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ========================================================================================
# 主程序入口 (Main Application Entry Point)
# ========================================================================================

def main():
    """启动推荐服务"""
    logger.info("启动EEG情绪驱动的视频推荐服务...")
    logger.info(f"服务将在端口 {RECOMMENDATION_SERVICE_PORT} 上运行")
    logger.info("API端点:")
    logger.info("  POST /update_emotion - 接收情绪数据")
    logger.info("  GET /status - 获取服务状态")
    logger.info("  GET /health - 健康检查")
    logger.info("  POST /feedback - 记录用户反馈")
    logger.info("  GET /recommendations/<user_id> - 获取用户推荐历史")
    logger.info("  GET /user_profile/<user_id> - 获取用户画像")
    
    try:
        app.run(
            host='0.0.0.0',
            port=RECOMMENDATION_SERVICE_PORT,
            debug=False,
            threaded=True
        )
    except Exception as e:
        logger.error(f"启动服务失败: {e}")

if __name__ == "__main__":
    main() 