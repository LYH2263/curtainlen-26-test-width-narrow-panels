"""门幅收窄单调测例包 —— 断言辅助。

纯函数路径与服务干算路径共用同一组断言语义：
门幅由宽到窄时 panels 不下降、至少一档严格变大、
meters 与 panels * cut_height 保持乘积关系（容差 0.011）。
"""
import pytest

METER_TOLERANCE = 0.011


def results_by_desc_width(widths, results):
    """把门幅与结果按门幅由宽到窄配对，保证比较顺序确定。"""
    pairs = sorted(zip(widths, results), key=lambda p: p[0], reverse=True)
    return [w for w, _ in pairs], [r for _, r in pairs]


def assert_panels_not_decreasing(widths, results):
    """门幅逐档收窄，panels 相对基准不允许下降（允许持平）。"""
    ordered_widths, ordered = results_by_desc_width(widths, results)
    base_panels = ordered[0]["panels"]
    for width, r in zip(ordered_widths, ordered):
        assert r["panels"] >= base_panels, (
            f"门幅 {width} 相对基准 {ordered_widths[0]} 出现 panels 下降: "
            f"{r['panels']} < {base_panels}"
        )
    for prev, curr in zip(ordered, ordered[1:]):
        assert curr["panels"] >= prev["panels"], (
            "门幅收窄后 panels 不允许下降: "
            f"{prev['panels']} -> {curr['panels']}"
        )


def assert_at_least_one_strict_increase(widths, results):
    """每组两档更小门幅中，至少有一档 panels 严格变大。"""
    _, ordered = results_by_desc_width(widths, results)
    assert any(
        curr["panels"] > prev["panels"]
        for prev, curr in zip(ordered, ordered[1:])
    ), f"所有收窄档 panels 均与基准持平，未观察到严格变大: {[r['panels'] for r in ordered]}"


def assert_meters_product_relation(result, tolerance=METER_TOLERANCE):
    """meters 必须等于 panels * cut_height（结果经四舍五入，按容差比较）。"""
    expected = result["panels"] * result["cut_height"]
    assert abs(result["meters"] - expected) <= tolerance, (
        f"meters={result['meters']} 与 panels*cut_height="
        f"{result['panels']}*{result['cut_height']}={expected} 之差超过容差 {tolerance}"
    )


def assert_meters_relation_for_ladder(widths, results, tolerance=METER_TOLERANCE):
    for r in results_by_desc_width(widths, results)[1]:
        assert_meters_product_relation(r, tolerance)


def assert_zero_width_rejected(calc):
    """门幅取 0 必须被拒绝。"""
    with pytest.raises(ValueError, match="fabric width"):
        calc(0.0)


def assert_negative_width_rejected(calc):
    """门幅取负必须被拒绝。"""
    with pytest.raises(ValueError, match="fabric width"):
        calc(-1.4)
