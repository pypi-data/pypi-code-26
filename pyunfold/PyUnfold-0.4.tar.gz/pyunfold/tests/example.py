from pyunfold import iterative_unfold, Logger

# Run example case
data = [100, 150]
data_err = [10, 12.2]
response = [[0.9, 0.1],
            [0.1, 0.9]]
response_err = [[0.01, 0.01],
                [0.01, 0.01]]
efficiencies = [0.4, 0.67]
efficiencies_err = [0.01, 0.01]
# Perform iterative unfolding
unfolded = iterative_unfold(data, data_err,
                            response, response_err,
                            efficiencies, efficiencies_err,
                            return_iterations=True,
                            callbacks=[Logger()])

# unfolded.to_hdf('example1_python3.hdf', 'dataframe')
