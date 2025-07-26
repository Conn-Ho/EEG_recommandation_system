# 前端音频状态监控使用说明

## 🎯 概述

前端提供了一个实时的音频状态监控界面，让你可以：
- 📊 实时监控音频生成服务的状态
- 🔄 查看缓冲进度和连接状态
- ❌ 查看错误详情并重启服务
- 📝 查看连接日志

## 🚀 启动前端

### 1. 安装依赖
```bash
cd frontend/
npm install
```

### 2. 启动开发服务器
```bash
npm run dev
```

### 3. 访问界面
打开浏览器访问：http://localhost:5173

## 📱 界面功能

### 🎵 音频生成状态卡片

#### 状态类型
- **⏹️ 已停止 (stopped)**: 音频服务未运行
- **🚀 启动中 (starting)**: 服务正在启动
- **⚙️ 初始化中 (initializing)**: 正在初始化Google AI客户端
- **🔗 连接中 (connecting)**: 正在连接Lyria模型
- **⏳ 缓冲中 (buffering)**: 正在预缓冲音频数据
- **🎵 播放中 (playing)**: 音频流已开启，正在播放
- **❌ 错误 (error)**: 出现错误
- **🛑 停止中 (stopping)**: 正在停止服务

#### 进度显示
在缓冲阶段，会显示一个进度条显示缓冲进度（0-100%）

#### 错误处理
如果出现错误，会显示：
- 错误详情（可展开查看）
- 重启按钮（仅在错误状态下显示）

### 🌐 连接指示器
- **🟢 已连接**: WebSocket连接正常，可以实时接收状态更新
- **🔴 未连接**: WebSocket连接断开，会自动尝试重连

### 🔄 操作按钮

#### 重启音频服务
- 仅在错误状态下显示
- 点击后会向后端发送重启请求
- 重启期间按钮显示"重启中..."

#### 刷新状态
- 手动刷新当前状态
- 在网络不稳定时可以手动获取最新状态

### 📝 连接日志
- 显示最近50条连接和状态变化日志
- 包含时间戳和详细信息
- 自动滚动显示最新日志

## 🔧 技术实现

### WebSocket实时通信
```javascript
// 连接WebSocket
const wsUrl = 'ws://localhost:8080/ws/audio_status'
const websocket = new WebSocket(wsUrl)

// 接收状态更新
websocket.onmessage = (event) => {
  const data = JSON.parse(event.data)
  // 更新界面状态
}
```

### HTTP API调用
```javascript
// 获取状态
const response = await fetch('http://localhost:8080/audio_status')
const status = await response.json()

// 重启服务
const response = await fetch('http://localhost:8080/restart_audio', {
  method: 'POST'
})
```

### 自动重连机制
- WebSocket断开后会自动重连
- 使用指数退避策略（最大30秒）
- 最多尝试10次重连

## 🎨 状态颜色说明

- **🟢 绿色**: 正常运行（playing）
- **🟡 黄色**: 缓冲中（buffering）
- **🔵 蓝色**: 连接中（connecting, initializing, starting）
- **🔴 红色**: 错误状态（error）
- **⚫ 灰色**: 停止状态（stopped）

## 🛠️ 故障排除

### 前端无法连接到后端
1. 确认音频服务正在运行（端口8080）
2. 检查防火墙设置
3. 确认前端和后端在同一网络环境

### WebSocket连接失败
1. 检查浏览器控制台错误
2. 确认WebSocket端点 `ws://localhost:8080/ws/audio_status` 可访问
3. 尝试刷新页面重新建立连接

### 状态更新不及时
1. 检查WebSocket连接状态
2. 手动点击刷新状态按钮
3. 查看连接日志确认问题

## 📊 实际使用流程

### 启动系统时
1. 前端显示 "🚀 启动中"
2. 然后显示 "⚙️ 初始化中"
3. 接着显示 "🔗 连接中"
4. 进入 "⏳ 缓冲中" 并显示进度条
5. 最终显示 "🎵 播放中"

### 遇到错误时
1. 状态变为 "❌ 错误"
2. 显示错误详情
3. 点击重启按钮尝试恢复
4. 或检查后端服务状态

### 正常运行时
1. 状态保持 "🎵 播放中"
2. WebSocket连接显示 "🟢 已连接"
3. 情绪数据会每5秒更新一次（在后端控制台显示）

## 🔮 扩展功能

未来可以添加：
- 情绪数据可视化图表
- 音乐参数实时调整
- 历史数据记录和回放
- 多用户支持

---

**注意**: 这个前端界面主要用于监控和调试，实际的音频播放和EEG数据处理都在后端服务中进行。 