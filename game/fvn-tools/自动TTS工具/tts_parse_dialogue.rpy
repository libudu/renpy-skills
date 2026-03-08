init python:
    import os
    import csv
    import json
    import time

    # 定义对话条目类
    class DialogueEntry:
        def __init__(self, id, character, dialogue, filename, line_number, instructions=""):
            self.id = id
            self.character = character
            self.dialogue = dialogue
            self.filename = filename
            self.line_number = line_number
            self.instructions = instructions


    # 解析 dialogue.tab 函数
    def parse_dialogue_tab():
        # dialogue.tab 位于项目根目录
        path = os.path.join(config.basedir, "dialogue.tab")
        
        if not os.path.exists(path):
            return
        
        # 临时存储分组数据
        file_groups = {} # filename_base -> list of entries
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                reader = csv.reader(f, delimiter="\t")
                next(reader, None) # 跳过标题行
                for row in reader:
                    if len(row) >= 3:
                        # 假设列顺序: Identifier, Character, Dialogue, Filename, Line Number
                        d_id = row[0]
                        d_char = row[1]
                        d_text = row[2]
                        d_file = row[3] if len(row) > 3 else ""
                        d_line = row[4] if len(row) > 4 else ""
                        
                        # 提取文件名 (Identifier的哈希码之前就是文件名)
                        if "_" in d_id:
                            filename_base = d_id.rsplit('_', 1)[0]
                        else:
                            filename_base = d_id

                        if filename_base not in file_groups:
                            file_groups[filename_base] = []
                        
                        file_groups[filename_base].append({
                            "id": d_id,
                            "who": d_char,
                            "what": d_text,
                            "file": d_file,
                            "line": d_line
                        })
        except Exception as e:
            renpy.log("Error parsing dialogue.tab: " + str(e))
            return

        # 确保存储JSON的目录存在
        json_dir = os.path.join(config.gamedir, tts_config['tts_parse_dialogue_path'])
        if not os.path.exists(json_dir):
            try:
                os.makedirs(json_dir)
            except:
                pass

        # 处理每个文件分组
        for filename_base, entries in file_groups.items():
            json_path = os.path.join(json_dir, filename_base + ".json")
            
            # 加载现有JSON数据以保留 instructions
            existing_data = {}
            if os.path.exists(json_path):
                try:
                    with open(json_path, "r", encoding="utf-8") as f:
                        old_list = json.load(f)
                        for item in old_list:
                            if "id" in item:
                                existing_data[item["id"]] = item
                except Exception as e:
                    renpy.log("Error loading JSON " + json_path + ": " + str(e))
            
            # 构建新的列表并合并数据
            final_json_list = []
            
            for entry in entries:
                d_id = entry["id"]
                instructions = ""
                
                # 如果存在旧数据，保留 instructions
                if d_id in existing_data:
                    instructions = existing_data[d_id].get("instructions", "")
                
                # 创建JSON条目
                json_entry = {
                    "id": d_id,
                    "who": entry["who"],
                    "what": entry["what"],
                    "instructions": instructions
                }
                final_json_list.append(json_entry)
            
            # 保存更新后的JSON
            try:
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(final_json_list, f, ensure_ascii=False, indent=4)
            except Exception as e:
                renpy.log("Error saving JSON " + json_path + ": " + str(e))

    # 初始化时执行解析
    parse_dialogue_tab()
