import csv

try:
    import pandas as pd
except ImportError as e:
    HAS_PANDAS = False
else:
    HAS_PANDAS = True

try:
    import numpy as np
except ImportError as e:
    HAS_NUMPY = False
else:
    HAS_NUMPY = True


def to_csv(csvpath, X, columns):
    if HAS_PANDAS and isinstance(X, pd.DataFrame):
        X.to_csv(csvpath, columns=columns, index=False)
    elif HAS_NUMPY and isinstance(X, np.ndarray):
        np.savetxt(csvpath, X, header=','.join(columns), delimiter=',', comments='')
    else:
        with open(csvpath, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            for row in X:
                writer.writerow(list(row))


def convert_X_y_to_csv(X, y, csvpath):
    if HAS_PANDAS and isinstance(X, pd.DataFrame):
        X['y'] = y
        data = X
        columns = X.columns
    else:
        columns = ['c:%d' % i for i in range(len(X[0]))] + ['y']
        if HAS_NUMPY and isinstance(X, np.ndarray):
            data = np.vstack([X.T, y]).T
        else:
            data = [list(row) + [val_y] for row, val_y in zip(X, y)]
    to_csv(csvpath, data, columns)


def convert_X_to_csv(X, csvpath):
    if HAS_PANDAS and isinstance(X, pd.DataFrame):
        columns = X.columns
    else:
        columns = ['c:%d' % i for i in range(len(X[0]))]
    to_csv(csvpath, X, columns)


def rename_col_y(col_y, csvpath, new_csvpath):
    with open(csvpath, 'r') as f:
        reader = csv.reader(f)
        columns = next(reader)
        if col_y not in columns:
            raise Exception("No column named '{}'".format(col_y))
        columns = [c if c != col_y else 'y' for c in columns]

        with open(new_csvpath, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            for row in reader:
                writer.writerow(row)


def chunk_csv(csvpath, new_csvpath, max_rows=1000):
    with open(csvpath, 'r') as f_in:
        header = f_in.readline()
        f_out = open(new_csvpath, 'w')
        f_out.write(header)
        nrows = 0
        for row in f_in:
            f_out.write(row)
            nrows += 1
            if nrows == max_rows:
                f_out.close()
                yield f_out
                f_out = open(new_csvpath, 'w')
                f_out.write(header)
                nrows = 0
        if nrows > 0:
            yield f_out

