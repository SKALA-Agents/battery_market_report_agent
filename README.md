# Battery Market Report Agent

LG에너지솔루션과 CATL의 전략을 데이터 기반으로 비교 분석하고, 의사결정에 활용 가능한 시장 보고서를 생성하는 멀티 에이전트 시스템입니다.

이 프로젝트는 단순 요약형 에이전트가 아니라, `시장 분석 -> 기업별 조사/전략 분석 -> 비교 -> SWOT -> 인사이트 -> 보고서 생성`까지 이어지는 구조적 분석 파이프라인을 구현합니다. 핵심 목표는 **비교 가능성, 근거성, 추적 가능성**을 갖춘 배터리 시장 인텔리전스 리포트를 자동 생성하는 것입니다.

## Overview
- **Objective**
  LG에너지솔루션과 CATL의 경쟁력, 전략 차이, 리스크를 동일한 기준으로 비교하고 실행 가능한 시사점을 도출합니다.
- **Method**
  `Supervisor Pattern`, `Parallel Branch`, `RAG-first Retrieval`, `Web Search Fallback` 구조를 결합해 신뢰도 높은 분석 흐름을 구성합니다.
- **Output**
  Executive Summary, 시장 분석, 기업별 전략 분석, 비교표, 기업별 SWOT, 전략 인사이트, References를 포함한 최종 보고서를 생성합니다.

## Key Features
- `Supervisor`가 전체 workflow를 통제하며 단계별 실행, 검증, retry/loop, branch synchronization을 관리합니다.
- `LG`와 `CATL` 브랜치를 병렬로 분리해 데이터 혼입 없이 독립적인 분석을 수행합니다.
- `Market KB`, `LG KB`, `CATL KB`를 분리한 RAG 구조로 컨텍스트 오염을 줄입니다.
- `RAG-first` 전략을 적용하고, 자료 부족·최신성 부족·출처 편향이 감지될 때만 `Web Search`로 보강합니다.
- 동일한 7개 평가 기준을 양사에 공통 적용해 비교 일관성과 해석 가능성을 확보합니다.
- source id와 metadata 기반 추적 구조를 통해 보고서의 근거를 역추적할 수 있습니다.
- 대칭 질의, 출처 다양성, 반증 근거 수집을 통해 확증 편향을 완화합니다.

## Workflow
1. `Market Agent`가 시장 환경과 공통 분석 프레임을 구성합니다.
2. `Supervisor`가 `LG`와 `CATL` 브랜치를 병렬 실행합니다.
3. 각 브랜치는 자료 수집, 검증, 전략 분석을 독립적으로 수행합니다.
4. 두 브랜치가 모두 검증을 통과하면 `Compare` 단계로 진입합니다.
5. 이후 `SWOT`, `Insight`, `Report` 순으로 통합 분석을 수행합니다.
6. 최종적으로 의사결정형 보고서를 생성합니다.

![Workflow](README.img/flow.png)

## Analysis Criteria
- 포트폴리오 다양성
- 기술 경쟁력
- 시장 대응력
- 공급망 전략
- 고객/파트너 구조
- 글로벌 확장성
- 리스크 대응력

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

## Agent Roles
- `Supervisor Agent`: 실행 순서 제어, validation 판단, retry/loop 분기, 브랜치 동기화
- `Market Agent`: 시장 환경 구조화 및 공통 분석 프레임 생성
- `LG Research Agent`: LG 관련 자료 수집 및 검증
- `CATL Research Agent`: CATL 관련 자료 수집 및 검증
- `LG Strategy Agent`: LG 전략 분석
- `CATL Strategy Agent`: CATL 전략 분석
- `Synthesis Agent`: 비교 분석, SWOT 생성, 전략 인사이트 도출, 최종 보고서 생성

## Architecture
본 시스템은 `Supervisor Pattern with Parallel Branch` 구조를 채택합니다.

- `Supervisor`는 직접 분석을 수행하기보다 각 단계의 결과를 검증하고 다음 실행 단계를 결정합니다.
- `LG`와 `CATL` 브랜치는 병렬 실행되며, branch별 retry/loop 정책을 독립적으로 가집니다.
- `compare_node`는 두 브랜치가 모두 pass 상태일 때만 실행됩니다.
- 비교 이후 단계는 기존 분석 결과와 source metadata를 기반으로만 통합 분석을 수행합니다.

관련 설계 문서와 다이어그램:
- [`설계 산출물_v2_2_3.md`](/Users/yangyewon/workspace/battery_report_agent/설계%20산출물/설계%20산출물_v2_2_3.md)
- [`diagram.png`](/Users/yangyewon/workspace/battery_report_agent/설계%20산출물/설계%20산출물_v2_2_3.img/diagram.png)
- [`flow.png`](/Users/yangyewon/workspace/battery_report_agent/설계%20산출물/설계%20산출물_v2_2_3.img/flow.png)


![diagram](README.img/diagram.png)

## Output Structure
- Executive Summary
- Market Context
- LG vs CATL 비교 분석
- 기업별 SWOT
- SO/ST/WO/WT 기반 전략 인사이트
- 상세 시사점
- References

## Quality Controls
- **근거성**: 모든 핵심 판단은 출처 또는 정량 근거와 연결됩니다.
- **일관성**: 두 기업에 동일한 평가 기준을 적용합니다.
- **분리성**: LG와 CATL의 데이터 및 분석 컨텍스트를 분리합니다.
- **추적 가능성**: source id와 metadata를 기반으로 결과를 역추적할 수 있습니다.
- **불확실성 관리**: 근거가 부족한 경우 단정 대신 정보 부족을 명시합니다.
- **편향 완화**: 다양한 출처 유형과 반증 자료를 함께 검토합니다.

## Directory Structure
```text
.
├── README.md
├── README.img/
│   ├── diagram.png
│   └── flow.png
├── rag_data/
│   ├── rag_battery_market.md
│   ├── rag_catl.md
│   └── rag_lg_energy_solution.md
└── 설계 산출물/
    ├── 설계 산출물_v2_2_3.md
    └── 설계 산출물_v2_2_3.img/
        ├── diagram.png
        └── flow.png
```

## Data Sources
- [`rag_battery_market.md`](/Users/yangyewon/workspace/battery_report_agent/rag_data/rag_battery_market.md): 시장 환경 및 산업 동향 자료
- [`rag_lg_energy_solution.md`](/Users/yangyewon/workspace/battery_report_agent/rag_data/rag_lg_energy_solution.md): LG에너지솔루션 관련 자료
- [`rag_catl.md`](/Users/yangyewon/workspace/battery_report_agent/rag_data/rag_catl.md): CATL 관련 자료

## Why This Project Stands Out
- 단순 리서치 자동화가 아니라, 비교 분석에 최적화된 구조적 멀티 에이전트 시스템입니다.
- 병렬 브랜치와 중앙 통제 구조를 함께 사용해 유연성과 통제 가능성을 동시에 확보했습니다.
- `RAG-first + Web Search fallback` 설계를 통해 최신성, 재현성, 효율성의 균형을 맞췄습니다.
- 최종 산출물이 단순 텍스트가 아니라 비교표, SWOT, 전략 인사이트, References까지 포함한 의사결정형 보고서라는 점이 강점입니다.
