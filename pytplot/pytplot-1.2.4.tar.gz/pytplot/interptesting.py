from scipy import interpolate

asdf = interpolate.splrep([2,5,8,11,14], [1,2,1000,4,5])

print(interpolate.splev([4,8,12], asdf))

