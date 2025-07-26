"""
EEG情绪识别与视频推荐集成系统
将脑机接口情绪数据与推荐算法无缝集成
"""

import sys
import os
from datetime import datetime
from typing import List, Dict, Optional

# 添加父目录到路径以导入EEG模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from recommendation_engine import EmotionBasedRecommendationEngine
from user_learning import UserLearningSystem
from cortex import Cortex
from EEG2EMO import analyze_emotion_from_sample

class IntegratedEEGRecommendationSystem:
    """
    集成的EEG情绪识别与视频推荐系统
    """
    
    def __init__(self, app_client_id: str, app_client_secret: str, user_id: str = "default_user"):
        """
        初始化集成系统
        
        Args:
            app_client_id: Emotiv应用客户端ID
            app_client_secret: Emotiv应用客户端密钥
            user_id: 用户ID
        """
        print("正在初始化EEG情绪识别与推荐集成系统...")
        
        # 初始化各个组件
        self.user_id = user_id
        self.recommendation_engine = EmotionBasedRecommendationEngine()
        self.learning_system = UserLearningSystem()
        
        # 初始化Cortex客户端
        self.cortex_client = Cortex(app_client_id, app_client_secret, debug_mode=False)
        self.cortex_client.bind(new_met_data=self.on_new_met_data)
        self.cortex_client.bind(inform_error=self.on_inform_error)
        self.cortex_client.bind(create_session_done=self.on_create_session_done)
        
        # 系统状态
        self.is_running = False
        self.current_emotion_state = None
        self.recommendation_history = []
        self.auto_recommend = True  # 是否自动推荐
        self.recommendation_interval = 30  # 推荐间隔（秒）
        self.last_recommendation_time = None
        
        print("集成系统初始化完成")
    
    def start_system(self, headset_id: str = '', auto_recommend: bool = True):
        """
        启动系统
        
        Args:
            headset_id: 头戴设备ID
            auto_recommend: 是否自动推荐
        """
        print("正在启动EEG情绪识别与推荐系统...")
        
        self.auto_recommend = auto_recommend
        self.is_running = True
        
        # 设置头戴设备
        if headset_id:
            self.cortex_client.set_wanted_headset(headset_id)
        
        # 启动Cortex连接
        self.cortex_client.open()
        print("系统启动成功，等待EEG数据...")
    
    def stop_system(self):
        """停止系统"""
        print("正在停止系统...")
        self.is_running = False
        # 这里可以添加清理代码
        print("系统已停止")
    
    def on_create_session_done(self, *args, **kwargs):
        """会话创建完成回调"""
        print("EEG会话创建成功，开始订阅情绪数据")
        self.cortex_client.sub_request(['met'])
    
    def on_new_met_data(self, *args, **kwargs):
        """接收到新的EEG情绪数据"""
        if not self.is_running:
            return
        
        try:
            # 解析EEG数据
            met_values = kwargs.get('data')['met']
            numerical_values = [
                met_values[1], met_values[3], met_values[5], met_values[7],
                met_values[9], met_values[11], met_values[13]
            ]
            
            # 情绪分析
            emotion, intensity, valence, arousal = analyze_emotion_from_sample(numerical_values)
            
            # 更新当前情绪状态
            self.current_emotion_state = {
                "emotion": emotion,
                "intensity": intensity,
                "valence": valence,
                "arousal": arousal,
                "timestamp": datetime.now(),
                "raw_met_data": numerical_values
            }
            
            # 显示情绪状态
            print(f"\n[EEG] 情绪: {emotion} | 强度: {intensity:.1f}/100 | V: {valence:.2f} | A: {arousal:.2f}")
            
            # 检查是否需要推荐
            if self.auto_recommend and self._should_generate_recommendation():
                self._generate_and_show_recommendations()
                
        except Exception as e:
            print(f"处理EEG数据时发生错误: {e}")
    
    def on_inform_error(self, *args, **kwargs):
        """错误处理回调"""
        error_data = kwargs.get('error_data')
        print(f"[EEG错误] {error_data}")
    
    def _should_generate_recommendation(self) -> bool:
        """判断是否应该生成推荐"""
        if not self.current_emotion_state:
            return False
        
        # 检查时间间隔
        current_time = datetime.now()
        if (self.last_recommendation_time and 
            (current_time - self.last_recommendation_time).seconds < self.recommendation_interval):
            return False
        
        # 检查情绪强度（高强度情绪时推荐）
        if self.current_emotion_state["intensity"] > 40:
            return True
        
        # 检查情绪变化（情绪有明显变化时推荐）
        if len(self.recommendation_history) > 0:
            last_emotion = self.recommendation_history[-1]["emotion_context"]["emotion"]
            current_emotion = self.current_emotion_state["emotion"]
            if last_emotion != current_emotion:
                return True
        
        return False
    
    def _generate_and_show_recommendations(self):
        """生成并显示推荐"""
        if not self.current_emotion_state:
            print("没有可用的情绪数据")
            return
        
        try:
            # 生成推荐
            recommendations = self.recommendation_engine.recommend_videos(
                emotion=self.current_emotion_state["emotion"],
                intensity=self.current_emotion_state["intensity"],
                valence=self.current_emotion_state["valence"],
                arousal=self.current_emotion_state["arousal"],
                user_id=self.user_id,
                num_recommendations=5
            )
            
            # 应用用户学习优化
            optimized_recommendations = self.learning_system.get_adaptive_recommendations(
                self.user_id, recommendations
            )
            
            # 显示推荐结果
            self._display_recommendations(optimized_recommendations)
            
            # 记录推荐历史
            self.recommendation_history.append({
                "timestamp": datetime.now(),
                "emotion_context": self.current_emotion_state.copy(),
                "recommendations": optimized_recommendations
            })
            
            self.last_recommendation_time = datetime.now()
            
        except Exception as e:
            print(f"生成推荐时发生错误: {e}")
    
    def _display_recommendations(self, recommendations: List[Dict]):
        """显示推荐结果"""
        print(f"\n{'='*60}")
        print(f"🎯 基于当前情绪的视频推荐 (用户: {self.user_id})")
        print(f"{'='*60}")
        
        if not recommendations:
            print("暂无推荐内容")
            return
        
        for i, video in enumerate(recommendations, 1):
            category_cn = self._get_category_chinese_name(video["category"])
            duration_min = video["duration"] // 60
            
            print(f"\n📺 推荐 {i}: {video['title']}")
            print(f"   分类: {category_cn}")
            print(f"   时长: {duration_min}分钟 | 热度: {video['popularity']:.1f}")
            print(f"   推荐分数: {video['recommendation_score']:.2f}")
            
            # 显示推荐理由
            explanation = self.recommendation_engine.get_recommendation_explanation(video)
            print(f"   推荐理由: {explanation}")
            
            # 显示个性化因子
            if "personalization_factor" in video:
                factor = video["personalization_factor"]
                print(f"   个性化匹配: {factor:.2f}")
        
        print(f"\n💡 操作提示:")
        print(f"   输入 'feedback <视频序号> <like/skip/share>' 来提供反馈")
        print(f"   输入 'manual' 手动获取推荐")
        print(f"   输入 'profile' 查看用户画像")
        print(f"   输入 'stop' 停止系统")
        print(f"{'='*60}")
    
    def _get_category_chinese_name(self, category: str) -> str:
        """获取视频类别的中文名称"""
        from emotion_video_mapping import VIDEO_CATEGORIES
        return VIDEO_CATEGORIES.get(category, category)
    
    def manual_recommendation(self):
        """手动获取推荐"""
        if not self.current_emotion_state:
            print("没有可用的情绪数据，请确保EEG设备正常连接")
            return
        
        print("正在基于当前情绪生成推荐...")
        self._generate_and_show_recommendations()
    
    def record_user_feedback(self, video_index: int, feedback_type: str):
        """记录用户反馈"""
        if not self.recommendation_history:
            print("没有可用的推荐历史")
            return
        
        last_recommendations = self.recommendation_history[-1]["recommendations"]
        
        if video_index < 1 or video_index > len(last_recommendations):
            print(f"无效的视频序号。请输入1-{len(last_recommendations)}之间的数字")
            return
        
        video = last_recommendations[video_index - 1]
        emotion_context = self.recommendation_history[-1]["emotion_context"]
        
        # 记录反馈到推荐引擎
        self.recommendation_engine.record_user_feedback(
            self.user_id, video["id"], feedback_type, emotion_context
        )
        
        # 记录到学习系统
        interaction_data = {
            "video_id": video["id"],
            "video_category": video["category"],
            "interaction_type": feedback_type,
            "emotion_context": emotion_context,
            "timestamp": datetime.now()
        }
        
        self.learning_system.record_interaction(self.user_id, interaction_data)
        
        print(f"✅ 已记录对《{video['title']}》的反馈: {feedback_type}")
    
    def show_user_profile(self):
        """显示用户画像"""
        insights = self.learning_system.get_user_insights(self.user_id)
        
        print(f"\n{'='*50}")
        print(f"👤 用户画像 ({self.user_id})")
        print(f"{'='*50}")
        
        if "error" in insights:
            print("用户数据不足，请多使用系统来构建个人画像")
            return
        
        print(f"总交互次数: {insights['total_interactions']}")
        print(f"近期活跃度: {insights['recent_activity']} 次(最近7天)")
        print(f"多样性偏好: {insights['diversity_preference']:.2f}")
        print(f"偏好稳定性: {insights['preference_stability']:.2f}")
        
        print(f"\n🔥 最喜欢的内容类型:")
        for category, score in insights['top_categories']:
            category_cn = self._get_category_chinese_name(category)
            print(f"   {category_cn}: {score:.2f}")
        
        emotion_patterns = insights['emotion_patterns']
        if emotion_patterns and emotion_patterns.get('status') != 'insufficient_data':
            print(f"\n😊 主要情绪模式:")
            for emotion in emotion_patterns.get('dominant_emotions', []):
                print(f"   {emotion}")
            
            print(f"\n📊 情绪稳定性: {emotion_patterns.get('emotion_stability', 0):.2f}")
        
        print(f"{'='*50}")
    
    def get_current_emotion_state(self) -> Optional[Dict]:
        """获取当前情绪状态"""
        return self.current_emotion_state
    
    def set_recommendation_interval(self, seconds: int):
        """设置推荐间隔"""
        self.recommendation_interval = max(10, seconds)  # 最小10秒
        print(f"推荐间隔已设置为 {self.recommendation_interval} 秒")
    
    def export_user_data(self) -> str:
        """导出用户数据"""
        return self.learning_system.export_user_data(self.user_id)
    
    def import_user_data(self, data_json: str):
        """导入用户数据"""
        self.learning_system.import_user_data(self.user_id, data_json)

def interactive_mode(system: IntegratedEEGRecommendationSystem):
    """交互模式"""
    print("\n🚀 进入交互模式")
    print("可用命令: manual, feedback <序号> <类型>, profile, interval <秒数>, stop")
    
    while system.is_running:
        try:
            command = input("\n>>> ").strip().lower()
            
            if command == "stop":
                break
            elif command == "manual":
                system.manual_recommendation()
            elif command == "profile":
                system.show_user_profile()
            elif command.startswith("feedback"):
                parts = command.split()
                if len(parts) >= 3:
                    try:
                        video_index = int(parts[1])
                        feedback_type = parts[2]
                        system.record_user_feedback(video_index, feedback_type)
                    except ValueError:
                        print("请输入正确的格式: feedback <序号> <类型>")
                else:
                    print("请输入完整的反馈命令: feedback <序号> <类型>")
            elif command.startswith("interval"):
                parts = command.split()
                if len(parts) >= 2:
                    try:
                        seconds = int(parts[1])
                        system.set_recommendation_interval(seconds)
                    except ValueError:
                        print("请输入正确的秒数")
                else:
                    print("请输入间隔秒数: interval <秒数>")
            else:
                print("未知命令，可用命令: manual, feedback, profile, interval, stop")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"命令执行错误: {e}")
    
    system.stop_system()

def main():
    """主函数"""
    print("EEG情绪识别与视频推荐集成系统")
    print("=" * 50)
    
    # 配置信息
    your_app_client_id = '6OV53rWuPZiJo6419CHi4ppabSdqKpTgfYCU5mvV'
    your_app_client_secret = 'XMWhqlpRTnQfe8a0b363jYFD976u7Ar17mQw2IWJT6eS2Z5LllaMckJbfbrSEqJYZ2LBpru6cvusWDapvjPSPutglsUwgNXYUzzcLKZqIhYOV52Rcy0YilZDJwoaQWnE'
    
    if your_app_client_id == '你的Client ID' or your_app_client_secret == '你的Client Secret':
        print("错误：请在代码中填入你的 Emotiv App Client ID 和 Client Secret!")
        return
    
    user_id = input("请输入用户ID (按回车使用默认): ").strip() or "default_user"
    
    try:
        # 创建集成系统
        system = IntegratedEEGRecommendationSystem(
            your_app_client_id, 
            your_app_client_secret, 
            user_id
        )
        
        # 启动系统
        print(f"\n正在为用户 '{user_id}' 启动系统...")
        system.start_system(auto_recommend=True)
        
        # 进入交互模式
        interactive_mode(system)
        
    except Exception as e:
        print(f"系统启动失败: {e}")

if __name__ == "__main__":
    main() 