# QwenTTS API 文档：https://help.aliyun.com/zh/model-studio/qwen-tts-api

init python:
    import requests
    import json
    import os

    def generate_tts(text, instructions=''):
        url = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation'
        headers = {
            'Authorization': f"Bearer {tts_config['aliyun_token']}",
            'Content-Type': 'application/json'
        }
        payload = {
            "model": tts_config['model'],
            "input": {
                "text": text,
                "voice": "Ethan",
                "language_type": "Chinese",
                # Qwen 指令控制，用于语音优化
                "instructions": instructions,
                "optimize_instructions": True,
            },
            "parameters": {
                "sample_rate": 12000,
                "response_format": "wav"
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error during TTS request: {e}")
            if response.content:
                print(f"Response content: {response.text}")
            return None

    def download_and_save_voice(text, save_dir, file_id, instructions=''):
        # 1. 调用 API
        resp = generate_tts(text, instructions)
        if not resp:
            raise Exception("API 请求失败")

        # 2. 解析 URL
        audio_url = None
        # 尝试解析 DashScope 响应结构
        try:
            if 'output' in resp:
                audio_url = resp['output']['audio']['url']
        except Exception as e:
            raise Exception("JSON Parse Error: " + str(e))

        if not audio_url:
            raise Exception("未找到音频地址，请查看日志. Response: " + str(resp))

        # 3. 下载音频
        try:
            r = requests.get(audio_url)
            r.raise_for_status()
        except Exception as e:
            raise Exception("Network/Download Error: " + str(e))
        
        # 4. 保存文件
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        # 根据 Content-Type 或默认保存为 mp3
        content_type = r.headers.get('content-type', '').lower()
        ext = ".mp3"
        if "wav" in content_type:
            ext = ".wav"
        elif "ogg" in content_type:
            ext = ".ogg"
        
        save_path = os.path.join(save_dir, file_id + ext)
        with open(save_path, "wb") as f:
            f.write(r.content)
        
        return save_path