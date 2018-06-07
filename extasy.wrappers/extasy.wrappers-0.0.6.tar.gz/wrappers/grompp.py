'''
Methods to wrap Grompp runs as python functions of the form:

  results = grompp.run(inputs)

where inputs and results are dictionaries.

Also supports a rudimentary PBS-based 'Map' method:

  resultss = grompp.pbsmap(inputss)

where resultss and inputss are lists of results and inputs dictionaries, 
respectively.
'''
import tempfile
import script
import os

DEFAULTS = { 0: 'gmx grompp',
             '-o'        : '{}.tpr'}

def _check_and_assemble(inputs):
    '''
    Prepare a grompp job, with the given inputs.
    '''

    if not 0 in inputs.keys():
        raise RuntimeError('No executable specified.')
    if not '-f' in inputs.keys():
        raise RuntimeError('No input (mdp) file specified.')
    if not '-c' in inputs.keys():
        raise RuntimeError('No structure (.gro) file specified.')
    if not '-p' in inputs.keys():
        raise RuntimeError('No topology (.top) file specified.')
 
    result = inputs.copy()
    execstr = inputs[0] + " "

    for key in inputs:
        if key != 0:
            execstr = execstr + key + " "
            if inputs[key] is not None:
                execstr = execstr + inputs[key] + " "

    return execstr

def _check_results(result):
    # insert checks that things are really OK here...
    pass

def new_inputs(default=DEFAULTS, deffnm=None, defdir=None):
    '''
    returns a prototype dictionary for an amber run.
    '''
    result = default.copy()
    if deffnm is None:
        deffnm = os.path.relpath(tempfile.NamedTemporaryFile(dir=defdir).name)

    for key in result:
        if type(result[key]) == str:
            result[key] = result[key].format(deffnm)
    return result

def run(inputs):
    '''
    Run a job, with the given inputs.
    '''
    execstr = _check_and_assemble(inputs)
    result  = inputs.copy()
    s = script.Script()
    s.append(execstr)

    try:
        out = s.run(os.environ["SHELL"] + ' -f {}')
    except:
        raise RuntimeError('Error running {} job,'.format(inputs[0]))

    result['STDOUT'] = out

    # checks that things are really OK...
    _check_results(result)

    return result

def pbsmap(inputs, num_workers=None, cores_per_job=None, cores_per_node=None):
    '''
    Run multiple jobs in parallel via pbs.
    '''
    if (os.getenv("PBS_ENVIRONMENT")) is None:
        raise RuntimeError("No PBS environment detected.")

    num_nodes = int(os.getenv('NODE_COUNT'))
    total_cores = int(os.getenv('NUM_PES'))

    max_workers = min(num_nodes, 1000)
    max_cores_per_node = total_cores / num_nodes

    if cores_per_node is None:
        cores_per_node = max_cores_per_node
    else:
        cores_per_node = min(cores_per_node, max_cores_per_node)

    if num_workers is None:
        num_workers = max_workers
    else:
        num_workers = min(num_workers, max_workers)

    max_cores_per_job = total_cores / num_workers
    if cores_per_job is None:
        cores_per_job = max_cores_per_job
    else:
        cores_per_job = min(cores_per_job, max_cores_per_job)

    results = []
    for i in range(0, len(inputs), num_workers):
        s = script.Script()
        for inp in inputs[i:i + num_workers]:
            execstr = _check_and_assemble(inp)
            execstr = 'aprun -n {} '.format(cores_per_job) + execstr + ' &'
            s.append(execstr)
            results.append(inp)

        s.append('wait')
        try:
            out = s.run(os.environ["SHELL"] + ' -f {}')
        except:
            raise RuntimeError('Error running parallel jobs,')
        for result in results[i:i + num_workers]:
            result['STDOUT'] = out
            _check_results(result)

    return results

