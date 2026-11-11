# 분열-융합 감시 군집: 선행 연구 조사 (split-merge-tracking)

- 작업 태그: SMT
- 조사일: 2026-11-10
- 상태: 한 회차 완료. 검색과 읽기 약 35회.
- 용도: 소유자 개인 연구 주제 후보. 수업 프로젝트(CSCI 6371)보다 넓게 본다.

## 요약

- **결론: 조각마다 선행 연구가 있다. 반복 분열-융합에서 "관측률 대 전환 빈도"를 잰 출처는 이번 조사에서 찾지 못했다.**
- 전체 그림: 펼치기 → 탐색 → 탐지·묶기 → 분열·배정 → 추적 → 몰이 (§14). 새 기여는 분열·배정 단계 하나다 (inference).
- 응용: 몸속 세포 무리 추적, 목초지 소 떼 추적 (§12). 사람 감시가 아니다.
- 점수(비교용, `submodule_project/research/lu_qi.md` §2.0과 같은 기준): 추적만 R2 · F2 · Fit2 = 8. 전체 파이프라인 R2 · F1 · Fit3 = 6 (§14.2).
- 연구 질문(research question, RQ) 후보 5개 (§4).
- 출처 31개: 이번 회차 검증(verified) 15, 부분(partial) 4, 미검증(unverifiable) 3, 이전 회차(LQ)에서 가져옴 9.
- 미해결 질문 16개: 아래 open_questions.

## 1. 문제

소유자 원문 (2026-11-10):

> 감시 swarm. 집단이 있고 그 집단이 갈라지면 swarm 도 집단 처럼 분리하고 분리된 swarm 들이 계속 나눠지고 집단이 합쳐지면 합쳐지고 그리고 포메이션은 숫자에 맞게 자동 조절되고 이건 어때?

```
 t1: 표적 한 무리            t2: 표적이 둘로 갈림          t3: 다시 합침
   o o o o o o                o o o      o o o            o o o o o o
  [  링 하나  ]              [링 A]      [링 B]          [  링 하나  ]
   로봇 12대                 로봇 6대     로봇 6대          로봇 12대
```

- 표적(target): 함께 움직이는 무리. 무리가 갈라지고 다시 합친다.
- [군집(swarm)](#term-swarm)도 표적 무리를 따라 갈라지고 합친다.
- 갈라짐은 여러 번 이어질 수 있다.
- 각 부분 군집의 [대형(formation)](#term-formation)은 로봇 수와 무리 크기에 맞춰 크기를 바꾼다.
- 예: 표적을 둘러싼 링(ring). 링 반지름은 무리의 퍼짐에 따른다.

## 2. 선행 연구 갈래

| 갈래 | 있는 것 | 남은 빈틈 (inference) | 검증 | 출처 |
| --- | --- | --- | --- | --- |
| [협력 다중 로봇 다중 이동 표적 관측(cooperative multi-robot observation of multiple moving targets, CMOMMT)](#term-cmommt) | Parker가 문제를 정의했다. 로봇은 가까운 표적에 끌리고 다른 로봇에 밀린다 | 표적 무리 구조를 다루는지 확인하지 못했다 | partial: 서지는 확인, 방법은 검색 요약 [STALE] | [S-SMT-1] |
| 다중 로봇 표적 탐지·추적 분류 | Robin과 Lacroix의 분류(taxonomy). 추적을 위치 추정, 따라가기, 관측으로 나눈다 | 조사 논문이다 | unverifiable: 페이지 봇 차단 [UNVERIFIED] | [S-SMT-4] |
| 다중 표적 추적의 분열-융합 | La와 Sheng: 센서가 [무리 짓기(flocking)](#term-flocking) 대형에서 갈라져 새 표적을 따른다. 표적이 사라지면 다시 합친다. [씨앗 성장 그래프 분할(seed growing graph partition, SGGP)](#term-sggp)이 누가 갈라질지 정한다. 갈라질 때의 총 에너지와 시간을 무작위 선택과 비교했다 | 갈라짐 한 번의 비용은 쟀다. 반복 분열-융합에서 관측률과 전환 빈도의 맞교환은 1–2쪽에 없다. 분할 규칙이 분산형인지는 읽지 않았다 | verified: 1–2쪽 [STALE] | [S-SMT-6] |
| 표적 수에 비례한 배치 | Low, Leow, Ang: 개미 방식 작업 배분으로 구역별 로봇 수를 표적 수에 비례시킨다. 지역 감지(만남 간격)로 밀도를 추정한다. 실험장은 고정 구역 6개다 | 구역이 고정이다. 움직이며 갈라지는 무리가 아니다 | verified: 1–2쪽 [STALE] | [S-SMT-7] |
| 지역 밀도로 다중 표적 가두기 | Lei 등: 로봇 간 통신 없이 여러 이동 표적을 가둔다. 단일 링, 다중 링, 다중 소그룹 포위가 저절로 생긴다. 로봇 최대 40대, 표적 8개 | 반복 분열-융합과 전환 빈도는 초록에 없다 | verified: 초록 | [S-SMT-8] |
| 학습한 다중 표적 [포위(encirclement)](#term-encirclement) | [트랜스포머 강화 강화 학습(Transformer-Enhanced Reinforcement Learning, TERL)](#term-terl): 추격자 15대, 표적 4개로 학습했다. 재학습 없이 추격자 80대, 표적 20개에서 성공률 100%를 보고했다 | 학습 정책이다. 학습은 클러스터에서 돌려야 한다 | verified: 초록 | [S-SMT-9] |
| 동물의 [분열-융합(fission-fusion)](#term-fission-fusion) | Couzin과 Laidre: 무리가 자주 갈라지고 합치는 개체군 | 생물학이다. 로봇 규칙은 없다 | unverifiable: 서지만 검색 요약 [UNVERIFIED] [STALE] | [S-SMT-3] |
| 군집의 분열-융합 제어 | 2022년 Aerospace 논문: 찌르레기에서 착안한 [무인 항공기(unmanned aerial vehicle, UAV)](#term-uav) 군집 분열-융합 제어. 부분 군집 선택과 가두기 | 검색 요약상 동적 장애물 대응이 목적이다 | unverifiable: HTTP 403 [UNVERIFIED] | [S-SMT-5] |
| 로봇 몸체의 합치기·나누기 | Mathews 등: 병합 가능한 신경계(mergeable nervous systems). marXbot 유닛이 한 몸, 한 두뇌로 합치고, 나뉘고, 고장 부품을 바꾼다 | 몸체의 물리적 결합이다. 군집 무리의 결합이 아니다 | verified [STALE] | [S-SMT-2] |
| 경매 기반 작업 배분 | [합의 기반 묶음 알고리즘(consensus-based bundle algorithm, CBBA)](#term-cbba): 중앙 배차 없이 작업을 나눈다 | 배정 기준선 후보 | 이전 회차, partial [STALE] | [S-SMT-18] |

- La와 Sheng의 문헌 검토에는 구역 기반 다중 표적 추적(Jung 등)과 분산 다중 표적 감시(Kolling과 Carpin)도 있다 [S-SMT-6]. 이번 회차에서 원문은 읽지 않았다.

## 3. 빈틈 (inference)

- 세 조각은 각각 선행 연구가 있다.
  1. 표적 수에 비례한 배치 [S-SMT-7].
  2. 분열-융합 추적과 갈라짐 한 번의 비용 [S-SMT-6].
  3. 다중 소그룹 링 [S-SMT-8].
- 이번 조사에서 못 찾은 것: 무리가 **반복해서** 갈라지고 합칠 때 관측률과 [전환 빈도(churn)](#term-churn)의 맞교환(trade-off).
- 전환 빈도: 로봇 1대가 1분에 부분 군집을 바꾸는 횟수.
- 로봇이 옮기면 비율은 맞는다. 하지만 이동 중에는 관측하지 못한다.
- 로봇이 안 옮기면 관측은 이어진다. 하지만 비율이 틀어진다.
- 이 빈틈은 "이번 조사에서 출처를 못 찾음"이다. 아무도 안 했다는 증거가 아니다 (`rules/research.md` §10).
- 개인 연구로 가려면 빈틈 재확인 조사가 한 번 더 필요하다.
- 재확인 키워드 후보: "fission-fusion target tracking", "dynamic coalition target tracking", "CMOMMT target groups".
- 재확인 대상 논문: La와 Sheng 3–4절, Kolling과 Carpin, Jung 등 [S-SMT-6].

## 4. 연구 질문(research question, RQ) 후보

| ID | 질문 | 무엇이 새로운가 (inference) |
| --- | --- | --- |
| RQ1 | 지역 감지만으로 정한 분열-융합 규칙이 전역 정보 배정(oracle)에 얼마나 가까운가? | 전역 기준 대비 차이를 무리 분열 횟수별로 잰다 |
| RQ2 | [이력 현상(hysteresis)](#term-hysteresis) 시간 T가 관측률과 전환 빈도를 어떻게 맞바꾸나? 최적 T는 표적 속도와 어떤 관계인가? | 반복 분열-융합에서의 맞교환 곡선. 갈라짐 한 번의 비용[S-SMT-6]이 아니다 |
| RQ3 | 무리 크기에 비례한 배치는 언제 최선인가? 무리 퍼짐, 표적 속도, 감지 거리가 바뀌면 어떻게 되나? | 고정 구역의 비례 배치[S-SMT-7]를 움직이는 무리에서 시험한다 |
| RQ4 | 몰이 중 무리가 갈라지면, 몰이 로봇 여럿을 부분 무리에 어떻게 나눠 보내나? 지역 규칙이 순서 계획(외판원 문제)에 얼마나 가까운가? | 몰이꾼 하나의 순서 계획[S-SMT-27]을 여럿과 반복 분열로 넓힌다 (§13) |
| RQ5 | "관측" 로봇과 "몰기" 로봇의 비율은 얼마가 좋은가? 동물 안전 거리 제약에서 어떻게 바뀌나? | 역할 나눔과 복지 제약[S-SMT-28]을 함께 잰다 (§13) |

- 연구 질문(research question, RQ) 2가 가장 좁고 재기 쉽다. 수업 프로젝트의 핵심으로 맞다 (inference).
- 연구 질문(research question, RQ) 1과 3은 개인 연구로 넓힐 때 쓴다.
- 확장 후보: [무인 지상 차량(unmanned ground vehicle, UGV)](#term-ugv)과 무인 항공기(unmanned aerial vehicle, UAV)를 섞은 이종 군집. 무인 항공기(unmanned aerial vehicle, UAV)가 전체 무리를 보고, 무인 지상 차량(unmanned ground vehicle, UGV)이 소그룹을 따른다 (inference).

## 5. ARGoS로 할 수 있나

```
 loop functions          표적 foot-bot 8–16대        추적 foot-bot 12–30대
 (분열-융합 일정) ---> (정해진 경로, "나는 표적" 송신) ---> (묶기 -> 배정 -> 링)
        |                                                       |
        +-------------- 정답 기록: 관측 여부, 전환 횟수 <------+
```

- 판본: 수업이 정한 ARGoS 3.0.0-beta59. 여기서 읽은 자료는 beta59 전용이 아니다 (inference).
- 표적: foot-bot. [루프 함수(loop functions)](#term-loop-functions)가 정해진 일정으로 무리를 가르고 합친다.
- 표적은 [발광 다이오드(light-emitting diode, LED)](#term-led) 색으로 구분한다.
- [거리-방위 센서(range-and-bearing sensor)](#term-rab): 메시지마다 `range`(cm), `horizontal_bearing`, 10바이트 `data`를 준다 [S-SMT-10], [S-SMT-11]. 출처는 Lua 인터페이스 안내서다.
- 표적이 거리-방위 센서(range-and-bearing sensor)로 "나는 표적"을 보낸다. 추적 로봇은 표적의 거리와 방향을 지역적으로 안다.
- [위치 센서(positioning sensor)](#term-positioning): [응용 프로그래밍 인터페이스(application programming interface, API)](#term-api) 문서에 `CCI_PositioningSensor` 클래스가 있다 [S-SMT-12]. 읽는 값의 내용은 확인하지 못했다.
- argos3-examples가 루프 함수(loop functions) 틀을 준다 [S-SMT-13].

### 5.1 알고리즘 초안 (inference)

1. 추적 로봇이 감지한 표적을 거리로 묶는다. 간격이 d보다 크면 다른 무리다.
2. 가장 가까운 무리에 붙는다. 무리 중심과 부분 군집 크기를 송신한다.
3. 분열: 두 무리가 d보다 멀어지면 먼 쪽 로봇이 먼 무리를 따른다.
4. 비례 규칙: 표적당 로봇이 많은 쪽이 적은 쪽에 로봇을 넘긴다.
5. 이력 현상(hysteresis): 불균형이 T초 이어질 때만 옮긴다.
6. 대형: 부분 군집마다 중심 둘레 링. 반지름은 무리 퍼짐에 따른다. 로봇은 각도로 고르게 선다.
7. 융합: 두 중심이 d보다 가까워지면 링 하나로 합친다.

기준선:

- 고정 대형: 전체 표적 중심 둘레 링 하나.
- 가장 가까운 표적 따라가기: 협력 다중 로봇 다중 이동 표적 관측(cooperative multi-robot observation of multiple moving targets, CMOMMT) 방식과 비슷하다 (inference) [S-SMT-1].
- 전역 배정(oracle): 루프 함수(loop functions)가 실제 무리 크기에 비례해 배정한다.

### 5.2 최소 실행 제품(minimum viable product, MVP) 1단계와 확장

| 단계 | 내용 |
| --- | --- |
| [최소 실행 제품(minimum viable product, MVP)](#term-mvp) 1단계 | 무리 2개. 분열 한 번, 융합 한 번. 관측률과 전환 빈도 기록. 고정 대형 기준선 |
| 확장 1 | 3–4개 무리로 반복 분열 |
| 확장 2 | T를 바꿔 가며 관측률 대 전환 빈도 곡선 (연구 질문(research question, RQ) 2) |
| 확장 3 | 추적 로봇 고장, 또는 추적 로봇보다 빠른 표적 |
| 확장 4 (개인 연구) | 전역 배정 대비 차이 (연구 질문 1). 무리 퍼짐과 속도 조건 (연구 질문 3) |
| 확장 5 (추적 다음 단계) | 몰이: 관측 로봇과 몰이 로봇으로 역할을 나눈다. 갈라진 무리를 목표 구역으로 모은다 (연구 질문 4, 5, §13) |
| 전체 | 펼치기, 탐색, 탐지·묶기, 분열·배정, 추적, 몰이를 잇는다. 순서는 §14.3 로드맵 |

- 실행은 소유자가 직접 한다. 이 조사는 아무것도 돌리지 않았다.

## 6. 지표

| 지표 | 정의 | 답하는 질문 |
| --- | --- | --- |
| 관측률 | 시간마다 관측 중인 표적의 비율. 감지 거리 안에 추적 로봇이 있으면 관측 | 감시가 되나 |
| 무리별 로봇 비율 | 부분 군집마다 표적당 로봇 수. 비례 이상값과 비교 | 배치가 맞나 |
| 전환 빈도(churn) | 로봇 1대가 1분에 부분 군집을 바꾼 횟수 | 얼마나 흔들리나 |
| 맞교환 곡선 | x = 전환 빈도, y = 평균 관측률. T마다 점 하나 | 연구 질문 2의 답 |

## 7. Qi (Luki) Lu 교수와의 맞음

- 근거: `lu_qi.md` Part 1의 연구 페이지와 Google Scholar(첫 20편만 보임)다.
- 그 범위에서 표적 추적이나 대형 논문을 찾지 못했다 [S-SMT-15].
- 연구 페이지에 동적 로봇 사슬 네트워크(dynamic robot chain networks)가 있다 [S-SMT-15]. 과제에 맞춰 구조가 바뀐다는 점이 공통이다 (inference, 방법은 읽지 않음).
- 주 과제는 무인 지상 차량(unmanned ground vehicle, UGV)과 무인 항공기(unmanned aerial vehicle, UAV)의 이종 채집 군집이다 [S-SMT-16]. §4의 이종 확장과 이어진다 (inference).
- 자금 목록에 [미국 국토안보부(Department of Homeland Security, DHS)](#term-dhs) SLA가 있다 [S-SMT-14]. 이 주제와의 연결은 추정일 뿐이다 (inference).
- 결론: 추적만 보면 Fit 2. 직접 논문은 없고 연결은 모두 추정이다.
- 전체 파이프라인의 탐색 단계는 그의 나선 탐색 논문과 직접 겹친다 [S-SMT-30]. §14.2 참고.

## 8. 윤리

- 사람을 추적하는 감시는 민감하다. 이 조사는 사람 감시를 응용으로 두지 않는다.
- 응용 틀: 몸속 세포 무리 추적, 목초지 가축 무리 추적과 몰이 (§12, §13).
- 가축 몰이에는 동물 복지 한계가 있다. 예: 심박 상한, 안전 거리 [S-SMT-28].
- 가축 무리를 로봇이 감싸 위험에서 돌리는 연구가 이미 있다 [S-SMT-17].

## 9. 점수 (비교용, inference)

기준은 `submodule_project/research/lu_qi.md` §2.0과 같다. 각 1–3점, 합계는 곱(최대 27).

| 항목 | 점수 | 이유 |
| --- | --- | --- |
| 연구 가능성(research potential, R) | 2 | 세 조각에 선행 연구가 있다 [S-SMT-6], [S-SMT-7], [S-SMT-8]. 반복 분열-융합의 맞교환 곡선만 열려 있다 |
| 실현 가능성(feasibility, F) | 2 | 기본 foot-bot과 거리-방위 센서(range-and-bearing sensor)로 된다 [S-SMT-10]. 부품(묶기, 분열 규칙, 링, 기준선 3개)이 2주에 많다 |
| 맞음(Fit) | 2 | 표적 추적 논문을 찾지 못했다 [S-SMT-15]. 연결은 추정뿐이다 |
| 합계 | 8 | `lu_qi.md` 표에 넣으면 7위 공동(정렬과 분리 과제와 같은 8점) |

- 연구 가능성(research potential, R)이 3이 되는 조건: 빈틈 재확인 조사(§3)가 맞교환 측정이 없음을 다시 확인한다.

## 10. 투고처 후보 (inference)

- 모두 추정이다. 마감과 범위는 확인하지 않았다.

| 단계 | 후보 | 맞는 결과 |
| --- | --- | --- |
| 워크숍 | IROS·ICRA의 다중 로봇 워크숍 | 연구 질문 2의 첫 곡선 |
| 학회 (군집 전문) | ANTS, SWARM, DARS | 연구 질문 1과 2, 기준선 3개 |
| 학회 (일반 로봇·에이전트) | IROS, ICRA, AAMAS | 연구 질문 1–3, 이종 확장 |
| 학술지 | Swarm Intelligence, Autonomous Robots | 전체 결과와 실제 로봇 또는 이종 확장 |

- 투고처 전체 이름은 용어 부록에 있다.

## 11. 선택 기록 (selection log)

| 후보 | 결정 | 이유 |
| --- | --- | --- |
| 협력 다중 로봇 다중 이동 표적 관측(cooperative multi-robot observation of multiple moving targets, CMOMMT) 갈래 (Parker 2002) | 유지 | 문제 정의의 원조 |
| La와 Sheng 2012 | 유지 | 가장 가까운 분열-융합 추적 |
| Low 등 2004 | 유지 | 비례 배치의 선행 |
| Lei 등 2023 | 유지 | 다중 소그룹 링 |
| 트랜스포머 강화 강화 학습(Transformer-Enhanced Reinforcement Learning, TERL) 2025 | 유지 | 최신 학습 기반 기준 |
| 분열-융합 무인 항공기(unmanned aerial vehicle, UAV) 제어 2022 | 유지, 미검증 | HTTP 403 |
| Mathews 등 2017 | 유지 | 소유자가 예로 든 갈래 |
| Senanayake 등 2016 군집 탐색·추적 조사 | 제외 | 검색 요약만 봤다. 예산 |
| 무리 분열 물리 모형 (Physica A 2022) | 제외 | 검색 요약만 봤다. 로봇 규칙 아님 |
| UNR 계층 추적 (로봇보다 표적이 많을 때) | 제외 | 검색 요약만 봤다. 예산 |
| Franchi 등 분산 포위 | 제외 | 페이지 봇 차단 |
| Aceto 등 2014 순환 종양 세포 무리 | 유지, 부분 | 응용 (a). 뉴스로만 읽었다 |
| Yang 등 2022 군집 미세 로봇 조사 | 유지 | 응용 (a)의 감지 한계 |
| Friedl과 Mayor 2017 집단 세포 이동 | 유지 | 응용 (a)의 분열-융합 모습 |
| Friedl과 Gilmour 2009 집단 세포 이동 | 제외 | 검색 요약만 봤다 |
| 가상 울타리 사실 자료 (BCRC) | 유지 | 응용 (b)의 감지와 구동 |
| 들소 분열-융합 2026 | 유지 | 응용 (b). 소 자료 대신 |
| Cape buffalo 분열-융합 | 제외 | 페이지 봇 차단 |
| 드론 가축 탐지 조사 2025 | 유지 | 응용 (b)의 성숙도 |
| Long 등 2020 몰이 조사, Liu 등 2023 흩어진 무리 몰이 | 유지 | §13 몰이 확장 |
| Yaxley 등 2021 드론 양 몰이 | 유지 | §13 복지 한계 |
| Dames 2017 탐색과 추적 | 유지 | §14 탐색 단계의 선행 |
| Senanayake 등 2016 군집 탐색·추적 조사 (재시도) | 제외 | HTTP 403 |

## 12. 응용 (applications)

- 응용 틀은 사람 감시가 아니다 (소유자, 2026-11-10).
- 소유자 원문: "인체 내부에서 특정 세포 이동을 추적한다던지, 농장에서 목초지에서 퍼진 소들을 추적한다던지".

| 항목 | (a) 몸속 세포 추적 | (b) 목초지 소 떼 추적 |
| --- | --- | --- |
| 표적 | 함께 이동하는 세포 무리 | 퍼져서 풀을 뜯는 소 떼 |
| 추적자 | 미세 로봇(microrobot) 군집 | 무인 지상 차량(unmanned ground vehicle, UGV), 드론, 목걸이 |
| 감지·계산 | 매우 제한적 | 넉넉함 (위성 위치, 카메라) |
| ARGoS 대응 | 감지를 줄인 foot-bot | 기본 foot-bot |
| 성숙도 | 연구 단계 | 일부 제품화 (가상 울타리 목걸이) |

### 12.1 (a) 몸속 미세 로봇 군집이 이동 세포를 추적

분열과 융합의 모습:

- 세포는 무리로 함께 이동한다(collective cell migration). 세포 간 접합(junction)이 조정, 고정, 떨어짐을 정한다 [S-SMT-21].
- 갈라짐: 접합이 풀리면 세포가 무리에서 떨어진다. 암 침윤과 전이에서도 접합이 바뀐다 [S-SMT-21].
- 합침: 백혈구(leukocyte)가 잠깐 접합을 맺어 단단한 무리로 모인다고 본문이 설명한다 [S-SMT-21]. 본문 중 일부만 읽었다.
- 순환 종양 세포 무리(circulating tumor cell cluster): 순환 종양 세포의 2–5%지만, 동물 모형에서 폐 전이의 약 절반에 기여했다 [S-SMT-19].
- 전이 가능성은 단일 세포의 23–50배로 추정됐다 [S-SMT-19].
- 이 무리는 혈관 안에서 뭉친 것이 아니라 원래 종양에서 붙어 있던 세포에서 온다고 본다 [S-SMT-19].
- 그래서 무리 단위 추적은 의미가 있다. 다만 혈액 속 무리가 반복해서 갈라지고 합치는지는 확인하지 못했다 (inference).

감지와 구동의 한계:

- 미세 로봇 하나는 부피와 표면이 작다. 그래서 몸속 추적 같은 일은 큰 군집을 동시에 제어해야 한다 [S-SMT-20].
- 미세 로봇에는 몸에 센서와 구동기를 넣기 어렵다 [S-SMT-20].
- 군집 제어 자체가 이 분야의 주요 과제다 [S-SMT-20].
- 그래서 로봇마다 다른 결정을 내리는 지역 규칙은 지금 기술로는 어렵다 (inference).

ARGoS foot-bot에 옮기는 법 (inference):

- 거리-방위 센서(range-and-bearing sensor) 통신을 끈다. 미세 로봇끼리 메시지를 주고받기 어렵기 때문이다.
- 위치 센서(positioning sensor)를 끈다. 근접 센서의 짧은 거리만 남긴다.
- 선택: 모든 로봇에 같은 명령(외부 자기장 같은 전역 신호)을 주는 기준선을 둔다.
- 질문이 바뀐다: "감지가 거의 없을 때 분열-융합 추적이 얼마나 무너지나?"

성숙도:

- 연구 단계다. 조사 논문은 생체 내 추적에 대형 군집 제어가 필요하다고 한다 [S-SMT-20].
- 이 응용은 시뮬레이션 연구 질문을 위한 동기로 쓴다. 의료 실현을 주장하지 않는다 (inference).

Qi (Luki) Lu 교수와의 연결:

- 연구 페이지에 나노 규모 채집과 자기 조립(nanoscale foraging and self-assembly)이 있다 [S-SMT-15].
- 감지가 적은 군집이라는 점이 이 응용과 닿는다 (inference, 그 작업의 방법은 읽지 않음).

### 12.2 (b) 목초지에서 퍼진 소 떼 추적

분열과 융합의 모습:

- 들소(plains bison)는 작은 무리로 갈라지고 큰 무리로 다시 합친다 [S-SMT-23].
- Montana 연구: 태양광 위성 위치(GPS) 귀표로 세 무리를 여러 해 추적했다. 무리마다 성체 암컷의 25–90%에 달았다 [S-SMT-23].
- 사건 정의: 2마리 이상이 무리를 떠나거나 합류하면 분열 또는 융합으로 센다 [S-SMT-23].
- 먹이의 질과 양, 땅 덮개, 무리 크기와 혈연이 분열-융합 확률에 영향을 준다 [S-SMT-23].
- 가축 소 자체의 분열-융합 측정 논문은 이번 조사에서 찾지 못했다.
- 이 정의는 로봇 실험의 분열과 융합 판정 규칙으로 그대로 쓸 수 있다 (inference).

감지와 구동의 한계:

- 가상 울타리 목걸이: 사용자가 경계를 그린다. 위치 정확도는 2 m 이내라고 한다 [S-SMT-22].
- 경계에 가까워지면 소리 신호가 커지고, 전기 자극을 준다 [S-SMT-22].
- 휴대 전화망(LTE)이 있으면 쓰고, 없으면 위성 위치만 쓴다 [S-SMT-22].
- 1세대 목걸이는 하드웨어 고장이 있었다. 세게 머리를 흔들면 목걸이가 옆으로 밀렸다 [S-SMT-22].
- 드론 영상의 가축 탐지: 조사 논문이 딥러닝 탐지기를 맞춤 소 영상 자료로 비교했다. 지표마다 맞교환이 있다 [S-SMT-24].
- 넓은 목초지에서는 배터리와 통신 거리가 추적 로봇의 한계가 된다 (inference).

ARGoS foot-bot에 옮기는 법 (inference):

- 표적 foot-bot = 소. 무작위 걷기로 풀을 뜯고, 먹이 구역 쪽으로 갈라진다.
- 추적 foot-bot = 무인 지상 차량(unmanned ground vehicle, UGV). 기본 센서를 모두 쓴다.
- 확장: 넓게 보는 로봇 하나를 무인 항공기(unmanned aerial vehicle, UAV) 역할로 둔다.
- 분열과 융합 판정은 들소 연구의 "2마리 이상" 규칙을 따른다 [S-SMT-23].

성숙도:

- 가상 울타리 목걸이는 현장 시험과 2세대 제품 단계다 [S-SMT-22].
- 드론 가축 탐지는 연구와 비교 평가 단계다 [S-SMT-24].
- 여러 로봇이 갈라지는 소 떼를 나눠 따라가는 시스템은 이번 조사에서 찾지 못했다.

## 13. 확장: 추적에서 몰이로 (extension: from tracking to herding, shepherding)

소유자 원문 (2026-11-10):

> 이 드론들이 소들을 필요한 곳으로 몰이 할 수 있는 거잖아?

```
 추적 (§1–§6)                         몰이 (이 절)
 무리가 갈라짐 -> 로봇이 따라감        무리가 갈라짐 -> 로봇이 "관측" 또는 "몰기" 역할
 지표: 관측률, 전환 빈도               지표: 목표 도착 비율, 시간, 동물 스트레스
 질문: 몇 대를 어느 무리에?            질문: 어느 무리를 먼저 모으나? 몇 대를 보내나?
```

### 13.1 선행 연구

| 갈래 | 있는 것 | 검증 | 출처 |
| --- | --- | --- | --- |
| [몰이(shepherding)](#term-shepherding) 기본 규칙 | Strömbom 등: 몰이꾼 하나가 "모으기(collect)"와 "밀기(drive)" 두 방식을 오간다 | 이전 회차 [STALE] | [S-SMT-25] |
| 군집 몰이 조사 | Long, Sammut, Sgarioto, Garratt, Abbass: 소수의 몰이꾼이 단순한 군집을 목표로 이끈다. 모의 양 몰이부터 실제 차량과 로봇까지 검토한다 | verified: 초록 | [S-SMT-26] |
| 흩어진 무리 몰이 순서 | Liu 등 (Abbass 그룹): 양을 거리로 묶어 부분 무리로 나눈다. 몰이 전체를 외판원 문제(travelling salesman problem)로 풀어 모으는 순서를 정한다. 장애물을 피한다 | verified: 초록 | [S-SMT-27] |
| 드론의 실제 양 몰이 | Yaxley, Joiner, Abbass: Dorper 양 12마리. 소리를 내면 경계 거리가 약 51 m에서 약 82 m로 늘었다. 심박은 크게 오르지 않았다 | verified: 본문 일부 | [S-SMT-28] |
| 동물 복지 한계 | 같은 연구: 양의 최고 심박이 200 bpm을 넘으면 시험을 멈췄다. 드론은 양 둘레 20 m 안전 구역에 들어가지 않았다 | verified | [S-SMT-28] |
| 위험에서 무리 돌리기 | 여러 로봇이 무리를 감싸 위험에서 돌린다 | 이전 회차 | [S-SMT-17] |

- 소를 드론이나 로봇으로 모는 현장 연구는 이번 조사에서 찾지 못했다.
- 양 연구는 한 농장, 12마리다 [S-SMT-28]. 소에 그대로 옮길 수 없다 (inference).

### 13.2 추적에서 몰이로 가면 문제가 어떻게 바뀌나 (inference)

1. 역할이 둘로 나뉜다: "관측" 로봇과 "몰기" 로봇.
2. 관측 로봇은 무리 위치를 몰이 로봇에게 알린다. 몰이 로봇은 모으기와 밀기를 한다 [S-SMT-25].
3. 무리가 계속 갈라지면 배정 문제가 된다.
   - 어느 부분 무리를 먼저 모으나?
   - 부분 무리마다 몰이 로봇을 몇 대 보내나?
4. 모으는 동안 다른 무리가 또 갈라질 수 있다. 그래서 순서는 고정이 아니라 다시 짜야 한다.
5. 새 지표: 목표에 도착한 동물 비율, 걸린 시간, 동물 스트레스 대용값(로봇과의 최소 거리).
6. 복지 제약이 규칙에 들어간다. 예: 안전 거리 안으로 들어가지 않는다 [S-SMT-28].

### 13.3 열려 있나 (inference)

- 모으는 순서는 몰이꾼 하나에 대해 연구가 있다 [S-SMT-27].
- 이번 조사에서 못 찾은 것:
  - 몰이꾼 여럿을 부분 무리에 나눠 보내는 분산 배정.
  - 몰이 도중 무리가 반복해서 갈라지고 합치는 조건.
  - "관측"과 "몰기"의 역할 나눔과 그 비율.
- 이 셋의 조합은 출처를 못 찾았다. 아무도 안 했다는 증거가 아니다 (`rules/research.md` §10).
- 다중 몰이꾼 절은 조사 논문 [S-SMT-26]의 본문에서 확인하지 않았다. 재확인이 필요하다.
- 정정 (2026-11-10): 첫 항목 "다중 몰이꾼 분산 배정"은 선행 연구가 있다. `recent_review.md`의 [S-RR-3], [S-RR-16], [S-RR-29]를 본다.
- 남은 빈틈은 둘째와 셋째 항목이다. 반복 분열·융합 조건과 관측·몰기 역할 비율이다.

### 13.4 기존 몰이 과제와의 관계

- `submodule_project/research/lu_qi.md`의 "Shepherding and herding" 과제를 읽기만 했다. 고치지 않았다.
- 그 과제: 9위, R2 F2 Fit1 = 4. Strömbom 모으기·밀기, 몰이꾼 1·2·4대 비교, 각도 구역 나눔.
- 차이:

| 항목 | 기존 몰이 과제 | 이 확장 |
| --- | --- | --- |
| 무리 | 한 무리 (양 20마리) | 반복해서 갈라지고 합치는 무리 |
| 로봇 역할 | 몰이만 | 관측과 몰이 |
| 핵심 질문 | 몰이꾼 수에 따른 시간 | 어느 무리를 먼저, 몇 대씩 |
| 앞 단계 | 없음 | 분열-융합 추적 (§1–§6) |

- 기존 과제의 양 제어기와 모으기·밀기 코드는 이 확장의 몰이 단계로 다시 쓸 수 있다 (inference).
- 기존 과제의 맞음(Fit)은 1이다. 이 확장도 몰이 부분은 Qi Lu 교수 논문과 직접 겹치지 않는다 (inference).

## 14. 전체 파이프라인: 펼치기에서 몰이까지

소유자 원문 (2026-11-10):

> 드론을 펼치고 자동으로 분열후 목표 대상 또는 그룹을 찾아서 원하는 방향으로 이동 시키기?

```
 1 펼치기 -> 2 탐색 -> 3 탐지·묶기 -> 4 분열·배정 -> 5 추적 -> 6 몰이
  (기존)     (기존:      (기존)          (새 기여)       (기존)    (기존 + §13)
            Qi Lu 나선)
                 ^                            |
                 +---- 새 무리가 나타나면 다시 탐색 ----+
```

| 단계 | 하는 일 | 쓰는 방법 | 새로움 | 출처 |
| --- | --- | --- | --- | --- |
| 1 펼치기 | 로봇을 출발 구역에서 퍼뜨린다 | 무작위 퍼짐 또는 구역 나눔 | 기존 | inference |
| 2 탐색 | 아직 못 찾은 표적을 찾는다 | Qi Lu의 양방향 나선 탐색, 무작위 걷기 채집 | 기존. Qi Lu와의 실제 맞음 지점 | [S-SMT-30], [S-SMT-15] |
| 3 탐지·묶기 | 표적을 보고 거리로 무리를 묶는다 | 거리 기반 묶기. Qi Lu 연구실은 밀도 기반 묶기(density-based spatial clustering of applications with noise, DBSCAN)를 방어에 썼다 | 기존 | [S-SMT-31] |
| 4 분열·배정 | 로봇 군집을 무리마다 나누고, 반복 분열-융합에 다시 나눈다 | 비례 규칙 + 이력 현상(hysteresis) (§5.1) | **새 기여 후보** | §3, §13.3 |
| 5 추적 | 부분 군집이 링으로 무리를 둘러싼다 | 협력 관측, 밀도 기반 포위 | 기존 | [S-SMT-1], [S-SMT-8] |
| 6 몰이 | 무리를 목표 구역으로 모은다 | 모으기·밀기, 모으는 순서 계획 | 기존. 다중 몰이꾼 배정은 4단계와 같은 문제 | [S-SMT-25], [S-SMT-27] |

- 새 기여는 4단계 하나에 둔다 (inference).
- 이유: 2, 3, 5, 6단계는 각각 알려진 방법이 있다. 4단계의 반복 분열-융합 배정은 이번 조사에서 출처를 못 찾았다 (§3, §13.3).
- 6단계의 다중 몰이꾼 배정(연구 질문 4)은 4단계 배정 규칙을 몰이에 다시 쓰는 것이다 (inference).

### 14.1 탐색과 추적을 함께 다룬 선행 연구

- Dames: 로봇 팀이 수를 모르는 표적을 찾고 추적한다. 표적은 들어오고 나간다 [S-SMT-29].
- 방법: 분산 확률 가설 밀도 필터(probability hypothesis density filter, PHD filter)로 표적 수와 위치를 추정한다. 그 출력을 Lloyd 알고리즘의 가중치로 쓴다 [S-SMT-29].
- 시뮬레이션: 로봇 10–100대, 표적 10–50개 [S-SMT-29].
- 같은 논문은 협력 다중 로봇 다중 이동 표적 관측(cooperative multi-robot observation of multiple moving targets, CMOMMT)을 이렇게 설명한다: 모든 표적을 동시에 관측하려 하고, 안 되면 안 보이는 시간을 줄인다 [S-SMT-29].
- 표적 무리의 분열-융합과 몰이는 이 논문 1쪽에 없다.
- 확률적 탐색은 센서 잡음이 클 때 맞는다고 그 논문은 쓴다 [S-SMT-29].
- 탐색 다음 몰이까지 잇는 연구는 이번 조사에서 찾지 못했다. Liu 등은 흩어진 무리를 묶고 순서를 정하지만, 탐색 단계는 초록에 없다 [S-SMT-27].

### 14.2 맞음(Fit) 다시 보기 (inference)

- 2단계 탐색은 Qi Lu의 나선 탐색 논문[S-SMT-30]과 채집 논문들[S-SMT-15]을 그대로 쓴다.
- 그래서 전체 파이프라인은 추적만 할 때보다 맞음(Fit)이 높다.

| 범위 | R | F | Fit | 합계 | 이유 |
| --- | --- | --- | --- | --- | --- |
| 추적만 (§9) | 2 | 2 | 2 | 8 | 위와 같다 |
| 전체 파이프라인, 수업 2주 기준 | 2 | 1 | 3 | 6 | 2단계가 Qi Lu 논문과 직접 겹친다. 6단계를 2주에 다 만들기 어렵다 |

- 개인 연구로 길게 가면 실현 가능성(F)의 2주 기준이 맞지 않는다. 이 점수는 비교용이다.

### 14.3 로드맵

| 순서 | 단계 | 내용 | 연구 질문 |
| --- | --- | --- | --- |
| 1 | 최소 실행 제품(minimum viable product, MVP) 1단계 | 표적 위치를 알고 시작. 4·5단계만. 무리 2개 | 연구 질문 2 |
| 2 | 반복 분열 | 4·5단계, 무리 3–4개, T 바꾸기 | 연구 질문 1, 2, 3 |
| 3 | 탐색 붙이기 | 2·3단계 추가. 나선 탐색 [S-SMT-30] | 탐색 비용이 관측률에 주는 영향 (inference) |
| 4 | 몰이 붙이기 | 6단계 추가. 관측과 몰기 역할 나눔 | 연구 질문 4, 5 |
| 5 | 전체 | 1–6단계, 새 무리가 나타나면 다시 탐색 | 전체 성공률, 시간 |

## open_questions:

- Parker 2002의 초록과 방법은 읽지 못했다. 검색 요약뿐이다 [S-SMT-1].
- Robin과 Lacroix 2016: HAL 봇 차단 [S-SMT-4].
- 2022 Aerospace 분열-융합 논문: 저자와 내용을 원문에서 확인하지 못했다 [S-SMT-5].
- Couzin과 Laidre 2009: 서지만 검색 요약에서 봤다 [S-SMT-3].
- La와 Sheng 2012의 분할 규칙이 분산형인지, 반복 분열-융합 실험이 있는지: 3쪽 이후를 읽지 않았다 [S-SMT-6].
- Lei 등 2023 본문에 반복 분열-융합 실험이 있는지 확인하지 않았다 [S-SMT-8].
- Kolling과 Carpin, Jung 등의 다중 표적 추적: 원문을 읽지 않았다 [S-SMT-6].
- foot-bot 거리-방위 센서(range-and-bearing sensor) 기본 거리(포럼 요약은 6 m)를 확인하지 못했다.
- `CCI_PositioningSensor`가 주는 값의 내용을 확인하지 못했다 [S-SMT-12].
- 빈틈 재확인 조사를 아직 하지 않았다 (§3).
- 순환 종양 세포 무리 수치는 뉴스 기사로 읽었다. 원문(Cell 2014)은 읽지 않았다 [S-SMT-19].
- 혈액 속 세포 무리가 반복해서 갈라지고 합치는지 확인하지 못했다 (§12.1).
- 가축 소의 분열-융합 측정 논문을 찾지 못했다. 들소 연구로 대신했다 [S-SMT-23].
- 드론 가축 탐지 조사 논문 본문을 읽지 않았다. 서지 정보와 초록만 봤다 [S-SMT-24].
- 소를 드론이나 로봇으로 모는 현장 연구를 찾지 못했다 (§13.1).
- 군집 몰이 조사 논문의 다중 몰이꾼 절을 확인하지 않았다 [S-SMT-26].

## 용어 부록 (terms appendix)

- <a id="term-swarm"></a>군집(swarm): 단순한 로봇 여럿이 지역 규칙으로 함께 일하는 무리.
- <a id="term-formation"></a>대형(formation): 로봇들이 지키는 상대 위치 모양. 예: 링.
- <a id="term-cmommt"></a>협력 다중 로봇 다중 이동 표적 관측(cooperative multi-robot observation of multiple moving targets, CMOMMT): 로봇 팀이 이동 표적을 최대한 오래 관측하는 문제.
- <a id="term-flocking"></a>무리 짓기(flocking): 가까이 붙고, 부딪히지 않고, 같은 방향으로 가는 집단 운동.
- <a id="term-sggp"></a>씨앗 성장 그래프 분할(seed growing graph partition, SGGP): 센서 연결 그래프를 씨앗에서 키워 무리를 나누는 방법.
- <a id="term-encirclement"></a>포위(encirclement): 로봇들이 표적 둘레를 감싸는 일.
- <a id="term-terl"></a>트랜스포머 강화 강화 학습(Transformer-Enhanced Reinforcement Learning, TERL): 트랜스포머로 표적 우선순위를 배우는 다중 표적 포위 방법.
- <a id="term-fission-fusion"></a>분열-융합(fission-fusion): 무리가 자주 갈라지고 다시 합치는 집단 구조.
- <a id="term-uav"></a>무인 항공기(unmanned aerial vehicle, UAV): 사람이 타지 않는 비행 로봇.
- <a id="term-ugv"></a>무인 지상 차량(unmanned ground vehicle, UGV): 사람이 타지 않는 지상 로봇.
- <a id="term-cbba"></a>합의 기반 묶음 알고리즘(consensus-based bundle algorithm, CBBA): 로봇들이 경매와 합의로 작업을 나누는 방법.
- <a id="term-churn"></a>전환 빈도(churn): 로봇 1대가 1분에 부분 군집을 바꾸는 횟수.
- <a id="term-hysteresis"></a>이력 현상(hysteresis): 조건이 일정 시간 이어져야 상태를 바꾸는 규칙. 잦은 뒤집힘을 막는다.
- <a id="term-loop-functions"></a>루프 함수(loop functions): ARGoS에서 매 단계 실험 환경을 다루는 사용자 코드.
- <a id="term-led"></a>발광 다이오드(light-emitting diode, LED): 로봇 몸의 색 표시등.
- <a id="term-rab"></a>거리-방위 센서(range-and-bearing sensor): 이웃 로봇의 메시지와 함께 그 거리와 방향을 받는 장치.
- <a id="term-positioning"></a>위치 센서(positioning sensor): 시뮬레이터가 로봇의 위치와 방향을 주는 센서.
- <a id="term-api"></a>응용 프로그래밍 인터페이스(application programming interface, API): 코드가 부르는 클래스와 함수의 목록.
- <a id="term-mvp"></a>최소 실행 제품(minimum viable product, MVP): 처음부터 끝까지 도는 가장 단순한 판.
- <a id="term-shepherding"></a>몰이(shepherding): 소수의 몰이꾼이 무리를 목표 쪽으로 모으고 미는 일.
- <a id="term-dhs"></a>미국 국토안보부(Department of Homeland Security, DHS): 미국 연방 부처. 연구 자금을 준다.
- 연구 질문(research question, RQ): 이 연구가 답하려는 물음.
- 투고처 이름:
  - ANTS: International Conference on Swarm Intelligence.
  - DARS: International Symposium on Distributed Autonomous Robotic Systems.
  - SWARM: International Symposium on Swarm Behavior and Bio-Inspired Robotics.
  - IROS: IEEE/RSJ International Conference on Intelligent Robots and Systems.
  - ICRA: IEEE International Conference on Robotics and Automation.
  - AAMAS: International Conference on Autonomous Agents and Multiagent Systems.

## Sources

[S-SMT-1] Distributed Algorithms for Multi-Robot Observation of Multiple Moving Targets | https://bibbase.org/network/publication/parker-distributedalgorithmsformultirobotobservationofmultiplemovingtargets-2002 | published: 2002-05, Autonomous Robots 12(3) 231 to 255 | accessed: 2026-11-10 | type: paper | note: BibBase record only, method from search snippet, DOI 10.1023/A:1015256330750 per snippet, partial
[S-SMT-2] Mergeable nervous systems for robots | https://pmc.ncbi.nlm.nih.gov/articles/PMC5595853 | published: 2017-09-12, Nature Communications 8:439 | accessed: 2026-11-10 | type: paper | note: PMC full text page, verified
[S-SMT-3] Fission-fusion populations | https://doi.org/10.1016/j.cub.2009.05.034 | published: 2009-08, Current Biology 19(15) R633 to R635 per search snippet | accessed: 2026-11-10 | type: paper | note: PubMed and Cell pages blocked, search snippet only, UNVERIFIED
[S-SMT-4] Multi-robot target detection and tracking: taxonomy and survey | https://hal.archives-ouvertes.fr/hal-01183372 | published: 2016, Autonomous Robots 40(4) 729 to 760 per search snippet | accessed: 2026-11-10 | type: paper | note: blocked by bot check, search snippet only, UNVERIFIED
[S-SMT-5] Bio-Inspired Self-Organized Fission-Fusion Control Algorithm for UAV Swarm | https://doaj.org/article/5f928ede5d1c4b5882e5d932d6e2c692 | published: 2022-11 per search snippet, Aerospace | accessed: 2026-11-10 | type: paper | note: HTTP 403, search snippet only, UNVERIFIED
[S-SMT-6] Dynamic target tracking and observing in a mobile sensor network | https://ara.cse.unr.edu/wp-content/uploads/2014/12/Elsevier_RAS_La2012.pdf | published: 2012, Robotics and Autonomous Systems 60 996 to 1009 | accessed: 2026-11-10 | type: paper | note: pages 1 and 2 read, authors La and Sheng, DOI 10.1016/j.robot.2012.03.006, verified
[S-SMT-7] Task Allocation via Self-Organizing Swarm Coalitions in Distributed Mobile Sensor Network | https://www.comp.nus.edu.sg/~lowkh/pubs/aaai2004.pdf | published: 2004, AAAI per copyright line | accessed: 2026-11-10 | type: paper | note: pages 1 and 2 read, authors Low, Leow, Ang, verified
[S-SMT-8] Self-organized multi-target trapping of swarm robots with density-based interaction | https://www.springerprofessional.de/self-organized-multi-target-trapping-of-swarm-robots-with-densit/24596984 | published: 2023-03-08, Complex and Intelligent Systems | accessed: 2026-11-10 | type: paper | note: abstract on a secondary host, authors Lei, Zhang, Xiang, Duan, verified
[S-SMT-9] TERL: Large-Scale Multi-Target Encirclement Using Transformer-Enhanced Reinforcement Learning | https://arxiv.org/abs/2503.12395 | published: 2025-03-16, revised 2025-08-27 | accessed: 2026-11-10 | type: paper | note: abstract page, accepted IROS 2025, verified
[S-SMT-10] AI for robots and swarms: ARGoS reference | https://opentechschool-brussels.github.io/AI-for-robots-and-swarms/ref_argos.html | published: undated | accessed: 2026-11-10 | type: blog | note: third-party tutorial, range_and_bearing fields of the Lua interface, partial
[S-SMT-11] User guide: The foot-bot | https://dgarzonramos.github.io/robotics101/fbot | published: undated | accessed: 2026-11-10 | type: blog | note: third-party tutorial, range_and_bearing fields of the Lua interface, partial
[S-SMT-12] argos::CCI_PositioningSensor Class Reference | https://www.argos-sim.info/api/a03140.php | published: live API docs | accessed: 2026-11-10 | type: official | note: class existence verified, reading contents not shown
[S-SMT-13] argos3-examples: loop_functions folder | https://github.com/ilpincy/argos3-examples/tree/master/loop_functions | published: master branch | accessed: 2026-11-10 | type: official | note: carried over from the LQ pass (S-LQ-7), not re-read
[S-SMT-14] Qi (Luki) Lu: personal site | https://sites.google.com/view/qilu/ | published: undated | accessed: 2026-11-10 | type: official | note: carried over from the LQ pass (S-LQ-1), funding list, not re-read
[S-SMT-15] Qi Lu: Research | https://sites.google.com/view/qilu/research | published: undated | accessed: 2026-11-10 | type: official | note: carried over from the LQ pass (S-LQ-2), not re-read
[S-SMT-16] CAHSI expert profile: Qi Lu | https://cahsi.utep.edu/expert/qi-lu/ | published: undated | accessed: 2026-11-10 | type: official | note: carried over from the LQ pass (S-LQ-4), not re-read
[S-SMT-17] Steering herds away from dangers in dynamic environments | https://research.wur.nl/en/publications/steering-herds-away-from-dangers-in-dynamic-environments/ | published: 2023, Royal Society Open Science 10(5) 230015 | accessed: 2026-11-10 | type: paper | note: carried over from the LQ pass (S-LQ-11), record page, not re-read
[S-SMT-18] Consensus-Based Decentralized Auctions for Robust Task Allocation | https://dspace.mit.edu/handle/1721.1/52330 | published: 2009, IEEE Transactions on Robotics 25(4) 912 to 926 per search snippet | accessed: 2026-11-10 | type: paper | note: carried over from the LQ pass (S-LQ-38), HTTP 429 there, partial
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
