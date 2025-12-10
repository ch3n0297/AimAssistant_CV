"""
座標轉換工具模組 (Coordinate Utility Module)

負責座標系統之間的轉換。
"""

from typing import Tuple


def scale_coordinates(
    x: float,
    y: float,
    from_size: Tuple[int, int],
    to_size: Tuple[int, int]
) -> Tuple[float, float]:
    """
    縮放座標從一個尺寸到另一個尺寸

    Args:
        x: 原始 x 座標
        y: 原始 y 座標
        from_size: 原始尺寸 (width, height)
        to_size: 目標尺寸 (width, height)

    Returns:
        (scaled_x, scaled_y)
    """
    scale_x = to_size[0] / from_size[0]
    scale_y = to_size[1] / from_size[1]

    return (x * scale_x, y * scale_y)


def map_to_screen(
    x: float,
    y: float,
    model_size: Tuple[int, int] = (640, 360),
    screen_size: Tuple[int, int] = (1920, 1080)
) -> Tuple[float, float]:
    """
    將模型座標映射到螢幕座標

    Args:
        x: 模型座標 x
        y: 模型座標 y
        model_size: 模型輸入尺寸 (width, height)
        screen_size: 螢幕尺寸 (width, height)

    Returns:
        (screen_x, screen_y)
    """
    return scale_coordinates(x, y, model_size, screen_size)


def map_to_model(
    x: float,
    y: float,
    screen_size: Tuple[int, int] = (1920, 1080),
    model_size: Tuple[int, int] = (640, 360)
) -> Tuple[float, float]:
    """
    將螢幕座標映射到模型座標

    Args:
        x: 螢幕座標 x
        y: 螢幕座標 y
        screen_size: 螢幕尺寸 (width, height)
        model_size: 模型輸入尺寸 (width, height)

    Returns:
        (model_x, model_y)
    """
    return scale_coordinates(x, y, screen_size, model_size)


def get_scale_factors(
    model_size: Tuple[int, int] = (640, 360),
    screen_size: Tuple[int, int] = (1920, 1080)
) -> Tuple[float, float]:
    """
    取得從模型座標到螢幕座標的縮放因子

    Args:
        model_size: 模型輸入尺寸
        screen_size: 螢幕尺寸

    Returns:
        (scale_x, scale_y)
    """
    return (
        screen_size[0] / model_size[0],
        screen_size[1] / model_size[1]
    )


# 測試用
if __name__ == "__main__":
    print("測試座標轉換工具...")

    # 模型座標
    model_x, model_y = 320, 180  # 模型畫面中央

    # 轉換到螢幕座標
    screen_x, screen_y = map_to_screen(model_x, model_y)
    print(f"模型座標 ({model_x}, {model_y}) -> 螢幕座標 ({screen_x}, {screen_y})")

    # 轉換回模型座標
    back_x, back_y = map_to_model(screen_x, screen_y)
    print(f"螢幕座標 ({screen_x}, {screen_y}) -> 模型座標 ({back_x}, {back_y})")

    # 縮放因子
    scale_x, scale_y = get_scale_factors()
    print(f"縮放因子: x={scale_x}, y={scale_y}")
