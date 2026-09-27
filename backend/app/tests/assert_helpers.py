"""门幅收窄幅数单调测例的断言辅助。"""

import pytest

from width_narrowing_fixtures import calc_args

METER_TOLERANCE = 0.011


def ordered_results(calc, group):
    """按基准 → 两档更窄门幅的顺序返回计算结果。"""
    widths = [group["baseline_width"], *group["narrower_widths"]]
    return [calc(*calc_args(group, w)) for w in widths]


def assert_panels_monotonic(results, group):
    """门幅收窄时 panels 相对基准不下降，且至少一档严格变大。"""
    baseline_panels = results[0]["panels"]
    assert all(
        r["panels"] >= baseline_panels for r in results
    ), f"{group['label']}: 收窄后 panels 跌破基准 {baseline_panels}"
    assert any(
        r["panels"] > baseline_panels for r in results[1:]
    ), f"{group['label']}: 两档窄门幅均未使 panels 严格变大"


def assert_meters_product(results, group):
    """meters == panels * cut_height（容差 0.011）。"""
    for r in results:
        expected = r["panels"] * r["cut_height"]
        assert abs(r["meters"] - expected) <= METER_TOLERANCE, (
            f"{group['label']}: meters={r['meters']} 与 "
            f"panels({r['panels']}) * cut_height({r['cut_height']})={expected} 不符"
        )


def assert_width_rejected(calc, group, bad_width):
    """门幅取 0 或负值必须被拒绝（ValueError）。"""
    with pytest.raises(ValueError):
        calc(*calc_args(group, bad_width))
