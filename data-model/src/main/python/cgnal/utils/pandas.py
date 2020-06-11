from pandas import DataFrame
from pandas.core.arrays.sparse.dtype import SparseDtype

def is_sparse(df: DataFrame):
    return True if all([isinstance(v, SparseDtype) for k, v in df.dtypes.items()]) else False

def loc(df: DataFrame, idx):
    """
    This loc function is designed to work propertly with sparse dataframe as well

    :param df: DataFrame
    :param idx: index list
    :return: DataFrame which is filtered
    """
    if is_sparse(df):
        csr = df.sparse.to_coo().tocsr()
        pos = [pos for pos, elem in enumerate(df.index) if elem in idx]
        return DataFrame.sparse.from_spmatrix(csr[pos, :], index=idx[pos], columns=df.columns)
    else:
        return df.loc[idx]


