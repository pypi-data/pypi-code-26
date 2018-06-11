from StreamFig import StreamFig

# s = StreamFig(directed=True)
s = StreamFig()

s.addNode("a")
s.addNode("b")

s.addLink("a", "b", 1, 2)
