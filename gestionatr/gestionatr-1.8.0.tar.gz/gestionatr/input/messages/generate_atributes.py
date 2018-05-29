file = open("info")
out = open("out.txt", 'w')

method = "@property\n" \
         "def {0}(self):\n" \
         "    tree = '{{0}}.{2}'.format(self._header)\n" \
         "    data = get_rec_attr(self.{1}, tree, False)\n" \
         "    if data not in [None, False]:\n" \
         "        return data.text\n" \
         "    else:\n" \
         "        return False\n\n"

obj = "obj"

from A1_41 import A1_41 as check_repeated

for line in file.readlines():
    line = line[1:-1]
    mname = line[0].lower()
    for c in line[1:-1]:
        if c.isupper():
            mname += "_{0}".format(c.lower())
        else:
            mname += c
    if not getattr(check_repeated, mname, False):
        out.write(method.format(
            mname,
            obj,
            line[0:-1]
        ))
