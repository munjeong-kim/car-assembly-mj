import sys
import time
from dataclasses import dataclass
from enum import Enum
from typing import Callable, List, Optional

CLEAR_SCREEN = "\033[H\033[2J"

CAR_ASCII_ART = (
    "        ______________\n"
    "       /|            |\n"
    "  ____/_|_____________|____\n"
    " |                      O  |\n"
    " '-(@)----------------(@)--'"
)
SEPARATOR = "==============================="


class Step(Enum):
    CAR_TYPE = 0
    ENGINE = 1
    BRAKE = 2
    STEERING = 3
    RUN_TEST = 4


class CarType(Enum):
    SEDAN = 1
    SUV = 2
    TRUCK = 3


class Engine(Enum):
    GM = 1
    TOYOTA = 2
    WIA = 3
    BROKEN = 4


class Brake(Enum):
    MANDO = 1
    CONTINENTAL = 2
    BOSCH = 3


class Steering(Enum):
    BOSCH = 1
    MOBIS = 2


@dataclass
class CarConfig:
    car_type: Optional[CarType] = None
    engine: Optional[Engine] = None
    brake: Optional[Brake] = None
    steering: Optional[Steering] = None


# Menu option labels. Also reused as run-output labels for CarType/Engine,
# whose casing happens to match between the menu and the run output.
CAR_TYPE_LABELS = {CarType.SEDAN: "Sedan", CarType.SUV: "SUV", CarType.TRUCK: "Truck"}
ENGINE_LABELS = {
    Engine.GM: "GM",
    Engine.TOYOTA: "TOYOTA",
    Engine.WIA: "WIA",
    Engine.BROKEN: "고장난 엔진",
}
BRAKE_LABELS = {Brake.MANDO: "MANDO", Brake.CONTINENTAL: "CONTINENTAL", Brake.BOSCH: "BOSCH"}
STEERING_LABELS = {Steering.BOSCH: "BOSCH", Steering.MOBIS: "MOBIS"}

# Run-output labels where casing differs from the menu label.
BRAKE_DISPLAY_LABELS = {Brake.MANDO: "Mando", Brake.CONTINENTAL: "Continental", Brake.BOSCH: "Bosch"}
STEERING_DISPLAY_LABELS = {Steering.BOSCH: "Bosch", Steering.MOBIS: "Mobis"}

CAR_TYPE_SELECTED_MESSAGES = {
    CarType.SEDAN: "차량 타입으로 Sedan을 선택하셨습니다.",
    CarType.SUV: "차량 타입으로 SUV을 선택하셨습니다.",
    CarType.TRUCK: "차량 타입으로 Truck을 선택하셨습니다.",
}
ENGINE_SELECTED_MESSAGES = {
    Engine.GM: "GM 엔진을 선택하셨습니다.",
    Engine.TOYOTA: "TOYOTA 엔진을 선택하셨습니다.",
    Engine.WIA: "WIA 엔진을 선택하셨습니다.",
    Engine.BROKEN: "고장난 엔진을 선택하셨습니다.",
}
BRAKE_SELECTED_MESSAGES = {
    Brake.MANDO: "MANDO 제동장치를 선택하셨습니다.",
    Brake.CONTINENTAL: "CONTINENTAL 제동장치를 선택하셨습니다.",
    Brake.BOSCH: "BOSCH 제동장치를 선택하셨습니다.",
}
STEERING_SELECTED_MESSAGES = {
    Steering.BOSCH: "BOSCH 조향장치를 선택하셨습니다.",
    Steering.MOBIS: "MOBIS 조향장치를 선택하셨습니다.",
}

STEP_TITLES = {
    Step.CAR_TYPE: "어떤 차량 타입을 선택할까요?",
    Step.ENGINE: "어떤 엔진을 탑재할까요?",
    Step.BRAKE: "어떤 제동장치를 선택할까요?",
    Step.STEERING: "어떤 조향장치를 선택할까요?",
}
STEP_OPTIONS = {
    Step.CAR_TYPE: CarType,
    Step.ENGINE: Engine,
    Step.BRAKE: Brake,
    Step.STEERING: Steering,
}
STEP_LABELS = {
    Step.CAR_TYPE: CAR_TYPE_LABELS,
    Step.ENGINE: ENGINE_LABELS,
    Step.BRAKE: BRAKE_LABELS,
    Step.STEERING: STEERING_LABELS,
}

# Allowed input ranges, derived from each step's Enum size so that adding a
# new CarType/Engine/Brake/Steering member automatically widens the range.
STEP_RANGES = {
    Step.CAR_TYPE: range(1, len(CarType) + 1),
    Step.ENGINE: range(0, len(Engine) + 1),
    Step.BRAKE: range(0, len(Brake) + 1),
    Step.STEERING: range(0, len(Steering) + 1),
    Step.RUN_TEST: range(0, 3),
}
STEP_RANGE_ERRORS = {
    Step.CAR_TYPE: "차량 타입은 1 ~ 3 범위만 선택 가능",
    Step.ENGINE: "엔진은 1 ~ 4 범위만 선택 가능",
    Step.BRAKE: "제동장치는 1 ~ 3 범위만 선택 가능",
    Step.STEERING: "조향장치는 1 ~ 2 범위만 선택 가능",
    Step.RUN_TEST: "Run 또는 Test 중 하나를 선택 필요",
}


@dataclass(frozen=True)
class Rule:
    reason: str
    violated: Callable[[CarConfig], bool]


COMPATIBILITY_RULES: List[Rule] = [
    Rule(
        "Sedan에는 Continental제동장치 사용 불가",
        lambda c: c.car_type == CarType.SEDAN and c.brake == Brake.CONTINENTAL,
    ),
    Rule(
        "SUV에는 TOYOTA엔진 사용 불가",
        lambda c: c.car_type == CarType.SUV and c.engine == Engine.TOYOTA,
    ),
    Rule(
        "Truck에는 WIA엔진 사용 불가",
        lambda c: c.car_type == CarType.TRUCK and c.engine == Engine.WIA,
    ),
    Rule(
        "Truck에는 Mando제동장치 사용 불가",
        lambda c: c.car_type == CarType.TRUCK and c.brake == Brake.MANDO,
    ),
    Rule(
        "Bosch제동장치에는 Bosch조향장치 이외 사용 불가",
        lambda c: c.brake == Brake.BOSCH and c.steering != Steering.BOSCH,
    ),
]
BROKEN_ENGINE_RULE = Rule("엔진이 고장나있습니다.", lambda c: c.engine == Engine.BROKEN)
ALL_RULES: List[Rule] = COMPATIBILITY_RULES + [BROKEN_ENGINE_RULE]


def find_violations(config: CarConfig, rules: List[Rule] = ALL_RULES) -> List[str]:
    return [rule.reason for rule in rules if rule.violated(config)]


@dataclass
class AssemblyResult:
    success: bool
    lines: List[str]


@dataclass
class TestResult:
    passed: bool
    reasons: List[str]


def delay(ms):
    time.sleep(ms / 1000.0)


def clear():
    sys.stdout.write(CLEAR_SCREEN)
    sys.stdout.flush()


def show_menu(step: Step) -> None:
    clear()
    if step == Step.CAR_TYPE:
        print(CAR_ASCII_ART)
        print(SEPARATOR)

    if step in STEP_TITLES:
        print(STEP_TITLES[step])
        if step != Step.CAR_TYPE:
            print("0. 뒤로가기")
        labels = STEP_LABELS[step]
        for i, member in enumerate(STEP_OPTIONS[step], start=1):
            print(f"{i}. {labels[member]}")
    else:
        print("멋진 차량이 완성되었습니다.")
        print("0. 처음 화면으로 돌아가기")
        print("1. RUN")
        print("2. Test")

    print(SEPARATOR)


def is_valid_range(step: Step, ans: int) -> bool:
    if ans not in STEP_RANGES[step]:
        print(f"ERROR :: {STEP_RANGE_ERRORS[step]}")
        return False
    return True


def select_car_type(config: CarConfig, choice: CarType) -> str:
    config.car_type = choice
    return CAR_TYPE_SELECTED_MESSAGES[choice]


def select_engine(config: CarConfig, choice: Engine) -> str:
    config.engine = choice
    return ENGINE_SELECTED_MESSAGES[choice]


def select_brake(config: CarConfig, choice: Brake) -> str:
    config.brake = choice
    return BRAKE_SELECTED_MESSAGES[choice]


def select_steering(config: CarConfig, choice: Steering) -> str:
    config.steering = choice
    return STEERING_SELECTED_MESSAGES[choice]


def assemble_car(config: CarConfig) -> AssemblyResult:
    if find_violations(config, COMPATIBILITY_RULES):
        return AssemblyResult(False, ["자동차가 동작되지 않습니다"])

    if config.engine == Engine.BROKEN:
        return AssemblyResult(False, ["엔진이 고장나있습니다.", "자동차가 움직이지 않습니다."])

    lines = [
        f"Car Type : {CAR_TYPE_LABELS[config.car_type]}",
        f"Engine   : {ENGINE_LABELS[config.engine]}",
        f"Brake    : {BRAKE_DISPLAY_LABELS[config.brake]}",
        f"Steering : {STEERING_DISPLAY_LABELS[config.steering]}",
        "자동차가 동작됩니다.",
    ]
    return AssemblyResult(True, lines)


def run_produced_car(config: CarConfig) -> None:
    for line in assemble_car(config).lines:
        print(line)


def test_car_config(config: CarConfig) -> TestResult:
    violations = find_violations(config, ALL_RULES)
    return TestResult(passed=not violations, reasons=violations)


def test_produced_car(config: CarConfig) -> None:
    result = test_car_config(config)
    if result.passed:
        print("PASS")
        return
    print("FAIL")
    for reason in result.reasons:
        print(reason)


def next_step(step: Step) -> Step:
    if step == Step.RUN_TEST:
        return Step.CAR_TYPE
    if step == Step.CAR_TYPE:
        return step
    return Step(step.value - 1)


def advance(step: Step, ans: int, config: CarConfig) -> Step:
    if step == Step.CAR_TYPE:
        print(select_car_type(config, CarType(ans)))
        return Step.ENGINE
    if step == Step.ENGINE:
        print(select_engine(config, Engine(ans)))
        return Step.BRAKE
    if step == Step.BRAKE:
        print(select_brake(config, Brake(ans)))
        return Step.STEERING
    if step == Step.STEERING:
        print(select_steering(config, Steering(ans)))
        return Step.RUN_TEST
    return step


def main() -> None:
    step = Step.CAR_TYPE
    config = CarConfig()

    while True:
        show_menu(step)
        buf = input("INPUT > ").strip()

        if buf == "exit":
            print("바이바이")
            break

        try:
            ans = int(buf)
        except ValueError:
            print("ERROR :: 숫자만 입력 가능")
            delay(800)
            continue

        if not is_valid_range(step, ans):
            delay(800)
            continue

        if ans == 0:
            step = next_step(step)
            continue

        if step == Step.RUN_TEST:
            if ans == 1:
                run_produced_car(config)
                delay(2000)
            elif ans == 2:
                print("Test...")
                delay(1500)
                test_produced_car(config)
                delay(2000)
            continue

        step = advance(step, ans, config)
        delay(800)


if __name__ == "__main__":
    main()
