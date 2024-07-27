import numpy as np
import pandas as pd
from pandas import DataFrame, Series
from typing import Any, List, Tuple, Union, Callable, Optional
import statsmodels.api as sm

from ..utils.operator import StatsLogit, NumRange
from ..utils.logger import LoggerMixin
from .psi import psi
from .utils import lift
from .binary_metrics import BinaryMetrics


__all__ = [
    "ScoreEvaluate",
    "ModelEvaluate",
]


class ScoreEvaluate(LoggerMixin):
    """"""
    df_lifts: DataFrame
    lifts: List[DataFrame]

    def __init__(
            self,
            scores: Union[DataFrame, List[DataFrame]],
            score_name: Optional[str] = 'score',
            target_name: Optional[str] = 'target',
            bins: Optional[Union[int, List[float]]] = 20,
            border: Optional[Tuple[Union[int, float], Union[int, float]]] = None,
            keys: Optional[List[str]] = None,
            logger: Optional[Callable] = None,
            verbose: Optional[bool] = False,
            **kwargs: Any
    ):
        """
        :param scores: DataFrame 评分、PD 结果文件。
        :param score_name: 分数字段名称。
        :param target_name: 目标变量名称。
        :param bins: 分数分析分箱数量。
        :param border: 分数的最大最小边界， [min, max]。
        :param keys: 用于多样本中区分不同样本的lift。
        :param logger: 日志记录器。
        :param verbose: 是否打印日志。
        """
        self.scores = scores
        self.score_name = score_name
        self.target_name = target_name
        self.bins = bins
        self.border = border
        self.keys = keys
        self.logger = logger
        self.verbose = verbose
        self.kwargs = kwargs
        self.lift_columns = ['total', 'bad', 'bad_rate', 'cum_bad', 'ks', 'lift',]
        self.psi_columns = ['psi', 'psi_val']

        self._validate_data()
        self._lift_borders()

    def _validate_data(self):
        """"""
        if isinstance(self.scores, DataFrame):
            self.scores = [self.scores]

        for i, score in enumerate(self.scores):
            if self.score_name not in score.columns.tolist():
                raise ValueError(f"score_name {self.score_name} not in score columns, score idx is {i}.")
            if self.target_name not in score.columns.tolist():
                # raise ValueError(f"target_name {self.target_name} not in score columns, score idx is {i}.")
                self._logger(msg=f"[{__class__.__name__}] target_name {self.target_name} not in score columns, score idx is {i}.", color='red')
        if self.keys is None:
            self.keys = [f"score-{i}" for i, score in enumerate(self.scores)]

    def _lift_borders(self):
        """"""
        if self.border is None:
            self.border = (0, 100)

        if isinstance(self.bins, int):
            self.bins = np.linspace(*self.border, self.bins + 1)

    def lift(self, score: DataFrame) -> DataFrame:
        """ 计算模型结果的lift """
        return lift(score=score, target_name=self.target_name, score_name=self.score_name, bins=self.bins)

    def score_lifts(self) -> DataFrame:
        """"""
        self.lifts = []
        keys = []
        for key, score in zip(self.keys, self.scores):
            if self.target_name not in score.columns.tolist():
                self._logger(msg=f"[{__class__.__name__}] Skip Evaluate. Message: target_name {self.target_name} not in score columns", color='red')
            else:
                df_lift = self.lift(score)[self.lift_columns]
                self.lifts.append(df_lift)
                keys.append(key)
        self.df_lifts = pd.concat(self.lifts, keys=keys, join="outer", axis=1)
        return self.df_lifts

    def score_psi(
            self,
            score_idx: Optional[Tuple[int, int]] = None,
    ) -> DataFrame:
        """"""
        if len(self.scores) < 2:
            raise ValueError("At least two scores are required to calculate PSI")

        if len(self.lifts) == 0:
            raise ValueError("Lifts have not been calculated yet")

        if score_idx is None:
            score_idx = (0, 1)
        origin_dist = self.lifts[score_idx[0]].total
        current_dist = self.lifts[score_idx[1]].total
        df_psi_data = pd.DataFrame({
            "origin": origin_dist,
            "current": current_dist
        })
        df_psi = psi(df_psi_data, ex_name='origin', ac_name='current')
        return df_psi[self.psi_columns]

    def add_psi(
            self,
            score_idx: Optional[Tuple[int, int]] = None,
    ) -> Union[DataFrame, None]:
        """"""
        if len(self.scores) < 2 or len(self.lifts) < 2:
            self._logger(msg=f"[{__class__.__name__}] At least two scores are required to calculate PSI.", color="red")
            # raise ValueError("At least two scores are required to calculate PSI")
            return None
        else:
            if "psi" not in self.df_lifts.columns:
                df_psi = self.score_psi(score_idx=score_idx)
                self.df_lifts = pd.concat([self.df_lifts, df_psi], axis=1)
            else:
                self._logger(msg=f"[{__class__.__name__}] PSI already exists in {self.df_lifts.columns}", color="blue")
            return self.df_lifts

    def score_evaluate(
            self,
            score_idx: Optional[Tuple[int, int]] = None,
    ):
        """"""
        self.score_lifts()
        self.add_psi(score_idx=score_idx)


class ModelEvaluate(ScoreEvaluate):
    """"""
    model: Any
    weight: DataFrame

    def __init__(
            self,
            samples: List[DataFrame],
            columns: Optional[List[str]] = None,
            train_sample_idx: Optional[int] = 0,
            id_name: str = "uuid",
            target_name: str = "target",
            score_range: Optional[Tuple[int, int]] = None,
            decimal: Optional[int] = 2,
            threshold: Optional[float] = None,
            bins: Optional[Union[int, List[float]]] = 20,
            border: Optional[Tuple[Union[int, float], Union[int, float]]] = None,
            logger: Optional[Callable] = None,
            verbose: Optional[bool] = False,
            **kwargs: Any,
    ):
        """
        :param samples: List of DataFrame
        :param columns: List of columns to evaluate
        :param train_sample_idx: Index of the training sample
        :param id_name: Name of the id column
        :param target_name: Name of the target column
        :param score_range: Range of the score
        :param decimal: Number of decimal places
        :param threshold: Threshold for bad predictions
        :param bins: Number of bins for score
        :param border: Border for score
        :param logger: Logger
        :param verbose: Verbose mode
        """
        self.samples = samples
        self.columns = columns
        self.train_sample_idx = train_sample_idx
        self.id_name = id_name
        self.target_name = target_name
        self.score_range = score_range
        self.decimal = decimal
        self.logger = logger
        self.verbose = verbose
        self.threshold = self.set_threshold(threshold=threshold)
        self.columns = self.set_columns(columns=columns)
        self.scores_metrics = []
        self.model_fit()
        scores = self.model_inference()
        super().__init__(
            scores=scores, target_name=target_name, logger=logger, verbose=verbose,
            bins=bins, border=border, **kwargs,)

    def set_columns(self, columns: Optional[List[str]] = None) -> List[str]:
        """"""
        if columns is None:
            columns = self.samples[self.train_sample_idx].columns.tolist()
        for col in [self.id_name, self.target_name]:
            if col in columns:
                columns.remove(col)
        return columns

    def set_threshold(self, threshold: Optional[float] = None) -> float:
        if threshold is None:
            threshold = self.samples[self.train_sample_idx][self.target_name].mean()
        return threshold

    def model_score(
            self,
            sample: DataFrame,
    ) -> Series:
        """  """
        score = sample[self.columns].dot(self.weight.weight) / 100.
        if self.score_range:
            a, b = self.score_range
            score = NumRange(a, b, score.min(), score.max(), score)
        return score.round(self.decimal)

    def model_inference(self) -> List[DataFrame]:
        """"""
        scores = []
        for sample in self.samples:
            df_sample = sm.add_constant(sample[self.columns])
            proba = self.model.predict(df_sample)
            score_data = {
                "uuid": sample[self.id_name],
                "proba": proba,
                "score": self.model_score(sample),
                "prediction": (proba > self.threshold).astype(int),
            }
            if self.target_name in sample.columns.tolist():
                score_data.update({"target": sample[self.target_name],})
            scores.append(pd.DataFrame(score_data))
        return scores

    def model_fit(self):
        """"""
        x_train = self.samples[self.train_sample_idx][self.columns]
        y_train = self.samples[self.train_sample_idx][self.target_name]
        self.model = StatsLogit(X=x_train, y=y_train)
        self._logger(msg=f"{str(self.model.summary())}\n", color='green')
        self.weight = pd.DataFrame(self.model.params.drop('const'), columns=['param'])
        self.weight['weight'] = self.weight['param'] * 100 / self.weight['param'].sum()

    def model_evaluate(self):
        """"""
        for i, score in enumerate(self.scores):
            if self.target_name in score.columns.tolist():
                binary_metrics = BinaryMetrics(target=score.target, proba=score.proba, prediction=score.prediction)
                score_metrics = binary_metrics.evaluate()
                self.scores_metrics.append(score_metrics)
                metrics_info = f"AUC = {score_metrics.auc:.2f}, KS = {score_metrics.ks:.2f}, Lift = {score_metrics.lift:.2f}, recall = {score_metrics.recall:.2f}, precision = {score_metrics.precision:.2f}, f1-score = {score_metrics.f1_score:.2f}\n"
                self._logger(msg=f"[{__class__.__name__}] Sample ID {i} Metrics: {metrics_info}", color='blue')
            else:
                self._logger(msg=f"[{__class__.__name__}] Sample ID {i} Metrics: No target in score", color='red')

    def evaluate(
            self,
            psi_score_idx: Optional[Tuple[int, int]] = None
    ):
        """"""
        self.model_evaluate()
        self.score_evaluate(score_idx=psi_score_idx)
