# Battery Market RAG Source Pack

## Purpose

This file collects market, policy, and technical-review sources for the `market_policy`, `battery_tech_reviews`, and `recycling_safety` corpora.

Use this corpus to answer:

- What is happening in the global battery market
- How EV and ESS demand are shifting
- Which policies affect battery strategy
- Which chemistry trends matter now
- What recycling and safety issues should shape strategic interpretation

## Recommended Sources

### 1. Market and Policy

#### IEA Global EV Outlook 2025 - Electric Vehicle Batteries

- Link: [https://www.iea.org/reports/global-ev-outlook-2025/electric-vehicle-batteries](https://www.iea.org/reports/global-ev-outlook-2025/electric-vehicle-batteries)
- Why it matters:
  - Best market-context source for battery demand, capacity, regional manufacturing, and chemistry trends
  - Strong baseline for compare and SWOT stages
- Suggested tags:
  - `market`, `ev`, `capacity`, `regional_competition`, `lfp`

#### IEA Batteries and Secure Energy Transitions

- Link: [https://www.iea.org/reports/batteries-and-secure-energy-transitions](https://www.iea.org/reports/batteries-and-secure-energy-transitions)
- Why it matters:
  - Covers battery supply-chain concentration, cost trends, critical minerals, and policy relevance
- Suggested tags:
  - `market`, `critical_minerals`, `supply_chain`, `cost`

#### EU Regulation 2023/1542 on Batteries and Waste Batteries

- Link: [https://eur-lex.europa.eu/eli/reg/2023/1542/2023-07-28/eng](https://eur-lex.europa.eu/eli/reg/2023/1542/2023-07-28/eng)
- Why it matters:
  - Central source for battery passport, due diligence, carbon footprint, and recycling obligations
- Suggested tags:
  - `policy`, `eu`, `battery_passport`, `recycling`, `compliance`

#### EU Regulation 2025/1561 Amendment

- Link: [https://eur-lex.europa.eu/eli/reg/2025/1561/oj](https://eur-lex.europa.eu/eli/reg/2025/1561/oj)
- Why it matters:
  - Useful for updated implementation detail and timing
- Suggested tags:
  - `policy`, `eu`, `regulation_update`

#### DOE CESER Battery Storage Supply-Chain Mitigation Report Summary

- Link: [https://www.energy.gov/ceser/articles/new-ceser-report-offers-supply-chain-mitigation-strategies-battery-storage-systems](https://www.energy.gov/ceser/articles/new-ceser-report-offers-supply-chain-mitigation-strategies-battery-storage-systems)
- Why it matters:
  - Good source for U.S. BESS supply-chain risk framing
- Suggested tags:
  - `policy`, `bess`, `supply_chain`, `us`

#### DOE Battery Supply-Chain Review Fact Sheet

- Link: [https://www.energy.gov/articles/fact-sheet-biden-harris-administration-100-day-battery-supply-chain-review](https://www.energy.gov/articles/fact-sheet-biden-harris-administration-100-day-battery-supply-chain-review)
- Why it matters:
  - Good source for localization logic and strategic vulnerability framing
- Suggested tags:
  - `policy`, `us`, `localization`, `supply_chain`

### 2. Battery Technology Reviews

#### A Cost and Resource Analysis of Sodium-Ion Batteries

- Link: [https://www.nature.com/articles/natrevmats201813](https://www.nature.com/articles/natrevmats201813)
- Why it matters:
  - Strong paper for sodium-ion economics and resource availability
- Suggested tags:
  - `sodium_ion`, `cost`, `materials`

#### Next-Generation Anodes for High-Energy and Low-Cost Sodium-Ion Batteries

- Link: [https://www.nature.com/articles/s41578-025-00857-4](https://www.nature.com/articles/s41578-025-00857-4)
- Why it matters:
  - Helps describe what is promising versus still developing in sodium-ion
- Suggested tags:
  - `sodium_ion`, `anodes`, `technology_readiness`

#### Benchmarking the Reproducibility of All-Solid-State Battery Cell Performance

- Link: [https://www.nature.com/articles/s41560-024-01634-3](https://www.nature.com/articles/s41560-024-01634-3)
- Why it matters:
  - Good for cautioning against overclaiming solid-state readiness
- Suggested tags:
  - `solid_state`, `benchmark`, `reproducibility`

#### Benchmarking the Performance of All-Solid-State Lithium Batteries

- Link: [https://www.nature.com/articles/s41560-020-0565-1](https://www.nature.com/articles/s41560-020-0565-1)
- Why it matters:
  - Useful benchmark framework for comparing future-facing claims
- Suggested tags:
  - `solid_state`, `benchmark`, `performance`

#### An Experimental Study on the Thermal Characteristics of the Cell-To-Pack System

- Link: [https://www.sciencedirect.com/science/article/abs/pii/S0360544221005879](https://www.sciencedirect.com/science/article/abs/pii/S0360544221005879)
- Why it matters:
  - Useful if CTP technology enters technology or safety comparison
- Suggested tags:
  - `ctp`, `thermal`, `safety`

### 3. Recycling and Safety

#### The Evolution of Lithium-Ion Battery Recycling

- Link: [https://www.nature.com/articles/s44359-024-00010-4](https://www.nature.com/articles/s44359-024-00010-4)
- Why it matters:
  - Broad review of recycling maturity and industrial bottlenecks
- Suggested tags:
  - `recycling`, `circularity`, `supply_security`

#### Recycling Lithium-Ion Batteries from Electric Vehicles

- Link: [https://www.nature.com/articles/s41586-019-1682-5](https://www.nature.com/articles/s41586-019-1682-5)
- Why it matters:
  - Foundational paper for hazards, process design, and circular value-chain framing
- Suggested tags:
  - `recycling`, `ev`, `hazards`, `circularity`

#### Lithium-Ion Battery Recycling: A Perspective on Key Challenges and Opportunities

- Link: [https://www.nature.com/articles/s44296-025-00083-7](https://www.nature.com/articles/s44296-025-00083-7)
- Why it matters:
  - Useful update for chemistry diversification and recycling economics
- Suggested tags:
  - `recycling`, `economics`, `chemistry_mix`

#### Experimental Analysis and Safety Assessment of Thermal Runaway Behavior in LFP Batteries Under Mechanical Abuse

- Link: [https://www.nature.com/articles/s41598-024-58891-1](https://www.nature.com/articles/s41598-024-58891-1)
- Why it matters:
  - Useful for safety nuance when discussing LFP advantages
- Suggested tags:
  - `lfp`, `safety`, `thermal_runaway`

## Best RAG Usage Notes

- This collection should stay company-neutral
- Use it for `market_node` first, then as supporting evidence in `compare_node`, `swot_node`, and `insight_node`
- Attach metadata:
  - `company_scope=market`
  - `collection=market_policy` or `battery_tech_reviews` or `recycling_safety`
  - `source_type=report`, `regulation`, or `paper`

## Should References Be Inside the Markdown?

Short answer: yes, but not as a giant bibliography only.

Best practice is:

1. Put a short summary for each source
2. Add the original link right there with the summary
3. Add tags / metadata hints
4. Keep a reference list at the bottom too

That way:

- the LLM can retrieve useful descriptive text
- you can trace where each chunk came from
- later report generation can cite the original source more reliably

If you put only a bare list of paper titles and links, retrieval quality usually drops because the chunks contain very little semantic context.

## Reference List

1. IEA. "Global EV Outlook 2025 - Electric Vehicle Batteries." [https://www.iea.org/reports/global-ev-outlook-2025/electric-vehicle-batteries](https://www.iea.org/reports/global-ev-outlook-2025/electric-vehicle-batteries)
2. IEA. "Batteries and Secure Energy Transitions." [https://www.iea.org/reports/batteries-and-secure-energy-transitions](https://www.iea.org/reports/batteries-and-secure-energy-transitions)
3. European Union. "Regulation (EU) 2023/1542 on Batteries and Waste Batteries." [https://eur-lex.europa.eu/eli/reg/2023/1542/2023-07-28/eng](https://eur-lex.europa.eu/eli/reg/2023/1542/2023-07-28/eng)
4. European Union. "Regulation (EU) 2025/1561." [https://eur-lex.europa.eu/eli/reg/2025/1561/oj](https://eur-lex.europa.eu/eli/reg/2025/1561/oj)
5. U.S. Department of Energy CESER. "Battery Storage Supply-Chain Mitigation Strategies." [https://www.energy.gov/ceser/articles/new-ceser-report-offers-supply-chain-mitigation-strategies-battery-storage-systems](https://www.energy.gov/ceser/articles/new-ceser-report-offers-supply-chain-mitigation-strategies-battery-storage-systems)
6. U.S. Department of Energy. "Fact Sheet: 100-Day Battery Supply Chain Review." [https://www.energy.gov/articles/fact-sheet-biden-harris-administration-100-day-battery-supply-chain-review](https://www.energy.gov/articles/fact-sheet-biden-harris-administration-100-day-battery-supply-chain-review)
7. Peters, J. F. et al. "A Cost and Resource Analysis of Sodium-Ion Batteries." [https://www.nature.com/articles/natrevmats201813](https://www.nature.com/articles/natrevmats201813)
8. Yan, J. et al. "Next-Generation Anodes for High-Energy and Low-Cost Sodium-Ion Batteries." [https://www.nature.com/articles/s41578-025-00857-4](https://www.nature.com/articles/s41578-025-00857-4)
9. Ohno, S. et al. "Benchmarking the Performance of All-Solid-State Lithium Batteries." [https://www.nature.com/articles/s41560-020-0565-1](https://www.nature.com/articles/s41560-020-0565-1)
10. Chen, X. et al. "Benchmarking the Reproducibility of All-Solid-State Battery Cell Performance." [https://www.nature.com/articles/s41560-024-01634-3](https://www.nature.com/articles/s41560-024-01634-3)
11. Wei, C. et al. "An Experimental Study on the Thermal Characteristics of the Cell-To-Pack System." [https://www.sciencedirect.com/science/article/abs/pii/S0360544221005879](https://www.sciencedirect.com/science/article/abs/pii/S0360544221005879)
12. Harper, G. et al. "Recycling Lithium-Ion Batteries from Electric Vehicles." [https://www.nature.com/articles/s41586-019-1682-5](https://www.nature.com/articles/s41586-019-1682-5)
13. Nature Reviews Clean Technology. "The Evolution of Lithium-Ion Battery Recycling." [https://www.nature.com/articles/s44359-024-00010-4](https://www.nature.com/articles/s44359-024-00010-4)
14. Nature Reviews Clean Technology. "Lithium-Ion Battery Recycling: A Perspective on Key Challenges and Opportunities." [https://www.nature.com/articles/s44296-025-00083-7](https://www.nature.com/articles/s44296-025-00083-7)
15. Scientific Reports. "Experimental Analysis and Safety Assessment of Thermal Runaway Behavior in LFP Batteries Under Mechanical Abuse." [https://www.nature.com/articles/s41598-024-58891-1](https://www.nature.com/articles/s41598-024-58891-1)

