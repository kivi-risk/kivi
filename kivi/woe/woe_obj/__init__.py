from .woe_frequency import *
from .woe_distance import *
from .woe_category import *
from .woe_manually import *
from .woe_pearson import *
from .woe_chi2 import *
from .woe_tree import *
from .woe_ks import *
from .woe_kmeans import *
from typing import Union, Type


TypeWoe = Union[
    Type[DistanceBins],
    Type[FrequencyBins],
    Type[CategoryBins],
    Type[ManuallyBins],
    Type[PearsonBins],
    Type[Chi2Bins],
    Type[TreeBins],
    Type[KSBins],
    Type[KmeansBins],
]
