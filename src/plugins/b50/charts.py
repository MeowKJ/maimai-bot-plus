import plotly.express as px
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO


def generate_pie_chart():
    # 1. 使用 Plotly 生成饼图并保存在内存中
    labels = ["苹果", "香蕉", "橙子", "葡萄"]
    sizes = [20, 25, 35, 20]
    fig = px.pie(values=sizes, names=labels, title="水果比例")

    # 使用 BytesIO 将图片保存在内存中
    img_bytes = BytesIO()
    fig.write_image(img_bytes, format="png")
    img_bytes.seek(0)  # 重置指针到开头

    # 2. 使用 Pillow 处理内存中的图片
    image = Image.open(img_bytes)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    # 添加文本（例如水印）
    draw.text((10, 10), "水果饼图", font=font, fill="black")

    # 如果你需要再次使用这张图，可以继续将它保存在内存中
    output_bytes = BytesIO()
    image.save(output_bytes, format="PNG")
    output_bytes.seek(0)

    # 显示图片（可选）
    image.show()

    return output_bytes
