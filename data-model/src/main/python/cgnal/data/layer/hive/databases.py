from cgnal.data.layer import DatabaseABC, TableABC
from cgnal.logging.defaults import WithLogging
from datetime import datetime


class Database(DatabaseABC):

    def __init__(self, sqlContext, db_name):
        """
        A class implementing an interface to databases via HIVE client

        :param sqlContext: spark context
        :param db_name: name of the database

        :type sqlContext: spark context
        :type db_name: str
        """
        self.sqlContext = sqlContext
        self.name = db_name
        self.sql = self.sqlContext.sql
        self.sql('USE ' + db_name)
        self.tables = self.sql('show tables').toPandas()['tableName'].values

    def __getitem__(self, table_name):
        """
        Return table from the database

        :param table_name: Name of the table
        :type table_name: str

        :return: object of class PickleTable
        """
        return self.table(table_name)

    def table(self, table_name):
        """
        Table selector

        :param table_name: name of the table

        :type table_name: str

        :return: object of class HiveTable
        """
        if table_name in self.tables:
            return Table(self, table_name)
        else:
            raise ValueError("Table %s not found in database %s" % (table_name, self.name))


class Table(TableABC, WithLogging):

    def __init__(self, db, table_name):
        """
        Table class constructor to interface with hive

        :param db: database containing the table
        :param table_name: name of the table

        :type db: cgnal.data.layer.hive.databases.Database
        :type table_name: str
        """
        self.db = db
        self.table_name = table_name
        self.columns = self.get(1).columns

    @staticmethod
    def cast(x):
        """
        Cast values to correct datetime or string format

        :param x: input value

        :return: casted value
        """
        if isinstance(x, datetime):
            return Table.format_datetime(x)
        else:
            return str(x)

    @staticmethod
    def row2sql(row, fields):
        """
        Transform DataFrame's rows to comma separated strings

        :param row: input row
        :param fields: column names

        :type row: pd.Series
        :type fields: list

        :return: comma separated string of row's values
        """
        return "'" + "','".join(map(lambda f: Table.cast(row[f]), fields)) + "'"

    @staticmethod
    def format_datetime(x):
        """
        Formats a datetime object as 'YYY-MM-DD<T>HH:MM:SS.mmm'

        :param x: datetime object

        :return: formatted string
        """
        return str(x).replace(' ', 'T')

    def sql(self, query):
        """
        Run sql query

        :param query: sql query

        :type query: str

        :return: a query for the selected Database
        """
        self.logger.debug("Executing query:\n%s" % query)
        return self.db.sql(query)

    def to_df(self, query, partitions=500):
        """
        Create pandas DataFrame according to input query

        :param query: input query
        :param partitions: number of partitions

        :type: str
        :type: int

        :return: pd.DataFrame resulting from the query
        """
        self.logger.info("Creating dataframe from table: %s" % self.table_name)
        return self.sql(query).repartition(partitions).toPandas()

    def get(self, limit=None):
        """
        Retrieve records from one or more tables in a database and limit the number of records returned

        :param limit: limiting value

        :type limit: str

        :return: a Table with limited number of selected records
        """
        limit_str = "LIMIT %d" % limit if limit is not None else ""
        return self.sql("SELECT * FROM %s.%s %s" % (self.db.name, self.table_name, limit_str))

    def where(self, condition):
        """
        Retrieve records from given table in applying given filtering condition

        :param condition: condition to be applied

        :type condition: str

        :return: a Table with limited number of selected records
        """
        filter_str = "WHERE %d" % condition
        return self.sql("SELECT * FROM %s.%s %s" % (self.db.name, self.table_name, filter_str))

    def write(self, df, partition_by=None, fields=None):
        """
        Write input DataFrame as a hive table

        :param df: input DataFrame
        :param partition_by: partition list
        :param fields: list of fields to print

        :type df: pd.DataFrame
        :type partition_by: list
        :type fields: list

        :return: None
        """

        fields = fields if fields is not None else df.columns
        # fields = self.sql("describe %s" % self.table_name).toPandas()["col_name"]

        header = 'insert into table {} '.format(self.table_name)
        partition = '' if (partition_by is None) else ' partition ({}={}) '.format(partition_by[0], partition_by[1])

        sql_statement = header + partition + ' select '

        rows = df.apply(lambda row: self.row2sql(row, fields), axis=1).values

        sql_statement += '\n union all select '.join(rows)

        self.logger.info("Writing on table: %s" % self.table_name)

        self.sql(sql_statement)
