from pydantic import BaseModel, Field
from typing import List, Union, Optional, Sequence


__all__ = [
    "FeatureEvaluateSchema",
    "StepwiseReport",
]


class FeatureEvaluateSchema(BaseModel):
    """"""
    var_name: str = Field(default=None, description="")
    bad_rate: Optional[float] = Field(default=None, description="")
    desc: Optional[str] = Field(default=None, description="")
    missing: Optional[float] = Field(default=None, description="")

    miss_bad_rate: Optional[float] = Field(default=None, description="")
    not_miss_bad_rate: Optional[float] = Field(default=None, description="")
    null_lift: Optional[float] = Field(default=None, description="")
    not_null_lift: Optional[float] = Field(default=None, description="")

    min: Optional[float] = Field(default=None, description="")
    max: Optional[float] = Field(default=None, description="")
    std: Optional[float] = Field(default=None, description="")
    mode: Optional[float] = Field(default=None, description="")

    skew: Optional[float] = Field(default=None, description="")
    kurt: Optional[float] = Field(default=None, description="")
    cv: Optional[float] = Field(default=None, description="")
    unique: Optional[float] = Field(default=None, description="")

    bad: Optional[Union[int, float]] = Field(default=None, description="")
    count: Optional[Union[int, float]] = Field(default=None, description="")
    good: Optional[Union[int, float]] = Field(default=None, description="")
    ks_test: Optional[float] = Field(default=None, description="")

    chi_statistic: Optional[float] = Field(default=None, description="")
    chi_pvalue: Optional[float] = Field(default=None, description="")

    R2: Optional[float] = Field(default=None, description="")
    intercept: Optional[float] = Field(default=None, description="")
    pvalue_intercept: Optional[float] = Field(default=None, description="")
    param: Optional[float] = Field(default=None, description="")
    pvalue_param: Optional[float] = Field(default=None, description="")

    auc: Optional[float] = Field(default=None, description="")
    ks: Optional[float] = Field(default=None, description="")
    fpr: Optional[Sequence] = Field(default=None, description="")
    tpr: Optional[Sequence] = Field(default=None, description="")


class StepwiseReport(BaseModel):
    """Stepwise report schema"""

    feature: List[str] = Field(default=None, description="")
    auc: Optional[float] = Field(default=None, description="")
    ks: Optional[float] = Field(default=None, description="")
    num_features: Optional[int] = Field(default=None, description="")
    implication: Optional[str] = Field(default=None, description="")
