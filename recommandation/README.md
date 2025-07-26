# EEG情绪驱动的短视频推荐系统

基于脑机接口(EEG)情绪识别技术的智能短视频推荐系统，能够实时分析用户情绪状态并提供个性化的视频内容推荐。

## 系统架构

### 核心组件

1. **情绪-视频映射系统** (`emotion_video_mapping.py`)
   - 定义15种视频类别和9种情绪状态的映射关系
   - 基于心理学研究的情绪调节策略
   - 支持Valence-Arousal二维情绪模型
   - 强度等级调节机制

2. **视频数据库模拟** (`video_database.py`)
   - 视频元数据管理（标题、类别、时长、热度等）
   - 情感标签系统
   - 用户交互记录
   - 多维度视频检索功能

3. **推荐引擎** (`recommendation_engine.py`)
   - 多因子推荐算法（情绪匹配、用户偏好、内容质量等）
   - 实时情绪适配
   - 多样性控制
   - 推荐解释生成

4. **用户学习系统** (`user_learning.py`)
   - 用户画像构建
   - 情绪模式分析
   - 偏好学习与适应
   - 个性化策略优化

5. **集成系统** (`integrated_system.py`)
   - EEG数据实时处理
   - 情绪识别集成
   - 自动推荐触发
   - 交互式用户界面

## 情绪-视频映射策略

### 情绪类别与推荐策略

| 情绪状态 | 推荐策略 | 避免内容 |
|---------|---------|---------|
| 开心 (Happy) | 搞笑幽默、音乐舞蹈、萌宠动物 | - |
| 悲伤 (Sad) | 治愈温暖、萌宠动物、音乐 | 新闻资讯 |
| 愤怒 (Angry) | 放松冥想、治愈内容、旅行风景 | 新闻、游戏 |
| 疲倦 (Tired) | 轻松娱乐、放松冥想 | 知识科普、新闻 |
| 放松 (Relaxed) | 旅行风景、艺术创作、音乐 | - |
| 惊喜 (Surprised) | 科技数码、艺术创作、知识科普 | - |
| 厌恶 (Disgust) | 治愈内容、萌宠动物、美好事物 | 新闻资讯 |
| 平静 (Pleased) | 艺术创作、旅行风景、生活日常 | - |
| 中性 (Neutral) | 多样化内容、发现新内容 | - |

### 强度等级影响

- **高强度 (>70)**: 优先即时情绪调节，偏好短内容
- **中等强度 (30-70)**: 平衡推荐策略
- **低强度 (<30)**: 降低情绪匹配权重，偏好多样性

## 推荐算法

### 评分机制

推荐分数由以下因子加权计算：

1. **基础分数** (30%): 视频流行度 + 质量评分
2. **情绪策略匹配** (40%): 基于当前情绪的策略适配
3. **V-A维度匹配** (40%): Valence-Arousal二维情绪相似度
4. **用户偏好** (30%): 历史行为学习的个性化权重
5. **新颖性** (20%): 基于观看次数的反向分数
6. **时效性** (10%): 新近上传内容加权

### 多样性控制

- 同类别视频不超过推荐总数的50%
- 根据用户多样性偏好动态调整
- 平衡热门内容与小众发现

## 用户学习机制

### 画像构建

- **类别偏好**: 基于交互行为的加权学习
- **情绪-内容映射**: 成功率统计与策略优化
- **时间模式**: 活跃时段与内容时长偏好
- **多样性偏好**: 内容选择多样性分析

### 适应性优化

- **快速适应** (权重0.3): 快速响应用户偏好变化
- **中等适应** (权重0.15): 平衡稳定性与灵活性
- **缓慢适应** (权重0.05): 维持长期偏好稳定性

## 使用方法

### 1. 完整集成系统

```python
from integrated_system import IntegratedEEGRecommendationSystem

# 创建系统实例
system = IntegratedEEGRecommendationSystem(
    app_client_id="your_client_id",
    app_client_secret="your_client_secret",
    user_id="user123"
)

# 启动系统
system.start_system(auto_recommend=True)

# 手动获取推荐
system.manual_recommendation()

# 记录用户反馈
system.record_user_feedback(video_index=1, feedback_type="like")

# 查看用户画像
system.show_user_profile()
```

### 2. 独立推荐引擎

```python
from recommendation_engine import EmotionBasedRecommendationEngine

engine = EmotionBasedRecommendationEngine()

recommendations = engine.recommend_videos(
    emotion="开心 (Happy)",
    intensity=75,
    valence=0.6,
    arousal=0.4,
    user_id="user123",
    num_recommendations=5
)

for video in recommendations:
    print(f"{video['title']} - 分数: {video['recommendation_score']:.2f}")
```

### 3. 演示和测试

```python
# 运行演示脚本
python demo_test.py

# 选择演示项目:
# 1. 基础推荐功能
# 2. 用户学习功能  
# 3. 情绪模式分析
# 4. 推荐解释功能
# 5. 运行所有演示
```

## 交互命令

在集成系统的交互模式下，支持以下命令：

- `manual`: 手动获取推荐
- `feedback <序号> <类型>`: 提供反馈 (like/skip/share)
- `profile`: 查看用户画像
- `interval <秒数>`: 设置推荐间隔
- `stop`: 停止系统

## 系统特性

### 实时性
- 实时EEG数据处理
- 毫秒级情绪识别
- 自动推荐触发

### 个性化
- 用户行为学习
- 情绪模式识别
- 动态策略调整

### 可解释性
- 推荐理由生成
- 评分因子透明
- 用户画像可视化

### 可扩展性
- 模块化设计
- 插件式视频源
- 策略配置化

## 技术要求

### 依赖库
```
numpy
datetime
json
random
collections
typing
```

### EEG设备
- Emotiv EPOC/Insight系列头戴设备
- Cortex API访问权限
- 稳定的设备连接

## 配置参数

### 推荐引擎参数
- `num_recommendations`: 推荐数量 (默认5)
- `recommendation_interval`: 自动推荐间隔 (默认30秒)
- `intensity_threshold`: 触发推荐的情绪强度阈值 (默认40)

### 学习系统参数
- `adaptation_rate`: 学习速率 (fast/medium/slow)
- `diversity_preference`: 多样性偏好 (0-1)
- `history_length`: 保持的历史记录长度 (默认100)

## 性能优化

### 算法优化
- 候选视频预筛选
- 分数计算向量化
- 缓存机制

### 内存管理
- 历史记录限制
- 定期清理过期数据
- 延迟加载机制

## 扩展方向

### 内容源扩展
- 音频内容推荐
- 图文内容推荐
- 实时直播推荐

### 情绪维度扩展
- 多用户群体情绪
- 环境因子融合
- 生理信号集成

### 算法优化
- 深度学习模型
- 协同过滤
- 强化学习

## 许可证

本项目遵循 MIT 许可证。

## 联系方式

如有问题或建议，请联系开发团队。

---

*基于EEG技术的情绪识别推荐系统，让内容推荐更懂你的心！* 