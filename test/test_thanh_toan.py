from views.thanh_toan_view import validate_payment


def test_payment_less_than_order():
    ok, message = validate_payment(
        500_000_000,
        300_000_000
    )

    assert ok is True


def test_payment_equal_order():
    ok, message = validate_payment(
        500_000_000,
        500_000_000
    )

    assert ok is True


def test_payment_exceeds_order():
    ok, message = validate_payment(
        500_000_000,
        600_000_000
    )

    assert ok is False
    assert message == "Số tiền thanh toán vượt giá trị đơn hàng"


def test_negative_payment():
    ok, message = validate_payment(
        500_000_000,
        -1
    )

    assert ok is False