"""
视频数据库模拟系统
用于存储和管理视频信息，包括标签、特征和元数据
"""

import random
import json
from datetime import datetime, timedelta
from emotion_video_mapping import VIDEO_CATEGORIES

class VideoDatabase:
    def __init__(self):
        self.videos = []
        self.user_interactions = {}  # 用户交互历史
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """初始化示例视频数据"""
        sample_videos = [
            # 搞笑幽默类
            {"id": "v001", "title": "猫咪搞笑集锦", "category": "comedy", "tags": ["动物", "搞笑", "萌宠"], "duration": 180, "popularity": 0.9},
            {"id": "v002", "title": "沙雕网友神回复", "category": "comedy", "tags": ["搞笑", "段子", "网络"], "duration": 120, "popularity": 0.8},
            
            # 治愈温暖类
            {"id": "v003", "title": "夕阳下的小镇", "category": "healing", "tags": ["风景", "治愈", "温暖"], "duration": 300, "popularity": 0.7},
            {"id": "v004", "title": "奶奶的手工编织", "category": "healing", "tags": ["手工", "家庭", "温情"], "duration": 240, "popularity": 0.6},
            
            # 放松冥想类
            {"id": "v005", "title": "森林雨声冥想", "category": "relaxing", "tags": ["自然", "放松", "冥想"], "duration": 600, "popularity": 0.5},
            {"id": "v006", "title": "海浪声助眠", "category": "relaxing", "tags": ["海洋", "放松", "助眠"], "duration": 1800, "popularity": 0.4},
            
            # 音乐舞蹈类
            {"id": "v007", "title": "古典钢琴名曲", "category": "music", "tags": ["音乐", "钢琴", "古典"], "duration": 360, "popularity": 0.8},
            {"id": "v008", "title": "街舞教学基础", "category": "music", "tags": ["舞蹈", "教学", "街舞"], "duration": 480, "popularity": 0.7},
            
            # 萌宠动物类
            {"id": "v009", "title": "小狗学游泳", "category": "pets", "tags": ["狗狗", "游泳", "可爱"], "duration": 200, "popularity": 0.9},
            {"id": "v010", "title": "仓鼠囤食日常", "category": "pets", "tags": ["仓鼠", "日常", "萌宠"], "duration": 150, "popularity": 0.8},
            
            # 美食料理类
            {"id": "v011", "title": "家常菜快手做法", "category": "food", "tags": ["美食", "家常菜", "教学"], "duration": 300, "popularity": 0.7},
            {"id": "v012", "title": "日式便当制作", "category": "food", "tags": ["便当", "日式", "精致"], "duration": 420, "popularity": 0.6},
            
            # 旅行风景类
            {"id": "v013", "title": "新疆天山美景", "category": "travel", "tags": ["新疆", "天山", "风景"], "duration": 480, "popularity": 0.8},
            {"id": "v014", "title": "京都樱花季", "category": "travel", "tags": ["京都", "樱花", "日本"], "duration": 360, "popularity": 0.9},
            
            # 知识科普类
            {"id": "v015", "title": "量子物理入门", "category": "educational", "tags": ["科学", "物理", "教育"], "duration": 720, "popularity": 0.5},
            {"id": "v016", "title": "如何培养专注力", "category": "educational", "tags": ["心理学", "专注力", "自我提升"], "duration": 600, "popularity": 0.6},
        ]
        
        for video in sample_videos:
            video.update({
                "upload_time": datetime.now() - timedelta(days=random.randint(1, 30)),
                "view_count": random.randint(1000, 100000),
                "like_ratio": random.uniform(0.6, 0.95),
                "emotional_tags": self._generate_emotional_tags(video["category"]),
                "valence_score": random.uniform(-0.5, 0.8),  # 大多数视频偏正面
                "arousal_score": random.uniform(-0.3, 0.7),
            })
        
        self.videos = sample_videos
    
    def _generate_emotional_tags(self, category):
        """根据视频类别生成情感标签"""
        emotional_mapping = {
            "comedy": ["joy", "amusement", "surprise"],
            "healing": ["calm", "warmth", "comfort"],
            "relaxing": ["peace", "tranquility", "meditation"],
            "music": ["rhythm", "emotion", "expression"],
            "pets": ["cuteness", "joy", "warmth"],
            "food": ["satisfaction", "comfort", "pleasure"],
            "travel": ["wonder", "beauty", "inspiration"],
            "educational": ["curiosity", "growth", "achievement"],
        }
        return emotional_mapping.get(category, ["neutral"])
    
    def get_videos_by_category(self, categories, limit=10):
        """按类别获取视频"""
        if isinstance(categories, str):
            categories = [categories]
        
        matching_videos = [v for v in self.videos if v["category"] in categories]
        return sorted(matching_videos, key=lambda x: x["popularity"], reverse=True)[:limit]
    
    def get_videos_by_tags(self, tags, limit=10):
        """按标签获取视频"""
        if isinstance(tags, str):
            tags = [tags]
        
        matching_videos = []
        for video in self.videos:
            video_tags = video.get("tags", []) + video.get("emotional_tags", [])
            if any(tag in video_tags for tag in tags):
                matching_videos.append(video)
        
        return sorted(matching_videos, key=lambda x: x["popularity"], reverse=True)[:limit]
    
    def get_videos_by_valence_arousal(self, target_valence, target_arousal, tolerance=0.3, limit=10):
        """根据V-A值获取相似情感的视频"""
        matching_videos = []
        for video in self.videos:
            v_diff = abs(video["valence_score"] - target_valence)
            a_diff = abs(video["arousal_score"] - target_arousal)
            if v_diff <= tolerance and a_diff <= tolerance:
                # 计算相似度分数
                similarity = 1 - (v_diff + a_diff) / (2 * tolerance)
                video["similarity_score"] = similarity
                matching_videos.append(video)
        
        return sorted(matching_videos, key=lambda x: x["similarity_score"], reverse=True)[:limit]
    
    def filter_by_duration(self, videos, content_length):
        """按时长过滤视频"""
        if content_length == "short":
            return [v for v in videos if v["duration"] <= 300]  # 5分钟以内
        elif content_length == "medium":
            return [v for v in videos if 300 < v["duration"] <= 900]  # 5-15分钟
        elif content_length == "long":
            return [v for v in videos if v["duration"] > 900]  # 15分钟以上
        else:
            return videos
    
    def exclude_categories(self, videos, avoid_categories):
        """排除特定类别的视频"""
        if not avoid_categories:
            return videos
        return [v for v in videos if v["category"] not in avoid_categories]
    
    def record_user_interaction(self, user_id, video_id, interaction_type, emotion_context=None):
        """记录用户交互行为"""
        if user_id not in self.user_interactions:
            self.user_interactions[user_id] = []
        
        interaction = {
            "video_id": video_id,
            "interaction_type": interaction_type,  # "view", "like", "skip", "share"
            "timestamp": datetime.now(),
            "emotion_context": emotion_context
        }
        
        self.user_interactions[user_id].append(interaction)
    
    def get_user_preferences(self, user_id):
        """分析用户偏好"""
        if user_id not in self.user_interactions:
            return {}
        
        interactions = self.user_interactions[user_id]
        category_scores = {}
        
        for interaction in interactions:
            video = self.get_video_by_id(interaction["video_id"])
            if video:
                category = video["category"]
                score_delta = self._get_interaction_score(interaction["interaction_type"])
                category_scores[category] = category_scores.get(category, 0) + score_delta
        
        # 归一化分数
        if category_scores:
            max_score = max(category_scores.values())
            min_score = min(category_scores.values())
            if max_score > min_score:
                for category in category_scores:
                    category_scores[category] = (category_scores[category] - min_score) / (max_score - min_score)
        
        return category_scores
    
    def _get_interaction_score(self, interaction_type):
        """获取交互行为的分数"""
        scores = {
            "view": 1,
            "like": 3,
            "share": 5,
            "skip": -1,
            "dislike": -3
        }
        return scores.get(interaction_type, 0)
    
    def get_video_by_id(self, video_id):
        """根据ID获取视频"""
        for video in self.videos:
            if video["id"] == video_id:
                return video
        return None
    
    def add_video(self, video_data):
        """添加新视频"""
        self.videos.append(video_data)
    
    def get_trending_videos(self, limit=10):
        """获取热门视频"""
        return sorted(self.videos, key=lambda x: x["view_count"], reverse=True)[:limit]
    
    def get_recent_videos(self, limit=10):
        """获取最新视频"""
        return sorted(self.videos, key=lambda x: x["upload_time"], reverse=True)[:limit] 