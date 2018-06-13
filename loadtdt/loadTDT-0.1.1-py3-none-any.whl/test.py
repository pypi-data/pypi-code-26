import loadTDT

def test():
    tank = 'test_tanks/0_LFP'
    data = loadTDT.loadTDT(tank)
    import ipdb; ipdb.set_trace()
    
if __name__ == '__main__':
    test()
