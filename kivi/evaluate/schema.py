from pydantic import BaseModel, Field
from typing import List, Dict, Optional


__all__ = [
    "ROCCurveOutput",
    "PrecisionRecallCurveOutput",
    "ConfusionMatrixOutput",
    "BinaryMetricsOutput",
]


class ConfusionMatrixOutput(BaseModel):
    """"""
    tp: Optional[int] = Field(default=None, description="")
    fp: Optional[int] = Field(default=None, description="")
    tn: Optional[int] = Field(default=None, description="")
    fn: Optional[int] = Field(default=None, description="")


class ROCCurveOutput(BaseModel):
    """"""
    fpr: Optional[List[float]] = Field(default=None, description="")
    tpr: Optional[List[float]] = Field(default=None, description="")
    thresholds: Optional[List[float]] = Field(default=None, description="")


class PrecisionRecallCurveOutput(BaseModel):
    """"""
    recall: Optional[List[float]] = Field(default=None, description="")
    precision: Optional[List[float]] = Field(default=None, description="")
    thresholds: Optional[List[float]] = Field(default=None, description="")


class BinaryMetricsOutput(BaseModel):
    """"""
    ks: Optional[float] = Field(default=None, description="")
    auc: Optional[float] = Field(default=None, description="")
    recall: Optional[float] = Field(default=None, description="")
    lift: Optional[float] = Field(default=None, description="")
    precision: Optional[float] = Field(default=None, description="")
    f1_score: Optional[float] = Field(default=None, description="")
    confusion_matrix: Optional[ConfusionMatrixOutput] = Field(default=None, description="")
    roc_curve: Optional[ROCCurveOutput] = Field(default=None, description="")
    pr_curve: Optional[PrecisionRecallCurveOutput] = Field(default=None, description="")

    def show(self):
        """"""
        for key, value in self.model_dump().items():
            if key not in ["fpr", "tpr"]:
                if isinstance(value, float):
                    print(f"{key}: {value:.4f}")

    def to_univariate(self) -> Dict:
        """"""
        _eval = {
            "auc": self.auc,
            "ks": self.ks,
            "tpr": self.roc_curve.tpr,
            "fpr": self.roc_curve.fpr,
        }
        return _eval
