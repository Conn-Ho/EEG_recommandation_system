#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
EEG情绪识别与推荐系统 - 完整服务启动管理器
Complete Service Startup Manager for EEG Emotion Recognition and Recommendation System

管理以下服务：
1. 音频生成服务 (端口 8080) - 来自 EEG/audio_service.py
2. 视频推荐服务 (端口 8081) - 来自 recommandation/recommendation_service.py  
3. EEG脑波数据处理服务 - 来自 EEG/brain_processor_with_recommendation.py
"""

import subprocess
import time
import signal
import sys
import threading
import os
import requests
from datetime import datetime

class IntegratedServiceManager:
    def __init__(self):
        self.audio_process = None
        self.recommendation_process = None
        self.brain_process = None
        self.running = True
        self.services_status = {
            "audio_service": {"process": None, "port": 8080, "name": "音频生成服务"},
            "recommendation_service": {"process": None, "port": 8081, "name": "视频推荐服务"},
            "brain_processor": {"process": None, "port": None, "name": "EEG脑波处理服务"}
        }
        
    def check_service_health(self, port: int, timeout: int = 2) -> bool:
        """检查服务健康状态"""
        try:
            response = requests.get(f"http://localhost:{port}/health", timeout=timeout)
            return response.status_code == 200
        except:
            return False
    
    def wait_for_service(self, port: int, name: str, max_wait: int = 30) -> bool:
        """等待服务启动"""
        print(f"等待 {name} 启动...")
        for i in range(max_wait):
            if self.check_service_health(port):
                print(f"✅ {name} 已启动并就绪")
                return True
            time.sleep(1)
            if i % 5 == 0 and i > 0:
                print(f"⏳ 仍在等待 {name} 启动... ({i}/{max_wait}秒)")
        
        print(f"❌ {name} 启动超时")
        return False
    
    def start_audio_service(self):
        """启动音频生成服务"""
        print("🎵 启动音频生成服务...")
        try:
            audio_script = os.path.join("EEG", "audio_service.py")
            if not os.path.exists(audio_script):
                print(f"❌ 找不到音频服务脚本: {audio_script}")
                return False
                
            self.audio_process = subprocess.Popen(
                [sys.executable, audio_script],
                cwd=os.getcwd()
            )
            self.services_status["audio_service"]["process"] = self.audio_process
            print(f"✅ 音频生成服务已启动 (PID: {self.audio_process.pid})")
            
            # 等待服务就绪
            return self.wait_for_service(8080, "音频生成服务")
            
        except Exception as e:
            print(f"❌ 启动音频服务失败: {e}")
            return False
    
    def start_recommendation_service(self):
        """启动视频推荐服务"""
        print("🎯 启动视频推荐服务...")
        try:
            rec_script = os.path.join("recommandation", "recommendation_service.py")
            if not os.path.exists(rec_script):
                print(f"❌ 找不到推荐服务脚本: {rec_script}")
                return False
                
            self.recommendation_process = subprocess.Popen(
                [sys.executable, rec_script],
                cwd=os.getcwd()
            )
            self.services_status["recommendation_service"]["process"] = self.recommendation_process
            print(f"✅ 视频推荐服务已启动 (PID: {self.recommendation_process.pid})")
            
            # 等待服务就绪
            return self.wait_for_service(8081, "视频推荐服务")
            
        except Exception as e:
            print(f"❌ 启动推荐服务失败: {e}")
            return False
    
    def start_brain_processor(self):
        """启动EEG脑波数据处理服务"""
        print("🧠 启动EEG脑波数据处理服务...")
        try:
            brain_script = os.path.join("EEG", "brain_processor_with_recommendation.py")
            if not os.path.exists(brain_script):
                print(f"❌ 找不到EEG处理脚本: {brain_script}")
                return False
                
            self.brain_process = subprocess.Popen(
                [sys.executable, brain_script],
                cwd=os.getcwd()
            )
            self.services_status["brain_processor"]["process"] = self.brain_process
            print(f"✅ EEG脑波数据处理服务已启动 (PID: {self.brain_process.pid})")
            
            # EEG服务没有HTTP端点，稍等一下让它初始化
            time.sleep(3)
            return True
            
        except Exception as e:
            print(f"❌ 启动EEG处理服务失败: {e}")
            return False
    
    def stop_all_services(self):
        """停止所有服务"""
        print("\n🛑 正在停止所有服务...")
        self.running = False
        
        for service_name, service_info in self.services_status.items():
            process = service_info["process"]
            if process and process.poll() is None:
                try:
                    print(f"🔸 停止 {service_info['name']}...")
                    process.terminate()
                    
                    # 等待进程优雅退出
                    try:
                        process.wait(timeout=5)
                        print(f"✅ {service_info['name']} 已停止")
                    except subprocess.TimeoutExpired:
                        print(f"⚡ 强制终止 {service_info['name']}...")
                        process.kill()
                        process.wait()
                        
                except Exception as e:
                    print(f"❌ 停止 {service_info['name']} 时出错: {e}")
        
        print("✅ 所有服务已停止")
    
    def monitor_services(self):
        """监控服务状态"""
        while self.running:
            time.sleep(10)  # 每10秒检查一次
            
            if not self.running:
                break
                
            # 检查进程状态
            for service_name, service_info in self.services_status.items():
                process = service_info["process"]
                if process and process.poll() is not None:
                    print(f"⚠️ {service_info['name']} 进程已退出")
                    
                # 检查HTTP服务健康状态
                if service_info["port"]:
                    if not self.check_service_health(service_info["port"]):
                        print(f"⚠️ {service_info['name']} HTTP服务不响应")
    
    def display_status(self):
        """显示系统状态"""
        print(f"\n{'='*60}")
        print(f"🔍 系统服务状态 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        for service_name, service_info in self.services_status.items():
            process = service_info["process"]
            name = service_info["name"]
            port = service_info["port"]
            
            if process:
                if process.poll() is None:
                    status = "🟢 运行中"
                    if port:
                        if self.check_service_health(port):
                            status += f" (端口 {port} 可访问)"
                        else:
                            status += f" (端口 {port} 不可访问)"
                else:
                    status = "🔴 已停止"
            else:
                status = "⚫ 未启动"
            
            print(f"{name:<20} {status}")
        
        print(f"{'='*60}")
        
        # 显示API端点
        print("📡 可用的API端点:")
        if self.check_service_health(8080):
            print("  🎵 音频服务: http://localhost:8080")
            print("     - GET  /health - 健康检查")
            print("     - POST /update_emotion - 接收情绪数据")
            print("     - GET  /status - 获取音频状态")
        
        if self.check_service_health(8081):
            print("  🎯 推荐服务: http://localhost:8081")
            print("     - GET  /health - 健康检查")
            print("     - POST /update_emotion - 接收情绪数据")
            print("     - GET  /status - 获取服务状态")
            print("     - POST /feedback - 记录用户反馈")
            print("     - GET  /recommendations/<user_id> - 获取推荐历史")
            print("     - GET  /user_profile/<user_id> - 获取用户画像")
        
        print(f"{'='*60}\n")
    
    def interactive_mode(self):
        """交互模式"""
        print("\n💬 进入交互模式")
        print("可用命令:")
        print("  status  - 显示服务状态")
        print("  test    - 测试服务连接")
        print("  logs    - 显示服务日志状态")
        print("  stop    - 停止所有服务")
        print("  help    - 显示帮助")
        print("  exit    - 退出系统")
        
        while self.running:
            try:
                command = input("\n请输入命令: ").strip().lower()
                
                if command == 'status':
                    self.display_status()
                    
                elif command == 'test':
                    print("🔧 测试服务连接...")
                    if self.check_service_health(8080):
                        print("✅ 音频服务连接正常")
                    else:
                        print("❌ 音频服务连接失败")
                        
                    if self.check_service_health(8081):
                        print("✅ 推荐服务连接正常")
                    else:
                        print("❌ 推荐服务连接失败")
                
                elif command == 'logs':
                    print("📋 服务进程状态:")
                    for service_name, service_info in self.services_status.items():
                        process = service_info["process"]
                        if process:
                            status = "运行中" if process.poll() is None else "已停止"
                            print(f"  {service_info['name']}: PID {process.pid} - {status}")
                        else:
                            print(f"  {service_info['name']}: 未启动")
                
                elif command == 'stop' or command == 'exit':
                    break
                    
                elif command == 'help':
                    print("📖 命令说明:")
                    print("  status - 显示所有服务的运行状态和API端点")
                    print("  test   - 测试各服务的HTTP连接是否正常")
                    print("  logs   - 显示各服务进程的基本信息")
                    print("  stop   - 停止所有服务并退出")
                    print("  exit   - 停止所有服务并退出")
                    
                else:
                    print("❓ 未知命令，输入 'help' 查看可用命令")
                    
            except KeyboardInterrupt:
                break
            except EOFError:
                break
    
    def start_all_services(self):
        """启动所有服务"""
        print("🚀 启动EEG情绪识别与推荐系统完整服务...")
        print(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        success_count = 0
        
        # 1. 启动音频服务
        if self.start_audio_service():
            success_count += 1
        
        # 2. 启动推荐服务
        if self.start_recommendation_service():
            success_count += 1
        
        # 3. 启动EEG脑波处理服务
        if self.start_brain_processor():
            success_count += 1
        
        print(f"\n📊 启动结果: {success_count}/3 个服务成功启动")
        
        if success_count > 0:
            print("✅ 系统启动成功！")
            self.display_status()
            
            # 启动监控线程
            monitor_thread = threading.Thread(target=self.monitor_services, daemon=True)
            monitor_thread.start()
            
            return True
        else:
            print("❌ 系统启动失败")
            return False

def signal_handler(signum, frame):
    """信号处理器"""
    print("\n\n收到停止信号...")
    global service_manager
    if service_manager:
        service_manager.stop_all_services()
    sys.exit(0)

def main():
    """主函数"""
    global service_manager
    
    print("=" * 80)
    print("🧠 EEG情绪识别与推荐系统 - 完整服务启动器")
    print("=" * 80)
    print("系统功能:")
    print("  🎵 实时EEG情绪分析 + 音乐生成")
    print("  🎯 基于情绪的个性化视频推荐")
    print("  📡 微服务架构，支持独立扩展")
    print("=" * 80)
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    service_manager = IntegratedServiceManager()
    
    try:
        # 启动所有服务
        if service_manager.start_all_services():
            # 进入交互模式
            service_manager.interactive_mode()
        
    except Exception as e:
        print(f"❌ 系统运行时发生错误: {e}")
    
    finally:
        # 确保清理所有服务
        service_manager.stop_all_services()

if __name__ == "__main__":
    main() 