"""门幅收窄幅数单调测例的基准数据。

每组固定一个「窗 × 面料」基准，再给两档更小的正门幅；
期望的 panels 由 app.engines.curtain_math.fabric_meters 实际计算验证过。
"""

# 基准组 1：客厅落地窗 × 遮光（hems 0.10/0.15，基准门幅 1.4m）
LIVING_BLACKOUT = {
    "label": "客厅落地窗×遮光",
    "window": {"width": 3.0, "height": 2.6, "fullness": 2.0},
    "fabric": {"hem_top": 0.10, "hem_bottom": 0.15},
    "baseline_width": 1.4,
    "narrower_widths": [1.2, 1.0],
    "expected_panels": {1.4: 5, 1.2: 5, 1.0: 6},
}

# 基准组 2：卧室窗 × 纱帘（hems 0.08/0.12，基准门幅 2.8m）
BEDROOM_SHEER = {
    "label": "卧室窗×纱帘",
    "window": {"width": 2.2, "height": 1.5, "fullness": 2.0},
    "fabric": {"hem_top": 0.08, "hem_bottom": 0.12},
    "baseline_width": 2.8,
    "narrower_widths": [2.2, 1.5],
    "expected_panels": {2.8: 2, 2.2: 2, 1.5: 3},
}

GROUPS = [LIVING_BLACKOUT, BEDROOM_SHEER]

# 服务干算路径用的窗/面料 id（与 seed.py 的插入顺序一致）
SERVICE_WINDOW_IDS = {
    "客厅落地窗×遮光": 1,
    "卧室窗×纱帘": 2,
}
SERVICE_BASELINE_FABRIC_IDS = {
    "客厅落地窗×遮光": 1,  # 遮光1.4m
    "卧室窗×纱帘": 2,  # 纱帘2.8m
}


def calc_args(group, width):
    """把基准组 + 门幅展开成 fabric_meters 的位置参数。"""
    w, f = group["window"], group["fabric"]
    return (w["width"], w["height"], w["fullness"], f["hem_top"], f["hem_bottom"], width)
