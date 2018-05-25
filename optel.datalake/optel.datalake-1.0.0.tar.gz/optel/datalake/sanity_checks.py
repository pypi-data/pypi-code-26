import pyspark.sql.functions as sf
from optel.datalake import transform
import logging


def real_dups(df):
    """
    Check and remove duplicated rows.

    Args:
        df (pyspark.sql.DataFrame): A spark dataframe
    """
    nb_rows = df.count()
    nb_distinct = df.distinct().count()
    nb_dups = nb_rows - nb_distinct
    if nb_rows != nb_distinct:
        logging.info("%s real duplicates found, removing them" % nb_dups)
        dedup_df = df.drop_duplicates()
    else:
        logging.info("No real duplicates found")
        dedup_df = df
    return dedup_df


def empty_columns(df):
    """
    Remove columns with 100% missing values.

    Args:
        df (pyspark.sql.DataFrame): A spark dataframe

    Returns:
        pyspark.sql.DataFrame: A data frame free of any empty columns.
    """
    missing_obs = df.agg(*[(1 - (sf.count(c) / sf.count('*'))).
                           alias(c) for c in df.columns])
    values = missing_obs.first()
    dict_values = values.asDict()
    logging.info(
        "Percentage of empties in each columns %s", dict_values)
    empty_cols = transform.find_key(dict_values, 1.0)
    logging.info("Empty columns found %s", empty_cols)
    for column in empty_cols:
        df = df.drop(column)
    return df


def convert_decimal_to_float(df):
    """
    Convert columns with decimal types to floating type.

    Args:
        df (pyspark.sql.DataFrame): A spark dataframe.

    Returns:
        pyspark.sql.DataFrame: A dataframe free of any decimal type column.

    """
    names = [c[0] for c in df.dtypes if 'decimal' in c[1]]
    return_df = df
    for name in names:
        return_df = return_df.withColumn(name, return_df[name].cast("double"))
    return return_df


def convert_date_to_string(df):
    """
    Convert columns with timestamp and date types to string type with
    the following formatting: yyyy/MM/dd

    Args:
        df (pyspark.sql.DataFrame): A spark dataframe.

    Returns:
        pyspark.sql.DataFrame: A dataframe with dates converted to string

    """

    names = [c[0] for c in df.dtypes if "timestamp" in c[1] or "date" in c[1]]
    print(df.dtypes)
    return_df = df
    for name in names:
        return_df = return_df. \
            withColumn(name, sf.date_format(return_df[name], 'yyyy/MM/dd'))
    return return_df
