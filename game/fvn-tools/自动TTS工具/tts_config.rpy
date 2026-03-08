
init -1 python:
    ########################### 警告：避免打包等场景导致 token 泄露 ##############
    tts_config = {
        # 使用的 token，用于请求
        'aliyun_token': aliyun_token_secret,
        # 使用的模型，用于请求
        'model': 'qwen3-tts-flash',
        # 解析后的对话 JSON 数据存储路径，后续用于赋予语音指令
        'tts_parse_dialogue_path': 'fvn-tools/自动TTS工具/dialogues'
    }