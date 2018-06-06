#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import xml.etree.ElementTree as ET

from .binary import BinaryModel

class PseudoDolloModel(BinaryModel):
    package_notice = """[DEPENDENCY]: The Pseudo-Dollo model is implemented in the BEAST package "Babel"."""

    def __init__(self, model_config, global_config):

        BinaryModel.__init__(self, model_config, global_config)
        self.datatype_id = None
        self.subst_model_id = None
#        self.freq_str = self.build_freq_str()
        
    def JUNK_build_freq_str(self):
        if self.binarised:
            all_data = []
            for f in self.features:
                for lang in self.data:
                    if self.data[lang][f] == "?":
                        continue
                    dpoint, index = self.data[lang][f], self.unique_values[f].index(self.data[lang][f])
                    all_data.append(index)
        else:
            all_data = []
            for f in self.features:
                for lang in self.data:
                    if self.data[lang].get(f,"?") == "?":
                        valuestring = "".join(["?" for i in range(0,len(self.unique_values[f])+1)])
                    else:
                        valuestring = ["0" for i in range(0,len(self.unique_values[f])+1)]
                        valuestring[self.unique_values[f].index(self.data[lang][f])+1] = "1"
                        all_data.extend(valuestring)

        all_data = [d for d in all_data if d !="?"]
        all_data = [int(d) for d in all_data]
        zerf = 1.0*all_data.count(0) / len(all_data)
        onef = 1.0*all_data.count(1) / len(all_data)
        assert abs(1.0 - (zerf+onef)) < 1e-6
        return "%.2f %.2f" % (zerf, onef)

    def add_state(self, state):
        BinaryModel.add_state(self, state)
        ET.SubElement(state, "parameter", {"id":"PDCognateDeathRate", "name":"stateNode", "upper":"1.0"}).text = "0.05"
        ET.SubElement(state, "parameter", {"id":"PDFreqParameter", "dimension":"3", "lower":"0.0", "name":"stateNode", "upper":"1.0"}).text = "0.95 0.03 0.02 0.00"

    def get_userdatatype(self, feature, fname):
        if self.datatype_id:
            return ET.Element("userDataType", {"idref":self.datatype_id})
        else:
            self.datatype_id = "bdDataType"
            datatype = ET.Element("userDataType", {
                "id":self.datatype_id,
                "spec":"beast.evolution.datatype.UserDataType",
                "states":"4",
                "codelength":"1",
                "codeMap": "A = 0, 1 = 1, B = 2, 0 = 0 2, ? = 0 1 2, - = 0 1 2, C = 0 1 2, D = 3",
                })
            return datatype

    def add_sitemodel(self, distribution, feature, fname):

        # Sitemodel
        mr = self.get_mutation_rate(feature, fname)
        sitemodel = ET.SubElement(distribution, "siteModel", {"id":"SiteModel.%s"%fname,"spec":"SiteModel", "mutationRate":mr,"shape":"1","proportionInvariant":"0"})
        substmodel = self.add_substmodel(sitemodel, feature, fname)

    def add_substmodel(self, sitemodel, feature, fname):
        if self.subst_model_id:
            sitemodel.set("substModel", "@%s" % self.subst_model_id)
            return

        self.subst_model_id = "%s:pseudodollo.s" % self.name
        substmodel = ET.SubElement(sitemodel, "substModel",{"id":self.subst_model_id,"spec":"beast.evolution.substitutionmodel.BirthDeathModel", "deathprob":"@PDCognateDeathRate"})
        ET.SubElement(substmodel, "frequencies", {"id":"PDfrequencies","spec":"Frequencies","frequencies":"@PDFreqParameter"})

    def add_prior(self, prior):
        BinaryModel.add_prior(self, prior)
        deathrate_prior = ET.SubElement(prior, "prior", {"id":"PDCognateDeathRatePrior", "name":"distribution","x":"@PDCognateDeathRate"})
        ET.SubElement(deathrate_prior, "Exponential", {"name":"distr","id":"%s:pd_deathrate_prior.s"%self.name, "mean":"1.0"} )

        freq_prior = ET.SubElement(prior, "prior", {"id":"PDFreqParameterPrior", "name":"distribution", "x":"@PDFreqParameter"})
        dirich = ET.SubElement(freq_prior, "distr", {"id":"PDFreqUniform", "spec":"beast.math.distributions.Uniform", "lower":"0.0", "upper":"1.0"})

    def add_operators(self, run):
        BinaryModel.add_operators(self, run)
        ET.SubElement(run, "operator", {"id":"pd_deathrate_scaler.s", "spec":"ScaleOperator","parameter":"@PDCognateDeathRate","scaleFactor":"0.75","weight":"3.0"})
        ET.SubElement(run, "operator", {"id":"pd_frequencies_exchanger", "spec":"DeltaExchangeOperator","parameter":"@PDFreqParameter", "weight":"3.0"})

    def add_param_logs(self, logger):
        BinaryModel.add_param_logs(self, logger)
#        ET.SubElement(logger,"log",{"idref":"%s:dollo_alpha.s" % self.name})
#        ET.SubElement(logger,"log",{"idref":"%s:dollo_s.s" % self.name})
#        if self.config.log_fine_probs:
#            ET.SubElement(logger,"log",{"idref":"%s:dollo_alpha_prior.s" % self.name})
#            ET.SubElement(logger,"log",{"idref":"%s:dollo_s_prior.s" % self.name})
