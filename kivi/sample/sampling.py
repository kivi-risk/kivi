

import logging

def upsampling(df, down_rate=None, up_rate=None, target_name='target', label=(0, 1)):
    """

    :param df:
    :param down_rate:
    :param up_rate:
    :param target_name:
    :param label:
    :return:
    """
    logging.warning('未来采样API为sampling, upsampling即将弃用。')
    df_observation = df[df[target_name] == label[1]].copy()
    df_no_obser = df[df[target_name] == label[0]].copy()

    if up_rate:
        num = int(df_no_obser.shape[0] * up_rate)
        df_observation = df_observation.sample(n=num, replace=True)

    if down_rate:
        num = int(df_no_obser.shape[0] * down_rate)
        df_no_obser = df_no_obser.sample(n=num, replace=False)

    df = df_no_obser.append(df_observation)
    return df.sample(frac=1).reset_index(drop=True)


def sampling(df, down_rate=None, up_rate=None, target_name='target', label=(0, 1)):
    """
    上采样与下采样
    :param df:
    :param down_rate:
    :param up_rate:
    :param target_name:
    :param label:
    :return:
    """
    df_observation = df[df[target_name] == label[1]].copy()
    df_no_obser = df[df[target_name] == label[0]].copy()

    if up_rate:
        num = int(df_no_obser.shape[0] * up_rate)
        df_observation = df_observation.sample(n=num, replace=True)

    if down_rate:
        num = int(df_no_obser.shape[0] * down_rate)
        df_no_obser = df_no_obser.sample(n=num, replace=False)

    df = df_no_obser.append(df_observation)
    return df.sample(frac=1).reset_index(drop=True)
