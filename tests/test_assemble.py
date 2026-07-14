import pytest

import assemble


@pytest.fixture(autouse=True)
def reset_globals():
    assemble.q0 = 0
    assemble.q1 = 0
    assemble.q2 = 0
    assemble.q3 = 0
    assemble.q4 = 0
    yield


# ---------------------------------------------------------------------------
# is_valid_range
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("ans", [1, 2, 3])
def test_valid_range_step0_valid(ans):
    assert assemble.is_valid_range(0, ans) is True


@pytest.mark.parametrize("ans", [0, 4, -1])
def test_valid_range_step0_invalid(ans):
    assert assemble.is_valid_range(0, ans) is False


@pytest.mark.parametrize("ans", [0, 1, 2, 3, 4])
def test_valid_range_step1_valid(ans):
    assert assemble.is_valid_range(1, ans) is True


@pytest.mark.parametrize("ans", [-1, 5])
def test_valid_range_step1_invalid(ans):
    assert assemble.is_valid_range(1, ans) is False


@pytest.mark.parametrize("ans", [0, 1, 2, 3])
def test_valid_range_step2_valid(ans):
    assert assemble.is_valid_range(2, ans) is True


@pytest.mark.parametrize("ans", [-1, 4])
def test_valid_range_step2_invalid(ans):
    assert assemble.is_valid_range(2, ans) is False


@pytest.mark.parametrize("ans", [0, 1, 2])
def test_valid_range_step3_valid(ans):
    assert assemble.is_valid_range(3, ans) is True


@pytest.mark.parametrize("ans", [-1, 3])
def test_valid_range_step3_invalid(ans):
    assert assemble.is_valid_range(3, ans) is False


@pytest.mark.parametrize("ans", [0, 1, 2])
def test_valid_range_step4_valid(ans):
    assert assemble.is_valid_range(4, ans) is True


@pytest.mark.parametrize("ans", [-1, 3])
def test_valid_range_step4_invalid(ans):
    assert assemble.is_valid_range(4, ans) is False


# ---------------------------------------------------------------------------
# select_* : global state update
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("ans", [1, 2, 3])
def test_select_car_type_sets_q0(ans):
    assemble.select_car_type(ans)
    assert assemble.q0 == ans


@pytest.mark.parametrize("ans", [1, 2, 3, 4])
def test_select_engine_sets_q1(ans):
    assemble.select_engine(ans)
    assert assemble.q1 == ans


@pytest.mark.parametrize("ans", [1, 2, 3])
def test_select_brake_sets_q2(ans):
    assemble.select_brake(ans)
    assert assemble.q2 == ans


@pytest.mark.parametrize("ans", [1, 2])
def test_select_steering_sets_q3(ans):
    assemble.select_steering(ans)
    assert assemble.q3 == ans


# ---------------------------------------------------------------------------
# is_valid_check : compatibility rules
# ---------------------------------------------------------------------------

def _set_state(car_type, engine, brake, steering):
    assemble.q0 = car_type
    assemble.q1 = engine
    assemble.q2 = brake
    assemble.q3 = steering


def test_valid_combo_is_valid():
    # Sedan + GM + Mando + Mobis: no rule violated
    _set_state(assemble.SEDAN, assemble.GM, assemble.MANDO, assemble.MOBIS)
    assert assemble.is_valid_check() is True


def test_sedan_continental_invalid():
    _set_state(assemble.SEDAN, assemble.GM, assemble.CONTINENTAL, assemble.MOBIS)
    assert assemble.is_valid_check() is False


def test_suv_toyota_invalid():
    _set_state(assemble.SUV, assemble.TOYOTA, assemble.MANDO, assemble.MOBIS)
    assert assemble.is_valid_check() is False


def test_truck_wia_invalid():
    _set_state(assemble.TRUCK, assemble.WIA, assemble.CONTINENTAL, assemble.MOBIS)
    assert assemble.is_valid_check() is False


def test_truck_mando_invalid():
    _set_state(assemble.TRUCK, assemble.GM, assemble.MANDO, assemble.MOBIS)
    assert assemble.is_valid_check() is False


def test_bosch_brake_requires_bosch_steering_invalid():
    _set_state(assemble.SEDAN, assemble.GM, assemble.BOSCH_B, assemble.MOBIS)
    assert assemble.is_valid_check() is False


def test_bosch_brake_with_bosch_steering_valid():
    _set_state(assemble.SEDAN, assemble.GM, assemble.BOSCH_B, assemble.BOSCH_S)
    assert assemble.is_valid_check() is True


# ---------------------------------------------------------------------------
# run_produced_car
# ---------------------------------------------------------------------------

def test_run_produced_car_valid_combo(capsys):
    _set_state(assemble.SEDAN, assemble.GM, assemble.MANDO, assemble.MOBIS)
    assemble.run_produced_car()
    out = capsys.readouterr().out
    assert "Car Type : Sedan" in out
    assert "Engine   : GM" in out
    assert "Brake    : Mando" in out
    assert "Steering : Mobis" in out
    assert "자동차가 동작됩니다." in out


def test_run_produced_car_invalid_combo(capsys):
    _set_state(assemble.SEDAN, assemble.GM, assemble.CONTINENTAL, assemble.MOBIS)
    assemble.run_produced_car()
    out = capsys.readouterr().out
    assert "자동차가 동작되지 않습니다" in out


def test_run_produced_car_broken_engine(capsys):
    _set_state(assemble.SEDAN, 4, assemble.MANDO, assemble.MOBIS)
    assemble.run_produced_car()
    out = capsys.readouterr().out
    assert "엔진이 고장나있습니다." in out
    assert "자동차가 움직이지 않습니다." in out


# ---------------------------------------------------------------------------
# test_produced_car
# ---------------------------------------------------------------------------

def test_test_produced_car_pass(capsys):
    _set_state(assemble.SEDAN, assemble.GM, assemble.MANDO, assemble.MOBIS)
    assemble.test_produced_car()
    out = capsys.readouterr().out
    assert "PASS" in out


def test_test_produced_car_fail_sedan_continental(capsys):
    _set_state(assemble.SEDAN, assemble.GM, assemble.CONTINENTAL, assemble.MOBIS)
    assemble.test_produced_car()
    out = capsys.readouterr().out
    assert "FAIL" in out
    assert "Sedan에는 Continental제동장치 사용 불가" in out


def test_test_produced_car_fail_suv_toyota(capsys):
    _set_state(assemble.SUV, assemble.TOYOTA, assemble.MANDO, assemble.MOBIS)
    assemble.test_produced_car()
    out = capsys.readouterr().out
    assert "FAIL" in out
    assert "SUV에는 TOYOTA엔진 사용 불가" in out


def test_test_produced_car_fail_truck_wia(capsys):
    _set_state(assemble.TRUCK, assemble.WIA, assemble.CONTINENTAL, assemble.MOBIS)
    assemble.test_produced_car()
    out = capsys.readouterr().out
    assert "FAIL" in out
    assert "Truck에는 WIA엔진 사용 불가" in out


def test_test_produced_car_fail_truck_mando(capsys):
    _set_state(assemble.TRUCK, assemble.GM, assemble.MANDO, assemble.MOBIS)
    assemble.test_produced_car()
    out = capsys.readouterr().out
    assert "FAIL" in out
    assert "Truck에는 Mando제동장치 사용 불가" in out


def test_test_produced_car_fail_bosch_brake_non_bosch_steering(capsys):
    _set_state(assemble.SEDAN, assemble.GM, assemble.BOSCH_B, assemble.MOBIS)
    assemble.test_produced_car()
    out = capsys.readouterr().out
    assert "FAIL" in out
    assert "Bosch제동장치에는 Bosch조향장치 이외 사용 불가" in out


# ---------------------------------------------------------------------------
# run_produced_car : remaining print branches (SUV/Truck, TOYOTA/WIA, Continental/Bosch, Bosch steering)
# ---------------------------------------------------------------------------

def test_run_produced_car_suv(capsys):
    _set_state(assemble.SUV, assemble.GM, assemble.MANDO, assemble.MOBIS)
    assemble.run_produced_car()
    out = capsys.readouterr().out
    assert "Car Type : SUV" in out


def test_run_produced_car_truck_and_continental(capsys):
    _set_state(assemble.TRUCK, assemble.GM, assemble.CONTINENTAL, assemble.MOBIS)
    assemble.run_produced_car()
    out = capsys.readouterr().out
    assert "Car Type : Truck" in out
    assert "Brake    : Continental" in out


def test_run_produced_car_toyota_engine(capsys):
    _set_state(assemble.SEDAN, assemble.TOYOTA, assemble.MANDO, assemble.MOBIS)
    assemble.run_produced_car()
    out = capsys.readouterr().out
    assert "Engine   : TOYOTA" in out


def test_run_produced_car_wia_engine(capsys):
    _set_state(assemble.SEDAN, assemble.WIA, assemble.MANDO, assemble.MOBIS)
    assemble.run_produced_car()
    out = capsys.readouterr().out
    assert "Engine   : WIA" in out


def test_run_produced_car_bosch_brake_and_steering(capsys):
    _set_state(assemble.SEDAN, assemble.GM, assemble.BOSCH_B, assemble.BOSCH_S)
    assemble.run_produced_car()
    out = capsys.readouterr().out
    assert "Brake    : Bosch" in out
    assert "Steering : Bosch" in out


# ---------------------------------------------------------------------------
# show_menu
# ---------------------------------------------------------------------------

def test_show_menu_step0(capsys):
    assemble.show_menu(0)
    out = capsys.readouterr().out
    assert "어떤 차량 타입을 선택할까요?" in out
    assert "1. Sedan" in out
    assert "2. SUV" in out
    assert "3. Truck" in out


def test_show_menu_step1(capsys):
    assemble.show_menu(1)
    out = capsys.readouterr().out
    assert "어떤 엔진을 탑재할까요?" in out
    assert "4. 고장난 엔진" in out


def test_show_menu_step2(capsys):
    assemble.show_menu(2)
    out = capsys.readouterr().out
    assert "어떤 제동장치를 선택할까요?" in out
    assert "3. BOSCH" in out


def test_show_menu_step3(capsys):
    assemble.show_menu(3)
    out = capsys.readouterr().out
    assert "어떤 조향장치를 선택할까요?" in out
    assert "2. MOBIS" in out


def test_show_menu_step4(capsys):
    assemble.show_menu(4)
    out = capsys.readouterr().out
    assert "멋진 차량이 완성되었습니다." in out
    assert "1. RUN" in out
    assert "2. Test" in out
