# CLAUDE.md

이 저장소는 CLI 메뉴 기반으로 차량(자동차)을 조립하는 시뮬레이션 프로그램이다.

## 개요

사용자가 차례로 차량 Type → Engine → Brake System → Steering System를 선택하면, 선택된 부품 조합의 유효성을 검사한 뒤 차량을 조립(RUN) 또는 유효성만 검사(TEST)할 수 있다.

## 진행 단계 (step)

0. 차량 Type 선택 (Sedan / SUV / Truck / 고장난 엔진)
1. Engine 선택 (GM / TOYOTA / WIA)
2. Brake System 선택 (MANDO / CONTINENTAL / BOSCH)
3. Steering System 선택 (BOSCH / MOBIS)
4. 완료 화면 (RUN 또는 TEST 선택)

각 단계에서 `0`을 입력하면 이전 단계로 돌아간다 (완료 화면에서는 처음 화면으로).
`exit` 입력 시 즉시 프로그램 종료.

## 입력 유효 범위

| step | 항목       | 허용 값 |
|---|----------|---|
| 0 | 차량 Type  | 1~3 |
| 1 | Engine       | 0~4 (0=뒤로가기, 4=고장난 엔진) |
| 2 | Brake System     | 0~3 |
| 3 | Steering System     | 0~2 |
| 4 | Run/Test | 0~2 |

범위를 벗어나거나 숫자가 아닌 입력은 에러 메시지를 출력하고 동일 단계에 머무른다.

## 부품 조합 제한사항 (호환성 규칙)

다음 조합은 유효하지 않으며, RUN 시 "자동차가 동작되지 않습니다", TEST 시 각 사유와 함께 FAIL로 판정된다.

- Sedan + Continental Brake System → 불가
- SUV + TOYOTA Engine → 불가
- Truck + WIA Engine → 불가
- Truck + MANDO Brake System → 불가
- BOSCH(Brake, `BOSCH_B`) 선택 시 Steering는 반드시 BOSCH(`BOSCH_S`)여야 함. 그 외 (MOBIS) 조합 불가

위 규칙 외의 모든 조합은 유효(PASS)하다.

## 고장난 엔진 처리

엔진 선택에서 `4`(고장난 엔진)을 선택하면, 위 호환성 규칙과 별개로 RUN 시 항상 "엔진이 고장나있습니다 / 자동차가 움직이지 않습니다"를 출력하고 차량이 동작하지 않는다. 

## 상수 정의

- 차량 Type: `SEDAN=1`, `SUV=2`, `TRUCK=3`
- Engine: `GM=1`, `TOYOTA=2`, `WIA=3` (엔진 4는 고장난 엔진, 별도 상수 없음)
- Brake System: `MANDO=1`, `CONTINENTAL=2`, `BOSCH_B=3`
- Steering System: `BOSCH_S=1`, `MOBIS=2`
