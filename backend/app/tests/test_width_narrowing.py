"""门幅收窄幅数单调测例。

两组基准（客厅落地窗×遮光、卧室窗×纱帘），每组两档更小的正门幅：
- panels 相对基准不下降，且每组至少一档严格变大；
- meters 与 panels、cut_height 满足乘积关系（容差 0.011）；
- 门幅取 0、取负分别拒绝。

纯函数路径（fabric_meters）覆盖两组；服务干算路径
（estimate_service.run_estimate, save=False）覆盖客厅落地窗×遮光一组。
"""

import pytest

from app.engines.curtain_math import fabric_meters
from app.services import estimate_service

from assert_helpers import (
    assert_meters_product,
    assert_panels_monotonic,
    assert_width_rejected,
    ordered_results,
)
from width_narrowing_fixtures import (
    BEDROOM_SHEER,
    GROUPS,
    LIVING_BLACKOUT,
    SERVICE_BASELINE_FABRIC_IDS,
    SERVICE_WINDOW_IDS,
)


@pytest.mark.parametrize("group", GROUPS, ids=[g["label"] for g in GROUPS])
def test_pure_path_panels_monotonic(group):
    results = ordered_results(fabric_meters, group)
    assert_panels_monotonic(results, group)
    assert_meters_product(results, group)
    for r in results:
        assert r["panels"] == group["expected_panels"][r["fabric_width"]]


@pytest.fixture()
def service_db(tmp_path, monkeypatch):
    """隔离的临时库：seed 基准数据 + 补插两组窄门幅面料。"""
    import app.config as config
    import app.db as db
    from app.seed import init_db

    db_file = tmp_path / "test.db"
    monkeypatch.setattr(config, "DB_PATH", db_file)
    monkeypatch.setattr(db, "DB_PATH", db_file)
    init_db()

    conn = db.connect()
    try:
        for group in GROUPS:
            f = group["fabric"]
            for w in group["narrower_widths"]:
                conn.execute(
                    "INSERT INTO fabrics(name,fabric_width,hem_top,hem_bottom,data_quality,note)"
                    " VALUES (?,?,?,?,?,?)",
                    (f"{group['label']}-窄{w}m", w, f["hem_top"], f["hem_bottom"], "clean", ""),
                )
        conn.commit()
    finally:
        conn.close()
    return db_file


def _narrower_fabric_ids(group):
    """按门幅查出 service_db 里补插的窄门幅面料 id。"""
    import app.db as db

    conn = db.connect()
    try:
        ids = {}
        for w in group["narrower_widths"]:
            row = conn.execute(
                "SELECT id FROM fabrics WHERE fabric_width=? AND name=?",
                (w, f"{group['label']}-窄{w}m"),
            ).fetchone()
            ids[w] = row["id"]
        return ids
    finally:
        conn.close()


def test_service_path_panels_monotonic(service_db):
    """走 estimate_service 干算（save=False 不落历史），覆盖客厅落地窗×遮光。"""
    group = LIVING_BLACKOUT
    window_id = SERVICE_WINDOW_IDS[group["label"]]
    narrow_ids = _narrower_fabric_ids(group)
    fabric_ids = [SERVICE_BASELINE_FABRIC_IDS[group["label"]]] + [
        narrow_ids[w] for w in group["narrower_widths"]
    ]

    results = [
        estimate_service.run_estimate(window_id, fid, save=False, note="")
        for fid in fabric_ids
    ]

    assert all(r["run_id"] is None for r in results)  # 干算不写历史
    assert_panels_monotonic(results, group)
    assert_meters_product(results, group)
    for r in results:
        assert r["panels"] == group["expected_panels"][r["fabric_width"]]


def test_zero_width_rejected():
    """门幅取 0：纯函数路径拒绝。"""
    assert_width_rejected(fabric_meters, BEDROOM_SHEER, 0)


def test_negative_width_rejected():
    """门幅取负：纯函数路径拒绝。"""
    assert_width_rejected(fabric_meters, BEDROOM_SHEER, -1.4)
