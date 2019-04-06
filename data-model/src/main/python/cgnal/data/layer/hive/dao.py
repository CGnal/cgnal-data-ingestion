from cgnal.data.layer import DAO


# TODO: completare, una volta capito cosa devono fare esattamente computeKey, get e parse e trovato un modo di testare
#  con Hive
class DataFrameDAO(DAO):
    """Data Access Object for HiveDataFrames"""

    def __init__(self, key_field="Date"):
        self.key_field = key_field

    def set_key_field(self, value):
        self.key_field = value
        return self

    def computeKey(self, df):
        return df[self.key_field]

    def get(self, df):
        pass
        #return pd.concat({k: df[k] for k in df})

    def parse(self, row):
        pass
        # return pd.concat({c: row[c] for c in row.index.levels[0]}, axis=1)


# class SeriesDAO(DAO):
#     """Data Access Object for pd.Series"""
#
#     def computeKey(self, df):
#         return df.name
#
#     def get(self, s):
#         return s
#
#     def parse(self, row):
#         return row
