import json
import os
from PIL import Image
import re

# 配置
INPUT_DIR = "."
OUTPUT_DIR = "compress"
BASE_URL = (
    "https://raw.githubusercontent.com/nyr-github/pets-asserts/refs/heads/master/"
)
TARGET_WIDTH = 800
WEBP_QUALITY = 80  # WebP格式，压缩率高且质量好

# 创建输出目录
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
    print(f"✓ 创建目录: {OUTPUT_DIR}")

# 读取原始JSON
json_file = "cat.json"
with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"✓ 读取 {json_file}")


# 压缩图片函数
def compress_image(image_path, output_dir, target_width):
    if not os.path.exists(image_path):
        print(f"  ⚠ 文件不存在: {image_path}")
        return None

    # 打开图片
    img = Image.open(image_path)

    # 计算新高度（保持宽高比）
    width, height = img.size
    if width > target_width:
        new_height = int(height * (target_width / width))
        new_size = (target_width, new_height)
        img = img.resize(new_size, Image.LANCZOS)
        print(f"  缩放: {image_path} ({width}x{height} -> {new_size[0]}x{new_size[1]})")
    else:
        print(f"  保持原尺寸: {image_path} ({width}x{height})")

    # 生成输出文件名
    base_name = os.path.splitext(image_path)[0]
    output_file = os.path.join(output_dir, f"{base_name}.webp")

    # 保存为WebP格式（高压缩率，广泛支持）
    img.save(output_file, "WEBP", quality=WEBP_QUALITY, method=6)
    output_size = os.path.getsize(output_file) / 1024  # KB
    print(f"  ✓ 保存: {output_file} ({output_size:.1f} KB)")

    return f"{base_name}.webp"


# 处理所有PNG图片
print("\n📸 开始压缩图片...")
png_files = [f for f in os.listdir(INPUT_DIR) if re.match(r"^\d+\.png$", f)]

compressed_files = {}
for png_file in sorted(png_files, key=lambda x: int(x.split(".")[0])):
    output_avif = compress_image(png_file, OUTPUT_DIR, TARGET_WIDTH)
    if output_avif:
        compressed_files[png_file] = output_avif

print(f"\n✓ 图片压缩完成: {len(compressed_files)} 张")

# 创建压缩版的JSON数据
compress_data = data.copy()
compress_data["growth_stages"] = []

for stage in data["growth_stages"]:
    new_stage = stage.copy()

    # 更新阶段图片路径
    if "image_url" in new_stage:
        old_image = new_stage["image_url"]
        if old_image in compressed_files:
            new_avif = compressed_files[old_image]
            # 添加GitHub URL前缀
            new_stage["image_url"] = f"{BASE_URL}compress/{new_avif}"
            print(
                f"更新阶段 {stage['stage_id']} 图片: {old_image} -> {new_stage['image_url']}"
            )

    # 更新动作数据
    new_stage["actions"] = []
    for action in stage["actions"]:
        new_action = action.copy()
        # 更新视频URL，添加GitHub前缀
        if "video_url" in new_action:
            old_video = new_action["video_url"]
            new_action["video_url"] = f"{BASE_URL}{old_video}"
        new_stage["actions"].append(new_action)

    compress_data["growth_stages"].append(new_stage)

# 保存压缩版JSON
compress_json_file = "cat-compress.json"
with open(compress_json_file, "w", encoding="utf-8") as f:
    json.dump(compress_data, f, ensure_ascii=False, indent=2)

print(f"\n✓ 生成 {compress_json_file}")

# 统计信息
print("\n📊 统计信息:")
print(f"  - 原始图片数量: {len(png_files)}")
print(f"  - 压缩图片数量: {len(compressed_files)}")
print(f"  - 压缩目录: {OUTPUT_DIR}/")
print(f"  - 新JSON文件: {compress_json_file}")
print(f"  - URL前缀: {BASE_URL}")
print(f"  - 输出格式: WebP (高质量压缩)")

# 计算压缩率
original_size = sum(os.path.getsize(f) for f in png_files if os.path.exists(f))
compressed_size = sum(
    os.path.getsize(os.path.join(OUTPUT_DIR, f))
    for f in compressed_files.values()
    if os.path.exists(os.path.join(OUTPUT_DIR, f))
)
if original_size > 0:
    compression_ratio = (1 - compressed_size / original_size) * 100
    print(f"\n💾 文件大小:")
    print(f"  - 原始PNG总计: {original_size / 1024:.1f} KB")
    print(f"  - 压缩AVIF总计: {compressed_size / 1024:.1f} KB")
    print(f"  - 压缩率: {compression_ratio:.1f}%")

print("\n✅ 全部完成！")
