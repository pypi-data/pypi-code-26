import fisher


def fisherTest(*args, alternative='two-sided', padOR=True):
    """Fisher's exact test on a 2x2 contingency table.
    (swiped from https://github.com/agartland/utils/blob/master/myfisher.py)

    Wrapper around fisher.pvalue found in:
    Fast Fisher's Exact Test (Haibao Tang, Brent Pedersen)
    https://pypi.python.org/pypi/fisher/

    Test is performed in C (100x speed-up)

    Parameters
    ----------
    tab : list of lists or 2x2 ndarray
        Each element should contain counts
    alternative : string
        Specfies the alternative hypothesis (similar to scipy.fisher_exact)
        Options: 'two-sided', 'less', 'greater', 'all'
    padOR : weither to pad 0 in contigency table with 1 for OR calculation, True by default.

    Returns
    -------
    OR : float
        Odds-ratio associated with the 2 x 2 table
    p : float
        P-value associated with the test and the alternative hypothesis"""

    if len(args) == 1:
        tab = [item for sublist in list(*args) for item in sublist]
    elif len(args) == 4:
        tab = list(args).copy()
    else:
        raise ValueError("either supply a contigency table or the values as arguments: fisherTest(a,b,c,d)")

    res = fisher.pvalue(*tab)

    if padOR:
        OR = (max(tab[0], 1) * max(tab[3], 1)) / (max(tab[1], 1) * max(tab[2], 1))
    else:
        OR = (tab[0] * tab[3]) / (tab[1] * tab[2])

    if alternative == 'two-sided':
        return (OR, res.two_tail)
    elif alternative == 'less':
        return (OR, res.left_tail)
    elif alternative == 'greater':
        return (OR, res.right_tail)
    elif alternative == 'all':
        return (OR, res)
