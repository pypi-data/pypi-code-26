import pygib





if __name__ == '__main__': 
    for i in xrange(3,6):
        for data in [
            ('traindata/ch_big.txt', 'traindata/ch_good.txt', 'traindata/ch_bad.txt', 'ch'), 
            ('traindata/en_big.txt', 'traindata/en_good.txt', 'traindata/en_bad.txt', 'en')
        ]:
            model = pygib.Gibberish(i)
            print "Training %d %s" % (i, data[3])
            model.train(data[0], data[1], data[2])
            model.save("%s%d.pki" % (data[3], i))

