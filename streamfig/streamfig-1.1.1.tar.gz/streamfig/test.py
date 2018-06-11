from StreamFig import StreamFig

s = StreamFig(alpha=0, omega=10, directed=True)
# s = StreamFig()

s.addNode("a")
s.addNode("b")
s.addNode("c")

s.addLink("a", "b", 1, 2)
s.addLink("b", "a", 3, 4)
s.addLink("c", "a", 5, 6)
s.addLink("a", "c", 8, 10)

