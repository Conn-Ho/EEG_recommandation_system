"""
EEG情绪驱动的短视频推荐引擎
整合情绪识别、用户偏好和内容匹配的核心推荐算法
"""

import random
from datetime import datetime
from typing import List, Dict, Tuple
from emotion_video_mapping import (
    EMOTION_STRATEGIES, INTENSITY_MODIFIERS, VA_STRATEGIES,
    get_va_category, get_intensity_category
)
from video_database import VideoDatabase

class EmotionBasedRecommendationEngine:
    def __init__(self):
        self.video_db = VideoDatabase()
        self.recommendation_history = {}  # 推荐历史记录
        
    def recommend_videos(self, 
                        emotion: str, 
                        intensity: float, 
                        valence: float, 
                        arousal: float, 
                        user_id: str = "default_user",
                        num_recommendations: int = 5) -> List[Dict]:
        """
        基于EEG情绪数据推荐视频的主函数
        
        Args:
            emotion: 情绪类型（如"开心 (Happy)"）
            intensity: 情绪强度 (0-100)
            valence: 效价值 (-1 to 1)
            arousal: 唤醒度 (-1 to 1)
            user_id: 用户ID
            num_recommendations: 推荐视频数量
            
        Returns:
            推荐视频列表
        """
        print(f"\n=== 开始为用户 {user_id} 生成推荐 ===")
        print(f"当前情绪状态: {emotion} | 强度: {intensity:.1f} | V: {valence:.2f} | A: {arousal:.2f}")
        
        # 1. 获取情绪策略
        emotion_strategy = self._get_emotion_strategy(emotion)
        if not emotion_strategy:
            print(f"警告: 未找到情绪 '{emotion}' 的推荐策略，使用默认策略")
            emotion_strategy = EMOTION_STRATEGIES["中性 (Neutral)"]
        
        # 2. 获取强度和V-A修正因子
        intensity_modifier = self._get_intensity_modifier(intensity)
        va_modifier = self._get_va_modifier(valence, arousal)
        
        # 3. 获取用户历史偏好
        user_preferences = self.video_db.get_user_preferences(user_id)
        
        # 4. 生成候选视频集合
        candidate_videos = self._generate_candidate_videos(
            emotion_strategy, intensity_modifier, va_modifier, user_preferences
        )
        
        # 5. 计算推荐分数并排序
        scored_videos = self._score_videos(
            candidate_videos, emotion_strategy, intensity_modifier, 
            va_modifier, user_preferences, valence, arousal
        )
        
        # 6. 多样性调整和最终选择
        final_recommendations = self._apply_diversity_and_select(
            scored_videos, num_recommendations, user_id
        )
        
        # 7. 记录推荐历史
        self._record_recommendation(user_id, final_recommendations, {
            "emotion": emotion, "intensity": intensity, 
            "valence": valence, "arousal": arousal
        })
        
        print(f"推荐完成，共生成 {len(final_recommendations)} 个推荐")
        return final_recommendations
    
    def _get_emotion_strategy(self, emotion: str) -> Dict:
        """获取情绪对应的推荐策略"""
        return EMOTION_STRATEGIES.get(emotion, {})
    
    def _get_intensity_modifier(self, intensity: float) -> Dict:
        """获取强度修正因子"""
        intensity_category = get_intensity_category(intensity)
        return INTENSITY_MODIFIERS.get(intensity_category, INTENSITY_MODIFIERS["medium_intensity"])
    
    def _get_va_modifier(self, valence: float, arousal: float) -> Dict:
        """获取V-A维度修正因子"""
        va_category = get_va_category(valence, arousal)
        return VA_STRATEGIES.get(va_category, {})
    
    def _generate_candidate_videos(self, emotion_strategy: Dict, 
                                 intensity_modifier: Dict, 
                                 va_modifier: Dict, 
                                 user_preferences: Dict) -> List[Dict]:
        """生成候选视频集合"""
        candidate_videos = []
        
        # 1. 根据情绪策略获取视频
        for strategy_type, categories in emotion_strategy.items():
            if strategy_type in ["weights", "avoid"]:
                continue
                
            videos = self.video_db.get_videos_by_category(categories, limit=20)
            for video in videos:
                video["source_strategy"] = strategy_type
                candidate_videos.append(video)
        
        # 2. 根据V-A维度补充视频
        if va_modifier and "boost_categories" in va_modifier:
            va_videos = self.video_db.get_videos_by_category(
                va_modifier["boost_categories"], limit=15
            )
            for video in va_videos:
                video["source_strategy"] = "va_boost"
                candidate_videos.append(video)
        
        # 3. 根据用户偏好补充视频
        if user_preferences:
            top_preferences = sorted(user_preferences.items(), 
                                   key=lambda x: x[1], reverse=True)[:3]
            for category, score in top_preferences:
                if score > 0.5:  # 只考虑较强偏好
                    pref_videos = self.video_db.get_videos_by_category(category, limit=10)
                    for video in pref_videos:
                        video["source_strategy"] = "user_preference"
                        candidate_videos.append(video)
        
        # 4. 排除避免的类别
        avoid_categories = emotion_strategy.get("avoid", [])
        candidate_videos = self.video_db.exclude_categories(candidate_videos, avoid_categories)
        
        # 5. 根据内容长度过滤
        content_length = intensity_modifier.get("content_length", "any")
        if content_length != "any":
            candidate_videos = self.video_db.filter_by_duration(candidate_videos, content_length)
        
        # 去重
        seen_ids = set()
        unique_videos = []
        for video in candidate_videos:
            if video["id"] not in seen_ids:
                seen_ids.add(video["id"])
                unique_videos.append(video)
        
        print(f"生成候选视频 {len(unique_videos)} 个")
        return unique_videos
    
    def _score_videos(self, candidate_videos: List[Dict], 
                     emotion_strategy: Dict, 
                     intensity_modifier: Dict, 
                     va_modifier: Dict, 
                     user_preferences: Dict,
                     valence: float, 
                     arousal: float) -> List[Dict]:
        """为候选视频计算推荐分数"""
        scored_videos = []
        
        for video in candidate_videos:
            score = 0.0
            score_details = {}
            
            # 1. 基础分数（流行度 + 质量）
            base_score = video["popularity"] * 0.3 + video["like_ratio"] * 0.2
            score += base_score
            score_details["base"] = base_score
            
            # 2. 情绪策略匹配分数
            strategy_score = self._calculate_strategy_score(
                video, emotion_strategy, intensity_modifier
            )
            score += strategy_score
            score_details["strategy"] = strategy_score
            
            # 3. V-A维度匹配分数
            va_score = self._calculate_va_score(video, valence, arousal, va_modifier)
            score += va_score
            score_details["va_match"] = va_score
            
            # 4. 用户偏好分数
            preference_score = self._calculate_preference_score(video, user_preferences)
            score += preference_score
            score_details["preference"] = preference_score
            
            # 5. 新颖性分数
            novelty_score = self._calculate_novelty_score(video)
            score += novelty_score
            score_details["novelty"] = novelty_score
            
            # 6. 时效性分数
            recency_score = self._calculate_recency_score(video)
            score += recency_score
            score_details["recency"] = recency_score
            
            video["recommendation_score"] = score
            video["score_details"] = score_details
            scored_videos.append(video)
        
        return sorted(scored_videos, key=lambda x: x["recommendation_score"], reverse=True)
    
    def _calculate_strategy_score(self, video: Dict, emotion_strategy: Dict, intensity_modifier: Dict) -> float:
        """计算情绪策略匹配分数"""
        strategy_source = video.get("source_strategy", "")
        base_score = 0.0
        
        # 根据视频来源策略给分
        if strategy_source in emotion_strategy.get("weights", {}):
            base_score = emotion_strategy["weights"][strategy_source] * 0.8
        elif strategy_source == "va_boost":
            base_score = 0.6
        elif strategy_source == "user_preference":
            base_score = 0.5
        
        # 强度修正
        intensity_factor = intensity_modifier.get("factor", 1.0)
        return base_score * intensity_factor
    
    def _calculate_va_score(self, video: Dict, target_valence: float, target_arousal: float, va_modifier: Dict) -> float:
        """计算V-A维度匹配分数"""
        video_valence = video.get("valence_score", 0)
        video_arousal = video.get("arousal_score", 0)
        
        # 计算V-A距离
        valence_diff = abs(video_valence - target_valence)
        arousal_diff = abs(video_arousal - target_arousal)
        va_distance = (valence_diff + arousal_diff) / 2
        
        # 转换为相似度分数 (距离越小分数越高)
        va_similarity = max(0, 1 - va_distance)
        
        # V-A加成
        va_boost = 1.0
        if va_modifier and "boost_categories" in va_modifier:
            if video["category"] in va_modifier["boost_categories"]:
                va_boost = va_modifier.get("boost_factor", 1.0)
        
        return va_similarity * 0.4 * va_boost
    
    def _calculate_preference_score(self, video: Dict, user_preferences: Dict) -> float:
        """计算用户偏好匹配分数"""
        if not user_preferences:
            return 0.0
        
        category = video["category"]
        preference_score = user_preferences.get(category, 0.0)
        return preference_score * 0.3
    
    def _calculate_novelty_score(self, video: Dict) -> float:
        """计算新颖性分数"""
        # 基于观看次数的反向分数
        view_count = video.get("view_count", 0)
        # 使用对数缩放避免热门视频分数过低
        import math
        novelty = max(0, 1 - math.log10(max(1, view_count / 1000)) / 5)
        return novelty * 0.2
    
    def _calculate_recency_score(self, video: Dict) -> float:
        """计算时效性分数"""
        upload_time = video.get("upload_time")
        if not upload_time:
            return 0.0
        
        days_ago = (datetime.now() - upload_time).days
        # 30天内的视频获得时效性加分
        if days_ago <= 30:
            recency_score = (30 - days_ago) / 30
            return recency_score * 0.1
        return 0.0
    
    def _apply_diversity_and_select(self, scored_videos: List[Dict], 
                                  num_recommendations: int, 
                                  user_id: str) -> List[Dict]:
        """应用多样性策略并选择最终推荐"""
        if len(scored_videos) <= num_recommendations:
            return scored_videos
        
        selected_videos = []
        category_counts = {}
        
        for video in scored_videos:
            if len(selected_videos) >= num_recommendations:
                break
                
            category = video["category"]
            
            # 多样性控制：同类别视频不超过总数的50%
            max_per_category = max(1, num_recommendations // 2)
            if category_counts.get(category, 0) < max_per_category:
                selected_videos.append(video)
                category_counts[category] = category_counts.get(category, 0) + 1
        
        # 如果没有选够，补充高分视频
        if len(selected_videos) < num_recommendations:
            for video in scored_videos:
                if video not in selected_videos and len(selected_videos) < num_recommendations:
                    selected_videos.append(video)
        
        return selected_videos
    
    def _record_recommendation(self, user_id: str, recommendations: List[Dict], emotion_context: Dict):
        """记录推荐历史"""
        if user_id not in self.recommendation_history:
            self.recommendation_history[user_id] = []
        
        record = {
            "timestamp": datetime.now(),
            "emotion_context": emotion_context,
            "recommended_videos": [v["id"] for v in recommendations],
            "recommendation_details": recommendations
        }
        
        self.recommendation_history[user_id].append(record)
    
    def get_recommendation_explanation(self, video: Dict) -> str:
        """生成推荐解释"""
        explanations = []
        
        if "score_details" not in video:
            return "基于您的当前情绪状态推荐"
        
        score_details = video["score_details"]
        source_strategy = video.get("source_strategy", "")
        
        if source_strategy == "user_preference":
            explanations.append("符合您的观看偏好")
        
        if score_details.get("va_match", 0) > 0.3:
            explanations.append("与您当前的情绪状态高度匹配")
        
        if score_details.get("strategy", 0) > 0.5:
            explanations.append("有助于调节您的当前情绪")
        
        if score_details.get("novelty", 0) > 0.15:
            explanations.append("为您发现新鲜内容")
        
        if not explanations:
            explanations.append("基于综合评分推荐")
        
        return " • ".join(explanations)
    
    def record_user_feedback(self, user_id: str, video_id: str, 
                           interaction_type: str, emotion_context: Dict = None):
        """记录用户反馈"""
        self.video_db.record_user_interaction(
            user_id, video_id, interaction_type, emotion_context
        )
        print(f"记录用户 {user_id} 对视频 {video_id} 的反馈: {interaction_type}")
    
    def get_user_emotion_history(self, user_id: str) -> List[Dict]:
        """获取用户情绪历史"""
        if user_id not in self.recommendation_history:
            return []
        
        emotion_history = []
        for record in self.recommendation_history[user_id]:
            emotion_history.append({
                "timestamp": record["timestamp"],
                "emotion_context": record["emotion_context"]
            })
        
        return emotion_history 