from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class KeyMetricModel(BaseModel):
    label: str
    value: Optional[float] = None
    unit: str = ""
    period: str = ""
    source_ids: List[str] = Field(default_factory=list)


class MarketContextModel(BaseModel):
    key_market_trends: List[str] = Field(default_factory=list)
    technology_trends: List[str] = Field(default_factory=list)
    policy_signals: List[str] = Field(default_factory=list)
    supply_chain_signals: List[str] = Field(default_factory=list)
    risk_signals: List[str] = Field(default_factory=list)
    key_metrics: List[KeyMetricModel] = Field(default_factory=list)
    source_ids: List[str] = Field(default_factory=list)


class CriteriaSectionModel(BaseModel):
    criterion: str
    summary: str
    evidence: List[str] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    source_ids: List[str] = Field(default_factory=list)


class CompanyAnalysisModel(BaseModel):
    company: str
    executive_takeaway: str
    criteria_sections: List[CriteriaSectionModel] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    key_metrics: List[KeyMetricModel] = Field(default_factory=list)
    source_ids: List[str] = Field(default_factory=list)
    uncertainty_notes: List[str] = Field(default_factory=list)


class CompanySwotModel(BaseModel):
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    opportunities: List[str] = Field(default_factory=list)
    threats: List[str] = Field(default_factory=list)
    source_ids: List[str] = Field(default_factory=list)


class SwotResultModel(BaseModel):
    lg: CompanySwotModel
    catl: CompanySwotModel


class InsightStrategyModel(BaseModel):
    type: str
    title: str
    rationale: str
    related_swot: List[str] = Field(default_factory=list)
    priority: str = ""
    source_ids: List[str] = Field(default_factory=list)


class InsightResultModel(BaseModel):
    selected_strategies: List[InsightStrategyModel] = Field(default_factory=list)
    strategic_implications: List[str] = Field(default_factory=list)
    source_ids: List[str] = Field(default_factory=list)


class SummaryModel(BaseModel):
    key_conclusions: List[str] = Field(default_factory=list)
    key_insights: List[str] = Field(default_factory=list)
    decision_points: List[str] = Field(default_factory=list)


class FinalReportModel(BaseModel):
    summary: SummaryModel
    market_background: str
    lg_strategy: str
    catl_strategy: str
    comparison_analysis: str
    swot_analysis: str
    lg_insights: str
    conclusion_or_implications: str
