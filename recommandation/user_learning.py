"""
用户偏好学习与适应性优化模块
基于用户行为数据和情绪反馈不断优化推荐策略
"""

import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from collections import defaultdict

class UserLearningSystem:
    def __init__(self):
        self.user_profiles = {}  # 用户画像
        self.emotion_patterns = {}  # 情绪模式分析
        self.adaptation_rates = {
            "fast": 0.3,    # 快速适应
            "medium": 0.15, # 中等适应
            "slow": 0.05    # 缓慢适应
        }
        
    def update_user_profile(self, user_id: str, interaction_data: Dict):
        """更新用户画像"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = self._initialize_user_profile()
        
        profile = self.user_profiles[user_id]
        
        # 更新基础偏好
        self._update_category_preferences(profile, interaction_data)
        
        # 更新情绪-内容关联
        self._update_emotion_content_mapping(profile, interaction_data)
        
        # 更新时间偏好
        self._update_temporal_preferences(profile, interaction_data)
        
        # 更新多样性偏好
        self._update_diversity_preferences(profile, interaction_data)
        
        print(f"已更新用户 {user_id} 的画像")
    
    def _initialize_user_profile(self) -> Dict:
        """初始化用户画像"""
        return {
            "category_preferences": {},  # 类别偏好
            "emotion_content_mapping": {},  # 情绪-内容映射
            "temporal_patterns": {  # 时间模式
                "active_hours": [],
                "preferred_duration": "medium",
                "session_length": 30  # 平均观看时长(分钟)
            },
            "diversity_preference": 0.5,  # 多样性偏好 0-1
            "adaptation_rate": "medium",  # 适应速度
            "interaction_history": [],
            "last_updated": datetime.now(),
            "total_interactions": 0
        }
    
    def _update_category_preferences(self, profile: Dict, interaction_data: Dict):
        """更新类别偏好"""
        video_category = interaction_data.get("video_category")
        interaction_type = interaction_data.get("interaction_type")
        
        if not video_category:
            return
        
        # 获取交互权重
        weights = {
            "view": 1.0,
            "like": 3.0,
            "share": 5.0,
            "comment": 4.0,
            "skip": -1.0,
            "dislike": -3.0
        }
        
        weight = weights.get(interaction_type, 0)
        adaptation_rate = self.adaptation_rates[profile["adaptation_rate"]]
        
        # 更新偏好分数
        current_score = profile["category_preferences"].get(video_category, 0.5)
        new_score = current_score + (weight * adaptation_rate * 0.1)
        new_score = max(0, min(1, new_score))  # 限制在0-1之间
        
        profile["category_preferences"][video_category] = new_score
    
    def _update_emotion_content_mapping(self, profile: Dict, interaction_data: Dict):
        """更新情绪-内容映射"""
        emotion_context = interaction_data.get("emotion_context")
        video_category = interaction_data.get("video_category")
        interaction_type = interaction_data.get("interaction_type")
        
        if not emotion_context or not video_category:
            return
        
        emotion = emotion_context.get("emotion")
        if not emotion:
            return
        
        if emotion not in profile["emotion_content_mapping"]:
            profile["emotion_content_mapping"][emotion] = {}
        
        # 计算情绪-内容匹配成功率
        positive_interactions = ["view", "like", "share", "comment"]
        is_positive = interaction_type in positive_interactions
        
        current_mapping = profile["emotion_content_mapping"][emotion].get(video_category, {"success": 0, "total": 0})
        current_mapping["total"] += 1
        if is_positive:
            current_mapping["success"] += 1
        
        profile["emotion_content_mapping"][emotion][video_category] = current_mapping
    
    def _update_temporal_preferences(self, profile: Dict, interaction_data: Dict):
        """更新时间偏好模式"""
        timestamp = interaction_data.get("timestamp", datetime.now())
        watch_duration = interaction_data.get("watch_duration")
        
        # 记录活跃时段
        hour = timestamp.hour
        if hour not in profile["temporal_patterns"]["active_hours"]:
            profile["temporal_patterns"]["active_hours"].append(hour)
        
        # 更新偏好时长
        if watch_duration:
            current_pref = profile["temporal_patterns"]["preferred_duration"]
            if watch_duration < 300:  # 5分钟
                new_pref = "short"
            elif watch_duration < 900:  # 15分钟
                new_pref = "medium"  
            else:
                new_pref = "long"
            
            # 平滑更新
            if current_pref != new_pref:
                profile["temporal_patterns"]["preferred_duration"] = new_pref
    
    def _update_diversity_preferences(self, profile: Dict, interaction_data: Dict):
        """更新多样性偏好"""
        # 分析用户是否喜欢多样性内容
        recent_categories = []
        for interaction in profile["interaction_history"][-10:]:  # 最近10次交互
            if interaction.get("video_category"):
                recent_categories.append(interaction["video_category"])
        
        if len(recent_categories) >= 3:
            unique_categories = len(set(recent_categories))
            diversity_ratio = unique_categories / len(recent_categories)
            
            # 如果用户经常与不同类别内容交互，提高多样性偏好
            current_diversity = profile["diversity_preference"]
            adjustment = (diversity_ratio - 0.5) * 0.1
            new_diversity = max(0, min(1, current_diversity + adjustment))
            profile["diversity_preference"] = new_diversity
    
    def get_personalized_emotion_strategy(self, user_id: str, emotion: str) -> Dict:
        """获取个性化的情绪策略"""
        if user_id not in self.user_profiles:
            return {}
        
        profile = self.user_profiles[user_id]
        emotion_mapping = profile.get("emotion_content_mapping", {}).get(emotion, {})
        
        # 基于历史成功率调整策略权重
        personalized_strategy = {}
        for category, stats in emotion_mapping.items():
            if stats["total"] >= 3:  # 至少3次交互才有统计意义
                success_rate = stats["success"] / stats["total"]
                if success_rate > 0.6:  # 成功率超过60%
                    personalized_strategy[category] = success_rate
        
        return personalized_strategy
    
    def analyze_emotion_patterns(self, user_id: str) -> Dict:
        """分析用户情绪模式"""
        if user_id not in self.user_profiles:
            return {}
        
        profile = self.user_profiles[user_id]
        interactions = profile["interaction_history"]
        
        if len(interactions) < 10:
            return {"status": "insufficient_data"}
        
        # 情绪频率分析
        emotion_frequency = defaultdict(int)
        emotion_transitions = defaultdict(list)
        
        prev_emotion = None
        for interaction in interactions[-50:]:  # 分析最近50次交互
            emotion_context = interaction.get("emotion_context", {})
            current_emotion = emotion_context.get("emotion")
            
            if current_emotion:
                emotion_frequency[current_emotion] += 1
                
                if prev_emotion and prev_emotion != current_emotion:
                    emotion_transitions[prev_emotion].append(current_emotion)
                
                prev_emotion = current_emotion
        
        # 计算情绪稳定性
        emotion_stability = self._calculate_emotion_stability(interactions)
        
        # 寻找情绪触发模式
        trigger_patterns = self._find_trigger_patterns(interactions)
        
        return {
            "emotion_frequency": dict(emotion_frequency),
            "emotion_transitions": dict(emotion_transitions),
            "emotion_stability": emotion_stability,
            "trigger_patterns": trigger_patterns,
            "dominant_emotions": self._get_dominant_emotions(emotion_frequency)
        }
    
    def _calculate_emotion_stability(self, interactions: List[Dict]) -> float:
        """计算情绪稳定性"""
        intensities = []
        for interaction in interactions[-20:]:
            emotion_context = interaction.get("emotion_context", {})
            intensity = emotion_context.get("intensity")
            if intensity is not None:
                intensities.append(intensity)
        
        if len(intensities) < 5:
            return 0.5  # 默认中等稳定性
        
        # 计算强度变化的标准差，标准差越小越稳定
        std_dev = np.std(intensities)
        stability = max(0, 1 - (std_dev / 50))  # 标准化到0-1
        return stability
    
    def _find_trigger_patterns(self, interactions: List[Dict]) -> Dict:
        """寻找情绪触发模式"""
        patterns = {
            "time_triggers": defaultdict(list),  # 时间触发器
            "content_triggers": defaultdict(list),  # 内容触发器
            "sequence_patterns": []  # 序列模式
        }
        
        for interaction in interactions[-30:]:
            emotion_context = interaction.get("emotion_context", {})
            emotion = emotion_context.get("emotion")
            timestamp = interaction.get("timestamp")
            category = interaction.get("video_category")
            
            if emotion and timestamp:
                hour = timestamp.hour
                patterns["time_triggers"][hour].append(emotion)
            
            if emotion and category:
                patterns["content_triggers"][category].append(emotion)
        
        return patterns
    
    def _get_dominant_emotions(self, emotion_frequency: Dict) -> List[str]:
        """获取主导情绪"""
        total_count = sum(emotion_frequency.values())
        if total_count == 0:
            return []
        
        dominant = []
        for emotion, count in emotion_frequency.items():
            if count / total_count > 0.15:  # 占比超过15%
                dominant.append(emotion)
        
        return sorted(dominant, key=lambda x: emotion_frequency[x], reverse=True)
    
    def get_adaptive_recommendations(self, user_id: str, base_recommendations: List[Dict]) -> List[Dict]:
        """基于用户学习结果调整推荐"""
        if user_id not in self.user_profiles:
            return base_recommendations
        
        profile = self.user_profiles[user_id]
        
        # 应用个性化权重
        adjusted_recommendations = []
        for video in base_recommendations:
            adjusted_video = video.copy()
            
            # 根据类别偏好调整分数
            category = video.get("category")
            category_preference = profile["category_preferences"].get(category, 0.5)
            
            current_score = video.get("recommendation_score", 0)
            adjusted_score = current_score * (0.7 + 0.6 * category_preference)
            
            # 根据多样性偏好调整
            diversity_pref = profile["diversity_preference"]
            if diversity_pref > 0.7:  # 喜欢多样性
                # 提升不常见类别的分数
                if category_preference < 0.3:
                    adjusted_score *= 1.2
            
            adjusted_video["recommendation_score"] = adjusted_score
            adjusted_video["personalization_factor"] = category_preference
            adjusted_recommendations.append(adjusted_video)
        
        # 重新排序
        return sorted(adjusted_recommendations, 
                     key=lambda x: x["recommendation_score"], reverse=True)
    
    def record_interaction(self, user_id: str, interaction_data: Dict):
        """记录用户交互"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = self._initialize_user_profile()
        
        profile = self.user_profiles[user_id]
        
        # 添加时间戳
        interaction_data["timestamp"] = interaction_data.get("timestamp", datetime.now())
        
        # 记录交互
        profile["interaction_history"].append(interaction_data)
        profile["total_interactions"] += 1
        profile["last_updated"] = datetime.now()
        
        # 保持历史记录在合理范围内
        if len(profile["interaction_history"]) > 100:
            profile["interaction_history"] = profile["interaction_history"][-100:]
        
        # 更新用户画像
        self.update_user_profile(user_id, interaction_data)
    
    def get_user_insights(self, user_id: str) -> Dict:
        """获取用户洞察报告"""
        if user_id not in self.user_profiles:
            return {"error": "用户不存在"}
        
        profile = self.user_profiles[user_id]
        
        # 分析情绪模式
        emotion_patterns = self.analyze_emotion_patterns(user_id)
        
        # 计算偏好稳定性
        category_prefs = profile["category_preferences"]
        preference_entropy = self._calculate_preference_entropy(category_prefs)
        
        # 活跃度分析
        recent_interactions = [i for i in profile["interaction_history"] 
                             if (datetime.now() - i["timestamp"]).days <= 7]
        
        return {
            "user_id": user_id,
            "total_interactions": profile["total_interactions"],
            "recent_activity": len(recent_interactions),
            "top_categories": sorted(category_prefs.items(), 
                                   key=lambda x: x[1], reverse=True)[:5],
            "diversity_preference": profile["diversity_preference"],
            "emotion_patterns": emotion_patterns,
            "preference_stability": 1 - preference_entropy,
            "adaptation_rate": profile["adaptation_rate"],
            "last_updated": profile["last_updated"]
        }
    
    def _calculate_preference_entropy(self, preferences: Dict) -> float:
        """计算偏好熵（衡量偏好的分散程度）"""
        if not preferences:
            return 0
        
        values = list(preferences.values())
        total = sum(values)
        if total == 0:
            return 0
        
        # 计算熵
        entropy = 0
        for value in values:
            if value > 0:
                p = value / total
                entropy -= p * np.log2(p)
        
        # 归一化
        max_entropy = np.log2(len(values)) if len(values) > 1 else 1
        return entropy / max_entropy if max_entropy > 0 else 0
    
    def export_user_data(self, user_id: str) -> str:
        """导出用户数据"""
        if user_id not in self.user_profiles:
            return "{}"
        
        profile = self.user_profiles[user_id].copy()
        
        # 转换datetime对象为字符串
        def datetime_converter(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        return json.dumps(profile, default=datetime_converter, indent=2, ensure_ascii=False)
    
    def import_user_data(self, user_id: str, data_json: str):
        """导入用户数据"""
        try:
            profile = json.loads(data_json)
            
            # 转换时间字符串回datetime对象
            if "last_updated" in profile:
                profile["last_updated"] = datetime.fromisoformat(profile["last_updated"])
            
            for interaction in profile.get("interaction_history", []):
                if "timestamp" in interaction:
                    interaction["timestamp"] = datetime.fromisoformat(interaction["timestamp"])
            
            self.user_profiles[user_id] = profile
            print(f"成功导入用户 {user_id} 的数据")
            
        except Exception as e:
            print(f"导入用户数据失败: {e}") 