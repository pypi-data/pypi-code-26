from pyunfold import iterative_unfold

# Run example case
data = [100, 150]
data_err = [10, 12.2]
response = [[0.8, 0.1, 0.6],
            [0.2, 0.9, 0.4]]
response_err = [[0.01, 0.01, 0.01],
                [0.01, 0.01, 0.01]]
efficiencies = [0.4, 0.67, 0.8]
efficiencies_err = [0.01, 0.01, 0.01]
# priors = [0.34, 1-0.34]
priors = [0.34, 0.21, 1 - (0.34 + 0.21)]
print('priors = {}'.format(priors))
# Perform iterative unfolding
unfolded = iterative_unfold(data, data_err,
                            response, response_err,
                            efficiencies, efficiencies_err,
                            priors=priors,
                            return_iterations=True)
unfolded.to_hdf('example3_python3.hdf', 'dataframe')
