'''
Methods to wrap DMDMD selection runs as python functions of the form:

  results = selection.run(inputs)

where inputs and results are dictionaries.
'''
import tempfile
import script
import os
import os.path as op

DEFAULTS = { 0: 'selection',
             '-o'        : '{}.nc'}

def new_inputs(default=DEFAULTS, deffnm=None, defdir=None):
    '''
    returns a prototype dictionary for a LSDMap selection run.
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
    Run a LSDMap selection job, with the given inputs.
    '''

    if not 0 in inputs.keys():
        raise RuntimeError('No executable specified.')
    if not 1 in inputs.keys():
        raise RuntimeError('Number of configurations not specified.')
    if not '-s' in inputs.keys():
        raise RuntimeError('No eigenvector file specified.')
 
    result = inputs.copy()

    execstr = inputs.pop(0) + " "
    execstr = execstr + str(inputs.pop(1)) + " "

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
        raise RuntimeError('Selection job failed.')

    result['STDOUT'] = out

    return result
