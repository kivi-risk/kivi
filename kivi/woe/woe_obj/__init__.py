from .woe_frequency import *
from .woe_distance import *
from .woe_category import *
from .woe_manually import *
from .woe_pearson import *
from .woe_chi2 import *
from .woe_tree import *
from .woe_ks import *
from .woe_kmeans import *
from typing import Union


TypeWoe = Union[
    DistanceBins,
    FrequencyBins,
    CategoryBins,
    ManuallyBins,
    PearsonBins,
    Chi2Bins,
    TreeBins,
    KSBins,
    KmeansBins,
]
