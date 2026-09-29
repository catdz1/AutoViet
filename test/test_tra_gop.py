import pytest

from views.tra_gop_view import tinh_tien_tra_gop


def test_tra_gop_0_percent():
    result = tinh_tien_tra_gop(
        240_000_000,
        0,
        12
    )

    assert result == pytest.approx(20_000_000)


def test_tra_gop_08_percent():
    result = tinh_tien_tra_gop(
        240_000_000,
        0.8,
        12
    )

    assert result == pytest.approx(
        21_056_000,
        rel=0.001
    )


def test_tra_gop_49_percent():
    result = tinh_tien_tra_gop(
        240_000_000,
        4.9,
        12
    )

    assert result == pytest.approx(
        26_925_000,
        rel=0.001
    )


def test_tra_gop_5_percent():
    result = tinh_tien_tra_gop(
        240_000_000,
        5,
        12
    )

    assert result == pytest.approx(
        27_078_000,
        rel=0.001
    )


def test_tra_gop_zero_period():
    result = tinh_tien_tra_gop(
        240_000_000,
        5,
        0
    )

    assert result == 0