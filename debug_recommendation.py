#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
推荐系统调试工具
Debug Tool for Recommendation System

用于快速测试和调试推荐生成功能
"""

import requests
import time
import json

def test_recommendation_generation():
    """测试推荐生成"""
    url = "http://localhost:8081/update_emotion"
    
    # 测试用例：确保能触发推荐的情绪数据
    test_cases = [
        {
            "name": "高强度开心",
            "data": {
                "emotion": "Happy (开心)",
                "intensity": 80,  # 高强度
                "valence": 0.7,
                "arousal": 0.5,
                "timestamp": time.time(),
                "user_id": "debug_user"
            }
        },
        {
            "name": "中等强度悲伤", 
            "data": {
                "emotion": "Sad (悲伤)",
                "intensity": 50,  # 中等强度
                "valence": -0.6,
                "arousal": -0.3,
                "timestamp": time.time(),
                "user_id": "debug_user"
            }
        },
        {
            "name": "低强度但变化情绪",
            "data": {
                "emotion": "Angry (愤怒)",
                "intensity": 30,  # 低强度
                "valence": -0.4,
                "arousal": 0.7,
                "timestamp": time.time(),
                "user_id": "debug_user"
            }
        }
    ]
    
    print("🧪 开始推荐生成调试测试")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n[测试 {i}] {test_case['name']}")
        print(f"情绪数据: {test_case['data']['emotion']} | 强度: {test_case['data']['intensity']}")
        
        try:
            response = requests.post(url, json=test_case['data'], timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 请求成功")
                print(f"   情绪接收: {result.get('emotion_received', False)}")
                print(f"   推荐生成: {result.get('recommendation_generated', False)}")
                
                if result.get('recommendation_generated', False):
                    recommendations = result.get('recommendations', [])
                    print(f"   推荐数量: {len(recommendations)}")
                    
                    # 显示前2个推荐
                    for j, video in enumerate(recommendations[:2], 1):
                        print(f"     {j}. {video['title']} (分数: {video['recommendation_score']:.2f})")
                else:
                    print(f"   ❌ 未生成推荐")
                    
            else:
                print(f"❌ 请求失败: HTTP {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ 连接失败: 请确保推荐服务正在运行 (python start_recommendation_only.py)")
            return
        except Exception as e:
            print(f"❌ 请求异常: {e}")
        
        # 等待一段时间避免时间阈值限制
        if i < len(test_cases):
            time.sleep(4)
    
    print(f"\n✅ 调试测试完成")

def check_service_status():
    """检查服务状态"""
    try:
        # 健康检查
        health_response = requests.get("http://localhost:8081/health", timeout=3)
        if health_response.status_code == 200:
            print("✅ 推荐服务健康状态正常")
        else:
            print(f"⚠️ 推荐服务健康检查异常: {health_response.status_code}")
            return False
            
        # 服务状态
        status_response = requests.get("http://localhost:8081/status", timeout=3)
        if status_response.status_code == 200:
            status_data = status_response.json()
            print(f"📊 服务状态:")
            print(f"   活跃用户: {status_data.get('active_users', 0)}")
            print(f"   总推荐次数: {status_data.get('total_recommendations', 0)}")
            return True
        else:
            print(f"⚠️ 获取服务状态失败: {status_response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到推荐服务")
        print("💡 请先运行: python start_recommendation_only.py")
        return False
    except Exception as e:
        print(f"❌ 检查服务状态时出错: {e}")
        return False

def main():
    """主函数"""
    print("🔧 推荐系统调试工具")
    print("=" * 30)
    
    # 检查服务状态
    if not check_service_status():
        return
    
    print("\n" + "=" * 30)
    
    # 运行推荐测试
    test_recommendation_generation()
    
    print("\n💡 提示:")
    print("- 如果仍无推荐生成，请检查推荐服务日志")
    print("- 推荐阈值已降低：强度>25 或首次>15")
    print("- 可以查看服务终端的详细日志信息")

if __name__ == "__main__":
    main() 