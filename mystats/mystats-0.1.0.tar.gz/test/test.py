import mystats as st

# Sanity Test

data = [1, 2, 3]
expected = 2
actual = st.avg(data)

if actual == expected:
    print("SUCCESS: The average is {}".format(actual))
else:
    print("FAIL: Oh no, your average is {} but it should be {}.".format(
        actual, expected))
