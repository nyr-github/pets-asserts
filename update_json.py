import json
import os
import re

# 读取JSON文件
json_file = "cat.json"
with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# 扫描文件夹中的所有文件
files = os.listdir(".")

# 处理阶段图片 (X.png)
for file in files:
    if re.match(r"^\d+\.png$", file):
        stage_id = int(file.split(".")[0])
        # 找到对应的阶段
        for stage in data["growth_stages"]:
            if stage["stage_id"] == stage_id:
                stage["image_url"] = file
                print(f"阶段 {stage_id} 添加图片: {file}")
                break

# 处理动作视频 (X-Y.mp4)
for file in files:
    if re.match(r"^\d+-\d+\.mp4$", file):
        match = re.match(r"^(\d+)-(\d+)\.mp4$", file)
        stage_id = int(match.group(1))
        action_id = int(match.group(2))

        # 找到对应的阶段和动作
        for stage in data["growth_stages"]:
            if stage["stage_id"] == stage_id:
                for action in stage["actions"]:
                    if action["action_id"] == action_id:
                        action["video_url"] = file
                        print(f"阶段 {stage_id} 动作 {action_id} 添加视频: {file}")
                        break
                break

# 保存更新后的JSON文件
with open(json_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("\n✓ JSON文件更新完成！")
print("\n统计信息：")
print(f"- 总阶段数: {len(data['growth_stages'])}")
print(f"- 总动作数: {sum(len(stage['actions']) for stage in data['growth_stages'])}")

# 统计已添加媒体的数量
stages_with_image = sum(1 for stage in data["growth_stages"] if "image_url" in stage)
actions_with_video = sum(
    1
    for stage in data["growth_stages"]
    for action in stage["actions"]
    if "video_url" in action
)
print(f"- 已有图片的阶段: {stages_with_image}/{len(data['growth_stages'])}")
print(f"- 已有视频的动作: {actions_with_video}")
