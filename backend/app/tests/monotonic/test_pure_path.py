"""纯函数路径（app.engines.curtain_math.fabric_meters）—— A 组：客厅落地窗×遮光。"""
from functools import partial

from app.engines.curtain_math import fabric_meters

from .assertions import (
    assert_at_least_one_strict_increase,
    assert_meters_product_relation,
    assert_meters_relation_for_ladder,
    assert_negative_width_rejected,
    assert_panels_not_decreasing,
    assert_zero_width_rejected,
)


def _calc_ladder(group):
    calc = partial(
        fabric_meters,
        group["window_w"],
        group["window_h"],
        group["fullness"],
        group["hem_top"],
        group["hem_bottom"],
    )
    return group["widths"], [calc(fw) for fw in group["widths"]]


def test_living_room_blackout_panels_monotonic(group_a):
    """门幅 1.4 -> 1.15 -> 1.0：panels 相对基准不下降，且至少一档严格变大。"""
    widths, results = _calc_ladder(group_a)

    assert results[0]["panels"] == 5  # 基准：6.0m 成品宽 / 1.4m 门幅
    assert_panels_not_decreasing(widths, results)
    assert_at_least_one_strict_increase(widths, results)


def test_living_room_blackout_meters_product(group_a):
    """每档 meters 都满足 meters == panels * cut_height（容差 0.011）。"""
    widths, results = _calc_ladder(group_a)
    assert all(r["cut_height"] == 2.85 for r in results)
    assert_meters_relation_for_ladder(widths, results)


def test_bedroom_sheer_baseline_anchor(group_b):
    """B 组基准门幅在纯函数路径下的锚点：panels==2、meters 满足乘积关系，
    与服务干算路径的基准结果互为交叉验证。"""
    fw = group_b["widths"][0]
    r = fabric_meters(
        group_b["window_w"], group_b["window_h"], group_b["fullness"],
        group_b["hem_top"], group_b["hem_bottom"], fw,
    )
    assert r["panels"] == 2
    assert r["cut_height"] == 1.7
    assert_meters_product_relation(r)


def test_zero_fabric_width_rejected(group_a):
    """门幅取 0：拒绝断言（独立一条）。"""
    calc = partial(
        fabric_meters,
        group_a["window_w"],
        group_a["window_h"],
        group_a["fullness"],
        group_a["hem_top"],
        group_a["hem_bottom"],
    )
    assert_zero_width_rejected(calc)


def test_negative_fabric_width_rejected(group_a):
    """门幅取负：拒绝断言（独立一条）。"""
    calc = partial(
        fabric_meters,
        group_a["window_w"],
        group_a["window_h"],
        group_a["fullness"],
        group_a["hem_top"],
        group_a["hem_bottom"],
    )
    assert_negative_width_rejected(calc)
