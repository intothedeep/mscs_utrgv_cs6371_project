# 연구 제안서: 갈라지고 합치는 집단을 따라가는 군집 로봇

**한 줄 요약: 표적 집단이 갈라지면 같이 갈라지고, 합쳐지면 같이 합쳐진다. 집단을 추적하고 원하는 곳으로 모는 드론·로봇 [군집(swarm)](#term-swarm)을 만든다.**

- 작성일: 2026-11-10
- 근거: `research/survey.md`(태그 SMT)와 메인 세션의 채팅 답변뿐이다.
- 숫자, 점수, 출처 ID, 판정은 그 근거에서 그대로 옮겼다. 새로 계산하지 않았다.
- 표시 `(inference)`와 `추정`은 근거 문서의 표시를 지켰다.

## 0. 결론 먼저

- **조각마다 선행 연구가 있다.** 반복 분열-융합에서 "관측률 대 전환 빈도"를 잰 출처는 이번 조사에서 찾지 못했다.
- 이 빈틈은 "출처를 못 찾음"이다. 아무도 안 했다는 증거가 아니다.
- 새 기여 후보는 두 곳이다. 4단계(분열·배정)와 6단계(몰이)다.
- 한 논문은 기여를 한 단계에만 둔다.
- 점수는 survey가 정한 값이 우선한다 (§7.2).

## 1. 문제와 동기

### 1.1 풀려던 문제

소유자 원문 (2026-11-10):

> 감시 swarm. 집단이 있고 그 집단이 갈라지면 swarm 도 집단 처럼 분리하고 분리된 swarm 들이 계속 나눠지고 집단이 합쳐지면 합쳐지고 그리고 포메이션은 숫자에 맞게 자동 조절되고

```
 t1: 표적 한 무리            t2: 표적이 둘로 갈림          t3: 다시 합침
   o o o o o o                o o o      o o o            o o o o o o
  [  링 하나  ]              [링 A]      [링 B]          [  링 하나  ]
   로봇 12대                 로봇 6대     로봇 6대          로봇 12대
```

- 표적(target)은 함께 움직이는 무리다.
- 군집도 표적을 따라 갈라지고 합친다.
- 갈라짐은 여러 번 이어질 수 있다.
- [대형(formation)](#term-formation)은 로봇 수와 무리 크기에 맞춰 크기를 바꾼다.

### 1.2 임무와 비전

| 항목 | 내용 |
| --- | --- |
| 임무(mission) | 갈라지고 합치는 집단을 군집이 따라가며 관측한다 |
| 비전(vision) | 군집이 집단을 찾아 원하는 방향으로 이동시킨다 |

소유자 원문 (2026-11-10):

> 드론을 펼치고 자동으로 분열후 목표 대상 또는 그룹을 찾아서 원하는 방향으로 이동 시키기?

### 1.3 왜 군집이어야 하나 (inference)

```
 분열 시점과 개수 모름 ──> 미리 짤 수 없다
 로봇은 지역 정보만 가짐 ──> 각자 판단한다
 중앙 제어기가 있으면 ──> 군집이 필요 없어진다
```

- 집단이 언제, 몇 개로 갈라질지 미리 모른다.
- 로봇은 지역 정보만으로 결정한다.
- 중앙 제어기가 모든 것을 정하면 군집을 쓸 이유가 없다.

## 2. 응용: 층으로 나눈다

소유자 원문 (2026-11-10):

> 인체 내부에서 특정 세포 이동을 추적한다던지, 농장에서 목초지에서 퍼진 소들을 추적한다던지

> 이 드론들이 소들을 필요한 곳으로 몰이 할 수 있는 거잖아?

```
 비전        몸속 미세 로봇이 세포 무리를 추적 (연구 단계)
   ^
 다리 실험   감지와 통신 거리를 줄여 성능 하락을 잰다
   ^
 주 응용     목초지 소 떼 추적과 몰이 (일부 제품화)
```

| 층 | 응용 | ARGoS 대응 | 성숙도 | 출처 |
| --- | --- | --- | --- | --- |
| 주 응용 | 목초지 소 떼 | 기본 foot-bot에 거의 1:1 (inference) | 가상 울타리 목걸이와 드론 가축 탐지가 이미 있다 | [S-SMT-22], [S-SMT-24] |
| 다리 실험 | 감지와 통신을 줄인 foot-bot | 거리-방위 센서와 위치 센서를 끈다 (inference) | 시뮬레이션 | [S-SMT-20] |
| 비전 | 미세 로봇(microrobot)이 세포 무리 추적 | 감지를 줄인 foot-bot (inference) | 연구 단계 | [S-SMT-20], [S-SMT-21] |

### 2.1 주 응용: 목초지 소 떼

- 들소(plains bison)는 작은 무리로 갈라지고 큰 무리로 다시 합친다 [S-SMT-23].
- 2마리 이상이 떠나거나 합류하면 분열 또는 융합으로 센다 [S-SMT-23].
- 이 정의를 로봇 실험의 판정 규칙으로 쓸 수 있다 (inference).
- 가상 울타리(virtual fencing) 목걸이의 위치 정확도는 2 m 이내라고 한다 [S-SMT-22].
- 여러 로봇이 갈라지는 소 떼를 나눠 따라가는 시스템은 이번 조사에서 찾지 못했다.
- 소를 드론이나 로봇으로 모는 현장 연구도 찾지 못했다.

### 2.2 비전: 몸속 세포 무리

- 순환 종양 세포 무리는 순환 종양 세포의 2–5%다 [S-SMT-19].
- 그 무리는 동물 모형에서 폐 전이의 약 절반에 기여했다 [S-SMT-19].
- 세포는 접합(junction)이 풀리면 무리에서 떨어진다 [S-SMT-21].
- 미세 로봇은 몸에 센서와 구동기를 넣기 어렵다 [S-SMT-20].
- 그래서 로봇마다 다른 결정을 내리는 지역 규칙은 지금 기술로 어렵다 (inference).
- Prof. Lu의 나노 규모 채집과 자기 조립 연구와 닿는다 [S-SMT-15].
- 이 연결은 추정이다. 그 작업의 방법은 읽지 않았다 (inference).
- 이 응용은 시뮬레이션 질문의 동기다. 의료 실현을 주장하지 않는다 (inference).
- 혈액 속 세포 무리가 반복해서 갈라지고 합치는지는 확인하지 못했다.

### 2.3 다리 실험

- 거리-방위 센서(range-and-bearing sensor) 통신을 끈다 (inference).
- 위치 센서(positioning sensor)를 끈다. 근접 센서의 짧은 거리만 남긴다 (inference).
- 질문이 바뀐다: "감지가 거의 없을 때 추적이 얼마나 무너지나?" (inference)
- 선택 기준선: 모든 로봇에 같은 전역 신호를 준다 (inference).

### 2.4 사람 감시는 틀이 아니다

- 사람을 추적하는 감시는 민감하다. 윤리 문제 때문에 응용 틀로 쓰지 않는다.
- 소유자도 응용 틀이 사람 감시가 아니라고 정했다 (2026-11-10).

## 3. 파이프라인

소유자의 흐름을 6단계로 나눈다.

```
 1 펼치기 -> 2 탐색 -> 3 탐지·묶기 -> 4 분열·배정 -> 5 추적 -> 6 몰이
  (기존)     (기존:      (기존)          (새 기여       (기존)    (기존 +
            Qi Lu 나선)                   후보)                   새 기여 후보)
                 ^                            |
                 +---- 새 무리가 나타나면 다시 탐색 ----+
```

| 단계 | 기존 방법 재사용? | Prof. Lu와의 연결 | 새로움 | 출처 |
| --- | --- | --- | --- | --- |
| 1 펼치기 | 예. 무작위 퍼짐 또는 구역 나눔 (inference) | 확인하지 않음 | 없음 | 없음 |
| 2 탐색 | 예. 양방향 나선 탐색, 무작위 걷기 채집 | **강한 맞음.** 그의 나선 탐색 논문이다 | 없음 | [S-SMT-30], [S-SMT-15] |
| 3 탐지·묶기 | 예. 거리 기반 묶기 | 그의 연구실이 DBSCAN을 방어에 썼다 | 없음 | [S-SMT-31] |
| 4 분열·배정 | 부분적. 비례 규칙과 [이력 현상(hysteresis)](#term-hysteresis) | 직접 겹치지 않음 | **새 기여 후보.** 반복 분열-융합에서 지역 비례 배정 | [S-SMT-6], [S-SMT-7] |
| 5 추적 | 예. 협력 관측, 밀도 기반 포위 | 직접 논문 없음 | 없음 | [S-SMT-1], [S-SMT-8], [S-SMT-15] |
| 6 몰이 | 부분적. 모으기·밀기, 모으는 순서 계획 | 직접 겹치지 않음 | **새 기여 후보.** 계속 갈라지는 무리 몰이, 관측과 조향 역할 나눔 | [S-SMT-25], [S-SMT-27] |

- DBSCAN은 밀도 기반 공간 군집화(density-based spatial clustering of applications with noise)다.
- 2단계가 Prof. Lu 연구와 가장 직접 겹친다.
- 한 논문은 기여를 한 단계에만 둔다.
- 6단계의 다중 몰이꾼 배정은 4단계 배정 규칙을 다시 쓰는 문제다 (inference).

## 4. 선행 연구와 빈틈

### 4.1 선행 연구

| 갈래 | 있는 것 | 남은 빈틈 (inference) | 출처 |
| --- | --- | --- | --- |
| [협력 다중 로봇 다중 이동 표적 관측(cooperative multi-robot observation of multiple moving targets, CMOMMT)](#term-cmommt) | Parker가 문제를 정의했다 | 표적 무리 구조를 다루는지 확인하지 못했다. 검색 요약만 읽었다 | [S-SMT-1] |
| 분열-융합 추적 | La와 Sheng: 센서가 갈라져 새 표적을 따르고, 표적이 사라지면 합친다 | 갈라짐 한 번의 비용만 쟀다. 반복 분열-융합의 맞교환은 1–2쪽에 없다 | [S-SMT-6] |
| 표적 수에 비례한 배치 | Low, Leow, Ang: 구역별 로봇 수를 표적 수에 비례시킨다 | 구역이 고정이다 | [S-SMT-7] |
| 지역 밀도로 다중 표적 가두기 | Lei 등: 통신 없이 단일 링, 다중 링, 다중 소그룹 포위가 생긴다 | 반복 분열-융합은 초록에 없다 | [S-SMT-8] |
| 학습한 다중 표적 [포위(encirclement)](#term-encirclement) | [트랜스포머 강화 강화 학습(Transformer-Enhanced Reinforcement Learning, TERL)](#term-terl): 추격자 15대와 표적 4개로 학습했다 | 학습 정책이다. 학습은 클러스터에서 돌려야 한다 | [S-SMT-9] |
| 군집의 [분열-융합(fission-fusion)](#term-fission-fusion) 제어 | 2022년 논문이 [무인 항공기(unmanned aerial vehicle, UAV)](#term-uav) 군집 분열-융합 제어를 다룬다 | 원문을 못 열었다 [UNVERIFIED] | [S-SMT-5] |
| 동물의 분열-융합 | Couzin과 Laidre | 생물학이다. 로봇 규칙이 없다 [UNVERIFIED] | [S-SMT-3] |
| 탐색과 추적 | Dames: 수를 모르는 표적을 찾고 추적한다 | 표적 무리의 분열-융합과 몰이는 1쪽에 없다 | [S-SMT-29] |
| [몰이(shepherding)](#term-shepherding) | Strömbom 등의 모으기와 밀기. Long 등의 조사 | 다중 몰이꾼 절은 본문에서 확인하지 않았다 | [S-SMT-25], [S-SMT-26] |
| 흩어진 무리 몰이 | Liu 등: 부분 무리로 묶고 외판원 문제로 순서를 정한다 | 몰이꾼 하나의 순서 계획이다. 탐색 단계는 초록에 없다 | [S-SMT-27] |
| 양 몰이와 복지 | Yaxley 등: 양 12마리, 최고 심박 200 bpm 초과 시 중단, 20 m 안전 구역 | 한 농장 12마리다. 소에 옮길 수 없다 (inference) | [S-SMT-28] |

- 수치의 뜻: 표의 숫자는 각 출처에서 옮겼다.
- 심박 단위 bpm은 분당 박동 수(beats per minute)다.

### 4.2 빈틈 (inference)

```
 비례 배치 [S-SMT-7] ─┐
 갈라짐 1회 비용 [S-SMT-6] ─┼─> 조각마다 있음
 다중 소그룹 링 [S-SMT-8] ─┘
                              ?
 반복 분열-융합에서 관측률 대 전환 빈도 ──> 출처를 못 찾음
```

- 로봇이 옮기면 비율은 맞는다. 이동 중에는 관측하지 못한다.
- 로봇이 안 옮기면 관측은 이어진다. 하지만 비율이 틀어진다.
- 이 맞교환을 잰 출처를 이번 조사에서 찾지 못했다.
- **이것은 아무도 안 했다는 증거가 아니다.**
- 개인 연구로 가려면 빈틈 재확인 조사가 한 번 더 필요하다.

## 5. 연구 질문(research question, RQ)

| ID | 질문 | 무엇이 새로운가 (inference) |
| --- | --- | --- |
| RQ1 | 지역 감지만으로 정한 분열-융합 규칙이 전역 정보 배정(oracle)에 얼마나 가까운가? | 전역 기준 대비 차이를 무리 분열 횟수별로 잰다 |
| RQ2 | [이력 현상(hysteresis)](#term-hysteresis) 시간 T가 관측률과 [전환 빈도(churn)](#term-churn)를 어떻게 맞바꾸나? 최적 T는 표적 속도와 어떤 관계인가? | 반복 분열-융합의 맞교환 곡선이다. 갈라짐 한 번의 비용[S-SMT-6]이 아니다 |
| RQ3 | 무리 크기에 비례한 배치는 언제 최선인가? 무리 퍼짐, 표적 속도, 감지 거리가 바뀌면 어떻게 되나? | 고정 구역의 비례 배치[S-SMT-7]를 움직이는 무리에서 시험한다 |
| RQ4 | 몰이 중 무리가 갈라지면, 몰이 로봇 여럿을 부분 무리에 어떻게 나눠 보내나? 지역 규칙이 순서 계획(외판원 문제)에 얼마나 가까운가? | 몰이꾼 하나의 순서 계획[S-SMT-27]을 여럿과 반복 분열로 넓힌다 |
| RQ5 | "관측" 로봇과 "몰기" 로봇의 비율은 얼마가 좋은가? 동물 안전 거리 제약에서 어떻게 바뀌나? | 역할 나눔과 복지 제약[S-SMT-28]을 함께 잰다 |

- RQ2가 가장 좁고 재기 쉽다. 수업 프로젝트의 핵심으로 맞다 (inference).
- RQ1과 RQ3은 개인 연구로 넓힐 때 쓴다 (inference).

## 6. 방법 초안과 지표

### 6.1 실험 틀

```
 loop functions          표적 foot-bot 8–16대        추적 foot-bot 12–30대
 (분열-융합 일정) ---> (정해진 경로, "나는 표적" 송신) ---> (묶기 -> 배정 -> 링)
        |                                                       |
        +-------------- 정답 기록: 관측 여부, 전환 횟수 <------+
```

- 이 틀은 survey §5의 초안이다 (inference).
- 표적은 foot-bot이다. [루프 함수(loop functions)](#term-loop-functions)가 정해진 일정으로 무리를 가르고 합친다.
- 표적은 [거리-방위 센서(range-and-bearing sensor)](#term-rab)로 "나는 표적"을 보낸다 [S-SMT-10].
- 추적 로봇은 표적의 거리와 방향을 지역적으로 안다.
- 판본은 수업이 정한 ARGoS 3.0.0-beta59다. 읽은 자료는 beta59 전용이 아니다 (inference).

### 6.2 알고리즘 초안 (inference)

1. 추적 로봇이 감지한 표적을 거리로 묶는다. 간격이 d보다 크면 다른 무리다.
2. 가장 가까운 무리에 붙는다. 무리 중심과 부분 군집 크기를 송신한다.
3. 분열: 두 무리가 d보다 멀어지면 먼 쪽 로봇이 먼 무리를 따른다.
4. 비례 규칙: 표적당 로봇이 많은 쪽이 적은 쪽에 로봇을 넘긴다.
5. 이력 현상: 불균형이 T초 이어질 때만 옮긴다.
6. 대형: 부분 군집마다 중심 둘레 링을 만든다. 반지름은 무리 퍼짐에 따른다.
7. 융합: 두 중심이 d보다 가까워지면 링 하나로 합친다.

기준선 (inference):

| 기준선 | 내용 |
| --- | --- |
| 고정 대형 | 전체 표적 중심 둘레 링 하나 |
| 가장 가까운 표적 따라가기 | CMOMMT 방식과 비슷하다 [S-SMT-1] |
| 전역 배정(oracle) | loop functions가 실제 무리 크기에 비례해 배정한다 |

### 6.3 지표

| 지표 | 정의 | 답하는 질문 |
| --- | --- | --- |
| 관측률 | 시간마다 관측 중인 표적의 비율. 감지 거리 안에 추적 로봇이 있으면 관측 | 감시가 되나 |
| 무리별 로봇 비율 | 부분 군집마다 표적당 로봇 수. 비례 이상값과 비교 | 배치가 맞나 |
| 전환 빈도(churn) | 로봇 1대가 1분에 부분 군집을 바꾼 횟수 | 얼마나 흔들리나 |
| 맞교환 곡선 | x = 전환 빈도, y = 평균 관측률. T마다 점 하나 | RQ2의 답 |

- 몰이 단계의 새 지표 (inference): 목표에 도착한 동물 비율, 걸린 시간, 동물 스트레스 대용값(로봇과의 최소 거리).
- 복지 제약은 규칙에 넣는다. 예: 안전 거리 안으로 들어가지 않는다 [S-SMT-28].

## 7. 로드맵과 가능성

### 7.1 단계

```
 수업 2주 ──> 확장성 분석 ──> 추적 + 몰이 ──> 이후
 2→4→5       로봇 수·분열 빈도   2→6           학습 정책
 (기여: 4)   ·감지 거리 변화     (기여: 6)      이종 군집 등
```

| 단계 | 범위 | 기여 | 수준 |
| --- | --- | --- | --- |
| 수업 프로젝트, 2주 | 2 → 4 → 5단계, 탐색은 나선 탐색 | 4단계 | 수업 |
| 확장성 분석 | 로봇 수, 분열 빈도, 감지 거리를 바꾼다 | 없음 | 워크숍 논문 |
| 추적 + 몰이 | 2 → 6단계 | 6단계, 관측과 조향 역할 배정 | 학회 논문 (ANTS, DARS, TAROS, IROS) |
| 이후 | 학습 정책(다중 에이전트 강화 학습 또는 그래프 신경망, Cradle 클러스터에서 학습), 이종 UAV와 UGV, 분열해 도망치는 적대적 표적, 미세 규모 비전 | | 학위 논문 방향 |

- 학습은 로컬에서 돌리지 않는다. Cradle 클러스터에서만 돌린다.

### 7.2 가능성: 채팅 추정과 survey 점수

채팅 추정(메인 세션, inference):

| 수준 | 가능성 |
| --- | --- |
| 수업 | 높음 |
| 워크숍 | 중상 |
| 학회 | 중간 |
| 학위 논문 방향 | 가능 |

survey의 출처 있는 점수 (R = 연구 가능성, F = 실현 가능성, Fit = 지도교수 연구와의 맞음, 각 1–3점, 합계는 곱):

| 범위 | R | F | Fit | 합계 | 이유 |
| --- | --- | --- | --- | --- | --- |
| 추적만 | 2 | 2 | 2 | 8 | 세 조각에 선행 연구가 있다. 추적 논문 연결은 추정뿐이다 |
| 전체 파이프라인, 수업 2주 기준 | 2 | 1 | 3 | 6 | 2단계가 Prof. Lu 논문과 직접 겹친다. 6단계를 2주에 다 만들기 어렵다 |

- 이 점수는 비교용 추정(inference)이다. 기준은 `submodule_project/research/lu_qi.md` §2.0과 같다.
- **채팅 추정이 survey보다 낙관적인 곳에서는 survey 점수가 우선한다.**
- 수업 "높음": survey의 F는 전체 파이프라인에서 1이다. 6단계를 2주에 다 만들기 어렵다고 본다.
- 수업 범위(2 → 4 → 5단계)에 맞는 survey 점수는 없다. 가장 가까운 두 점수는 8과 6이다.
- 학회 "중간": survey의 R은 2다. R이 3이 되는 조건은 빈틈 재확인이 맞교환 측정의 부재를 다시 확인하는 것이다.
- 개인 연구로 길게 가면 F의 2주 기준이 맞지 않는다. 이 점수는 비교용이다.

## 8. 위험

| 위험 | 대응 |
| --- | --- |
| 인접 분야가 붐빈다 (CMOMMT, 포위, 몰이) | 범위를 "분열-융합 + 지역 정보"로 좁힌다 |
| 제어 이론 학회는 증명을 요구한다 | 군집 전문 학회를 겨냥한다 (§9) |
| 윤리 틀 | 사람 감시를 응용으로 두지 않는다. 소 떼와 세포 무리만 쓴다 |
| 몰이 중 동물 복지 한계 | 안전 거리 제약을 규칙에 넣는다 [S-SMT-28] |
| 빈틈이 이미 메워졌을 수 있다 | 논문 쓰기 전에 빈틈 재확인 조사를 한다 (§4.2) |

- 양 연구는 한 농장 12마리다. 소로 일반화하지 않는다 [S-SMT-28].

## 9. 투고처 후보 (inference)

- 모두 추정이다. 마감과 범위는 확인하지 않았다.

| 단계 | 후보 | 맞는 결과 |
| --- | --- | --- |
| 워크숍 | IROS와 ICRA의 다중 로봇 워크숍 | RQ2의 첫 곡선 |
| 학회 (군집 전문) | ANTS, SWARM, DARS | RQ1과 RQ2, 기준선 3개 |
| 학회 (일반 로봇·에이전트) | IROS, ICRA, AAMAS | RQ1–RQ3, 이종 확장 |
| 학술지 | Swarm Intelligence, Autonomous Robots | 전체 결과와 실제 로봇 또는 이종 확장 |

- 이름 풀이는 [용어 부록](#term-venues)에 있다.
- TAROS는 채팅 답변의 로드맵에만 있다. survey §10 목록에는 없다.
- survey는 TAROS 2024 논문 한 편을 출처로 가졌다 [S-SMT-31].

## 10. 열린 질문

| 질문 | 출처 |
| --- | --- |
| 빈틈 재확인 조사를 아직 하지 않았다. 키워드 후보는 "fission-fusion target tracking", "dynamic coalition target tracking", "CMOMMT target groups"다 | §4.2 |
| La와 Sheng의 분할 규칙이 분산형인지, 반복 분열-융합 실험이 있는지 3쪽 이후를 읽지 않았다 | [S-SMT-6] |
| Lei 등의 본문에 반복 분열-융합 실험이 있는지 확인하지 않았다 | [S-SMT-8] |
| Kolling과 Carpin, Jung 등의 다중 표적 추적 원문을 읽지 않았다 | [S-SMT-6] |
| 군집 몰이 조사의 다중 몰이꾼 절을 확인하지 않았다 | [S-SMT-26] |
| 가축 소의 분열-융합 측정 논문을 찾지 못했다. 들소 연구로 대신했다 | [S-SMT-23] |
| 소를 드론이나 로봇으로 모는 현장 연구를 찾지 못했다 | §2.1 |
| 혈액 속 세포 무리가 반복해서 갈라지고 합치는지 확인하지 못했다 | §2.2 |
| 순환 종양 세포 무리 수치는 뉴스로 읽었다. 원문은 읽지 않았다 | [S-SMT-19] |
| foot-bot 거리-방위 센서의 기본 거리를 확인하지 못했다 (포럼 요약은 6 m) | 없음 |
| 2022년 분열-융합 UAV 논문의 저자와 내용을 원문에서 확인하지 못했다 | [S-SMT-5] |

## 11. 출처

cited 행만 옮겼다. 상태는 `note`에 있다.

[S-SMT-1] Distributed Algorithms for Multi-Robot Observation of Multiple Moving Targets | https://bibbase.org/network/publication/parker-distributedalgorithmsformultirobotobservationofmultiplemovingtargets-2002 | published: 2002-05, Autonomous Robots 12(3) 231 to 255 | accessed: 2026-11-10 | type: paper | note: BibBase record only, method from search snippet, DOI 10.1023/A:1015256330750 per snippet, partial
[S-SMT-3] Fission-fusion populations | https://doi.org/10.1016/j.cub.2009.05.034 | published: 2009-08, Current Biology 19(15) R633 to R635 per search snippet | accessed: 2026-11-10 | type: paper | note: PubMed and Cell pages blocked, search snippet only, UNVERIFIED
[S-SMT-5] Bio-Inspired Self-Organized Fission-Fusion Control Algorithm for UAV Swarm | https://doaj.org/article/5f928ede5d1c4b5882e5d932d6e2c692 | published: 2022-11 per search snippet, Aerospace | accessed: 2026-11-10 | type: paper | note: HTTP 403, search snippet only, UNVERIFIED
[S-SMT-6] Dynamic target tracking and observing in a mobile sensor network | https://ara.cse.unr.edu/wp-content/uploads/2014/12/Elsevier_RAS_La2012.pdf | published: 2012, Robotics and Autonomous Systems 60 996 to 1009 | accessed: 2026-11-10 | type: paper | note: pages 1 and 2 read, authors La and Sheng, DOI 10.1016/j.robot.2012.03.006, verified
[S-SMT-7] Task Allocation via Self-Organizing Swarm Coalitions in Distributed Mobile Sensor Network | https://www.comp.nus.edu.sg/~lowkh/pubs/aaai2004.pdf | published: 2004, AAAI per copyright line | accessed: 2026-11-10 | type: paper | note: pages 1 and 2 read, authors Low, Leow, Ang, verified
[S-SMT-8] Self-organized multi-target trapping of swarm robots with density-based interaction | https://www.springerprofessional.de/self-organized-multi-target-trapping-of-swarm-robots-with-densit/24596984 | published: 2023-03-08, Complex and Intelligent Systems | accessed: 2026-11-10 | type: paper | note: abstract on a secondary host, authors Lei, Zhang, Xiang, Duan, verified
[S-SMT-9] TERL: Large-Scale Multi-Target Encirclement Using Transformer-Enhanced Reinforcement Learning | https://arxiv.org/abs/2503.12395 | published: 2025-03-16, revised 2025-08-27 | accessed: 2026-11-10 | type: paper | note: abstract page, accepted IROS 2025, verified
[S-SMT-10] AI for robots and swarms: ARGoS reference | https://opentechschool-brussels.github.io/AI-for-robots-and-swarms/ref_argos.html | published: undated | accessed: 2026-11-10 | type: blog | note: third-party tutorial, range_and_bearing fields of the Lua interface, partial
[S-SMT-15] Qi Lu: Research | https://sites.google.com/view/qilu/research | published: undated | accessed: 2026-11-10 | type: official | note: carried over from the LQ pass (S-LQ-2), not re-read
[S-SMT-19] Circulating tumor cell clusters more likely to cause metastasis than single cells (news on Aceto et al., Circulating Tumor Cell Clusters Are Oligoclonal Precursors of Breast Cancer Metastasis, Cell 158(5) 1110) | https://www.sciencedaily.com/releases/2014/08/140828135519.htm | published: 2014-08-28 | accessed: 2026-11-10 | type: news | note: news page read, original paper DOI 10.1016/j.cell.2014.07.013 not read, partial
[S-SMT-20] A Survey on Swarm Microrobotics | https://research.polyu.edu.hk/en/publications/a-survey-on-swarm-microrobotics/ | published: 2022, IEEE Transactions on Robotics 38(3) 1531 to 1551 | accessed: 2026-11-10 | type: paper | note: record page and abstract, authors Yang, Yu, Yang, Wang, Nelson, Zhang, verified
[S-SMT-21] Tuning Collective Cell Migration by Cell-Cell Junction Regulation | https://pmc.ncbi.nlm.nih.gov/articles/PMC5378050 | published: 2017, Cold Spring Harbor Perspectives in Biology 9(4) a029199 | accessed: 2026-11-10 | type: paper | note: PMC page, abstract and first 100000 characters read, authors Friedl and Mayor, verified
[S-SMT-22] Evaluating Virtual Fencing Technology at Field Scale Today | https://www.beefresearch.ca/fact-sheets/evaluating-virtual-fencing-technolofy-at-field-scale-today/ | published: project completed 2023-02 | accessed: 2026-11-10 | type: official | note: Beef Cattle Research Council fact sheet, verified
[S-SMT-23] Factors Influencing Plains Bison Group Stability and Fission Fusion Events | https://arc.lib.montana.edu/ojs/index.php/IJS/article/view/3781 | published: 2026-04-15, Intermountain Journal of Sciences 32 | accessed: 2026-11-10 | type: paper | note: abstract page, authors Bresnan, Creel, Shamon, verified
[S-SMT-24] Deep Learning Approaches for Automatic Livestock Detection in UAV Imagery: State-of-the-Art and Future Directions | https://api.crossref.org/works/10.3390%2FFI17090431 | published: 2025-09-21, Future Internet 17(9) 431 | accessed: 2026-11-10 | type: paper | note: Crossref record and abstract, authors Adam, Song, Yu, Li, verified
[S-SMT-25] Solving the shepherding problem: heuristics for herding autonomous, interacting agents | https://pmc.ncbi.nlm.nih.gov/articles/PMC4191104 | published: 2014, J R Soc Interface 11(100) | accessed: 2026-11-10 | type: paper | note: carried over from the LQ pass (S-LQ-10), not re-read
[S-SMT-26] A Comprehensive Review of Shepherding as a Bio-inspired Swarm-Robotics Guidance Approach | https://arxiv.org/abs/1912.07796 | published: 2019-12-17, revised 2020-04-30, DOI 10.1109/TETCI.2020.2992778 | accessed: 2026-11-10 | type: paper | note: abstract page, authors Long, Sammut, Sgarioto, Garratt, Abbass, verified
[S-SMT-27] Planning-Assisted Context-Sensitive Autonomous Shepherding of Dispersed Robotic Swarms in Obstacle-Cluttered Environments | https://arxiv.org/abs/2301.10363 | published: 2023-01-25, revised 2023-02-27, IEEE TETCI 2025 per page | accessed: 2026-11-10 | type: paper | note: abstract page, authors Liu, Singh, Elsayed, Hunjet, Abbass, verified
[S-SMT-28] Drone approach parameters leading to lower stress sheep flocking and movement: sky shepherding | https://pmc.ncbi.nlm.nih.gov/articles/PMC8032684 | published: 2021, Scientific Reports | accessed: 2026-11-10 | type: paper | note: PMC page, authors Yaxley, Joiner, Abbass, verified
[S-SMT-29] Distributed Multi-Target Search and Tracking using the PHD Filter | https://sites.temple.edu/pdames/files/2017/10/DamesMRS2017.pdf | published: 2017 per file name (MRS) | accessed: 2026-11-10 | type: paper | note: page 1 read, author Dames, venue from file name only, verified
[S-SMT-30] Adaptive Multiple Distributed Bidirectional Spiral Path Planning for Foraging Robot Swarms | https://par.nsf.gov/biblio/10591790 | published: 2023 | accessed: 2026-11-10 | type: paper | note: carried over from the LQ pass (S-LQ-5), NSF PAR record and abstract, not re-read
[S-SMT-31] Robust Mitigation Strategy for Misleading Pheromone Trails in Foraging Robot Swarms | https://par.nsf.gov/servlets/purl/10593555 | published: 2025, TAROS 2024 LNAI 15052 pp. 307 to 319 | accessed: 2026-11-10 | type: paper | note: carried over from the LQ pass (S-LQ-21), DBSCAN defense, not re-read

## 용어 부록 (terms appendix)

- <a id="term-swarm"></a>군집(swarm): 단순한 로봇 여럿이 지역 규칙으로 함께 일하는 무리.
- <a id="term-formation"></a>대형(formation): 로봇들이 지키는 상대 위치 모양. 예: 링.
- <a id="term-cmommt"></a>협력 다중 로봇 다중 이동 표적 관측(cooperative multi-robot observation of multiple moving targets, CMOMMT): 로봇 팀이 이동 표적을 최대한 오래 관측하는 문제.
- <a id="term-encirclement"></a>포위(encirclement): 로봇들이 표적 둘레를 감싸는 일.
- <a id="term-terl"></a>트랜스포머 강화 강화 학습(Transformer-Enhanced Reinforcement Learning, TERL): 트랜스포머로 표적 우선순위를 배우는 다중 표적 포위 방법.
- <a id="term-fission-fusion"></a>분열-융합(fission-fusion): 무리가 자주 갈라지고 다시 합치는 집단 구조.
- <a id="term-uav"></a>무인 항공기(unmanned aerial vehicle, UAV): 사람이 타지 않는 비행 로봇.
- 무인 지상 차량(unmanned ground vehicle, UGV): 사람이 타지 않는 지상 로봇.
- <a id="term-churn"></a>전환 빈도(churn): 로봇 1대가 1분에 부분 군집을 바꾸는 횟수.
- <a id="term-hysteresis"></a>이력 현상(hysteresis): 조건이 일정 시간 이어져야 상태를 바꾸는 규칙. 잦은 뒤집힘을 막는다.
- <a id="term-loop-functions"></a>루프 함수(loop functions): ARGoS에서 매 단계 실험 환경을 다루는 사용자 코드.
- <a id="term-rab"></a>거리-방위 센서(range-and-bearing sensor): 이웃 로봇의 메시지와 함께 그 거리와 방향을 받는 장치.
- <a id="term-shepherding"></a>몰이(shepherding): 소수의 몰이꾼이 무리를 목표 쪽으로 모으고 미는 일.
- 연구 질문(research question, RQ): 이 연구가 답하려는 물음.
- 관측률(observation ratio): 시간마다 관측 중인 표적의 비율.
- 전역 배정(oracle): 시뮬레이터가 실제 값을 알고 내리는 기준 배정.
- 가상 울타리(virtual fencing): 목걸이로 경계를 정하고 소리와 전기 자극으로 소를 막는 기술.
- 미세 로봇(microrobot): 몸속에서 일할 만큼 작은 로봇.
- 다중 에이전트 강화 학습(multi-agent reinforcement learning, MARL): 여러 에이전트가 함께 보상으로 정책을 배우는 방법.
- 그래프 신경망(graph neural network, GNN): 연결 그래프 위에서 정보를 주고받는 신경망.
- 밀도 기반 공간 군집화(density-based spatial clustering of applications with noise, DBSCAN): 가까운 점을 밀도로 묶는 묶기 방법.
- ARGoS: 군집 로봇 시뮬레이터. foot-bot은 그 안의 바퀴 로봇 모델이다.
- 최소 실행 제품(minimum viable product, MVP): 처음부터 끝까지 도는 가장 단순한 판.
- <a id="term-venues"></a>투고처 이름:
  - ANTS: International Conference on Swarm Intelligence.
  - DARS: International Symposium on Distributed Autonomous Robotic Systems.
  - SWARM: International Symposium on Swarm Behavior and Bio-Inspired Robotics.
  - IROS: IEEE/RSJ International Conference on Intelligent Robots and Systems.
  - ICRA: IEEE International Conference on Robotics and Automation.
  - AAMAS: International Conference on Autonomous Agents and Multiagent Systems.
  - TAROS: 전체 이름이 조사 자료에 없다. 확인이 필요하다.
