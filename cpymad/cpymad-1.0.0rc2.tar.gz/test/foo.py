from cpymad.madx import Madx
from cpymad.util import format_command #, expr_names
m = Madx(command_log=print)
l = m._libmadx
m.call('testseq.madx')

m.command.beam('ex=1, ey=2, particle=electron, sequence=s1')

initial = dict(alfx=0.5, alfy=1.5,
               betx=2.5, bety=3.5)

m.use('s1')

twiss = m.twiss(sequence='s1',
                #columns=['betx', 'bety', 'alfx', 'alfy'],
                #file='foo.tfs',
                **initial)


cmd = m.command.match
