#
# service: Caller: implement rest/swagger caller functionality
#
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4:
#
#
import logging
import os
import json
import behavioral_signals_swagger_client as swagger_client
import time

class Caller():
    def __init__(self,opts,polling_time=5,indent=1):
        self.indent = indent
        self.opts = opts
	self.api = swagger_client.DefaultApi()
	self.api.api_client.configuration.host = opts.apiurl
	self.api.api_client.configuration.api_key['X-Auth-Token'] =\
	    opts.apitoken
	self.polling_time = polling_time

    # -- obtain process info and poll if necessary
    def GetInfo(self, pid, poll=False):
	elapsed_time = 0
	wait,resp = self.getInfo(pid)
	if not poll:
	    return resp
	while wait:
	    time.sleep(self.polling_time)
            elapsed_time += self.polling_time
	    wait,resp = self.getInfo(pid)
        if elapsed_time > 0 :
            logging.info("{} : polled process for {} seconds".
                format(pid, elapsed_time))
	return resp

    # -- obtain process results and dump them to a file as json
    def GetResults(self,pid,json_dir=None,dest=None):
        results = self.api.get_process_results(self.opts.apiid, pid)
        self.saveJSON2File(results.to_dict(),json_dir, dest,pid=pid)
        return results

    # -- obtain frame results and dump them to a file as json
    def GetFrameResults(self,pid,json_dir=None,dest=None):
        results = self.api.get_process_results_frames(self.opts.apiid, pid)
        self.saveJSON2File(results.to_dict(),json_dir, dest, "_frames",pid=pid)
        return results

    # -- obtain ASR results from caller
    # -- handle some exceptions -- return empty list
    def GetASRResults(self,pid,json_dir=None,dest=None):
        results = {}
        try:
            results = self.api.get_process_results_asr(self.opts.apiid, pid)
            results = results.to_dict()
        except ValueError as e:
            # -- in case there is no ASR record for it
            if str(e) == "Invalid value for `words`, must not be `None`":
                logging.warning("{}: No ASR output".format(pid))
            else:
                logging.warning("{}: ASR failed: {}".format(pid,e))
                results=None
        except Exception as e:
            if e.status == 405 or e.status == 503:
                msg = self.getResponse(e.body, 'message')
                logging.warning("{}: ASR failure: {}/{}".format(
                    pid, msg, e.status))
                results=None
            else:
                raise
        finally:
            if results is not None:
                self.saveJSON2File(results,json_dir, dest, "_words",pid=pid)
        return results
    # ----------------------------------------------------------------------
    # -- obtain process info -- see if we should continue to wait
    def getInfo(self,pid):
	resp = self.api.get_process_info(self.opts.apiid,pid)
	if resp.status == -1:
	    logging.info("{}: transient error -- retrying".format(pid))
	    return True,resp
	if resp.status in [0,1]:
	    return True,resp
	return False,resp

    # -- save a json dict to file
    def saveJSON2File(self,results, json_dir, dest, suffix="", pid=0):
        if not json_dir : return
        if not dest     : return
        fname = os.path.splitext(os.path.basename(dest))[0]
        json_file = os.path.join(
            json_dir, "{}_{}{}.json".format(fname, pid, suffix))
        with open(json_file, 'w') as jf:
            json.dump(results, jf, indent=self.indent)

    # -- try to parse json body and return its json attr, if possible
    def getResponse(self,body, attr):
        try:
            r = json.loads(body)
            return r[attr]
        except Exception:
            return "?"
