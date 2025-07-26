"""
EEG情绪推荐系统演示脚本
用于测试和展示推荐算法的功能
"""

import random
from datetime import datetime
from recommendation_engine import EmotionBasedRecommendationEngine
from user_learning import UserLearningSystem

def simulate_emotion_data():
    """模拟情绪数据"""
    emotions = [
        "开心 (Happy)", "悲伤 (Sad)", "愤怒 (Angry)", 
        "疲倦 (Tired)", "放松 (Relaxed)", "惊喜 (Surprised)",
        "厌恶 (Disgust)", "平静 (Pleased)", "中性 (Neutral)"
    ]
    
    emotion = random.choice(emotions)
    intensity = random.uniform(20, 90)
    valence = random.uniform(-0.8, 0.8)
    arousal = random.uniform(-0.6, 0.8)
    
    return emotion, intensity, valence, arousal

def demo_basic_recommendation():
    """演示基础推荐功能"""
    print("=" * 60)
    print("🔬 基础推荐功能演示")
    print("=" * 60)
    
    # 初始化推荐引擎
    engine = EmotionBasedRecommendationEngine()
    
    # 模拟不同情绪状态的推荐
    test_emotions = [
        ("开心 (Happy)", 75, 0.6, 0.4),
        ("悲伤 (Sad)", 60, -0.5, -0.2),
        ("愤怒 (Angry)", 85, -0.3, 0.7),
        ("疲倦 (Tired)", 40, -0.2, -0.6),
        ("放松 (Relaxed)", 30, 0.4, -0.3)
    ]
    
    for emotion, intensity, valence, arousal in test_emotions:
        print(f"\n📊 测试情绪: {emotion}")
        print(f"强度: {intensity} | V: {valence:.2f} | A: {arousal:.2f}")
        
        recommendations = engine.recommend_videos(
            emotion=emotion,
            intensity=intensity,
            valence=valence,
            arousal=arousal,
            user_id="demo_user",
            num_recommendations=3
        )
        
        print("推荐结果:")
        for i, video in enumerate(recommendations, 1):
            print(f"  {i}. {video['title']} ({video['category']})")
            print(f"     分数: {video['recommendation_score']:.2f}")
            explanation = engine.get_recommendation_explanation(video)
            print(f"     理由: {explanation}")
        
        print("-" * 50)

def demo_user_learning():
    """演示用户学习功能"""
    print("\n" + "=" * 60)
    print("🧠 用户学习功能演示")
    print("=" * 60)
    
    # 初始化系统
    engine = EmotionBasedRecommendationEngine()
    learning_system = UserLearningSystem()
    
    user_id = "learning_demo_user"
    
    # 模拟用户交互历史
    interactions = [
        {"emotion": "开心 (Happy)", "category": "comedy", "feedback": "like"},
        {"emotion": "开心 (Happy)", "category": "pets", "feedback": "share"},
        {"emotion": "悲伤 (Sad)", "category": "healing", "feedback": "like"},
        {"emotion": "悲伤 (Sad)", "category": "music", "feedback": "like"},
        {"emotion": "疲倦 (Tired)", "category": "relaxing", "feedback": "like"},
        {"emotion": "疲倦 (Tired)", "category": "comedy", "feedback": "skip"},
        {"emotion": "愤怒 (Angry)", "category": "relaxing", "feedback": "like"},
        {"emotion": "愤怒 (Angry)", "category": "sports", "feedback": "like"},
    ]
    
    print("📝 模拟用户交互历史...")
    for interaction in interactions:
        # 记录交互
        interaction_data = {
            "video_category": interaction["category"],
            "interaction_type": interaction["feedback"],
            "emotion_context": {"emotion": interaction["emotion"]},
            "timestamp": datetime.now()
        }
        learning_system.record_interaction(user_id, interaction_data)
    
    # 显示用户画像
    print("\n👤 用户画像分析:")
    insights = learning_system.get_user_insights(user_id)
    print(f"总交互次数: {insights['total_interactions']}")
    print(f"多样性偏好: {insights['diversity_preference']:.2f}")
    
    print("\n🔥 类别偏好:")
    for category, score in insights['top_categories'][:5]:
        print(f"  {category}: {score:.2f}")
    
    # 测试个性化推荐
    print("\n🎯 个性化推荐测试:")
    
    test_emotion = "开心 (Happy)"
    base_recommendations = engine.recommend_videos(
        emotion=test_emotion,
        intensity=70,
        valence=0.5,
        arousal=0.3,
        user_id=user_id,
        num_recommendations=5
    )
    
    personalized_recommendations = learning_system.get_adaptive_recommendations(
        user_id, base_recommendations
    )
    
    print(f"基于 '{test_emotion}' 的个性化推荐:")
    for i, video in enumerate(personalized_recommendations[:3], 1):
        factor = video.get("personalization_factor", 0)
        print(f"  {i}. {video['title']}")
        print(f"     类别: {video['category']} | 个性化因子: {factor:.2f}")
        print(f"     推荐分数: {video['recommendation_score']:.2f}")

def demo_emotion_patterns():
    """演示情绪模式分析"""
    print("\n" + "=" * 60)
    print("📈 情绪模式分析演示")
    print("=" * 60)
    
    learning_system = UserLearningSystem()
    user_id = "pattern_demo_user"
    
    # 模拟一周的情绪数据
    emotions_week = [
        "开心 (Happy)", "开心 (Happy)", "中性 (Neutral)",
        "疲倦 (Tired)", "悲伤 (Sad)", "开心 (Happy)",
        "放松 (Relaxed)", "开心 (Happy)", "开心 (Happy)",
        "愤怒 (Angry)", "悲伤 (Sad)", "放松 (Relaxed)",
        "开心 (Happy)", "中性 (Neutral)", "疲倦 (Tired)"
    ]
    
    categories = ["comedy", "healing", "relaxing", "music", "pets"]
    
    print("📊 模拟一周的用户行为数据...")
    for i, emotion in enumerate(emotions_week):
        category = random.choice(categories)
        feedback = random.choice(["like", "view", "skip"])
        
        interaction_data = {
            "video_category": category,
            "interaction_type": feedback,
            "emotion_context": {
                "emotion": emotion,
                "intensity": random.uniform(30, 80)
            },
            "timestamp": datetime.now()
        }
        learning_system.record_interaction(user_id, interaction_data)
    
    # 分析情绪模式
    patterns = learning_system.analyze_emotion_patterns(user_id)
    
    if patterns.get('status') != 'insufficient_data':
        print("\n😊 情绪频率分析:")
        for emotion, count in patterns['emotion_frequency'].items():
            print(f"  {emotion}: {count} 次")
        
        print(f"\n📊 情绪稳定性: {patterns['emotion_stability']:.2f}")
        
        print("\n🔥 主导情绪:")
        for emotion in patterns['dominant_emotions']:
            print(f"  {emotion}")
    else:
        print("数据不足，无法进行情绪模式分析")

def demo_recommendation_explanation():
    """演示推荐解释功能"""
    print("\n" + "=" * 60)
    print("💬 推荐解释功能演示")
    print("=" * 60)
    
    engine = EmotionBasedRecommendationEngine()
    
    # 获取推荐
    recommendations = engine.recommend_videos(
        emotion="悲伤 (Sad)",
        intensity=65,
        valence=-0.4,
        arousal=-0.1,
        user_id="explanation_demo",
        num_recommendations=3
    )
    
    print("📝 推荐解释演示:")
    for i, video in enumerate(recommendations, 1):
        print(f"\n{i}. 视频: {video['title']}")
        print(f"   类别: {video['category']}")
        
        # 显示详细分数
        if 'score_details' in video:
            details = video['score_details']
            print(f"   分数详情:")
            print(f"     基础分数: {details.get('base', 0):.3f}")
            print(f"     策略匹配: {details.get('strategy', 0):.3f}")
            print(f"     V-A匹配: {details.get('va_match', 0):.3f}")
            print(f"     用户偏好: {details.get('preference', 0):.3f}")
            print(f"     新颖性: {details.get('novelty', 0):.3f}")
            print(f"     时效性: {details.get('recency', 0):.3f}")
        
        # 显示推荐解释
        explanation = engine.get_recommendation_explanation(video)
        print(f"   推荐理由: {explanation}")

def main():
    """主演示函数"""
    print("🎬 EEG情绪推荐系统演示")
    print("=" * 60)
    
    demos = [
        ("1", "基础推荐功能", demo_basic_recommendation),
        ("2", "用户学习功能", demo_user_learning),
        ("3", "情绪模式分析", demo_emotion_patterns),
        ("4", "推荐解释功能", demo_recommendation_explanation),
        ("5", "运行所有演示", lambda: [demo() for _, _, demo in demos[:-1]])
    ]
    
    print("可用演示:")
    for num, name, _ in demos:
        print(f"  {num}. {name}")
    
    while True:
        try:
            choice = input("\n请选择要运行的演示 (输入数字，q退出): ").strip()
            
            if choice.lower() == 'q':
                print("演示结束")
                break
            
            demo_func = None
            for num, name, func in demos:
                if choice == num:
                    demo_func = func
                    break
            
            if demo_func:
                demo_func()
                print(f"\n✅ 演示完成")
                input("按回车继续...")
            else:
                print("无效选择，请重试")
                
        except KeyboardInterrupt:
            print("\n演示结束")
            break
        except Exception as e:
            print(f"演示过程中发生错误: {e}")

if __name__ == "__main__":
    main() 