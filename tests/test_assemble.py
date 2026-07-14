import pytest

import assemble
from assemble import (
    ALL_RULES,
    COMPATIBILITY_RULES,
    Brake,
    CarConfig,
    CarType,
    Engine,
    Step,
    Steering,
)


def make_config(car_type=None, engine=None, brake=None, steering=None) -> CarConfig:
    return CarConfig(car_type=car_type, engine=engine, brake=brake, steering=steering)


# ---------------------------------------------------------------------------
# is_valid_range
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("ans", [1, 2, 3])
def test_valid_range_car_type_valid(ans):
    assert assemble.is_valid_range(Step.CAR_TYPE, ans) is True


@pytest.mark.parametrize("ans", [0, 4, -1])
def test_valid_range_car_type_invalid(ans):
    assert assemble.is_valid_range(Step.CAR_TYPE, ans) is False


@pytest.mark.parametrize("ans", [0, 1, 2, 3, 4])
def test_valid_range_engine_valid(ans):
    assert assemble.is_valid_range(Step.ENGINE, ans) is True


@pytest.mark.parametrize("ans", [-1, 5])
def test_valid_range_engine_invalid(ans):
    assert assemble.is_valid_range(Step.ENGINE, ans) is False


@pytest.mark.parametrize("ans", [0, 1, 2, 3])
def test_valid_range_brake_valid(ans):
    assert assemble.is_valid_range(Step.BRAKE, ans) is True


@pytest.mark.parametrize("ans", [-1, 4])
def test_valid_range_brake_invalid(ans):
    assert assemble.is_valid_range(Step.BRAKE, ans) is False


@pytest.mark.parametrize("ans", [0, 1, 2])
def test_valid_range_steering_valid(ans):
    assert assemble.is_valid_range(Step.STEERING, ans) is True


@pytest.mark.parametrize("ans", [-1, 3])
def test_valid_range_steering_invalid(ans):
    assert assemble.is_valid_range(Step.STEERING, ans) is False


@pytest.mark.parametrize("ans", [0, 1, 2])
def test_valid_range_run_test_valid(ans):
    assert assemble.is_valid_range(Step.RUN_TEST, ans) is True


@pytest.mark.parametrize("ans", [-1, 3])
def test_valid_range_run_test_invalid(ans):
    assert assemble.is_valid_range(Step.RUN_TEST, ans) is False


def test_step_ranges_track_enum_size():
    assert assemble.STEP_RANGES[Step.CAR_TYPE] == range(1, len(CarType) + 1)
    assert assemble.STEP_RANGES[Step.ENGINE] == range(0, len(Engine) + 1)
    assert assemble.STEP_RANGES[Step.BRAKE] == range(0, len(Brake) + 1)
    assert assemble.STEP_RANGES[Step.STEERING] == range(0, len(Steering) + 1)


# ---------------------------------------------------------------------------
# select_* : state update + returned message (no printing involved)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("choice", list(CarType))
def test_select_car_type_updates_config_and_returns_message(choice):
    config = make_config()
    message = assemble.select_car_type(config, choice)
    assert config.car_type == choice
    assert assemble.CAR_TYPE_LABELS[choice] in message


@pytest.mark.parametrize("choice", list(Engine))
def test_select_engine_updates_config_and_returns_message(choice):
    config = make_config()
    message = assemble.select_engine(config, choice)
    assert config.engine == choice
    assert message == assemble.ENGINE_SELECTED_MESSAGES[choice]


@pytest.mark.parametrize("choice", list(Brake))
def test_select_brake_updates_config_and_returns_message(choice):
    config = make_config()
    message = assemble.select_brake(config, choice)
    assert config.brake == choice
    assert message == assemble.BRAKE_SELECTED_MESSAGES[choice]


@pytest.mark.parametrize("choice", list(Steering))
def test_select_steering_updates_config_and_returns_message(choice):
    config = make_config()
    message = assemble.select_steering(config, choice)
    assert config.steering == choice
    assert message == assemble.STEERING_SELECTED_MESSAGES[choice]


# ---------------------------------------------------------------------------
# find_violations : compatibility rules (single source of truth)
# ---------------------------------------------------------------------------

def test_valid_combo_has_no_violations():
    config = make_config(CarType.SEDAN, Engine.GM, Brake.MANDO, Steering.MOBIS)
    assert assemble.find_violations(config) == []


def test_sedan_continental_is_a_violation():
    config = make_config(CarType.SEDAN, Engine.GM, Brake.CONTINENTAL, Steering.MOBIS)
    assert "Sedan에는 Continental제동장치 사용 불가" in assemble.find_violations(config)


def test_suv_toyota_is_a_violation():
    config = make_config(CarType.SUV, Engine.TOYOTA, Brake.MANDO, Steering.MOBIS)
    assert "SUV에는 TOYOTA엔진 사용 불가" in assemble.find_violations(config)


def test_truck_wia_is_a_violation():
    config = make_config(CarType.TRUCK, Engine.WIA, Brake.CONTINENTAL, Steering.MOBIS)
    assert "Truck에는 WIA엔진 사용 불가" in assemble.find_violations(config)


def test_truck_mando_is_a_violation():
    config = make_config(CarType.TRUCK, Engine.GM, Brake.MANDO, Steering.MOBIS)
    assert "Truck에는 Mando제동장치 사용 불가" in assemble.find_violations(config)


def test_bosch_brake_requires_bosch_steering():
    config = make_config(CarType.SEDAN, Engine.GM, Brake.BOSCH, Steering.MOBIS)
    assert "Bosch제동장치에는 Bosch조향장치 이외 사용 불가" in assemble.find_violations(config)


def test_bosch_brake_with_bosch_steering_has_no_violation():
    config = make_config(CarType.SEDAN, Engine.GM, Brake.BOSCH, Steering.BOSCH)
    assert assemble.find_violations(config) == []


def test_broken_engine_is_a_violation_of_all_rules():
    config = make_config(CarType.SEDAN, Engine.BROKEN, Brake.MANDO, Steering.MOBIS)
    assert "엔진이 고장나있습니다." in assemble.find_violations(config, ALL_RULES)


def test_broken_engine_is_not_checked_by_compatibility_rules_alone():
    config = make_config(CarType.SEDAN, Engine.BROKEN, Brake.MANDO, Steering.MOBIS)
    assert assemble.find_violations(config, COMPATIBILITY_RULES) == []


def test_multiple_violations_are_all_reported():
    # Sedan + Continental (violation 1) and Bosch-brake-without-Bosch-steering
    # cannot co-occur since Sedan+Continental already picks Continental as
    # the brake; use Truck+Mando + Bosch steering mismatch is not composable
    # either. Compose two independently-triggerable rules instead:
    # SUV + TOYOTA engine, and Bosch brake without Bosch steering.
    config = make_config(CarType.SUV, Engine.TOYOTA, Brake.BOSCH, Steering.MOBIS)
    violations = assemble.find_violations(config)
    assert "SUV에는 TOYOTA엔진 사용 불가" in violations
    assert "Bosch제동장치에는 Bosch조향장치 이외 사용 불가" in violations
    assert len(violations) == 2


def test_broken_engine_combined_with_compatibility_violation():
    config = make_config(CarType.SUV, Engine.BROKEN, Brake.MANDO, Steering.MOBIS)
    violations = assemble.find_violations(config)
    assert "엔진이 고장나있습니다." in violations
    # Engine.BROKEN != Engine.TOYOTA, so the SUV+TOYOTA rule does not fire here;
    # only the broken-engine rule applies for this particular config.
    assert len(violations) == 1


# ---------------------------------------------------------------------------
# assemble_car / run_produced_car
# ---------------------------------------------------------------------------

def test_assemble_car_valid_combo_succeeds():
    config = make_config(CarType.SEDAN, Engine.GM, Brake.MANDO, Steering.MOBIS)
    result = assemble.assemble_car(config)
    assert result.success is True
    assert "Car Type : Sedan" in result.lines
    assert "Engine   : GM" in result.lines
    assert "Brake    : Mando" in result.lines
    assert "Steering : Mobis" in result.lines
    assert "자동차가 동작됩니다." in result.lines


def test_assemble_car_invalid_combo_fails():
    config = make_config(CarType.SEDAN, Engine.GM, Brake.CONTINENTAL, Steering.MOBIS)
    result = assemble.assemble_car(config)
    assert result.success is False
    assert result.lines == ["자동차가 동작되지 않습니다"]


def test_assemble_car_broken_engine_fails_with_specific_message():
    config = make_config(CarType.SEDAN, Engine.BROKEN, Brake.MANDO, Steering.MOBIS)
    result = assemble.assemble_car(config)
    assert result.success is False
    assert result.lines == ["엔진이 고장나있습니다.", "자동차가 움직이지 않습니다."]


def test_assemble_car_compatibility_violation_takes_priority_over_broken_engine():
    # Sedan+Continental is a structural violation AND the engine is broken;
    # the generic failure message must win, matching the original RUN behavior.
    config = make_config(CarType.SEDAN, Engine.BROKEN, Brake.CONTINENTAL, Steering.MOBIS)
    result = assemble.assemble_car(config)
    assert result.lines == ["자동차가 동작되지 않습니다"]


@pytest.mark.parametrize(
    "car_type, engine, brake, steering, expected",
    [
        (CarType.SUV, Engine.GM, Brake.MANDO, Steering.MOBIS, "Car Type : SUV"),
        (CarType.TRUCK, Engine.GM, Brake.CONTINENTAL, Steering.MOBIS, "Car Type : Truck"),
        (CarType.SEDAN, Engine.TOYOTA, Brake.MANDO, Steering.MOBIS, "Engine   : TOYOTA"),
        (CarType.SEDAN, Engine.WIA, Brake.MANDO, Steering.MOBIS, "Engine   : WIA"),
        (CarType.TRUCK, Engine.GM, Brake.CONTINENTAL, Steering.MOBIS, "Brake    : Continental"),
        (CarType.SEDAN, Engine.GM, Brake.BOSCH, Steering.BOSCH, "Brake    : Bosch"),
        (CarType.SEDAN, Engine.GM, Brake.BOSCH, Steering.BOSCH, "Steering : Bosch"),
    ],
)
def test_assemble_car_covers_every_valid_component_label(car_type, engine, brake, steering, expected):
    config = make_config(car_type, engine, brake, steering)
    result = assemble.assemble_car(config)
    assert expected in result.lines


def test_run_produced_car_prints_assembly_result(capsys):
    config = make_config(CarType.SEDAN, Engine.GM, Brake.MANDO, Steering.MOBIS)
    assemble.run_produced_car(config)
    out = capsys.readouterr().out
    assert "자동차가 동작됩니다." in out


# ---------------------------------------------------------------------------
# test_car_config / test_produced_car
# ---------------------------------------------------------------------------

def test_test_car_config_pass():
    config = make_config(CarType.SEDAN, Engine.GM, Brake.MANDO, Steering.MOBIS)
    result = assemble.test_car_config(config)
    assert result.passed is True
    assert result.reasons == []


def test_test_car_config_fail_single_reason():
    config = make_config(CarType.SEDAN, Engine.GM, Brake.CONTINENTAL, Steering.MOBIS)
    result = assemble.test_car_config(config)
    assert result.passed is False
    assert result.reasons == ["Sedan에는 Continental제동장치 사용 불가"]


def test_test_car_config_fail_broken_engine():
    config = make_config(CarType.SEDAN, Engine.BROKEN, Brake.MANDO, Steering.MOBIS)
    result = assemble.test_car_config(config)
    assert result.passed is False
    assert result.reasons == ["엔진이 고장나있습니다."]


def test_test_car_config_reports_all_violations():
    config = make_config(CarType.SUV, Engine.TOYOTA, Brake.BOSCH, Steering.MOBIS)
    result = assemble.test_car_config(config)
    assert result.passed is False
    assert result.reasons == [
        "SUV에는 TOYOTA엔진 사용 불가",
        "Bosch제동장치에는 Bosch조향장치 이외 사용 불가",
    ]


def test_test_produced_car_pass(capsys):
    config = make_config(CarType.SEDAN, Engine.GM, Brake.MANDO, Steering.MOBIS)
    assemble.test_produced_car(config)
    out = capsys.readouterr().out
    assert "PASS" in out
    assert "FAIL" not in out


def test_test_produced_car_fail_prints_all_reasons(capsys):
    config = make_config(CarType.SUV, Engine.TOYOTA, Brake.BOSCH, Steering.MOBIS)
    assemble.test_produced_car(config)
    out = capsys.readouterr().out
    assert "FAIL" in out
    assert "SUV에는 TOYOTA엔진 사용 불가" in out
    assert "Bosch제동장치에는 Bosch조향장치 이외 사용 불가" in out


def test_test_produced_car_fail_broken_engine(capsys):
    config = make_config(CarType.SEDAN, Engine.BROKEN, Brake.MANDO, Steering.MOBIS)
    assemble.test_produced_car(config)
    out = capsys.readouterr().out
    assert "FAIL" in out
    assert "엔진이 고장나있습니다." in out


def test_test_produced_car_fail_broken_engine_plus_other_violation(capsys):
    config = make_config(CarType.SUV, Engine.BROKEN, Brake.MANDO, Steering.MOBIS)
    assemble.test_produced_car(config)
    out = capsys.readouterr().out
    assert "FAIL" in out
    assert "엔진이 고장나있습니다." in out


# ---------------------------------------------------------------------------
# next_step / advance : pure step-transition logic
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "step, expected",
    [
        (Step.ENGINE, Step.CAR_TYPE),
        (Step.BRAKE, Step.ENGINE),
        (Step.STEERING, Step.BRAKE),
        (Step.RUN_TEST, Step.CAR_TYPE),
    ],
)
def test_next_step_goes_back(step, expected):
    assert assemble.next_step(step) == expected


def test_advance_car_type_sets_config_and_moves_to_engine(capsys):
    config = make_config()
    step = assemble.advance(Step.CAR_TYPE, 1, config)
    assert step == Step.ENGINE
    assert config.car_type == CarType.SEDAN


def test_advance_engine_sets_config_and_moves_to_brake():
    config = make_config()
    step = assemble.advance(Step.ENGINE, 2, config)
    assert step == Step.BRAKE
    assert config.engine == Engine.TOYOTA


def test_advance_brake_sets_config_and_moves_to_steering():
    config = make_config()
    step = assemble.advance(Step.BRAKE, 3, config)
    assert step == Step.STEERING
    assert config.brake == Brake.BOSCH


def test_advance_steering_sets_config_and_moves_to_run_test():
    config = make_config()
    step = assemble.advance(Step.STEERING, 1, config)
    assert step == Step.RUN_TEST
    assert config.steering == Steering.BOSCH


# ---------------------------------------------------------------------------
# show_menu
# ---------------------------------------------------------------------------

def test_show_menu_car_type(capsys):
    assemble.show_menu(Step.CAR_TYPE)
    out = capsys.readouterr().out
    assert "어떤 차량 타입을 선택할까요?" in out
    assert "1. Sedan" in out
    assert "2. SUV" in out
    assert "3. Truck" in out
    assert "0. 뒤로가기" not in out


def test_show_menu_engine(capsys):
    assemble.show_menu(Step.ENGINE)
    out = capsys.readouterr().out
    assert "어떤 엔진을 탑재할까요?" in out
    assert "0. 뒤로가기" in out
    assert "4. 고장난 엔진" in out


def test_show_menu_brake(capsys):
    assemble.show_menu(Step.BRAKE)
    out = capsys.readouterr().out
    assert "어떤 제동장치를 선택할까요?" in out
    assert "3. BOSCH" in out


def test_show_menu_steering(capsys):
    assemble.show_menu(Step.STEERING)
    out = capsys.readouterr().out
    assert "어떤 조향장치를 선택할까요?" in out
    assert "2. MOBIS" in out


def test_show_menu_run_test(capsys):
    assemble.show_menu(Step.RUN_TEST)
    out = capsys.readouterr().out
    assert "멋진 차량이 완성되었습니다." in out
    assert "1. RUN" in out
    assert "2. Test" in out


# ---------------------------------------------------------------------------
# show_menu / is_valid_range : options and ranges must track Enum membership,
# not a hardcoded count. These tests derive their expectations from the
# Enum/labels themselves, so they still pass if a member is added or removed
# without anyone touching show_menu()/STEP_RANGES by hand.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "step, enum_cls",
    [
        (Step.CAR_TYPE, CarType),
        (Step.ENGINE, Engine),
        (Step.BRAKE, Brake),
        (Step.STEERING, Steering),
    ],
)
def test_show_menu_option_count_matches_enum_size(step, enum_cls, capsys):
    assemble.show_menu(step)
    out = capsys.readouterr().out
    labels = assemble.STEP_LABELS[step]
    expected_lines = [f"{i}. {labels[member]}" for i, member in enumerate(enum_cls, start=1)]

    assert len(expected_lines) == len(enum_cls)
    for line in expected_lines:
        assert line in out
    # no extra numbered option beyond the last enum member
    assert f"{len(enum_cls) + 1}. " not in out


@pytest.mark.parametrize(
    "step, enum_cls",
    [
        (Step.CAR_TYPE, CarType),
        (Step.ENGINE, Engine),
        (Step.BRAKE, Brake),
        (Step.STEERING, Steering),
    ],
)
def test_is_valid_range_upper_bound_matches_enum_size(step, enum_cls):
    # Valid range is always 0/1..len(enum_cls) — the upper bound equals the
    # enum's member count for every step, regardless of the lower bound.
    assert assemble.is_valid_range(step, len(enum_cls)) is True
    assert assemble.is_valid_range(step, len(enum_cls) + 1) is False


# ---------------------------------------------------------------------------
# read_input / handle_run_test : main()'s input()/delay() side effects wrapped
# behind thin, mockable seams so the surrounding logic stays testable.
# ---------------------------------------------------------------------------

def test_read_input_strips_whitespace(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda prompt="": "  42  ")
    assert assemble.read_input() == "42"


def test_handle_run_test_run_prints_assembly_result(monkeypatch, capsys):
    monkeypatch.setattr(assemble, "delay", lambda ms: None)
    config = make_config(CarType.SEDAN, Engine.GM, Brake.MANDO, Steering.MOBIS)
    assemble.handle_run_test(1, config)
    out = capsys.readouterr().out
    assert "자동차가 동작됩니다." in out


def test_handle_run_test_test_prints_fail_reasons(monkeypatch, capsys):
    monkeypatch.setattr(assemble, "delay", lambda ms: None)
    config = make_config(CarType.SEDAN, Engine.GM, Brake.CONTINENTAL, Steering.MOBIS)
    assemble.handle_run_test(2, config)
    out = capsys.readouterr().out
    assert "Test..." in out
    assert "FAIL" in out
    assert "Sedan에는 Continental제동장치 사용 불가" in out


def test_handle_run_test_ignores_out_of_range_answer(monkeypatch, capsys):
    monkeypatch.setattr(assemble, "delay", lambda ms: None)
    config = make_config(CarType.SEDAN, Engine.GM, Brake.MANDO, Steering.MOBIS)
    assemble.handle_run_test(99, config)
    out = capsys.readouterr().out
    assert out == ""
