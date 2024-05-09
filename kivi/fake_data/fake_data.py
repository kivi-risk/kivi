import random
import hashlib
import numpy as np
import pandas as pd
from typing import *
from .fake_data_config import configs
from multiprocessing import Pool

__all__ = [
    'map_data_type',
    'gen_data',
    'generate_credit_data',
]

np.random.seed(1024)
map_data_type = {
    'uniform': np.random.uniform,
    'randint': np.random.randint,
}

#### TODO: 同一个用户多个时间的数据。
####

def gen_data(
        num_samples: int,
        low: Union[float, int],
        high: Union[float, int],
        data_type: str,
) -> np.array:
    """"""
    data_generator = map_data_type.get(data_type)
    data = data_generator(low, high, size=num_samples)
    return data


def generate_credit_data(
        num_samples: int,
        configs: List[Dict],
        target_ratio: float = 0.2,
        seed: int = 1024,
) -> pd.DataFrame:
    """"""
    num_good = int(num_samples * (1 - target_ratio))
    num_bad = num_samples - num_good

    data = dict()
    for config in configs:
        index_name = config.get('index_name')
        bad_range, good_range = config.get('index_range')
        index_type = config.get('index_type')
        index_bad_val = gen_data(num_bad, bad_range[0], bad_range[1], data_type=index_type, )
        index_good_val = gen_data(num_good, good_range[0], good_range[1], data_type=index_type, )
        index_val = np.concatenate((index_good_val, index_bad_val))
        data[index_name] = index_val
    df = pd.DataFrame(data)
    df['target'] = 0
    df.loc[num_good:, 'target'] = 1
    df = df.sample(frac=1, random_state=seed).reset_index(drop=True)
    df['uuid'] = df.index.map(calculate_md5)
    return df


def random_date(min_date, max_date):
    """"""
    min_date = int(min_date)
    max_date = int(max_date)

    min_datetime = pd.to_datetime(str(min_date), format='%Y%m%d')
    max_datetime = pd.to_datetime(str(max_date), format='%Y%m%d')
    random_datetime = random.choice(pd.date_range(min_datetime, max_datetime))
    random_date_str = random_datetime.strftime('%Y%m%d')
    return random_date_str


def calculate_md5(string):
    """
    desc: 生成md5编码
    :param string:
    :return:
    """
    md5_hash = hashlib.md5()
    md5_hash.update(string.encode('utf-8'))
    md5_encoded = md5_hash.hexdigest()
    return md5_encoded


