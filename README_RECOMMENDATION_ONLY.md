# 🎯 EEG情绪识别与视频推荐系统 - 仅推荐版本

专注于基于EEG情绪数据的智能视频推荐，不包含音频播放功能。

## 🚀 快速开始

### 1. 启动推荐系统

```bash
# 启动仅推荐服务（推荐服务 + EEG处理）
python start_recommendation_only.py
```

系统将启动：
- 🎯 视频推荐服务 (端口 8081)
- 🧠 EEG脑波数据处理服务（仅推荐模式）

### 2. 测试系统（无需EEG设备）

```bash
# 新终端窗口运行测试
python test_recommendation_only.py
```

## 📊 功能特性

### ✅ 包含功能
- 🧠 **EEG情绪识别** - 9种情绪状态实时识别
- 🎯 **智能视频推荐** - 基于情绪的个性化推荐
- 📈 **用户学习** - 行为模式学习与优化
- 📊 **反馈机制** - like/skip/share反馈收集
- 📡 **RESTful API** - 完整的HTTP接口

### ❌ 不包含功能
- 🔊 音频生成与播放
- 🎵 音乐推荐功能

## 🎮 使用方式

### 方式1：有EEG设备
1. 连接Emotiv设备并启动Cortex软件
2. 运行 `python start_recommendation_only.py`
3. 系统自动识别情绪并推荐视频

### 方式2：测试模式（无设备）
1. 运行 `python start_recommendation_only.py`
2. 运行 `python test_recommendation_only.py`
3. 模拟发送情绪数据并查看推荐

## 📡 API接口

### 推荐服务 (8081)

```bash
# 健康检查
GET /health

# 发送情绪数据
POST /update_emotion
{
  "emotion": "Happy (开心)",
  "intensity": 75.5,
  "valence": 0.6,
  "arousal": 0.4,
  "user_id": "user123"
}

# 获取推荐历史
GET /recommendations/{user_id}

# 发送用户反馈
POST /feedback
{
  "user_id": "user123",
  "video_index": 1,
  "feedback_type": "like"
}

# 获取用户画像
GET /user_profile/{user_id}
```

## 🎯 推荐策略

| 情绪状态 | 推荐内容 |
|---------|---------|
| 开心 (Happy) | 搞笑幽默、音乐舞蹈、萌宠动物 |
| 悲伤 (Sad) | 治愈温暖、萌宠动物、音乐 |
| 愤怒 (Angry) | 放松冥想、治愈内容、旅行风景 |
| 疲倦 (Tired) | 轻松娱乐、放松冥想 |
| 放松 (Relaxed) | 旅行风景、艺术创作、音乐 |
| 惊喜 (Surprised) | 科技数码、艺术创作、知识科普 |

## 🧪 测试功能

运行 `python test_recommendation_only.py` 后可选择：

1. **单次测试** - 发送一个随机情绪
2. **序列测试** - 测试多种情绪序列
3. **连续测试** - 自动连续发送情绪
4. **交互模式** - 手动控制和查看数据

### 交互模式命令
- `send` - 发送随机情绪
- `sequence` - 运行情绪序列测试
- `auto` - 连续自动测试
- `history` - 查看推荐历史
- `profile` - 查看用户画像
- `feedback` - 发送反馈
- `status` - 检查服务状态

## 🔧 配置

### EEG设备配置（可选）
在 `EEG/brain_processor_recommendation_only.py` 中配置：
```python
YOUR_APP_CLIENT_ID = '你的Emotiv Client ID'
YOUR_APP_CLIENT_SECRET = '你的Emotiv Client Secret'
```

### 依赖安装
```bash
# 推荐服务依赖
cd recommandation
pip install -r requirements.txt

# EEG模块依赖（如果使用真实设备）
cd ../EEG  
pip install -r requirements.txt
```

## 📊 系统架构

```
EEG设备 → 情绪识别 → 推荐算法 → 视频推荐
                   ↓
            用户反馈 ← 个性化学习
```

## 💡 优势

- 🎯 **专注推荐** - 去除音频功能，专注视频推荐
- ⚡ **轻量化** - 更少的系统资源占用
- 🧪 **易测试** - 完整的测试工具支持
- 📈 **高性能** - 简化架构提升性能

## 🛠️ 故障排除

### 常见问题

1. **推荐服务启动失败**
   ```bash
   # 安装依赖
   pip install flask flask-cors requests
   ```

2. **无法生成推荐**
   - 检查情绪强度是否达到阈值（>40）
   - 确认情绪数据格式正确

3. **EEG设备连接失败**
   - 确保Cortex软件已启动
   - 检查设备连接和授权

## 📞 使用帮助

1. 启动问题 → 检查依赖安装
2. 推荐问题 → 运行测试工具验证
3. API问题 → 查看服务状态接口

---

**🎯 专注视频推荐，让内容更懂你的情绪！** 