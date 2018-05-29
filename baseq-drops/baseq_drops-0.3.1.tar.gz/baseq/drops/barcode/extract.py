def HammingDistance(seq1, seq2):
    return sum([1 for x in zip(seq1, seq2) if x[0] != x[1]])

def extract_barcode(protocol, seq):
    """Extract cell barcode from reads 1 sequences, if protocol not defined, return blank.
        - 10X: seq[0:16]
        - indrop: seq[0:i] + seq[i + 22 : i + 22 + 8] (i is length of barcode 1)
        - dropseq: seq[0:12]

    Usages:
    ::
        from baseq.drops import extract_barcode
        extract_barcode("10X", "ATCGATCGATCGACTAAATTTTTTT")

    Returns:
        barcode sequence, if no valid barcode, return ""
    """

    if protocol == "10X":
        return seq[0:16]
    elif protocol == "dropseq":
        return seq[0:12]
    elif protocol == "indrop":
        w1 = "GAGTGATTGCTTGTGACGCCTT"
        if w1 in seq:
            w1_pos = seq.find(w1)
            if 7 < w1_pos < 12:
                return seq[0:w1_pos] + seq[w1_pos + 22:w1_pos + 22 + 8]
        else:
            for i in range(8, 12):
                w1_mutate = seq[i:i + 22]
                if HammingDistance(w1_mutate, w1) < 2:
                    return seq[0:i] + seq[i + 22 : i + 22 + 8]
                    break
        return ""
    else:
        return ""

def extract_UMI(protocol, barcode, seq1, mutate_last_base):
    """
    Extract the UMI from reads 1 sequences.
    ::
        10X: 16-26
        indrop: seq1[len(barcode) + 22:len(barcode) + 22 + 6]
        dropseq: 11-19/12-20

    """
    if protocol == "10X":
        UMI = seq1[16:26]
    if protocol == "dropseq":
        if mutate_last_base:
            UMI = seq1[11:19]
        else:
            UMI = seq1[12:20]
    if protocol == "indrop":
        UMI = seq1[len(barcode) + 22:len(barcode) + 22 + 6]
    return UMI