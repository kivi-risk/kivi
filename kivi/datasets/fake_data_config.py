__all__ = [
    'configs',
]


configs = [
    {
        'index_name': 'age',                 # 指标英文名
        'index_range': [[0, 30], [25, 80]],  # 指标值域，坏客户值域，好客户值域
        'index_type': 'randint',             # 数值类型
        'na_rate': [0.1, 0.2],
    },
    {
        'index_name': 'income',              # 指标英文名
        'index_range': [[500, 10000], [5000, 1e5]],  # 指标值域，坏客户值域，好客户值域
        'index_type': 'uniform',             # 数值类型
        'na_rate': [0.1, 0.2],
    },
]

