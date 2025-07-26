#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
EEG情绪视频推荐测试工具 - 仅推荐版本
Emotion Video Recommendation Test Tool - Recommendation Only

专门用于测试视频推荐服务，不包含音频功能
"""

import requests
import time
import random
import json
from datetime import datetime
from typing import Dict, List, Tuple

# 服务配置
RECOMMENDATION_SERVICE_URL = 'http://localhost:8081'

# 模拟情绪数据
EMOTIONS = [
    ("Happy (开心)", 0.6, 0.4),
    ("Sad (悲伤)", -0.5, -0.2),
    ("Angry (愤怒)", -0.3, 0.7),
    ("Relaxed (放松)", 0.4, -0.3),
    ("Excited (激动)", 0.7, 0.8),
    ("Tired (疲倦)", -0.2, -0.6),
    ("Surprised (惊喜)", 0.5, 0.6),
    ("Neutral (中性)", 0.0, 0.0),
    ("Pleased (平静)", 0.3, -0.1)
]

class RecommendationTester:
    def __init__(self):
        self.session = requests.Session()
        self.user_id = "test_user"
        
    def check_service_health(self) -> bool:
        """检查推荐服务健康状态"""
        try:
            response = self.session.get(f"{RECOMMENDATION_SERVICE_URL}/health", timeout=3)
            return response.status_code == 200
        except:
            return False
    
    def send_emotion_data(self, emotion: str, intensity: float, valence: float, arousal: float) -> Dict:
        """发送情绪数据到推荐服务"""
        emotion_data = {
            'emotion': emotion,
            'intensity': intensity,
            'valence': valence,
            'arousal': arousal,
            'timestamp': time.time(),
            'user_id': self.user_id
        }
        
        try:
            response = self.session.post(
                f"{RECOMMENDATION_SERVICE_URL}/update_emotion",
                json=emotion_data,
                timeout=5
            )
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "data": result
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_random_emotion(self) -> Tuple[str, float, float, float]:
        """生成随机情绪数据"""
        emotion, base_valence, base_arousal = random.choice(EMOTIONS)
        
        # 添加一些随机性
        valence = base_valence + random.uniform(-0.1, 0.1)
        arousal = base_arousal + random.uniform(-0.1, 0.1)
        
        # 限制范围
        valence = max(-1, min(1, valence))
        arousal = max(-1, min(1, arousal))
        
        # 计算强度（确保大多数情况下能触发推荐）
        intensity = min(100, max(20, random.uniform(30, 90)))
        
        return emotion, intensity, valence, arousal
    
    def display_recommendations(self, recommendations: List[Dict]):
        """显示推荐结果"""
        if not recommendations:
            print("      ℹ️ 暂未生成新推荐")
            return
        
        print(f"      🎯 生成了 {len(recommendations)} 个视频推荐:")
        for i, video in enumerate(recommendations, 1):
            category_cn = video.get('category_cn', video.get('category', ''))
            duration_min = video.get('duration', 0) // 60
            
            print(f"         {i}. {video['title']}")
            print(f"            分类: {category_cn} | 时长: {duration_min}分钟")
            print(f"            推荐分数: {video['recommendation_score']:.2f}")
            
            if 'explanation' in video:
                print(f"            推荐理由: {video['explanation']}")
            print()
    
    def test_single_emotion(self):
        """测试发送单个情绪数据"""
        print("🧪 单次情绪数据推荐测试")
        print("=" * 50)
        
        # 检查服务状态
        if not self.check_service_health():
            print("❌ 推荐服务不可用，请先启动服务")
            print("💡 运行: python start_recommendation_only.py")
            return
        
        print("✅ 推荐服务可用")
        
        # 生成测试数据
        emotion, intensity, valence, arousal = self.generate_random_emotion()
        
        print(f"\n📊 生成的测试情绪数据:")
        print(f"   情绪: {emotion}")
        print(f"   强度: {intensity:.1f}/100")
        print(f"   Valence: {valence:.2f}")
        print(f"   Arousal: {arousal:.2f}")
        
        # 发送数据
        print(f"\n📡 发送数据到推荐服务...")
        result = self.send_emotion_data(emotion, intensity, valence, arousal)
        
        # 显示结果
        print(f"\n📋 推荐结果:")
        if result["success"]:
            print(f"   ✅ 推荐服务: 响应成功")
            
            data = result["data"]
            if data.get("recommendation_generated", False):
                recommendations = data.get("recommendations", [])
                self.display_recommendations(recommendations)
            else:
                print(f"      ℹ️ 情绪数据已更新，暂未达到推荐阈值")
                
        else:
            print(f"   ❌ 推荐服务: 请求失败 - {result['error']}")
    
    def test_emotion_sequence(self):
        """测试情绪序列推荐"""
        print("🎭 情绪序列推荐测试")
        print("=" * 40)
        
        # 定义情绪序列
        emotion_sequence = [
            ("Happy (开心)", 80, 0.7, 0.5),
            ("Excited (激动)", 90, 0.8, 0.8),
            ("Surprised (惊喜)", 70, 0.5, 0.6),
            ("Sad (悲伤)", 60, -0.6, -0.3),
            ("Angry (愤怒)", 85, -0.4, 0.7),
            ("Relaxed (放松)", 40, 0.4, -0.4),
            ("Neutral (中性)", 20, 0.0, 0.0)
        ]
        
        for i, (emotion, intensity, valence, arousal) in enumerate(emotion_sequence, 1):
            print(f"\n[{i}/{len(emotion_sequence)}] 测试情绪: {emotion} (强度: {intensity})")
            
            result = self.send_emotion_data(emotion, intensity, valence, arousal)
            
            if result["success"]:
                data = result["data"]
                if data.get("recommendation_generated", False):
                    recommendations = data.get("recommendations", [])
                    print(f"     🎯 生成了 {len(recommendations)} 个推荐")
                    # 显示前2个推荐
                    for j, video in enumerate(recommendations[:2], 1):
                        print(f"       {j}. {video['title']} (分数: {video['recommendation_score']:.2f})")
                else:
                    print(f"     ℹ️ 暂未生成新推荐")
            else:
                print(f"     ❌ 请求失败: {result['error']}")
            
            time.sleep(2)  # 等待2秒
        
        print("\n✅ 情绪序列测试完成")
    
    def test_continuous_recommendations(self, duration: int = 60, interval: float = 5.0):
        """测试连续推荐生成"""
        print(f"🔄 连续推荐测试 (时长: {duration}秒, 间隔: {interval}秒)")
        print("=" * 60)
        
        start_time = time.time()
        count = 0
        total_recommendations = 0
        
        try:
            while (time.time() - start_time) < duration:
                count += 1
                
                # 生成情绪数据
                emotion, intensity, valence, arousal = self.generate_random_emotion()
                
                print(f"\n[{count:02d}] {datetime.now().strftime('%H:%M:%S')} - {emotion} (强度: {intensity:.1f})")
                
                # 发送数据
                result = self.send_emotion_data(emotion, intensity, valence, arousal)
                
                if result["success"]:
                    data = result["data"]
                    if data.get("recommendation_generated", False):
                        recommendations = data.get("recommendations", [])
                        rec_count = len(recommendations)
                        total_recommendations += rec_count
                        print(f"     🎯 生成了 {rec_count} 个推荐")
                    else:
                        print(f"     📊 情绪已更新，暂未生成推荐")
                else:
                    print(f"     ❌ 发送失败")
                
                # 等待下一次发送
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print(f"\n\n⏹️ 测试被用户停止")
        
        print(f"\n✅ 测试完成:")
        print(f"   📊 发送次数: {count}")
        print(f"   🎯 总推荐数: {total_recommendations}")
        print(f"   📈 推荐频率: {total_recommendations/count*100:.1f}%")
    
    def get_user_recommendations(self):
        """获取用户推荐历史"""
        try:
            response = self.session.get(f"{RECOMMENDATION_SERVICE_URL}/recommendations/{self.user_id}")
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                return None
        except Exception as e:
            print(f"获取推荐历史失败: {e}")
            return None
    
    def get_user_profile(self):
        """获取用户画像"""
        try:
            response = self.session.get(f"{RECOMMENDATION_SERVICE_URL}/user_profile/{self.user_id}")
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                return None
        except Exception as e:
            print(f"获取用户画像失败: {e}")
            return None
    
    def send_feedback(self, video_index: int, feedback_type: str):
        """发送用户反馈"""
        try:
            feedback_data = {
                'user_id': self.user_id,
                'video_index': video_index,
                'feedback_type': feedback_type
            }
            response = self.session.post(f"{RECOMMENDATION_SERVICE_URL}/feedback", json=feedback_data)
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception as e:
            print(f"发送反馈失败: {e}")
            return None
    
    def get_service_status(self):
        """获取服务状态"""
        try:
            response = self.session.get(f"{RECOMMENDATION_SERVICE_URL}/status")
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception as e:
            return None
    
    def interactive_mode(self):
        """交互模式"""
        print("\n💬 进入交互测试模式 (仅推荐)")
        print("可用命令:")
        print("  send     - 发送单个随机情绪")
        print("  sequence - 运行情绪序列测试")
        print("  auto     - 开始自动连续推荐 (Ctrl+C停止)")
        print("  history  - 查看推荐历史")
        print("  profile  - 查看用户画像")
        print("  feedback - 发送反馈 (需要先有推荐)")
        print("  status   - 检查服务状态")
        print("  clear    - 清屏")
        print("  exit     - 退出")
        
        while True:
            try:
                command = input("\n请输入命令: ").strip().lower()
                
                if command == 'send':
                    self.test_single_emotion()
                    
                elif command == 'sequence':
                    self.test_emotion_sequence()
                    
                elif command == 'auto':
                    duration = input("请输入测试时长(秒，默认60): ").strip()
                    duration = int(duration) if duration.isdigit() else 60
                    
                    interval = input("请输入发送间隔(秒，默认5): ").strip()
                    interval = float(interval) if interval.replace('.', '').isdigit() else 5.0
                    
                    self.test_continuous_recommendations(duration, interval)
                    
                elif command == 'history':
                    print("📚 获取推荐历史...")
                    history = self.get_user_recommendations()
                    if history:
                        print(f"用户 {self.user_id} 的推荐历史:")
                        print(f"总推荐次数: {history['total_recommendations']}")
                        print(f"最近推荐: {len(history['recent_recommendations'])} 条")
                        
                        # 显示最近的推荐摘要
                        recent = history['recent_recommendations']
                        if recent:
                            print("\n最近推荐摘要:")
                            for i, rec in enumerate(recent[-3:], 1):  # 显示最近3条
                                emotion = rec['emotion_context']['emotion']
                                rec_count = rec['num_recommendations']
                                timestamp = rec['datetime']
                                print(f"  {i}. {timestamp} - {emotion} -> {rec_count}个推荐")
                    else:
                        print("❌ 获取推荐历史失败")
                
                elif command == 'profile':
                    print("👤 获取用户画像...")
                    profile = self.get_user_profile()
                    if profile and profile.get('status') == 'success':
                        print(f"用户 {self.user_id} 的画像信息:")
                        profile_data = profile.get('profile', {})
                        if profile_data:
                            print(json.dumps(profile_data, indent=2, ensure_ascii=False))
                        else:
                            print("  暂无画像数据")
                    else:
                        print("❌ 获取用户画像失败")
                
                elif command == 'feedback':
                    video_index = input("请输入视频序号 (1-5): ").strip()
                    feedback_type = input("请输入反馈类型 (like/skip/share): ").strip()
                    
                    if video_index.isdigit() and feedback_type in ['like', 'skip', 'share']:
                        result = self.send_feedback(int(video_index), feedback_type)
                        if result and result.get('status') == 'success':
                            print(f"✅ 反馈发送成功: {result['message']}")
                        else:
                            print(f"❌ 反馈发送失败")
                            if result:
                                print(f"   错误: {result.get('message', '未知错误')}")
                    else:
                        print("❌ 无效输入")
                
                elif command == 'status':
                    print("🔍 检查推荐服务状态...")
                    if self.check_service_health():
                        print("✅ 推荐服务: 正常")
                        
                        # 获取详细状态
                        status = self.get_service_status()
                        if status:
                            print(f"   📊 活跃用户: {status.get('active_users', 0)}")
                            print(f"   📈 总推荐次数: {status.get('total_recommendations', 0)}")
                    else:
                        print("❌ 推荐服务: 异常")
                        print("💡 请确保已运行: python start_recommendation_only.py")
                
                elif command == 'clear':
                    os.system('clear' if os.name == 'posix' else 'cls')
                    print("🎯 EEG情绪视频推荐测试工具 - 仅推荐版本")
                    print("=" * 50)
                
                elif command == 'exit':
                    break
                    
                else:
                    print("❓ 未知命令，请重新输入")
                    
            except KeyboardInterrupt:
                break
            except EOFError:
                break

def main():
    """主函数"""
    print("=" * 60)
    print("🎯 EEG情绪视频推荐测试工具 - 仅推荐版本")
    print("=" * 60)
    print("功能:")
    print("  📡 发送模拟情绪数据到推荐服务")
    print("  🎯 测试视频推荐生成")
    print("  📊 验证用户学习功能")
    print("  🚫 不包含音频测试")
    print("=" * 60)
    
    tester = RecommendationTester()
    
    # 检查服务状态
    print("🔍 检查推荐服务连接状态...")
    service_available = tester.check_service_health()
    
    print(f"推荐服务 (8081): {'✅ 可用' if service_available else '❌ 不可用'}")
    
    if not service_available:
        print("\n❌ 推荐服务不可用")
        print("💡 请先运行 'python start_recommendation_only.py' 启动服务")
        return
    
    # 选择测试模式
    print("\n请选择测试模式:")
    print("1. 单次测试 - 发送一个随机情绪并查看推荐")
    print("2. 序列测试 - 按顺序测试多种情绪的推荐")
    print("3. 连续测试 - 自动连续发送情绪并生成推荐")
    print("4. 交互模式 - 手动控制测试和查看数据")
    
    try:
        choice = input("\n请输入选择 (1-4): ").strip()
        
        if choice == '1':
            tester.test_single_emotion()
            
        elif choice == '2':
            tester.test_emotion_sequence()
            
        elif choice == '3':
            tester.test_continuous_recommendations()
            
        elif choice == '4':
            tester.interactive_mode()
            
        else:
            print("❌ 无效选择，启动交互模式")
            tester.interactive_mode()
            
    except KeyboardInterrupt:
        print("\n\n👋 测试结束")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")

if __name__ == "__main__":
    import os
    main() 