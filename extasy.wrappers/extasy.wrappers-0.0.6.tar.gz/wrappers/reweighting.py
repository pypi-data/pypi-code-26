'''
Methods to wrap DMDMD reweighting runs as python functions of the form:

  results = reweighting.run(inputs)

where inputs and results are dictionaries.
'''
import tempfile
import script
import os
import os.path as op

DEFAULTS = { 0: 'reweighting',
             '-o'        : '{}.alb',
             '-w'        : '{}.w'}

def new_inputs(default=DEFAULTS, deffnm=None, defdir=None):
    '''
    returns a prototype dictionary for a LSDMap reweighting run.
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
    Run a DMDMD reweighting job, with the given inputs.
    '''

    if not 0 in inputs.keys():
        raise RuntimeError('No executable specified.')
    if not '-c' in inputs.keys():
        raise RuntimeError('Old structure file not specified.')
    if not '-n' in inputs.keys():
        raise RuntimeError('No nearest neighbours file specified.')
    if not '-s' in inputs.keys():
        raise RuntimeError('No nc file specified.')
 
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
        raise RuntimeError('Reweighting job failed.')

    result['STDOUT'] = out

    return result
