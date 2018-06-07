'''
Methods to wrap Amber MD runs as python functions of the form:

  results = amber.run(inputs)

where inputs and results are dictionaries.

Also supports a rudimentary PBS-based 'Map' method:

  resultss = amber.pbsmap(inputss)

where resultss and inputss are lists of results and inputs dictionaries, 
respectively.
'''
import tempfile
import script
import os

DEFAULTS = { 0: 'sander',
             '-O'        : None,
             '-o'        : '{}.out',
             '-r'        : '{}.rst',
             '-x'        : '{}.mdcrd',
             '-v'        : '{}.mdvel',
             '-inf'      : '{}.mdinfo',
             '-l'        : '{}.log',
             '-e'        : '{}.mden' }

def _check_and_assemble(inputs, defdir=None):
    '''
    Check the inputs dictionary and assemble into the string to be passed
    on for execution.
    '''
    if type(inputs) == list:
        groupfile = tempfile.NamedTemporaryFile(dir=defdir, delete=False,
                                                suffix='.grpfile')
        for inp in inputs:
            if not '-i' in inp.keys():
                raise RuntimeError('No input (mdin) file specified.')
            if not '-c' in inp.keys():
                raise RuntimeError('No start coordinates (inpcrd) file'
                                   + 'specified.')
            if not '-p' in inp.keys():
                raise RuntimeError('No topology (prmtop) file specified.')
        
            defstr = ''
            for key in inp:
                if not key in [0, 'STDOUT', 'STDERR']:
                    defstr = defstr + key + " "
                    if inp[key] is not None:
                        defstr = defstr + inp[key] + " "
            groupfile.write(defstr + "\n")
        groupfile.close()
        execstr = inputs[0][0] + " -ng {} -groupfile {}".format(len(inputs),
                                                                groupfile.name)
    else: 
        if not 0 in inputs.keys():
            raise RuntimeError('No executable specified.')
        if not '-i' in inputs.keys():
            raise RuntimeError('No input (mdin) file specified.')
        if not '-c' in inputs.keys():
            raise RuntimeError('No start coordinates (inpcrd) file specified.')
        if not '-p' in inputs.keys():
            raise RuntimeError('No topology (prmtop) file specified.')

        execstr = inputs[0] + " "

        for key in inputs:
            if not key in [0, 'STDOUT', 'STDERR']:
                execstr = execstr + key + " "
                if inputs[key] is not None:
                    execstr = execstr + inputs[key] + " "
    
    return execstr

def _check_results(result):

    with open(result['-o']) as f:
        data = f.read()

    if ('Amber 14 SANDER' in data) and (not 'wallclock() was called' in data):
        raise RuntimeError('Output file truncated - job terminated prematurely?')
    if ('PMEMD implementation' in data) and (not 'Total wall time' in data):
        raise RuntimeError('Output file truncated - job terminated prematurely?')

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
    if type(inputs) == list:
        raise RuntimeError('amber.run command only supports single jobs,')
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

def pbsmap(inputs, num_workers=None, cores_per_job=None, 
           cores_per_node=None, defdir=None):
    '''
    Run multiple jobs in parallel via pbs.
    Makes use of the AMBER multijob facility.
    '''
    if (os.getenv("PBS_ENVIRONMENT")) is None:
        raise RuntimeError("No PBS environment detected.")

    num_nodes = int(os.getenv('NODE_COUNT'))
    if cores_per_node is None:
        cores_per_node = int(os.getenv('NUM_PES'))

    total_cores = num_nodes * cores_per_node
    if cores_per_job is None:
        cores_per_job = max(total_cores/len(inputs), 1)
    else:
        cores_per_job = min(cores_per_job, total_cores)

    max_workers = total_cores/cores_per_job
    if num_workers is None:
        num_workers = max_workers
    else:
        num_workers = min(num_workers, max_workers)

    if type(inputs) == list:
        results = [input.copy() for input in inputs]
    else:
        results = inputs.copy()
    for i in range(0, len(inputs), num_workers):
        s = script.Script()
        inp = inputs[i:i + num_workers]
        execstr = _check_and_assemble(inp, defdir=defdir)
        execstr = 'aprun -n {} '.format(cores_per_job * len(inp)) + execstr
        s.append(execstr)
        try:
            out = s.run(os.environ["SHELL"] + ' -f {}')
        except:
            raise RuntimeError('Error running parallel jobs,')
        for result in results[i:i + num_workers]:
            result['STDOUT'] = out
            _check_results(result)

    return results

