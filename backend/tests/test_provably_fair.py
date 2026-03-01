from app.core.provably_fair import crash_multiplier, dice_roll_and_payout


def test_crash_deterministic() -> None:
    a = crash_multiplier("server", "client", 1, 0.01)
    b = crash_multiplier("server", "client", 1, 0.01)
    assert a.hmac_hex == b.hmac_hex
    assert a.multiplier == b.multiplier
    assert a.multiplier >= 1.0


def test_dice_deterministic() -> None:
    a = dice_roll_and_payout("server", "client", 2, 40, 0.01)
    b = dice_roll_and_payout("server", "client", 2, 40, 0.01)
    assert a.hmac_hex == b.hmac_hex
    assert a.roll == b.roll
    assert a.payout == 2.475
