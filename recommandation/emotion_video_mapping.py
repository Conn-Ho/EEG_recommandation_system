"""
情绪-视频推荐映射系统
基于心理学研究和用户行为分析的情绪匹配策略
"""

# 视频类型定义
VIDEO_CATEGORIES = {
    'comedy': '搞笑幽默',
    'healing': '治愈温暖', 
    'relaxing': '放松冥想',
    'educational': '知识科普',
    'music': '音乐舞蹈',
    'sports': '运动健身',
    'food': '美食料理',
    'travel': '旅行风景',
    'pets': '萌宠动物',
    'lifestyle': '生活日常',
    'art': '艺术创作',
    'news': '新闻资讯',
    'gaming': '游戏娱乐',
    'fashion': '时尚美妆',
    'technology': '科技数码'
}

# 情绪状态与推荐策略映射
EMOTION_STRATEGIES = {
    "开心 (Happy)": {
        "maintain_emotion": ['comedy', 'music', 'pets', 'lifestyle', 'gaming'],
        "enhance_emotion": ['sports', 'travel', 'art'],
        "weights": {
            "maintain_emotion": 0.7,
            "enhance_emotion": 0.3
        },
        "avoid": []
    },
    
    "悲伤 (Sad)": {
        "healing_content": ['healing', 'pets', 'music', 'art'],
        "gentle_distraction": ['food', 'travel', 'lifestyle'],
        "weights": {
            "healing_content": 0.6,
            "gentle_distraction": 0.4
        },
        "avoid": ['news']  # 避免可能加重负面情绪的内容
    },
    
    "愤怒 (Angry)": {
        "calming_content": ['relaxing', 'healing', 'travel', 'music'],
        "physical_release": ['sports'],
        "weights": {
            "calming_content": 0.8,
            "physical_release": 0.2
        },
        "avoid": ['news', 'gaming']  # 避免可能增加激动的内容
    },
    
    "疲倦 (Tired)": {
        "light_entertainment": ['comedy', 'pets', 'food'],
        "relaxing_content": ['relaxing', 'music', 'healing'],
        "weights": {
            "light_entertainment": 0.4,
            "relaxing_content": 0.6
        },
        "avoid": ['educational', 'news']  # 避免需要消耗精力的内容
    },
    
    "放松 (Relaxed)": {
        "maintain_state": ['relaxing', 'travel', 'art', 'music'],
        "gentle_engagement": ['lifestyle', 'food', 'pets'],
        "weights": {
            "maintain_state": 0.6,
            "gentle_engagement": 0.4
        },
        "avoid": []
    },
    
    "惊喜 (Surprised)": {
        "novel_content": ['technology', 'art', 'educational'],
        "entertaining": ['comedy', 'gaming', 'music'],
        "weights": {
            "novel_content": 0.5,
            "entertaining": 0.5
        },
        "avoid": []
    },
    
    "厌恶 (Disgust)": {
        "positive_content": ['healing', 'pets', 'art', 'music'],
        "beauty_content": ['travel', 'fashion', 'food'],
        "weights": {
            "positive_content": 0.6,
            "beauty_content": 0.4
        },
        "avoid": ['news']
    },
    
    "平静 (Pleased)": {
        "aesthetic_content": ['art', 'travel', 'music'],
        "gentle_content": ['lifestyle', 'food', 'pets'],
        "weights": {
            "aesthetic_content": 0.5,
            "gentle_content": 0.5
        },
        "avoid": []
    },
    
    "中性 (Neutral)": {
        "diverse_content": ['comedy', 'educational', 'lifestyle', 'music'],
        "discovery": ['technology', 'art', 'travel'],
        "weights": {
            "diverse_content": 0.6,
            "discovery": 0.4
        },
        "avoid": []
    }
}

# 基于强度的调整策略
INTENSITY_MODIFIERS = {
    "high_intensity": {  # 强度 > 70
        "factor": 1.2,  # 加强情绪匹配权重
        "prefer_immediate": True,  # 优先即时情绪调节
        "content_length": "short"  # 偏好短内容
    },
    "medium_intensity": {  # 强度 30-70
        "factor": 1.0,
        "prefer_immediate": False,
        "content_length": "medium"
    },
    "low_intensity": {  # 强度 < 30  
        "factor": 0.8,  # 降低情绪匹配权重
        "prefer_immediate": False,
        "content_length": "any"
    }
}

# Valence-Arousal 维度补充策略
VA_STRATEGIES = {
    "high_valence_high_arousal": {  # V>0.3, A>0.3 (兴奋、快乐)
        "boost_categories": ['music', 'sports', 'comedy'],
        "boost_factor": 1.3
    },
    "high_valence_low_arousal": {  # V>0.3, A<-0.3 (满足、放松)
        "boost_categories": ['relaxing', 'art', 'travel'],
        "boost_factor": 1.2
    },
    "low_valence_high_arousal": {  # V<-0.3, A>0.3 (紧张、愤怒)
        "boost_categories": ['relaxing', 'healing'],
        "boost_factor": 1.5
    },
    "low_valence_low_arousal": {  # V<-0.3, A<-0.3 (悲伤、疲倦)
        "boost_categories": ['healing', 'pets', 'music'],
        "boost_factor": 1.4
    }
}

def get_va_category(valence, arousal):
    """根据V-A值确定情绪象限"""
    if valence > 0.3 and arousal > 0.3:
        return "high_valence_high_arousal"
    elif valence > 0.3 and arousal < -0.3:
        return "high_valence_low_arousal"
    elif valence < -0.3 and arousal > 0.3:
        return "low_valence_high_arousal"
    elif valence < -0.3 and arousal < -0.3:
        return "low_valence_low_arousal"
    else:
        return "neutral_zone"

def get_intensity_category(intensity):
    """根据强度值确定强度类别"""
    if intensity > 70:
        return "high_intensity"
    elif intensity > 30:
        return "medium_intensity"
    else:
        return "low_intensity" 