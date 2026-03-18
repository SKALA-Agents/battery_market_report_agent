# Battery Market Report Agent

> LG에너지솔루션과 CATL의 전략을 데이터 기반으로 비교 분석하고, 의사결정에 활용 가능한 시장 보고서를 생성하는 멀티 에이전트 시스템

- 핵심 목표 : **비교 가능성, 근거성, 추적 가능성**을 갖춘 배터리 시장 리포트를 자동 생성
- 분석 파이프라인 : `시장 분석` → `기업별 조사/분석` → `비교` → `SWOT` → `인사이트 생성` → `보고서 생성`
- `LG 에너지 솔루션`이 보고서의 주요 독자라는 가정 하에 작성

## Overview
- **Objective**
  LG에너지솔루션과 CATL의 경쟁력, 전략 차이, 리스크를 동일한 기준으로 비교하고 의사결정에 활용 가능한 시사점을 도출하고 보고서로 작성

- **Method**
  `Supervisor Pattern`, `Parallel Branch`, `RAG-first Retrieval`, `Web Search Fallback` 구조를 결합해 신뢰도 높은 분석 흐름 구성

- **Output**
  배터리 시장 전략 분석 보고서
  - Executive Summary, 시장 분석, 기업별 전략 분석, 비교표, 기업별 SWOT, 전략 인사이트, References

## Key Features
1. SWOT 분석과 SO/ST/WO/WT 전략 인사이트 도출을 포함한 의사결정형 보고서 생성
2. `RAG-first + Web Search fallback` 설계를 통해 자료 부족·최신성 부족·출처 편향이 감지될 때 `retry/loop` 분기로 보강
3. 동일한 7개 평가 기준을 양사에 공통 적용해 비교 일관성과 해석 가능성을 확보
   - 포트폴리오 다양성, 기술 경쟁력, 시장 대응력, 공급망 전략, 고객/파트너 구조, 글로벌 확장성, 리스크 대응력
4. source id와 metadata 기반 근거 링크를 통해 보고서의 근거 확인 가능

## Multi-Agent & Role
- `Supervisor Agent`: 실행 순서 제어, validation 판단, retry/loop 분기, 브랜치 동기화
- `Market Agent`: 시장 환경 구조화 및 공통 분석 프레임 생성
- `LG Research Agent`: LG 관련 자료 수집 및 검증
- `CATL Research Agent`: CATL 관련 자료 수집 및 검증
- `LG Strategy Agent`: LG 전략 분석
- `CATL Strategy Agent`: CATL 전략 분석
- `Synthesis Agent`: 비교 분석, SWOT 생성, 전략 인사이트 도출, 최종 보고서 생성

## Architecture

![diagram](README.img/diagram.png)

`Supervisor Pattern with Parallel Branch` 구조를 사용

- 크게 3단계로 구성된 workflow에서 `Supervisor`가 각 단계의 결과를 검증하고 다음 실행 단계를 결정한다.
- `LGES`와 `CATL` 브랜치는 병렬 실행되며, branch별 retry/loop 정책을 독립적으로 판단하고 실행한다.
- `compare_node`는 두 브랜치가 모두 pass 상태일 때만 실행된다.

## Workflow

![Workflow](README.img/flow.png)

## Directory Structure
```text
[최종 나오면 채우기]
```

## Tech Stack

| Category | Details |
|----------|---------|
| Framework | LangGraph, LangChain, Python |
| LLM | OpenAI API |
| Retrieval | FAISS |
| Web Search | Tavily |
| Embedding | BAAI/bge-m3 |
| Runtime Pattern | Static KB + Runtime Augmentation |
| State Management | TypedDict-based Workflow State |

## Contributors 
- 김유빈 :
- 양예원 : 
