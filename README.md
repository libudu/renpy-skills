### AI 文本转剧幕工具

使用方法：

- **Trae 环境**：直接在对话中要求使用 `renpy-text2script` skill。
- **非 Trae 环境**：请引用或复制 [.trae/skills/renpy-text2script/SKILL.md](.trae/skills/renpy-text2script/SKILL.md) 文件内容作为提示词。

**核心功能：**

1.  **文本拆分与 Ren'Py 脚本编写**

    - 将原始文本拆分为多个独立的剧幕（Scene），每个剧幕对应一个 `.rpy` 文件。
    - 输出路径：`game/scripts/[章节名]/`（如 `game/scripts/ch4/`）。
    - 文件命名规范：`[章节]_[序号]_[描述].rpy`（如 `ch4_s1_meeting.rpy`）。
    - 代码规范：
      - 包含标准 Label 定义。
      - 自动声明未定义角色。
      - 转换对白为 Ren'Py 语法。
      - 添加详细的演出注释（场景、音乐、音效、表情、特效），并使用 Python 注释 `#` 标记。

2.  **资产需求设计**
    - 为每个剧幕生成配套的资产设计文档。
    - 输出路径：`game/assets/[剧幕名]_assets.md`。
    - 内容包含：背景、CG、BGM、SFX 的详细描述、搜索关键词及 AI 生成提示词。

**注意事项：**

1.  生成结果为仅供参考的草稿，不保证结果可直接运行，需要根据实际情况修改代码路径及补充静态资源。
2.  此工具主要用于快速搭建演出框架和梳理资源需求，约占 Ren'Py 脚本演出总工作量的 20%，剩余 80% 的精细化演出仍需人工调整。
3.  可根据自己经验和实际情况调整提示词，以取得更好的效果

### AI 自动语音 tts 工具

1. 使用 Renpy 的提取对话功能，生成以制表符分隔的表格文件 `dialogue.tab`
2. 添加自动语音配置：`define config.auto_voice = "voice/{id}.ogg"`
3. 前往阿里云创建 apikey：https://bailian.console.aliyun.com/cn-beijing/?tab=model#/api-key
4. Qwen TTS 支持音色：https://help.aliyun.com/zh/model-studio/qwen-tts?spm=a2c4g.11186623.0.0.72c0435af0Frr8#bac280ddf5a1u

按照 语音生成指令控制提示词.md 中的要求处理 dialogues 中的所有对话文件

注意 token 保密

### AI 自动翻译工具
