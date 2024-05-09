
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style="white")

def diagonal_corr(df):
    # Compute the correlation matrix
    corr = df.corr()

    # Generate a mask for the upper triangle
    mask = np.triu(np.ones_like(corr, dtype=np.bool))

    # Set up the matplotlib figure
    f, ax = plt.subplots(figsize=(11, 9))

    # Generate a custom diverging colormap
    cmap = sns.diverging_palette(220, 10, as_cmap=True)

    # Draw the heatmap with the mask and correct aspect ratio
    sns.heatmap(corr, mask=mask, cmap=cmap, vmax=.3, center=0,
                square=True, linewidths=.5, cbar_kws={"shrink": .5})


def structure_corr(df, col_cate, target_name='target'):
    '''
    col_cate = [f"{item.split('_')[0]}_{item.split('_')[1]}" for item in col]
    :param df:
    :param col_cate:
    :return:
    '''
    col_cate = sorted(col_cate)
    col = sorted(df.columns.tolist())
    df = df[col]
    col_cate_unique = np.unique(col_cate)
    col_cate_values = pd.Series(col_cate).replace(col_cate_unique, range(len(col_cate_unique))).values

    # Create a categorical palette to identify the networks
    pal = sns.husl_palette(len(col_cate), s=.45)
    lut = dict(zip(np.unique(col_cate_values), pal))
    colors = [lut[item] for item in col_cate_values]

    sns.clustermap(
        df.corr(), center=0, cmap="vlag",
        row_colors=colors, col_colors=colors,
        linewidths=.75, figsize=(18, 18)
    )



