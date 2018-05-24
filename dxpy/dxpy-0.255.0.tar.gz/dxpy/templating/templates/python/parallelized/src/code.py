#!/usr/bin/env python
# DX_APP_WIZARD_NAME DX_APP_WIZARD_VERSION
# Generated by dx-app-wizard.
#
# Parallelized execution pattern: Your app will generate multiple jobs
# to perform some computation in parallel, followed by a final
# "postprocess" stage that will perform any additional computations as
# necessary.
#
# See https://wiki.dnanexus.com/Developer-Portal for documentation and
# tutorials on how to modify this file.
#
# DNAnexus Python Bindings (dxpy) documentation:
#   http://autodoc.dnanexus.com/bindings/python/current/

import os
import dxpy

@dxpy.entry_point("postprocess")
def postprocess(process_outputs):
    # Change the following to process whatever input this stage
    # receives.  You may also want to copy and paste the logic to download
    # and upload files here as well if this stage receives file input
    # and/or makes file output.

    for output in process_outputs:
        pass

    return { "answer": "placeholder value" }

@dxpy.entry_point("process")
def process(input1):
    # Change the following to process whatever input this stage
    # receives.  You may also want to copy and paste the logic to download
    # and upload files here as well if this stage receives file input
    # and/or makes file output.

    print input1

    return { "output": "placeholder value" }

@dxpy.entry_point("main")
def main(DX_APP_WIZARD_INPUT_SIGNATURE):
DX_APP_WIZARD_INITIALIZE_INPUTDX_APP_WIZARD_DOWNLOAD_ANY_FILES
    # Split your work into parallel tasks.  As an example, the
    # following generates 10 subjobs running with the same dummy
    # input.

    subjobs = []
    for i in range(10):
        subjob_input = { "input1": True }
        subjobs.append(dxpy.new_dxjob(subjob_input, "process"))

    # The following line creates the job that will perform the
    # "postprocess" step of your app.  We've given it an input field
    # that is a list of job-based object references created from the
    # "process" jobs we just created.  Assuming those jobs have an
    # output field called "output", these values will be passed to the
    # "postprocess" job.  Because these values are not ready until the
    # "process" jobs finish, the "postprocess" job WILL NOT RUN until
    # all job-based object references have been resolved (i.e. the
    # jobs they reference have finished running).
    #
    # If you do not plan to have the "process" jobs create output that
    # the "postprocess" job will require, then you can explicitly list
    # the dependencies to wait for those jobs to finish by setting the
    # "depends_on" field to the list of subjobs to wait for (it
    # accepts either dxpy handlers or string IDs in the list).  We've
    # included this parameter in the line below as well for
    # completeness, though it is unnecessary if you are providing
    # job-based object references in the input that refer to the same
    # set of jobs.

    postprocess_job = dxpy.new_dxjob(fn_input={ "process_outputs": [subjob.get_output_ref("output") for subjob in subjobs] },
                                     fn_name="postprocess",
                                     depends_on=subjobs)
DX_APP_WIZARD_UPLOAD_ANY_FILES
    # If you would like to include any of the output fields from the
    # postprocess_job as the output of your app, you should return it
    # here using a job-based object reference.  If the output field in
    # the postprocess function is called "answer", you can pass that
    # on here as follows:
    #
    # return { "app_output_field": postprocess_job.get_output_ref("answer"), ...}
    #
    # Tip: you can include in your output at this point any open
    # objects (such as files) which will be closed by a job that
    # finishes later.  The system will check to make sure that the
    # output object is closed and will attempt to clone it out as
    # output into the parent container only after all subjobs have
    # finished.

    output = {}
DX_APP_WIZARD_OUTPUT
    return output

dxpy.run()
