'''
Methods to wrap Gromacs mdrun runs as python functions of the form:

  results = mdrun.run(inputs)

where inputs and results are dictionaries.

Also supports a rudimentary PBS-based 'Map' method:

  resultss = mdrun.pbsmap(inputss)

where resultss and inputss are lists of results and inputs dictionaries, 
respectively.
'''
import tempfile
import script
import os

DEFAULTS = { 0: 'gmx mdrun',
             '-o'        : '{}.trr',
             '-x'        : '{}.xtc',
             '-g'        : '{}.log',
             '-cpo'      : '{}.cpt',
             '-e'        : '{}.edr',
             '-c'        : '{}.gro'}

def _check_and_assemble(inputs, defdir=None):
    '''
    Prepare a gromacs job, with the given inputs.
    '''

    if type(inputs) == list:
        nreps = len(inputs)
        irep = 0
        for inp in inputs:
            if not 0 in inp.keys():
                raise RuntimeError('No executable specified.')
            if not '-s' in inp.keys():
                raise RuntimeError('No run (tpr) file specified.')
            if irep == 0:
                basename = os.path.splitext(inp['-s'])[0]
                execstr = inp[0] + " -multi {} ".format(len(inputs))
            for key in inp:
                if key != 0:
                    realfile = inp[key]
                    ext = os.path.splitext(realfile)[1]
                    tmpfile = basename + str(irep) + ext
                    if os.path.exists(realfile):
                        os.symlink(realfile, tmpfile)
                    inputs[irep][key] = (realfile, tmpfile)
                    if irep == 0:
                        execstr = execstr + key + " "
                        if inp[key] is not None:
                            execstr = execstr + basename + ext + " "
            irep += 1
    else:
                    
        if not 0 in inputs.keys():
            raise RuntimeError('No executable specified.')
        if not '-s' in inputs.keys():
            raise RuntimeError('No run (tpr) file specified.')
 
        execstr = inputs[0] + " "

        for key in inputs:
            if key != 0:
                execstr = execstr + key + " "
                if inputs[key] is not None:
                    execstr = execstr + inputs[key] + " "

    return execstr, inputs

def _check_results(result):
    # checks that things are really OK...
    with open(result['-g']) as f:
        data = f.read()

    if not 'Finished mdrun on' in data[-50:]:
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
    execstr, _  = _check_and_assemble(inputs)
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
    Makes use of the Gromacs -multi facility.
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

    for i in range(0, len(inputs), num_workers):
        s = script.Script()
        inp = inputs[i:i + num_workers]
        execstr, ninp = _check_and_assemble(inp, defdir=defdir)
        inputs[i:i + num_workers] = ninp
        execstr = 'aprun -n {} '.format(cores_per_job * len(inp)) + execstr
        s.append(execstr)
        try:
            out = s.run(os.environ["SHELL"] + ' -f {}')
        except:
            raise RuntimeError('Error running parallel jobs,')

    if type(inputs) != list:
        results = inputs.copy()
        results['STDOUT'] = out
        _check_results(results)
    else:
        results = [input.copy() for input in inputs]
        for i in range(len(results)):
            result = results[i]
            for key in result:
                if type(result[key]) == tuple:
                    realfile = result[key][0]
                    tmpfile = result[key][1]
                    if os.path.exists(realfile):
                        os.remove(tmpfile)
                    else:
                        if os.path.exists(tmpfile):
                            os.rename(tmpfile, realfile)
                    results[i][key] = realfile
            result['STDOUT'] = out
            _check_results(result)

    return results

