define config.log = 'tts_log.txt'

init python:
    # 禁用机器朗读按键
    config.keymap['self_voicing'] = [] 
    
    import os
    import csv
    import requests
    import time
    import json
    import glob
    
    # 全局变量存储对话
    all_dialogues = []
    
    class DialogueEntry:
        def __init__(self, id, who, what, instructions=""):
            self.id = id
            self.who = who
            self.what = what
            self.instructions = instructions

    # TTS 通知变量
    tts_toast_message = None
    tts_toast_start = 0

    def tts_log(msg):
        global tts_toast_message, tts_toast_start
        tts_toast_message = msg
        tts_toast_start = time.time()
        renpy.log(msg)
        renpy.restart_interaction()

    # 解析对话文件
    def parse_dialogue_files():
        global all_dialogues
        all_dialogues = []
        
        dialogue_dir = os.path.join(config.gamedir, "fvn-tools", "自动TTS工具", "dialogues")
        if not os.path.exists(dialogue_dir):
            tts_log("未找到 dialogues 目录")
            return

        json_pattern = os.path.join(dialogue_dir, "*.json")
        json_files = glob.glob(json_pattern)
        
        if not json_files:
            tts_log("未找到 json 文件")
            return

        for f_path in json_files:
            try:
                with open(f_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data:
                        entry = DialogueEntry(
                            item.get("id", ""),
                            item.get("who", ""),
                            item.get("what", ""),
                            item.get("instructions", "")
                        )
                        all_dialogues.append(entry)
            except Exception as e:
                tts_log("解析出错 " + os.path.basename(f_path) + ": " + str(e))
        
        tts_log("已加载 " + str(len(all_dialogues)) + " 条对话")

    # 获取语音文件路径（支持 ogg, mp3, wav）
    def get_voice_path(id):
        for ext in [".ogg", ".mp3", ".wav"]:
            # 检查文件是否存在
            full_path = os.path.join(config.gamedir, "voice", id + ext)
            if os.path.exists(full_path):
                return "voice/" + id + ext
        return None

    # 检查语音文件是否存在
    def voice_exists(id):
        return get_voice_path(id) is not None

    # 下载语音操作
    def download_voice_action(id, text, instructions=''):
        tts_log("正在请求生成语音: " + id)
        
        try:
            # 1. 准备保存目录
            voice_dir = os.path.join(config.gamedir, "voice")
            
            # 2. 调用 API 并下载保存 (逻辑已封装在 tts_api.rpy)
            save_path = download_and_save_voice(text, voice_dir, id, instructions)
            
            # 3. 清理同ID的其他格式文件 (防止重生成后格式变化导致旧文件残留)
            for ext in [".ogg", ".mp3", ".wav"]:
                check_path = os.path.join(voice_dir, id + ext)
                if os.path.exists(check_path):
                    # 如果路径不同（说明是不同扩展名），则删除
                    if os.path.abspath(check_path) != os.path.abspath(save_path):
                        try:
                            os.remove(check_path)
                        except:
                            pass

            tts_log("下载成功: " + id + '【' + str(instructions) + '】')
            renpy.restart_interaction()
            
        except Exception as e:
            tts_log("下载出错: " + str(e))

    parse_dialogue_files()

screen tts_screen():
    modal True
    zorder 100
    
    default page = 0
    default items_per_page = 20
    
    # 半透明黑色背景
    add Solid("#000000CC")
    
    # 按 V 或 ESC 关闭
    key "v" action Hide("tts_screen")
    key "game_menu" action Hide("tts_screen")

    frame:
        align (0.5, 0.5)
        xysize (config.screen_width - 100, config.screen_height - 100) # 增大尺寸以适应屏幕（1920x1080），留有边距
        padding (20, 20)
        background Solid("#222222") # 深色背景
        
        vbox:
            spacing 20
            
            # 标题栏
            hbox:
                xfill True
                text "TTS 语音管理工具" size 40 bold True align (0.0, 0.5) color "#FFFFFF"
                textbutton "刷新列表" action Function(parse_dialogue_files) align (1.0, 0.5) text_color "#AAAAAA" text_hover_color "#FFFFFF" text_size 24
            
            # 表头
            hbox:
                spacing 10
                frame:
                    background Solid("#444444")
                    xsize 250
                    ysize 60
                    text "ID" bold True size 24 align (0.5, 0.5) color "#EEEEEE"
                frame:
                    background Solid("#444444")
                    xsize 200
                    ysize 60
                    text "角色" bold True size 24 align (0.5, 0.5) color "#EEEEEE"
                frame:
                    background Solid("#444444")
                    xsize 1000
                    ysize 60
                    text "内容" bold True size 24 align (0.5, 0.5) color "#EEEEEE"
                frame:
                    background Solid("#444444")
                    xsize 200
                    ysize 60
                    text "操作" bold True size 24 align (0.5, 0.5) color "#EEEEEE"

            # 列表内容
            viewport:
                scrollbars "vertical"
                mousewheel True
                draggable True # 仅竖向有效，因宽度未溢出
                xfill True
                yfill True
                
                vbox:
                    spacing 5
                    
                    if not all_dialogues:
                        text "未找到 json 文件或文件为空" align (0.5, 0.5) color "#888888" size 24
                    
                    $ start_idx = page * items_per_page
                    $ end_idx = min((page + 1) * items_per_page, len(all_dialogues))
                    $ current_items = all_dialogues[start_idx:end_idx]
                    
                    for i, entry in enumerate(current_items):
                        # 交替背景色
                        $ row_bg = "#333333" if i % 2 == 0 else "#3A3A3A"
                        
                        hbox:
                            spacing 10
                            frame:
                                background Solid(row_bg)
                                xsize 250
                                ysize 75
                                padding (10, 10)
                                text entry.id size 18 align (0.0, 0.5) color "#CCCCCC"
                            frame:
                                background Solid(row_bg)
                                xsize 200
                                ysize 75
                                padding (10, 10)
                                text entry.who size 20 align (0.5, 0.5) color "#DDDDDD"
                            frame:
                                background Solid(row_bg)
                                xsize 1000
                                ysize 75
                                padding (10, 10)
                                text entry.what + '【' + entry.instructions + '】' size 22 align (0.0, 0.5) color "#FFFFFF"
                            frame:
                                background Solid(row_bg)
                                xsize 200
                                ysize 75
                                padding (10, 10)
                                align (0.5, 0.5)
                                $ v_path = get_voice_path(entry.id)
                                if v_path:
                                    hbox:
                                        spacing 10
                                        align (0.5, 0.5)
                                        textbutton "播放":
                                            action Play("voice", v_path)
                                            text_size 24
                                            text_color "#66CC66"
                                            text_hover_color "#88EE88"
                                        textbutton "重新生成":
                                            action Function(download_voice_action, entry.id, entry.what, entry.instructions)
                                            text_size 24
                                            text_color "#FFAA44"
                                            text_hover_color "#FFCC88"
                                else:
                                    textbutton "下载":
                                        action Function(download_voice_action, entry.id, entry.what, entry.instructions)
                                        align (0.5, 0.5)
                                        text_size 24
                                        text_color "#44AAFF"
                                        text_hover_color "#88CCFF"

            # 底部翻页
            hbox:
                align (0.5, 0.9)
                spacing 50
                
                textbutton "< 上一页":
                    action SetScreenVariable("page", max(0, page - 1))
                    sensitive page > 0
                    text_size 28
                    text_color "#FFFFFF"
                    text_insensitive_color "#555555"
                
                $ total_pages = ((len(all_dialogues) - 1) // items_per_page) + 1 if all_dialogues else 1
                text "第 [page + 1] / [total_pages] 页" yalign 0.5 size 24 color "#DDDDDD"
                
                textbutton "下一页 >":
                    action SetScreenVariable("page", min(total_pages - 1, page + 1))
                    sensitive (page + 1) < total_pages
                    text_size 28
                    text_color "#FFFFFF"
                    text_insensitive_color "#555555"

    # 关闭按钮
    textbutton "X":
        align (1.0, 0.0)
        offset (-40, 40)
        action Hide("tts_screen")
        text_size 40
        text_color "#AAAAAA"
        text_hover_color "#FFFFFF"

    # 顶部通知区域
    if tts_toast_message:
        text tts_toast_message color "#FFFFFF" size 28
        
        # 5秒后自动清除
        timer 0.1 repeat True action If(time.time() - tts_toast_start > 5.0, SetVariable("tts_toast_message", None), NullAction())

# 全局按键监听
screen tts_key_listener():
    zorder 90
    key "v" action ToggleScreen("tts_screen")

init python:
    # 将按键监听屏幕添加到 always_shown_screens 中，使其在游戏和主菜单中均有效
    if "tts_key_listener" not in config.always_shown_screens:
        config.always_shown_screens.append("tts_key_listener")
