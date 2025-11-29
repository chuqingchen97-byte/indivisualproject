# 🎬 电影评论多主体系统 (Multi-Agent System for Movie Review)

一个基于 DeepSeek LLM 构建的多主体系统，用于模拟不同专业角色对电影**《燃烧女子的肖像》**的专业辩论和评价过程。

---

## 1. ✨ Features (项目特性)

* **多重角色扮演 (Multi-Role Play):** 包含三种具有鲜明立场和语言风格的 Agent 角色。
* **动态情境指令 (Dynamic Contextual Instruction):** 在辩论后期（第4轮后），系统会向 Agent 施加**高级论证要求**，以加深辩论深度。
* **API 封装与色彩输出:** 使用 `colorama` 库美化终端输出，清晰区分不同 Agent 的发言。

## 2. ⚙️ Configuration (可配置参数)

以下是用户可以在 `succeedproject.py` 文件中调整的关键参数：

| 参数名称 | 所在位置 | 默认值 | 描述 |
| :--- | :--- | :--- | :--- |
| **API Key** | `MASConfig` 类 | (硬编码) | DeepSeek API 密钥，用于模型调用。 |
| **MODEL_NAME** | `MASConfig` 类 | `"deepseek-chat"` | 使用的 DeepSeek 模型名称。 |
| **total_rounds** | `ReviewController` 初始化 | `9` | 辩论的总回合数。 |
| **depth_start_round** | `ReviewController` 初始化 | `4` | 启用**高级论证要求**（如引用理论、数据）的回合开始编号。 |
| **temperature** | `DeepSeekClient.chat` 方法 | `0.7` | LLM 的随机性。值越高 (如 0.9) 发言越有创意，值越低 (如 0.5) 发言越稳定。 |

## 3. 🎭 核心 Agent 角色介绍

本项目设计了三个具有冲突视角的 Agent，以确保辩论的广度和深度。

| 角色名称 | 核心立场 (Title) | 身份/风格 (Role) | 辩论核心目标 |
| :--- | :--- | :--- | :--- |
| **学院派 Agent** | 罗兰·巴特 | 理性、精英、学术傲慢 | 证明电影的**形式美学成就**和**作者论价值**。 |
| **爆米花 Agent** | 普通影迷 | 感性、直接、情绪化 | 评价电影的**即时愉悦度和节奏**，追求爽快的观影体验。 |
| **制作人 Agent** | 华尔街制片人 | 功利、计算、务实 | 分析电影的**商业风险**和**制作效率**，强调市场价值。 |

## 4. ⚔️ 辩论规则与进行方式

本项目通过 `ReviewController` 控制器驱动 Agent 间的回合制辩论。

### 4.1. 辩论的进行流程

1.  **初始化：** 三个 Agent 被加载，设定 9 轮总回合数。
2.  **顺序发言：** Agent 轮流发言 (学院派 -> 爆米花 -> 制作人 -> 学院派...)。
3.  **循环迭代：** 每位 Agent 的发言都基于对**上一位 Agent 发言内容的反驳**。
4.  **记忆：** 每个 Agent 都会将自己的发言记录在本地内存中，以维持角色连贯性。

### 4.2. 动态难度调整 (高级论证要求)

为了确保辩论的专业性，系统在 **第 4 轮** 及之后会启用高级论证要求：

* **学院派 Agent：** 必须引用具体的**电影理论或电影史案例**。
* **爆米花 Agent：** 必须引用**具体的个人观影感受实例**。
* **制作人 Agent：** 必须引用**市场数据、ROI 估算或制作流程数据**。

---

## 5. 🛠️ Project Structure (项目结构)

本项目采用单文件架构，所有核心逻辑、配置和 Agent 角色定义均包含在 `succeedproject.py` 文件中。

* `succeedproject.py`: 核心代码文件，包含所有 Agent 类、API 客户端和辩论控制器。
* `.gitignore`: 确保敏感的 API 密钥文件 (`.env`) 不会被上传到 GitHub。

## 6. 🚀 Getting Started (运行指南)

### 6.1. 依赖安装

确保您的 Python 环境中安装了以下库：

```bash
pip install openai colorama
