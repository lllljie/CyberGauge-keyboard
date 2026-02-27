# GodMode Tracker (Cyberpunk System Monitor)

GodMode Tracker 是一款基于 PyQt5 开发的极客风（Cyberpunk Neon）桌面数据监控与行为分析小工具。它通过监听底层硬件事件，实时可视化你的工作节律、键盘热力图以及鼠标运行轨迹。

## ✨ 核心特性

- **全局行为追踪**：记录鼠标点击数、鼠标物理移动里程（meters）、总敲击键盘次数。
- **趣味灵魂指标**：
  - **Regret Rate (后悔率)**：统计 Backspace / Delete 键触发频率。
  - **Copy / Paste**：统计 Ctrl+C / Ctrl+V 操作频率。
- **硬核可视化**：
  - **机械键盘热力图**：根据按键频率动态渲染对应键位的赛博蓝发光特效。
  - **鼠标轨迹画板**：记录并在画布上绘制具有外发光效果的鼠标运动轨迹。
  - **24H 生理时钟**：柱状图直观展示全天 24 小时活跃度分布。
- **系统状态监控**：实时获取当前活动的焦点应用、CPU/RAM 占用率以及动态网速 (APM 监控)。
- **沉浸式 UI**：支持无边框拖拽、悬浮窗模式 (MiniMode)、系统托盘后台运行。

## ⚙️ 环境依赖

* **OS**: Windows 专属 (依赖 `win32gui` 获取活动窗口和屏幕上下文)
* **Python**: 3.8+ 建议

## 🚀 安装与运行

1. 克隆或下载本项目。
2. 在项目根目录下，安装依赖：
   ```bash
   pip install -r requirements.txt

   ```
3. 运行主程序：
   ```bash
   python main.py
   ```

## 🎨 项目截图

### 主界面

![主界面](godmode_tracker\data\view.png)

