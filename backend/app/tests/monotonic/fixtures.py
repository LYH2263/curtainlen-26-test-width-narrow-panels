"""门幅收窄单调测例包 —— 共享 fixtures 与基准数据。

固定两组基准，每组在基准正门幅之外再给两档更小的正门幅（由宽到窄排列）：

- A 组：客厅落地窗 3.0m × 2.6m，折倍 2.0，遮光布（上卷边 0.10 / 下摆 0.15），
  基准门幅 1.4m，收窄档 1.15m、1.0m（走纯函数路径）。
- B 组：卧室窗 2.2m × 1.5m，折倍 2.0，纱帘（上卷边 0.08 / 下摆 0.12），
  基准门幅 2.8m，收窄档 2.2m、1.5m（走服务干算路径）。
"""
import pytest

from app import seed
from app.db import connect

GROUP_A = {
    "name": "客厅落地窗×遮光",
    "window_w": 3.0,
    "window_h": 2.6,
    "fullness": 2.0,
    "hem_top": 0.10,
    "hem_bottom": 0.15,
    "widths": [1.4, 1.15, 1.0],
}

GROUP_B = {
    "name": "卧室窗×纱帘",
    "window_w": 2.2,
    "window_h": 1.5,
    "fullness": 2.0,
    "hem_top": 0.08,
    "hem_bottom": 0.12,
    "widths": [2.8, 2.2, 1.5],
}


@pytest.fixture
def group_a():
    return dict(GROUP_A)


@pytest.fixture
def group_b():
    return dict(GROUP_B)


@pytest.fixture
def isolated_db(tmp_path, monkeypatch):
    """把 app.db 指向临时库并建表、灌种子，测例之间互不污染，也不碰开发库。"""
    db_path = tmp_path / "test_monotonic.db"
    monkeypatch.setattr("app.db.DB_PATH", db_path)
    seed.init_db()
    return db_path


@pytest.fixture
def bedroom_sheer_ladder(isolated_db):
    """B 组服务路径夹具：seed 中卧室窗 id=2、纱帘基准门幅 2.8m 为 fabric id=2，
    再补两档更窄正门面幅 2.2m / 1.5m（卷边同纱帘）。

    返回 (window_id, [(fabric_width, fabric_id), ...])，门幅由宽到窄。
    """
    c = connect()
    try:
        c.executemany(
            "INSERT INTO fabrics(name,fabric_width,hem_top,hem_bottom,data_quality,note)"
            " VALUES (?,?,?,?,?,?)",
            [
                ("纱帘窄幅2.2m", 2.2, 0.08, 0.12, "clean", "门幅收窄单调测例"),
                ("纱帘窄幅1.5m", 1.5, 0.08, 0.12, "clean", "门幅收窄单调测例"),
            ],
        )
        c.commit()
        rows = c.execute(
            "SELECT id, fabric_width FROM fabrics "
            "WHERE hem_top=? AND hem_bottom=? ORDER BY fabric_width DESC",
            (0.08, 0.12),
        ).fetchall()
    finally:
        c.close()
    return 2, [(float(r["fabric_width"]), r["id"]) for r in rows]
