import json
from typing import List, Dict, Tuple
from typing_tools import DictStruct, AssignmentSupportable

# region Class Declarations
class Point(DictStruct):
    x: int
    y: int

class PointWithDefaults(DictStruct):
    x: int = 0
    y: int = 0
    
    def print_me(self):
        print(f"PointWithDefaults is: {self}")
        print(f"PointWithDefaults X is: {self.x} and {self['x']} and {self.get('x')}")
        print(f"PointWithDefaults Y is: {self.y} and {self['y']} and {self.get('y')}")
        

class Circle(DictStruct):
    r: int
    c: Point

class Arc(DictStruct):
    region: Circle
    vector: Point
    angle: int

class Figure(AssignmentSupportable):
    points: List[Point]

class NamedFigure(AssignmentSupportable):
    points_dict: Dict[str, Point]

class Monster(AssignmentSupportable):
    eyes: List[Circle] = None
    # torso: Figure
    # arms: List[NamedFigure]
    arc_of_danger: Arc = None
#endregion

# region Test functions:
def test_circle_1() -> Circle:
    o = Circle(r=4, c=Point(x=2, y=15))
    print(f"Circle is: {o}")
    print(f"Circle Radius is: {o.r}")
    print(f"Circle Center is: {o.c}")
    print(f"Circle Center X is: {o.c.x}")
    print(f"Circle Center Y is: {o.c.x}")
    print(json.dumps(o))
    print()
    
    return o

def test_circle_2() -> Circle:
    _point_dict = { 'x': 5, 'y': 18 }
    _circle_dict = { 'c': _point_dict, 'r': 6 }
    o = Circle(_circle_dict)
    print(f"Circle is: {o}")
    print(f"Circle Radius is: {o.r}")
    print(f"Circle Center is: {o.c}")
    print(f"Circle Center X is: {o.c.x}")
    print(f"Circle Center Y is: {o.c.x}")
    print(json.dumps(o))
    print()
    
    return o
    
def test_figure() -> Figure:
    f = Figure()
    f.points = [{ 'x': 5, 'y': 18 }, Point(x=2, y=15), dict(x=1, y=22)]
    print(f"Figure is: {f}")
    print(f"Figure Points are: {f.points}")
    for i, _p in enumerate(f.points):
        print(f"Figure Point #{i+1} is: {_p}")
        print(f"Figure Point #{i+1} X is: {_p.x}")
        print(f"Figure Point #{i+1} Y is: {_p.y}")
    print()
    
    return f
    
def test_named_figure():
    f2 = NamedFigure()
    f2.points_dict = { 'A': { 'x': 5, 'y': 18 }, 'PointB': Point(x=2, y=15), 'p.C': dict(x=1, y=22) }
    print(f"NamedFigure is: {f2}")
    print(f"NamedFigure Points are: {f2.points_dict}")
    for _name, _p in f2.points_dict.items():
        print(f"NamedFigure Point '{_name}' is: {_p}")
        print(f"NamedFigure Point '{_name}' X is: {_p.x}")
        print(f"NamedFigure Point '{_name}' Y is: {_p.y}")
    print()

def test_default_values_point():
    p = PointWithDefaults(y=6)
    p.print_me()
    
    p.x = 8
    p.y = 4
    p.print_me()
    print()

def test_mutable_circle(o: Circle):
    print("Supports assignment too!")
    print(f"Circle Radius was: {o.r}")
    o.r = 9
    print(f"Circle Radius is now: {o.r}")
    print()

def test_mutable_figure(f: Figure):
    print(f"Figure Points were: {f.points}")
    f.points = [ Point(x=1, y=1), Point(x=1, y=2), Point(x=2, y=3) ]
    print(f"Figure Points are now: {f.points}")
    print()

    print(f"Figure Point #{1} was: {f.points[0]}")
    f.points[0] = Point(x=8, y=4)
    print(f"Figure Point #{1} is now: {f.points[0]}")
    print()

    print(f"Figure Point #{2} X was: {f.points[1].x}")
    f.points[1].x = 88
    print(f"Figure Point #{2} X is now: {f.points[1].x}")
    print()
    
    print("And again...")
    print(f"Figure Points are: {f.points}")
    print()
    
def test_mutable_monster(o: Circle):
    _point_dict = { 'x': 5, 'y': 18 }
    _circle_dict = { 'c': _point_dict, 'r': 6 }
    print("Let's create a monster!")
    m = Monster()
    # m.arms = [ f2, NamedFigure(points_dict={'hand': Point(x=18, y=44), 'shoulder': {'x':10, 'y': 80}) ]
    if (not m.eyes):
        m.eyes = [ o, Circle(_circle_dict), dict(r=5, c=dict(x=5,y=108)), {'r': 9, 'c': {'x':1, 'y':2}} ]
    if (not m.arc_of_danger):
        m.arc_of_danger = json.loads('{"region": { "c": {"x": -5, "y": -9}, "r": 50}, "vector": { "x": 500, "y": 866 }, "angle": 120 }') 
    print(f"Monster is: {m}")
    print(f"Monster Eyes are: {m.eyes}")
    for i, _e in enumerate(m.eyes):
        print(f"Monster Eye #{i+1} is: {_e}")
        print(f"Monster Eye #{i+1} Radius is: {_e.r}")
        print(f"Monster Eye #{i+1} Center is: {_e.c}")
        print(f"Monster Eye #{i+1} Center X is: {_e.c.x}")
        print(f"Monster Eye #{i+1} Center Y is: {_e.c.y}")
    print(f"Monster Arc of Danger is: {m.arc_of_danger}")
    print()
    
    print("Let's mutate than monster!")
    m.arc_of_danger.region.r += 15
    m.eyes.append(dict(r=-5, c=dict(x=1, y=22)))
    print(f"Monster Eyes are now: {m.eyes}")
    print(f"Monster Arc of Danger is now: {m.arc_of_danger}")
#endregion

def main():
    _ = test_circle_1()
    o = test_circle_2()
    f = test_figure()
    test_default_values_point()
    test_mutable_circle(o)
    test_mutable_figure(f)
    test_mutable_monster(o)

if (__name__ == '__main__'):
    # print(issubclass(list, List))
    # print(List[DictChild].__dict__)
    # tt = Tuple[str, int, Point]
    # print(tt.__args__)
    # print(tt.__dict__)
    main()
