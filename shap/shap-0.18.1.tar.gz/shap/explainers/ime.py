from iml.common import convert_to_instance, convert_to_model, match_instance_to_data, match_model_to_data, convert_to_instance_with_index
from iml.explanations import AdditiveExplanation
from iml.links import convert_to_link, IdentityLink
from iml.datatypes import convert_to_data, DenseData
from iml.explanations import AdditiveExplanation
from .kernel import KernelExplainer
import numpy as np
import logging

log = logging.getLogger('shap')


class IMEExplainer(KernelExplainer):
    """ This is an implementation of the IME explanation method (aka. Shapley sampling values)

    IMEExplainer computes SHAP values under the assumption of feature independence and is based on
    the algorithm proposed in "An Efficient Explanation of Individual Classifications using
    Game Theory", Erik Štrumbelj, Igor Kononenko, JMLR 2010
    """

    def __init__(self, model, data, **kwargs):
        # silence warning about large datasets
        level = log.level
        log.setLevel(logging.ERROR)
        super(IMEExplainer, self).__init__(model, data, **kwargs)
        log.setLevel(level)

    def explain(self, incoming_instance, **kwargs):
        # convert incoming input to a standardized iml object
        instance = convert_to_instance(incoming_instance)
        match_instance_to_data(instance, self.data)

        # pick a reasonable number of samples if the user didn't specify how many they wanted
        self.nsamples = kwargs.get("nsamples", 0)
        if self.nsamples == 0:
            self.nsamples = 1000 * self.P

        # divide up the samples among the features
        self.nsamples_each = np.ones(self.P, dtype=np.int64) * 2 * (self.nsamples // (self.P * 2))
        for i in range((self.nsamples % (self.P * 2)) // 2):
            self.nsamples_each[i] += 2

        model_out = self.model.f(instance.x)

        # explain every feature
        phi = np.zeros(self.P)
        self.X_masked = np.zeros((self.nsamples_each.max(), self.data.data.shape[1]))
        for i in range(self.P):
            phi[i] = self.ime(i, self.model.f, instance.x, self.data.data, nsamples=self.nsamples_each[i])
        phi = np.array(phi)

        return AdditiveExplanation(self.link.f(model_out - phi.sum()), self.link.f(model_out), phi, np.zeros(len(phi)), instance, self.link,
                                   self.model, self.data)


    def ime(self, j, f, x, X, nsamples=10):
        assert nsamples % 2 == 0, "nsamples must be divisible by 2!"
        X_masked = self.X_masked[:nsamples,:]
        inds = np.arange(X.shape[1])

        for i in range(0, nsamples//2):
            np.random.shuffle(inds)
            pos = np.where(inds == j)[0][0]
            rind = np.random.randint(X.shape[0])
            X_masked[i,:] = x
            X_masked[i,inds[pos+1:]] = X[rind,inds[pos+1:]]
            X_masked[-(i+1),:] = x
            X_masked[-(i+1),inds[pos:]] = X[rind,inds[pos:]]

        evals = f(X_masked)
        evals_on = evals[:nsamples//2]
        evals_off = evals[nsamples//2:][::-1]

        return np.mean(evals[:nsamples//2] - evals[nsamples//2:])
