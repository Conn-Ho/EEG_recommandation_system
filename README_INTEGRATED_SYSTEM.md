# 🧠 EEG情绪识别与推荐系统 - 完整集成方案

基于脑机接口(EEG)情绪识别技术的智能视频推荐系统，实时分析用户情绪状态并提供个性化的视频内容推荐，同时支持音乐生成功能。

## 🏗️ 系统架构

### 微服务架构图

```
┌─────────────────┐    EEG Data    ┌─────────────────────┐
│                │ ──────────────→ │                     │
│  EEG脑波处理服务  │                 │   增强版数据处理器   │
│                │                 │                     │
└─────────────────┘                 └─────────────────────┘
                                             │
                                    HTTP API │
                                    (并行发送) │
                            ┌─────────────────┼─────────────────┐
                            ▼                 ▼                 ▼
                   ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
                   │   音频生成服务   │ │   视频推荐服务   │ │   其他扩展服务   │
                   │   (端口 8080)   │ │   (端口 8081)   │ │   (待开发)     │
                   │                │ │                │ │                │
                   │ • 实时音乐生成  │ │ • 情绪分析推荐  │ │ • 图文推荐     │
                   │ • Google Lyria │ │ • 用户学习优化  │ │ • 直播推荐     │
                   │ • 音频流播放   │ │ • 反馈收集     │ │                │
                   └─────────────────┘ └─────────────────┘ └─────────────────┘
```

### 核心组件

1. **EEG脑波数据处理服务** (`EEG/brain_processor_with_recommendation.py`)
   - 连接Emotiv EEG设备
   - 实时情绪识别 (9种情绪状态)
   - 并行数据分发到多个服务

2. **视频推荐服务** (`recommandation/recommendation_service.py`)
   - 基于情绪的视频推荐算法
   - 用户行为学习与个性化
   - RESTful API接口

3. **音频生成服务** (`EEG/audio_service.py`)
   - Google Lyria音乐生成模型
   - 实时音频流播放
   - 情绪驱动的音乐调节

4. **服务启动管理器** (`start_integrated_system.py`)
   - 一键启动所有服务
   - 服务状态监控
   - 交互式管理界面

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆仓库
cd EEG_recommandation_system

# 安装EEG模块依赖
cd EEG
pip install -r requirements.txt

# 安装推荐模块依赖
cd ../recommandation
pip install -r requirements.txt

# 返回根目录
cd ..
```

### 2. 配置API密钥

#### EEG设备配置
在 `EEG/brain_processor_with_recommendation.py` 中配置Emotiv凭证：
```python
YOUR_APP_CLIENT_ID = '你的Emotiv Client ID'
YOUR_APP_CLIENT_SECRET = '你的Emotiv Client Secret'
```

#### 音频服务配置 (可选)
在 `EEG/audio_service.py` 中配置Google API：
```python
GOOGLE_API_KEY = '你的Google API Key'
```

### 3. 启动完整系统

```bash
# 一键启动所有服务
python start_integrated_system.py
```

系统将按顺序启动：
1. 🎵 音频生成服务 (端口 8080)
2. 🎯 视频推荐服务 (端口 8081)  
3. 🧠 EEG脑波数据处理服务

### 4. 验证系统运行

启动后，系统会显示服务状态：
```
🔍 系统服务状态 - 2024-01-15 14:30:22
============================================================
音频生成服务          🟢 运行中 (端口 8080 可访问)
视频推荐服务          🟢 运行中 (端口 8081 可访问)
EEG脑波处理服务       🟢 运行中
============================================================
```

## 🧪 测试系统 (无需EEG设备)

如果没有EEG设备，可以使用测试工具模拟情绪数据：

```bash
# 运行情绪数据测试工具
python test_emotion_sender.py
```

测试工具支持：
- 🧪 单次情绪测试
- 🎭 情绪序列测试
- 🔄 连续自动测试
- 💬 交互式测试模式

## 📡 API接口说明

### 视频推荐服务 API (端口 8081)

#### 核心接口

```bash
# 健康检查
GET /health

# 接收情绪数据并生成推荐
POST /update_emotion
Content-Type: application/json
{
  "emotion": "Happy (开心)",
  "intensity": 75.5,
  "valence": 0.6,
  "arousal": 0.4,
  "timestamp": 1640995200,
  "user_id": "user123"
}

# 获取服务状态
GET /status

# 获取用户推荐历史
GET /recommendations/<user_id>

# 获取用户画像
GET /user_profile/<user_id>

# 记录用户反馈
POST /feedback
Content-Type: application/json
{
  "user_id": "user123",
  "video_index": 1,
  "feedback_type": "like"
}
```

### 音频服务 API (端口 8080)

```bash
# 健康检查
GET /health

# 接收情绪数据
POST /update_emotion

# 获取音频状态
GET /audio_status

# 重启音频生成
POST /restart_audio
```

## 🎯 情绪推荐策略

### 情绪映射表

| 情绪状态 | 推荐策略 | 避免内容 | 强度阈值 |
|---------|---------|---------|---------|
| 开心 (Happy) | 搞笑幽默、音乐舞蹈、萌宠动物 | - | >40 |
| 悲伤 (Sad) | 治愈温暖、萌宠动物、音乐 | 新闻资讯 | >40 |
| 愤怒 (Angry) | 放松冥想、治愈内容、旅行风景 | 新闻、游戏 | >50 |
| 疲倦 (Tired) | 轻松娱乐、放松冥想 | 知识科普、新闻 | >30 |
| 放松 (Relaxed) | 旅行风景、艺术创作、音乐 | - | >20 |
| 惊喜 (Surprised) | 科技数码、艺术创作、知识科普 | - | >40 |
| 厌恶 (Disgust) | 治愈内容、萌宠动物 | 新闻资讯 | >45 |
| 平静 (Pleased) | 艺术创作、旅行风景、生活日常 | - | >20 |
| 中性 (Neutral) | 多样化内容、发现新内容 | - | >30 |

### 个性化学习

- **用户画像构建**：基于历史行为的偏好学习
- **情绪模式分析**：识别个人情绪-内容偏好模式
- **适应性优化**：动态调整推荐策略权重
- **反馈集成**：基于用户反馈持续优化

## 🔄 使用流程

### 完整EEG模式

1. **设备准备**
   ```bash
   # 启动Emotiv Cortex软件
   # 连接并校准EEG设备
   # 确保设备正常工作
   ```

2. **启动系统**
   ```bash
   python start_integrated_system.py
   ```

3. **实时运行**
   - EEG设备采集脑波数据
   - 系统每5秒分析情绪状态
   - 自动生成音乐和视频推荐
   - 用户可以通过反馈优化推荐

### 测试模式

1. **启动服务**
   ```bash
   python start_integrated_system.py
   ```

2. **运行测试**
   ```bash
   # 新终端窗口
   python test_emotion_sender.py
   ```

3. **查看结果**
   - 在推荐服务中查看生成的推荐
   - 通过API获取用户画像和历史

## 📊 监控和管理

### 服务管理命令

在系统启动后的交互模式中：

```
可用命令:
  status  - 显示服务状态
  test    - 测试服务连接
  logs    - 显示服务日志状态
  stop    - 停止所有服务
  help    - 显示帮助
  exit    - 退出系统
```

### 实时监控

系统提供实时监控功能：
- 🔍 每10秒检查服务进程状态
- 📡 每60秒验证HTTP服务健康状态
- ⚠️ 自动检测并报告服务异常

### 日志查看

各服务的日志输出：
- **EEG处理服务**：情绪识别结果、数据发送状态
- **推荐服务**：推荐生成日志、用户反馈记录
- **音频服务**：音乐生成状态、播放信息

## 🛠️ 故障排除

### 常见问题

1. **EEG设备连接失败**
   ```
   问题：Cannot connect to Emotiv Cortex
   解决：确保Cortex软件已启动，设备已连接并授权
   ```

2. **推荐服务启动失败**
   ```
   问题：ModuleNotFoundError: No module named 'flask'
   解决：pip install flask flask-cors
   ```

3. **音频服务异常**
   ```
   问题：Google API Key错误
   解决：检查API密钥配置，确保网络连接正常
   ```

4. **服务间通信失败**
   ```
   问题：Connection refused
   解决：检查防火墙设置，确认端口8080和8081可用
   ```

### 调试模式

启用详细日志：
```python
# 在相应服务文件中修改
logging.basicConfig(level=logging.DEBUG)
```

### 性能优化

1. **网络优化**
   - 调整HTTP请求超时设置
   - 优化数据发送频率

2. **资源管理**
   - 限制历史记录长度
   - 定期清理过期数据

3. **算法优化**
   - 缓存推荐结果
   - 预计算用户偏好

## 🔮 扩展功能

### 支持的扩展

1. **新的推荐内容类型**
   - 图文内容推荐
   - 直播内容推荐
   - 音频内容推荐

2. **高级情绪分析**
   - 多用户群体情绪分析
   - 环境因子集成
   - 生理信号融合

3. **智能化升级**
   - 深度学习模型集成
   - 强化学习优化
   - 协同过滤算法

### 开发新服务

参考现有服务架构，新服务需要：

1. **实现HTTP API接口**
   ```python
   @app.route('/update_emotion', methods=['POST'])
   def update_emotion():
       # 处理情绪数据
       pass
   ```

2. **注册到启动管理器**
   ```python
   # 在start_integrated_system.py中添加新服务
   ```

3. **更新数据处理器**
   ```python
   # 在brain_processor_with_recommendation.py中添加新的服务URL
   ```

## 📝 许可证

本项目遵循 MIT 许可证。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进系统！

## 📞 联系方式

如有问题或建议，请联系开发团队。

---

**🧠 让AI真正理解你的情绪，提供最贴心的内容推荐！** 