"""服务干算路径（estimate_service.run_estimate, save=False）—— B 组：卧室窗×纱帘。"""
from app.services import estimate_service

from .assertions import (
    assert_at_least_one_strict_increase,
    assert_meters_relation_for_ladder,
    assert_panels_not_decreasing,
)


def _run_ladder(ladder):
    window_id, fabric_ladder = ladder  # [(fabric_width, fabric_id), ...] 门幅由宽到窄
    widths = [fw for fw, _ in fabric_ladder]
    results = [
        estimate_service.run_estimate(window_id, fabric_id, save=False, note="")
        for _, fabric_id in fabric_ladder
    ]
    return widths, results


def test_bedroom_sheer_panels_monotonic(bedroom_sheer_ladder):
    """门幅 2.8 -> 2.2 -> 1.5 走服务干算：panels 不下降，且至少一档严格变大。"""
    widths, results = _run_ladder(bedroom_sheer_ladder)

    assert results[0]["panels"] == 2  # 基准：4.4m 成品宽 / 2.8m 门幅
    assert_panels_not_decreasing(widths, results)
    assert_at_least_one_strict_increase(widths, results)
    assert all(r["run_id"] is None for r in results)  # 干算不落库


def test_bedroom_sheer_meters_product(bedroom_sheer_ladder):
    """服务返回的 meters 同样满足 meters == panels * cut_height（容差 0.011）。"""
    widths, results = _run_ladder(bedroom_sheer_ladder)
    assert all(r["cut_height"] == 1.7 for r in results)
    assert_meters_relation_for_ladder(widths, results)
