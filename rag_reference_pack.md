# RAG Reference Pack for Battery Strategy Agent

## 1. Purpose

This document curates external sources to load into the RAG corpus for the LG Energy Solution vs. CATL strategy-comparison workflow.

The design document requires:

- market-context grounding
- strict separation between `LG` and `CATL` evidence
- evidence-backed comparison on 7 criteria
- explicit handling of uncertainty

So the source pack is organized into six collections:

1. `market_policy`
2. `lg_official`
3. `catl_official`
4. `battery_tech_reviews`
5. `recycling_safety`
6. `rag_methods`

## 2. Recommended Ingestion Rule

### Must-ingest first

Use these as the minimum high-trust corpus:

- official company earnings / annual materials
- IEA market reports
- EU battery regulation
- DOE battery supply-chain reports
- a small number of broad battery-technology review papers
- a small number of RAG-method papers for system improvement

### Nice-to-have next

Add these after the core set:

- partner / plant / offtake press releases
- sodium-ion / solid-state / recycling specialization papers
- charging, battery swapping, and zero-carbon ecosystem materials

## 3. Core RAG Set

### 3.1 Market / Policy

| Priority | Source | Why it matters | Best use |
| --- | --- | --- | --- |
| P0 | [IEA Global EV Outlook 2025 - Electric vehicle batteries](https://www.iea.org/reports/global-ev-outlook-2025/electric-vehicle-batteries) | Current battery-demand, supply, regional production, LFP adoption, manufacturing-capacity trends | `market_node`, `compare_node` |
| P0 | [IEA Batteries and Secure Energy Transitions](https://www.iea.org/reports/batteries-and-secure-energy-transitions) | Battery-cost decline, demand/supply concentration, critical-minerals and energy-security framing | `market_node`, `swot_node` |
| P0 | [EU Regulation 2023/1542 on batteries and waste batteries](https://eur-lex.europa.eu/eli/reg/2023/1542/2023-07-28/eng) | Battery passport, due diligence, lifecycle and recycling compliance obligations | `market_node`, `insight_node` |
| P1 | [EU Regulation 2025/1561 amendment](https://eur-lex.europa.eu/eli/reg/2025/1561/oj) | Clarifies updated timing around implementation milestones | `market_node` |
| P1 | [DOE CESER battery storage supply-chain mitigation report summary](https://www.energy.gov/ceser/articles/new-ceser-report-offers-supply-chain-mitigation-strategies-battery-storage-systems) | U.S. BESS supply-chain risk framing and mitigation priorities | `market_node`, `swot_node` |
| P1 | [DOE battery supply-chain review fact sheet](https://www.energy.gov/articles/fact-sheet-biden-harris-administration-100-day-battery-supply-chain-review) | U.S. policy logic for domestic battery manufacturing and strategic vulnerability framing | `market_node` |
| P1 | [DOE actions to bolster domestic advanced-battery supply chain](https://www.energy.gov/articles/doe-announces-actions-bolster-domestic-supply-chain-advanced-batteries) | Useful for U.S. localization and supply-chain strategy context | `market_node` |

### 3.2 LG Energy Solution Official

| Priority | Source | Why it matters | Best use |
| --- | --- | --- | --- |
| P0 | [LG Energy Solution Releases 2024 Financial Results](https://news.lgensol.com/company-news/press-releases/3587/) | Revenue, operating profit, capex guidance, LFP for ESS, dry electrode and lithium-sulfur all-solid-state direction | `lg_research_node`, `lg_strategy_node` |
| P0 | [LG Energy Solution Releases 2025 First-Quarter Financial Results](https://news.lgensol.com/company-news/press-releases/3808/) | Profitability recovery, regulatory transition response, efficiency focus | `lg_research_node`, `lg_strategy_node` |
| P0 | [LG Energy Solution Releases 2025 Second-Quarter Financial Results](https://news.lgensol.com/company-news/press-releases/4052/) | North America ESS focus, product and technology-portfolio optimization | `lg_research_node`, `lg_strategy_node` |
| P1 | [LG Energy Solution Posts Steady Annual Growth, Aims for Continued Advancement Through Qualitative Growth](https://news.lgensol.com/company-news/press-releases/2389/) | Baseline strategic continuity from 2023 to 2024 | `lg_research_node` |
| P1 | [LG Energy Solution and GM to Jointly Develop Prismatic Battery Cell Technology](https://news.lgensol.com/company-news/press-releases/3436/) | Product-form-factor diversification and OEM partnership depth | `lg_strategy_node` |
| P1 | [LG Energy Solution Strengthens Partnership with WesCEF, Secures Stable Lithium Supply Chain for the North American Market](https://news.lgensol.com/company-news/press-releases/2435/) | Upstream raw-material strategy and IRA-linked supply-chain positioning | `lg_strategy_node` |
| P1 | [LG Energy Solution Showcases Next-Generation ESS Technologies at RE+ 2025 in Las Vegas](https://news.lgensol.com/company-news/press-releases/4155/) | North American ESS positioning, local value-chain narrative, product roadmap | `lg_strategy_node` |

### 3.3 CATL Official

| Priority | Source | Why it matters | Best use |
| --- | --- | --- | --- |
| P0 | [CATL 2025 Annual Report release page](https://www.catl.com/en/news/6773.html) | Anchor source for official company results and strategic positioning | `catl_research_node`, `catl_strategy_node` |
| P0 | [Naxtra Battery Breakthrough and Dual-Power Architecture](https://www.catl.com/en/news/6401.html) | Sodium-ion commercialization, dual-chemistry strategy, fast-charging technology | `catl_strategy_node` |
| P0 | [CATL and CHANGAN launch mass-production sodium-ion passenger vehicle](https://www.catl.com/en/news/6720.html) | Confirms sodium-ion strategy moved from prototype to commercialization | `catl_strategy_node` |
| P1 | [CATL and NIO form strategic partnership on battery swapping](https://www.catl.com/en/news/6381.html) | Service-network strategy and ecosystem expansion | `catl_strategy_node` |
| P1 | [Advancing the Construction of New Zero-Carbon Infrastructure: CATL Enters Strategic Partnership with Hainan Provincial Government](https://www.catl.com/en/news/6305.html) | Zero-carbon infrastructure, storage, and ecosystem-level expansion logic | `catl_strategy_node` |
| P1 | [CATL Partners with Changzhou to Build Zero Carbon Ecosystem](https://www.catl.com/en/news/6564.html) | Microgrid and city-scale energy ecosystem expansion | `catl_strategy_node` |
| P1 | [Indonesia integrated battery project announcement](https://www.catl.com/en/news/6481.html) | Critical-mineral control, vertical integration, geographic expansion | `catl_strategy_node` |

## 4. Extended Technical Paper Set

### 4.1 Battery Technology Reviews

| Priority | Source | Why it matters | Best use |
| --- | --- | --- | --- |
| P0 | [A cost and resource analysis of sodium-ion batteries](https://www.nature.com/articles/natrevmats201813) | Cost and raw-material logic for sodium-ion vs. lithium-ion | `market_node`, `insight_node` |
| P1 | [Next-generation anodes for high-energy and low-cost sodium-ion batteries](https://www.nature.com/articles/s41578-025-00857-4) | Forward-looking technical roadmap for sodium-ion competitiveness | `market_node`, `insight_node` |
| P1 | [Benchmarking the reproducibility of all-solid-state battery cell performance](https://www.nature.com/articles/s41560-024-01634-3) | Good source to temper hype around solid-state with reproducibility constraints | `market_node`, `insight_node` |
| P1 | [Benchmarking the performance of all-solid-state lithium batteries](https://www.nature.com/articles/s41560-020-0565-1) | Establishes practical evaluation frame for solid-state claims | `market_node` |
| P2 | [An experimental study on the thermal characteristics of the Cell-To-Pack system](https://www.sciencedirect.com/science/article/abs/pii/S0360544221005879) | Useful if CTP is treated as a comparison criterion in technology or safety discussion | `market_node`, `compare_node` |

### 4.2 Recycling / Circularity / Safety

| Priority | Source | Why it matters | Best use |
| --- | --- | --- | --- |
| P0 | [The evolution of lithium-ion battery recycling](https://www.nature.com/articles/s44359-024-00010-4) | Broad recycling process landscape and industrialization challenges | `market_node`, `swot_node` |
| P0 | [Recycling lithium-ion batteries from electric vehicles](https://www.nature.com/articles/s41586-019-1682-5) | Strong foundational paper for pack disassembly, hazards, and circular supply-chain logic | `market_node`, `swot_node` |
| P1 | [Lithium-ion battery recycling: a perspective on key challenges and opportunities](https://www.nature.com/articles/s44296-025-00083-7) | Good update for how chemistry diversification changes recycling economics | `market_node`, `insight_node` |
| P1 | [Experimental analysis and safety assessment of thermal runaway behavior in LFP batteries under mechanical abuse](https://www.nature.com/articles/s41598-024-58891-1) | Useful for LFP safety claims and nuance | `market_node`, `compare_node` |
| P2 | [Progress and prospect of spent lithium iron phosphate cathode materials recycling: A review](https://www.sciencedirect.com/science/article/abs/pii/S2352152X25024843) | Helpful if LFP recycling enters the strategy narrative | `market_node`, `insight_node` |

## 5. RAG Method Papers for System Design

These are not for business content directly. They are for improving retrieval quality, evidence control, and system robustness.

| Priority | Source | Why it matters | Best use |
| --- | --- | --- | --- |
| P0 | [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401) | Foundational RAG paper; useful for base architecture framing | system design |
| P0 | [Self-RAG: Learning to Retrieve, Generate, and Critique Through Self-Reflection](https://mlanthology.org/iclr/2024/asai2024iclr-selfrag/) | Good fit for adaptive retrieval and self-checking when evidence is weak | system design |
| P0 | [Precise Zero-Shot Dense Retrieval without Relevance Labels (HyDE)](https://aclanthology.org/2023.acl-long.99/) | Very relevant for low-label enterprise retrieval and query expansion | retriever improvement |
| P0 | [BGE M3-Embedding: Multi-Lingual, Multi-Functionality, Multi-Granularity Text Embeddings Through Self-Knowledge Distillation](https://arxiv.org/abs/2402.03216) | Directly supports the design choice of `bge-m3` | embedding strategy |
| P1 | [Retrieval-Augmented Generation for Large Language Models: A Survey](https://arxiv.org/abs/2312.10997) | Useful overview of naive, advanced, and modular RAG patterns | system design |
| P1 | [Corrective Retrieval Augmented Generation](https://arxiv.org/abs/2401.15884) | Helpful if you want a retrieval-quality evaluator before generation | robustness improvement |
| P1 | [Searching for Best Practices in Retrieval-Augmented Generation](https://arxiv.org/abs/2407.01219) | Practical guidance on chunking, retrieval, reranking, and prompt assembly | tuning guide |

## 6. What to Put in Each Collection

### `market_policy`

Put in:

- IEA battery demand / supply reports
- EV outlook battery sections
- EU battery regulation and updates
- DOE supply-chain and BESS risk materials
- broad technology and recycling review papers

Questions this collection should answer:

- Is EV demand slowing while ESS grows?
- How concentrated is global battery manufacturing?
- What policy or compliance changes affect strategy?
- What chemistry shifts matter now: LFP, sodium-ion, solid-state?

### `lg_official`

Put in:

- earnings releases
- annual / sustainability materials if available
- ESS strategy releases
- upstream offtake agreements
- OEM joint-development announcements

Questions this collection should answer:

- How is LG changing its capex and portfolio?
- What is LG doing in North America ESS?
- Which chemistries and form factors is LG pushing?
- How is LG building supply-chain resilience?

### `catl_official`

Put in:

- annual / results materials
- sodium-ion and fast-charging product releases
- Indonesia / upstream / vertical integration sources
- battery swapping and ecosystem expansion releases
- zero-carbon city / microgrid announcements

Questions this collection should answer:

- How does CATL turn chemistry breadth into strategy?
- How deep is CATL's vertical integration?
- What is CATL doing beyond EV cells?
- How much of CATL's moat is ecosystem plus service network?

### `battery_tech_reviews`

Put in:

- sodium-ion cost / materials reviews
- solid-state benchmark papers
- CTP and pack-architecture papers

Questions this collection should answer:

- Are next-gen chemistry claims commercially meaningful?
- Which technical advantages are real versus still immature?
- How should technology-readiness uncertainty be described?

### `recycling_safety`

Put in:

- EV battery recycling reviews
- LFP recycling reviews
- thermal-runaway and safety papers

Questions this collection should answer:

- How important is recycling to supply security?
- How do LFP and sodium-ion alter recycling economics?
- What safety nuances should be attached to chemistry claims?

### `rag_methods`

Put in:

- base RAG papers
- adaptive retrieval papers
- embedding-model papers
- retrieval robustness and best-practice surveys

Questions this collection should answer:

- Should retrieval be fixed or adaptive?
- Is `bge-m3` still a good fit?
- Do we need HyDE, reranking, or corrective retrieval?

## 7. Suggested Ingestion Priority

### Phase 1: Highest value

1. IEA market / battery reports
2. EU battery regulation
3. LG 2024, 2025 Q1, 2025 Q2 financial results
4. CATL annual report release and Naxtra / sodium-ion releases
5. 2-3 broad battery technology review papers
6. 2-3 recycling / circularity review papers

### Phase 2: Company strategy enrichment

1. LG OEM and upstream partnership releases
2. CATL Indonesia, NIO, zero-carbon ecosystem releases
3. DOE BESS and supply-chain materials

### Phase 3: System tuning

1. Self-RAG
2. HyDE
3. BGE-M3
4. CRAG
5. RAG survey / best-practice survey

## 8. Ingestion Notes

### Chunking

- earnings / press releases: 400-800 tokens, overlap 80-120
- long reports and regulations: 800-1200 tokens, overlap 120-180
- review papers: 700-1000 tokens, overlap 120-150

### Metadata fields

Use at least:

- `source_id`
- `collection`
- `company_scope`
- `source_type`
- `title`
- `publisher`
- `date`
- `region`
- `chemistry`
- `strategy_tags`
- `url`

### Recommended tags

- `portfolio`
- `technology`
- `supply_chain`
- `ess`
- `ev`
- `lfp`
- `sodium_ion`
- `solid_state`
- `recycling`
- `policy`
- `north_america`
- `europe`
- `china`
- `indonesia`

## 9. Gaps Still Not Fully Covered

These areas may need more targeted sourcing later:

- direct LG annual report PDF or sustainability report PDF
- direct CATL annual report PDF if the release page is not enough
- third-party market-share datasets by region
- ESS-only market outlook from a high-trust industry source
- exact line-item evidence for customer mix and utilization rates

## 10. Short Recommendation

If time is limited, do not start by loading random battery papers.

Start with:

1. IEA
2. EU regulation
3. LG official results and partnership releases
4. CATL official results and commercialization releases
5. 3-5 broad review papers on sodium-ion, solid-state, recycling, and safety

That set gives the best balance of:

- business strategy grounding
- technology realism
- policy relevance
- traceable references
- lower hallucination risk

