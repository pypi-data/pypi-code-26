'''
Methods to wrap LSDMap runs as python functions of the form:

  results = lsdmap.run(inputs)

where inputs and results are dictionaries.
'''
import tempfile
import script
import os
import os.path as op

DEFAULTS = { 0: 'lsdmap',
             '-n'        : '{}.nn'}

def new_inputs(default=DEFAULTS, deffnm=None, defdir=None):
    '''
    returns a prototype dictionary for a LSDMap run.
    '''
    result = default.copy()
    if deffnm is None:
        deffnm = os.path.relpath(tempfile.NamedTemporaryFile(dir=defdir).name)

    for key in result:
        if key is not 0:
            if type(result[key]) == str:
                result[key] = result[key].format(deffnm)
    return result

def run(inputs):
    '''
    Run a LSDMap job, with the given inputs.
    '''

    if not 0 in inputs.keys():
        raise RuntimeError('No executable specified.')
    if not '-f' in inputs.keys():
        raise RuntimeError('No configuration file specified.')
    if not '-c' in inputs.keys():
        raise RuntimeError('No structures file specified.')
    if not '-t' in inputs.keys():
        raise RuntimeError('No topology file specified.')
 
    result = inputs.copy()
    execstr = inputs.pop(0) + " "

    for key in inputs:
        execstr = execstr + str(key) + " "
        if inputs[key] is not None:
            if type(inputs[key]) != list:
                execstr = execstr + str(inputs[key]) + " "
            else:
                for v in inputs[key]:
                    execstr = execstr + str(v) + " "

    s = script.Script()
    s.append(execstr)

    try:
        out = s.run(os.environ["SHELL"] + ' -f {}')
    except:
        raise RuntimeError('LSDMap job failed.')

    result['STDOUT'] = out
    rc = result['-c']
    if isinstance(rc, str):
        rc = [rc,]
    basename = op.splitext(rc[0])[0]
    result['-eg'] = basename + '.eg'
    result['-ev'] = basename + '.ev'
    result['-eps'] = basename + '.eps'
    result['-l'] = 'lsdmap.log'

    # insert checks on output files here...
    with open(result['-l']) as f:
        data = f.read()

    if not 'LSDMap computation done' in data[-50:]:
        raise RuntimeError('Log file suggests job failed.')

    return result
