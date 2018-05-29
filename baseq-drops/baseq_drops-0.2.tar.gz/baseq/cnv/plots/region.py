from baseq.setting import r_script_dir
import os, sys
from baseq.mgt import get_config, run_cmd

def plot_region(bincount, cbs_path, path_out):
    """Plot the region of genome...

    ToDo: .......

    """
    script = os.path.join(r_script_dir, "Genome_Plot.R")
    cmd = "Rscript {} {} {} {}".format(script, bincount, cbs_path, path_out)
    try:
        run_cmd("Plot Genome", cmd)
    except:
        sys.exit("[error] Failed to run the Normalize Rscript ...")