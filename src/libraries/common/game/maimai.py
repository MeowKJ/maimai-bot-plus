import math

# 定义评级与对应的达成率下限和评级系数
grade_thresholds = [
    {"grade": "SSS+", "min_rate": 100.5000, "coefficient": 22.4},
    {"grade": "SSS", "min_rate": 100.0000, "coefficient": 21.6},
    {"grade": "SS+", "min_rate": 99.5000, "coefficient": 21.1},
    {"grade": "SS", "min_rate": 99.0000, "coefficient": 20.8},
    {"grade": "S+", "min_rate": 98.0000, "coefficient": 20.3},
    {"grade": "S", "min_rate": 97.0000, "coefficient": 20.0},
]


def rating_generator(chart_constant):
    """
    生成从 SSS+ 到 S 的 DX Rating 值。

    Args:
        chart_constant (float): 谱面定数。

    Yields:
        Tuple[str, int]: 评级名称与对应的 DX Rating 值。
    """
    for grade in grade_thresholds:
        # 计算 DX Rating，并向下取整
        dx_rating = math.floor(
            chart_constant * (grade["min_rate"] / 100) * grade["coefficient"]
        )
        yield (grade["grade"], dx_rating)
