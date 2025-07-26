# EEG音乐生成系统 - 服务拆分版本

这是EEG脑波情绪识别和实时音乐生成系统的微服务版本。系统被拆分为两个独立的服务，通过HTTP API进行通信。

## 📁 文件结构

```
EEG/
├── brain_processor.py      # 脑波数据处理主服务
├── audio_service.py        # 音频生成服务
├── start_services.py       # 服务启动管理器
├── main.py                 # 原始单体应用（保留备用）
├── cortex.py              # Emotiv Cortex SDK
├── requirements.txt        # 依赖包列表
└── README_SERVICES.md     # 本说明文件
```

## 🏗️ 系统架构

```
┌─────────────────┐    HTTP API    ┌─────────────────┐
│  脑波数据处理服务  │ ──────────────→ │   音频生成服务    │
│                │                │                │
│ • EEG数据采集   │                │ • 音乐生成控制   │
│ • 情绪识别      │                │ • 实时音频播放   │
│ • 数据发送      │                │ • HTTP API接收  │
└─────────────────┘                └─────────────────┘
```

## ⚙️ 服务详情

### 1. 脑波数据处理服务 (`brain_processor.py`)

**功能：**
- 连接Emotiv EEG设备
- 实时分析脑波数据
- 计算情绪状态和强度
- 通过HTTP API发送情绪数据给音频服务

**端口：** 无（作为客户端）

### 2. 音频生成服务 (`audio_service.py`)

**功能：**
- 连接Google Lyria音乐生成模型
- 接收情绪数据并调整音乐参数
- 实时生成并播放音乐
- 提供HTTP API接口

**端口：** 8080

**API接口：**
- `GET /health` - 健康检查
- `POST /update_emotion` - 接收情绪更新
- `GET /status` - 获取服务状态
- `GET /audio_status` - 获取音频流详细状态（专门用于前端监控）
- `POST /restart_audio` - 重启音频生成服务
- `WebSocket /ws/audio_status` - 实时推送音频状态（WebSocket）

## 🚀 快速开始

### 1. 安装依赖

```bash
cd EEG/
pip install -r requirements.txt
```

### 2. 配置API密钥

在 `brain_processor.py` 和 `audio_service.py` 文件中，确认已填入正确的API密钥：

```python
# Emotiv App Credentials
YOUR_APP_CLIENT_ID = '你的Client ID'
YOUR_APP_CLIENT_SECRET = '你的Client Secret'

# Google API Key
GOOGLE_API_KEY = '你的Google API Key'
```

### 3. 启动系统

**方法1：使用启动管理器（推荐）**
```bash
python start_services.py
```

**方法2：手动启动服务**

终端1 - 启动音频服务：
```bash
python audio_service.py
```

终端2 - 启动脑波处理服务：
```bash
python brain_processor.py
```

### 4. 启动前端监控界面（可选）

```bash
cd ../frontend/
npm install
npm run dev
```

然后访问 http://localhost:5173 查看音频状态监控界面

### 5. 验证运行状态

访问 http://localhost:8080/health 检查音频服务状态

访问 http://localhost:8080/audio_status 查看音频流详细状态

访问 http://localhost:5173 使用可视化监控界面

## 🔧 配置选项

### 基础音乐风格

在 `audio_service.py` 中修改：
```python
INITIAL_BASE_PROMPT = ("quiet", 0.8)  # (风格, 权重)
```

### 服务地址配置

在 `brain_processor.py` 中修改：
```python
AUDIO_SERVICE_URL = 'http://localhost:8080'
```

### 音频服务端口

在 `audio_service.py` 中修改：
```python
API_PORT = 8080
```

### 情绪数据输出频率

在 `brain_processor.py` 中修改输出间隔：
```python
self.output_interval = 5.0  # 5秒输出一次，可以调整为其他值
```

## 📊 监控和调试

### 查看实时情绪状态
脑波处理服务会每5秒在控制台输出一次：
```
[14:32:15] 当前情绪: Happy (开心) | 强度: 75.23/100 | (V: 0.45, A: 0.32)
```

**注意**：系统会持续采集脑波数据，但为了避免输出过于频繁，每5秒汇总输出一次最新的情绪状态。

### 查看服务状态
```bash
curl http://localhost:8080/status
```

### 查看日志
两个服务都会输出详细的日志信息，包括：
- 连接状态
- 数据处理状态
- 错误信息
- 性能指标

## 🛠️ 故障排除

### 常见问题

1. **音频服务无法启动**
   - 检查Google API Key是否正确
   - 确认网络连接正常
   - 查看端口8080是否被占用

2. **脑波服务连接失败**
   - 确认Emotiv Cortex软件已运行
   - 检查EEG设备连接状态
   - 验证App Credentials是否正确

3. **服务间通信失败**
   - 检查防火墙设置
   - 确认音频服务已完全启动
   - 验证网络配置

4. **音频播放异常**
   - 检查音频设备状态
   - 确认系统音频驱动正常
   - 查看缓冲区配置

### 手动测试

**测试情绪更新API：**
```bash
curl -X POST http://localhost:8080/update_emotion \
  -H "Content-Type: application/json" \
  -d '{
    "emotion": "Happy (开心)",
    "intensity": 0.8,
    "valence": 0.6,
    "arousal": 0.4,
    "timestamp": 1640995200
  }'
```

**测试音频状态API：**
```bash
# 获取音频状态
curl http://localhost:8080/audio_status

# 重启音频服务
curl -X POST http://localhost:8080/restart_audio

# 测试WebSocket连接
websocat ws://localhost:8080/ws/audio_status
```

## 🔄 服务管理

### 停止服务
使用Ctrl+C停止启动管理器，或分别停止各个服务

### 重启服务
```bash
python start_services.py
```

### 独立运行服务
每个服务都可以独立运行，便于开发和调试

## 📈 性能优化

1. **网络优化**
   - 调整HTTP超时设置
   - 控制情绪数据发送频率

2. **音频优化**
   - 调整音频缓冲区大小
   - 优化音频回调函数

3. **资源监控**
   - 监控CPU和内存使用
   - 观察网络延迟

## 🔮 未来扩展

这种微服务架构支持：
- 添加更多情绪分析算法
- 集成其他音乐生成模型
- 支持多用户同时使用
- 添加数据存储和分析功能
- 实现负载均衡和高可用性

---

**注意：** 使用前请确保已获得相应的API密钥，并已连接EEG设备。 