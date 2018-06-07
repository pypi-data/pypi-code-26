'''
Methods to wrap pyCoCo runs as python functions of the form:

  results = runcoco.run(inputs)

where inputs and results are dictionaries.
'''
import tempfile
import script
import os
import os.path as op

DEFAULTS = { 0: 'pyCoCo',
             '-o'        : '{}.pdb',
             '-f'        : 'pdb',
             '-s'        : 'all',
             '-n'        : 1,
             '-l'        : '{}.log'}

def new_inputs(default=DEFAULTS, deffnm=None, defdir=None):
    '''
    returns a prototype dictionary for an pyCoCo run.
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
    Run an pyCoCo job, with the given inputs.
    '''

    if not 0 in inputs.keys():
        raise RuntimeError('No executable specified.')
    if not '-i' in inputs.keys():
        raise RuntimeError('No input (trajectory) files specified.')
    if not '-t' in inputs.keys():
        raise RuntimeError('No topology file specified.')
 
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

    result = {}
    try:
        out = s.run(os.environ["SHELL"] + ' -f {}')
    except:
        raise RuntimeError('pyCoCo job failed.')

    result = inputs.copy()
    outname, ext = op.splitext(result['-o'])
    result['-o'] = []
    for i in range(result['-n']):
        result['-o'].append(outname+'{}'.format(i) + ext)

    return result
