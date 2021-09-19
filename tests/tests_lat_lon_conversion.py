import pytest

from dhvxml2cup import dd_to_ddm, lat_dd_to_cup_ddm, lon_dd_to_cup_ddm


def test_dd_to_ddm():
    dd = -77.33587
    deg, decimal_minutes = dd_to_ddm(dd)
    assert deg == -77
    assert decimal_minutes == pytest.approx(20.1525, 1e-04)

    dd = -dd
    deg, decimal_minutes = dd_to_ddm(dd)
    assert deg == 77
    assert decimal_minutes == pytest.approx(20.1525, 1e-04)


def test_dd_to_cup_lat():
    dd = -77.33587
    lat = lat_dd_to_cup_ddm(dd)
    assert lat == "7720.152S"

    dd = -dd
    lat = lat_dd_to_cup_ddm(dd)
    assert lat == "7720.152N"

    dd = -7.33587
    lat = lat_dd_to_cup_ddm(dd)
    assert lat == "0720.152S"


def test_dd_to_cup_lon():
    dd = -77.33587
    lon = lon_dd_to_cup_ddm(dd)
    assert lon == "07720.152W"

    dd = -dd
    lon = lon_dd_to_cup_ddm(dd)
    assert lon == "07720.152E"

    dd = -7.33587
    lon = lon_dd_to_cup_ddm(dd)
    assert lon == "00720.152W"

    dd = 138.21568
    lon = lon_dd_to_cup_ddm(dd)
    assert lon == "13812.941E"
