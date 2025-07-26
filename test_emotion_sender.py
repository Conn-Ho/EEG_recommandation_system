#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
EEG情绪数据发送测试工具
Emotion Data Sender Test Tool

用于测试和模拟向推荐服务发送情绪数据，无需真实EEG设备
"""

import requests
import time
import random
import json
from datetime import datetime
from typing import Dict, List, Tuple

# 服务配置
RECOMMENDATION_SERVICE_URL = 'http://localhost:8081'
AUDIO_SERVICE_URL = 'http://localhost:8080'

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

class EmotionDataSender:
    def __init__(self):
        self.session = requests.Session()
        self.user_id = "test_user"
        
    def check_service_health(self, service_url: str) -> bool:
        """检查服务健康状态"""
        try:
            response = self.session.get(f"{service_url}/health", timeout=3)
            return response.status_code == 200
        except:
            return False
    
    def send_emotion_data(self, emotion: str, intensity: float, valence: float, arousal: float, target_service: str = "both") -> Dict:
        """发送情绪数据到指定服务"""
        emotion_data = {
            'emotion': emotion,
            'intensity': intensity,
            'valence': valence,
            'arousal': arousal,
            'timestamp': time.time(),
            'user_id': self.user_id
        }
        
        results = {}
        
        if target_service in ["both", "recommendation"]:
            # 发送到推荐服务
            try:
                response = self.session.post(
                    f"{RECOMMENDATION_SERVICE_URL}/update_emotion",
                    json=emotion_data,
                    timeout=5
                )
                if response.status_code == 200:
                    result = response.json()
                    results["recommendation_service"] = {
                        "success": True,
                        "data": result
                    }
                else:
                    results["recommendation_service"] = {
                        "success": False,
                        "error": f"HTTP {response.status_code}"
                    }
            except Exception as e:
                results["recommendation_service"] = {
                    "success": False,
                    "error": str(e)
                }
        
        if target_service in ["both", "audio"]:
            # 发送到音频服务
            try:
                response = self.session.post(
                    f"{AUDIO_SERVICE_URL}/update_emotion",
                    json=emotion_data,
                    timeout=5
                )
                if response.status_code == 200:
                    results["audio_service"] = {
                        "success": True,
                        "data": "音频服务响应成功"
                    }
                else:
                    results["audio_service"] = {
                        "success": False,
                        "error": f"HTTP {response.status_code}"
                    }
            except Exception as e:
                results["audio_service"] = {
                    "success": False,
                    "error": str(e)
                }
        
        return results
    
    def generate_random_emotion(self) -> Tuple[str, float, float, float]:
        """生成随机情绪数据"""
        emotion, base_valence, base_arousal = random.choice(EMOTIONS)
        
        # 添加一些随机性
        valence = base_valence + random.uniform(-0.1, 0.1)
        arousal = base_arousal + random.uniform(-0.1, 0.1)
        
        # 限制范围
        valence = max(-1, min(1, valence))
        arousal = max(-1, min(1, arousal))
        
        # 计算强度
        intensity = min(100, max(10, random.uniform(30, 90)))
        
        return emotion, intensity, valence, arousal
    
    def test_single_emotion(self):
        """测试发送单个情绪数据"""
        print("🧪 单次情绪数据发送测试")
        print("=" * 50)
        
        # 检查服务状态
        rec_available = self.check_service_health(RECOMMENDATION_SERVICE_URL)
        audio_available = self.check_service_health(AUDIO_SERVICE_URL)
        
        print(f"推荐服务 (8081): {'✅ 可用' if rec_available else '❌ 不可用'}")
        print(f"音频服务 (8080): {'✅ 可用' if audio_available else '❌ 不可用'}")
        
        if not rec_available and not audio_available:
            print("❌ 没有可用的服务，请先启动服务")
            return
        
        # 生成测试数据
        emotion, intensity, valence, arousal = self.generate_random_emotion()
        
        print(f"\n📊 生成的测试情绪数据:")
        print(f"   情绪: {emotion}")
        print(f"   强度: {intensity:.1f}/100")
        print(f"   Valence: {valence:.2f}")
        print(f"   Arousal: {arousal:.2f}")
        
        # 发送数据
        print(f"\n📡 发送数据...")
        results = self.send_emotion_data(emotion, intensity, valence, arousal)
        
        # 显示结果
        print(f"\n📋 发送结果:")
        for service, result in results.items():
            service_name = "推荐服务" if "recommendation" in service else "音频服务"
            if result["success"]:
                print(f"   ✅ {service_name}: 发送成功")
                if "recommendation" in service and "recommendations" in result["data"]:
                    recs = result["data"]["recommendations"]
                    if recs:
                        print(f"      🎯 生成了 {len(recs)} 个视频推荐")
                        for i, video in enumerate(recs[:3], 1):  # 只显示前3个
                            print(f"         {i}. {video['title']} (分数: {video['recommendation_score']:.2f})")
                    else:
                        print(f"      ℹ️ 暂未生成新推荐")
            else:
                print(f"   ❌ {service_name}: 发送失败 - {result['error']}")
    
    def test_continuous_emotions(self, duration: int = 60, interval: float = 5.0):
        """测试连续发送情绪数据"""
        print(f"🔄 连续情绪数据发送测试 (时长: {duration}秒, 间隔: {interval}秒)")
        print("=" * 60)
        
        start_time = time.time()
        count = 0
        
        try:
            while (time.time() - start_time) < duration:
                count += 1
                
                # 生成情绪数据
                emotion, intensity, valence, arousal = self.generate_random_emotion()
                
                print(f"\n[{count:02d}] {datetime.now().strftime('%H:%M:%S')} - {emotion} (强度: {intensity:.1f})")
                
                # 发送数据
                results = self.send_emotion_data(emotion, intensity, valence, arousal)
                
                # 简化结果显示
                success_services = []
                for service, result in results.items():
                    if result["success"]:
                        service_name = "推荐" if "recommendation" in service else "音频"
                        success_services.append(service_name)
                
                if success_services:
                    print(f"     📡 发送成功: {', '.join(success_services)}")
                else:
                    print(f"     ❌ 发送失败")
                
                # 等待下一次发送
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print(f"\n\n⏹️ 测试被用户停止")
        
        print(f"\n✅ 测试完成，共发送 {count} 次情绪数据")
    
    def test_specific_emotion_sequence(self):
        """测试特定情绪序列"""
        print("🎭 特定情绪序列测试")
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
            print(f"\n[{i}/{len(emotion_sequence)}] 测试情绪: {emotion}")
            
            results = self.send_emotion_data(emotion, intensity, valence, arousal)
            
            success_count = sum(1 for r in results.values() if r["success"])
            total_count = len(results)
            
            print(f"     📊 结果: {success_count}/{total_count} 服务响应成功")
            
            # 如果有推荐生成，显示推荐信息
            if "recommendation_service" in results and results["recommendation_service"]["success"]:
                rec_data = results["recommendation_service"]["data"]
                if rec_data.get("recommendation_generated", False):
                    recs = rec_data.get("recommendations", [])
                    print(f"     🎯 生成了 {len(recs)} 个推荐")
            
            time.sleep(2)  # 等待2秒
        
        print("\n✅ 情绪序列测试完成")
    
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
    
    def interactive_mode(self):
        """交互模式"""
        print("\n💬 进入交互测试模式")
        print("可用命令:")
        print("  send     - 发送单个随机情绪")
        print("  sequence - 运行情绪序列测试")
        print("  auto     - 开始自动连续发送 (Ctrl+C停止)")
        print("  history  - 查看推荐历史")
        print("  profile  - 查看用户画像")
        print("  feedback - 发送反馈 (需要先有推荐)")
        print("  status   - 检查服务状态")
        print("  exit     - 退出")
        
        while True:
            try:
                command = input("\n请输入命令: ").strip().lower()
                
                if command == 'send':
                    self.test_single_emotion()
                    
                elif command == 'sequence':
                    self.test_specific_emotion_sequence()
                    
                elif command == 'auto':
                    duration = input("请输入测试时长(秒，默认60): ").strip()
                    duration = int(duration) if duration.isdigit() else 60
                    
                    interval = input("请输入发送间隔(秒，默认5): ").strip()
                    interval = float(interval) if interval.replace('.', '').isdigit() else 5.0
                    
                    self.test_continuous_emotions(duration, interval)
                    
                elif command == 'history':
                    print("📚 获取推荐历史...")
                    history = self.get_user_recommendations()
                    if history:
                        print(f"用户 {self.user_id} 的推荐历史:")
                        print(f"总推荐次数: {history['total_recommendations']}")
                        print(f"最近推荐: {len(history['recent_recommendations'])} 条")
                    else:
                        print("❌ 获取推荐历史失败")
                
                elif command == 'profile':
                    print("👤 获取用户画像...")
                    profile = self.get_user_profile()
                    if profile:
                        print(f"用户 {self.user_id} 的画像信息:")
                        print(json.dumps(profile, indent=2, ensure_ascii=False))
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
                    else:
                        print("❌ 无效输入")
                
                elif command == 'status':
                    print("🔍 检查服务状态...")
                    rec_ok = self.check_service_health(RECOMMENDATION_SERVICE_URL)
                    audio_ok = self.check_service_health(AUDIO_SERVICE_URL)
                    print(f"推荐服务: {'✅ 正常' if rec_ok else '❌ 异常'}")
                    print(f"音频服务: {'✅ 正常' if audio_ok else '❌ 异常'}")
                
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
    print("🧪 EEG情绪数据发送测试工具")
    print("=" * 60)
    print("功能:")
    print("  📡 模拟发送情绪数据到推荐服务")
    print("  🎯 测试推荐系统响应")
    print("  📊 验证系统集成")
    print("=" * 60)
    
    sender = EmotionDataSender()
    
    # 检查服务状态
    print("🔍 检查服务连接状态...")
    rec_available = sender.check_service_health(RECOMMENDATION_SERVICE_URL)
    audio_available = sender.check_service_health(AUDIO_SERVICE_URL)
    
    print(f"推荐服务 (8081): {'✅ 可用' if rec_available else '❌ 不可用'}")
    print(f"音频服务 (8080): {'✅ 可用' if audio_available else '❌ 不可用'}")
    
    if not rec_available and not audio_available:
        print("\n❌ 没有检测到可用的服务")
        print("💡 请先运行 'python start_integrated_system.py' 启动服务")
        return
    
    # 选择测试模式
    print("\n请选择测试模式:")
    print("1. 单次测试 - 发送一个随机情绪")
    print("2. 序列测试 - 按顺序测试多种情绪")
    print("3. 连续测试 - 自动连续发送情绪数据")
    print("4. 交互模式 - 手动控制测试")
    
    try:
        choice = input("\n请输入选择 (1-4): ").strip()
        
        if choice == '1':
            sender.test_single_emotion()
            
        elif choice == '2':
            sender.test_specific_emotion_sequence()
            
        elif choice == '3':
            sender.test_continuous_emotions()
            
        elif choice == '4':
            sender.interactive_mode()
            
        else:
            print("❌ 无效选择，启动交互模式")
            sender.interactive_mode()
            
    except KeyboardInterrupt:
        print("\n\n👋 测试结束")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")

if __name__ == "__main__":
    main() 