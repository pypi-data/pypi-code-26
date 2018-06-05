import sys

try:
    import wx
    hasWx = True
    #Check if wx is the newest 3.0+ version:
    try:
        from wx.lib.pubsub import pub
        pub.subscribe
        newWx = True
    except AttributeError as e:
        from wx.lib.pubsub import Publisher as pub
        newWx = False
except Exception as e:
    hasWx = False
    newWx = False

import os
import time
import ntpath
import math
import random
import numpy
import scipy.stats
import datetime

import matplotlib.pyplot as plt

import base
import pytransit
import pytransit.transit_tools as transit_tools
import pytransit.tnseq_tools as tnseq_tools
import pytransit.norm_tools as norm_tools
import pytransit.stat_tools as stat_tools



############# GUI ELEMENTS ##################

short_name = "mcce"
long_name = "MCCE"
short_desc = "MCCE test of conditional essentiality between two conditions"
long_desc = """Method for determining conditional essentiality based on mcce (i.e. permutation test). Identifies significant changes in mean read-counts for each gene after normalization."""

transposons = ["himar1", "tn5"]
columns = ["Orf","Name","Desc", "Num. of Sites","Obs Mean Ctrl","Obs Mean Exp", "Post Mean Ctrl", "Post Mean Exp", "log2FC","DE", "Bit"]

class MCCEAnalysis(base.TransitAnalysis):
    def __init__(self):
        base.TransitAnalysis.__init__(self, short_name, long_name, short_desc, long_desc, transposons, MCCEMethod, MCCEGUI, [MCCEFile])



############# FILE ##################

class MCCEFile(base.TransitFile):

    def __init__(self):
        base.TransitFile.__init__(self, "#MCCE", columns)

    def getHeader(self, path):
        DE=0; poslogfc=0; neglogfc=0;
        for line in open(path):
            if line.startswith("#"): continue
            tmp = line.strip().split("\t")
            if tmp[-1] == "True":
                DE +=1
                if float(tmp[-2]) > 0:
                    poslogfc+=1
                else:
                    neglogfc+=1

        text = """Results:
    Conditionally Essential: %s
        More Essential in Experimental datasets: %s
        Less Essential in Experimental datasets: %s
            """ % (DE, poslogfc, neglogfc)
        return text


    def getMenus(self):
        menus = []
        menus.append(("Display in Track View", self.displayInTrackView))
        menus.append(("Display Histogram", self.displayHistogram))
        return menus

    def displayHistogram(self, displayFrame, event):
            gene = displayFrame.grid.GetCellValue(displayFrame.row, 0)
            filepath = os.path.join(ntpath.dirname(displayFrame.path), transit_tools.fetch_name(displayFrame.path))
            filename = os.path.join(filepath, gene+".png")
            if os.path.exists(filename):
                imgWindow = pytransit.fileDisplay.ImgFrame(None, filename)
                imgWindow.Show()
            else:
                transit_tools.ShowError(MSG="Error Displaying File. Histogram image not found. Make sure results were obtained with the histogram option turned on.")
                print "Error Displaying File. Histogram image does not exist."


        

############# GUI ##################

class MCCEGUI(base.AnalysisGUI):

    def definePanel(self, wxobj):

        self.wxobj = wxobj
        mccePanel = wx.Panel( self.wxobj.optionsWindow, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )

        mcceSizer = wx.BoxSizer( wx.VERTICAL )

        mcceLabel = wx.StaticText( mccePanel, wx.ID_ANY, u"mcce Options", wx.DefaultPosition, (160,-1), 0 )
        mcceLabel.SetFont( wx.Font( 10, wx.DEFAULT, wx.NORMAL, wx.BOLD) )
        mcceSizer.Add( mcceLabel, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )

        mcceTopSizer = wx.BoxSizer( wx.HORIZONTAL )

        mcceTopSizer2 = wx.BoxSizer( wx.HORIZONTAL )

        mcceLabelSizer = wx.BoxSizer( wx.VERTICAL )

        mainSizer1 = wx.BoxSizer( wx.VERTICAL )

        #(, , Sizer) = self.defineChoiceBox(mccePanel, u"", u"", "")
        #mainSizer1.Add(Sizer, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND, 5 )

        # Samples 
        (mcceSampleLabel, self.wxobj.mcceSampleText, sampleSizer) = self.defineTextBox(mccePanel, u"Samples:", u"10000", "Number of samples to take when estimating the mcce histogram. More samples give more accurate estimates of the p-values at the cost of computation time.")
        mainSizer1.Add(sampleSizer, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND, 5 )

        # Rope
        (mcceROPELabel, self.wxobj.mcceROPEText, ROPESizer) = self.defineTextBox(mccePanel, u"ROPE:", u"1.0", "Defines Region Of Practical Equivalence: the region surrounding a difference of 0.0, that represents changes that are not meaningfully different than zero. Similar to the region of a null-hypothesis.")
        mainSizer1.Add(ROPESizer, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND, 5 )

        # Norm 
        mcceNormChoiceChoices = [ u"TTR", u"nzmean", u"totreads", u'zinfnb', u'quantile', u"betageom", u"nonorm" ]
        (mcceNormLabel, self.wxobj.mcceNormChoice, normSizer) = self.defineChoiceBox(mccePanel, u"Normalization: ", mcceNormChoiceChoices, "Choice of normalization method. The default choice, 'TTR', normalizes datasets to have the same expected count (while not being sensative to outliers). Read documentation for a description other methods. ")
        mainSizer1.Add(normSizer, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND, 5 )


        mcceSizer.Add( mainSizer1, 1, wx.EXPAND, 5 )


        # LOESS Check
        (self.wxobj.mcceLoessCheck, loessCheckSizer) = self.defineCheckBox(mccePanel, labelText="Correct for Genome Positional Bias", widgetCheck=False, widgetSize=(-1,-1), tooltipText="Check to correct read-counts for possible regional biase using LOESS. Clicking on the button below will plot a preview, which is helpful to visualize the possible bias in the counts.")
        mcceSizer.Add( loessCheckSizer, 0, wx.EXPAND, 5 )

        # LOESS Button
        self.wxobj.mcceLoessPrev = wx.Button( mccePanel, wx.ID_ANY, u"Preview LOESS fit", wx.DefaultPosition, wx.DefaultSize, 0 )
        mcceSizer.Add( self.wxobj.mcceLoessPrev, 0, wx.ALL|wx.CENTER, 5 )

        # Adaptive Check
        (self.wxobj.mcceAdaptiveCheckBox, adaptiveSizer) = self.defineCheckBox(mccePanel, labelText="Adaptive mcce (Faster)", widgetCheck=False, widgetSize=(-1,-1), tooltipText="Dynamically stops permutations early if it is unlikely the ORF will be significant given the results so far. Improves performance, though p-value calculations for genes that are not differentially essential will be less accurate.")
        mcceSizer.Add( adaptiveSizer, 0, wx.EXPAND, 5 )

        # Histogram Check
        (self.wxobj.mcceHistogramCheckBox, histSizer) = self.defineCheckBox(mccePanel, labelText="Generate mcce Histograms", widgetCheck=False, widgetSize=(-1,-1), tooltipText="Creates .png images with the mcce histogram for each of the ORFs. Histogram images are created in a folder with the same name as the output file.")
        mcceSizer.Add(histSizer, 0, wx.EXPAND, 5 )


        # Zeros Check
        (self.wxobj.mcceZeroCheckBox, zeroSizer) = self.defineCheckBox(mccePanel, labelText="Include sites with all zeros", widgetCheck=True, widgetSize=(-1,-1), tooltipText="Includes sites that are empty (zero) accross all datasets. Unchecking this may be useful for tn5 datasets, where all nucleotides are possible insertion sites and will have a large number of empty sites (significantly slowing down computation and affecting estimates).")
        mcceSizer.Add(zeroSizer, 0, wx.EXPAND, 5 )


        mcceButton = wx.Button( mccePanel, wx.ID_ANY, u"Run mcce", wx.DefaultPosition, wx.DefaultSize, 0 )
        mcceSizer.Add( mcceButton, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )


        mccePanel.SetSizer( mcceSizer )
        mccePanel.Layout()
        mcceSizer.Fit( mccePanel )


        #Connect events
        mcceButton.Bind( wx.EVT_BUTTON, self.wxobj.RunMethod )
        self.wxobj.mcceLoessPrev.Bind(wx.EVT_BUTTON, self.wxobj.LoessPrevFunc)

        self.panel = mccePanel



########## CLASS #######################

class MCCEMethod(base.DualConditionMethod):
    """   
    mcce
 
    """
    def __init__(self,
                ctrldata,
                expdata,
                annotation_path,
                output_file,
                normalization="TTR",
                samples=10000,
                adaptive=False,
                doHistogram=False,
                includeZeros=False,
                rope=0.0,
                replicates="Sum",
                LOESS=False,
                ignoreCodon=True,
                NTerminus=0.0,
                CTerminus=0.0, wxobj=None):

        base.DualConditionMethod.__init__(self, short_name, long_name, short_desc, long_desc, ctrldata, expdata, annotation_path, output_file, normalization=normalization, replicates=replicates, LOESS=LOESS, NTerminus=NTerminus, CTerminus=CTerminus, wxobj=wxobj)

        self.samples = samples
        self.adaptive = adaptive
        self.doHistogram = doHistogram
        self.includeZeros = includeZeros
        self.rope = rope

        self.mu_pi = 50.0
        self.s2_pi = 20
        self.k_pi = 1
        self.nu_pi = 1
        self.mu0 = 0.0
        self.std0 = 1.0
        self.alpha = 0.95

    @classmethod
    def fromGUI(self, wxobj):
        """ """
        #Get Annotation file
        annotationPath = wxobj.annotation
        if not transit_tools.validate_annotation(annotationPath):
            return None


        #Get selected files
        ctrldata = wxobj.ctrlSelected()
        expdata = wxobj.expSelected()
        if not transit_tools.validate_both_datasets(ctrldata, expdata):
            return None


        #Validate transposon types
        if not transit_tools.validate_transposons_used(ctrldata+expdata, transposons):
            return None


        #Read the parameters from the wxPython widgets
        ignoreCodon = True
        samples = int(wxobj.mcceSampleText.GetValue())
        normalization = wxobj.mcceNormChoice.GetString(wxobj.mcceNormChoice.GetCurrentSelection())
        replicates="Sum"
        adaptive = wxobj.mcceAdaptiveCheckBox.GetValue()
        doHistogram = wxobj.mcceHistogramCheckBox.GetValue()

        includeZeros = wxobj.mcceZeroCheckBox.GetValue()
        rope = float(wxobj.mcceROPEText.GetValue())

        NTerminus = float(wxobj.globalNTerminusText.GetValue())
        CTerminus = float(wxobj.globalCTerminusText.GetValue())
        LOESS = False


        #Get output path
        defaultFileName = "mcce_output_s%d_rope%1.2f" % (samples, rope)
        if adaptive: defaultFileName+= "_adaptive"
        if includeZeros: defaultFileName+= "_iz"
        defaultFileName+=".dat"
    
        defaultDir = os.getcwd()
        output_path = wxobj.SaveFile(defaultDir, defaultFileName)
        if not output_path: return None
        output_file = open(output_path, "w")



        return self(ctrldata,
                expdata,
                annotationPath,
                output_file,
                normalization,
                samples,
                adaptive,
                doHistogram,
                includeZeros,
                rope,
                replicates,
                LOESS,
                ignoreCodon,
                NTerminus,
                CTerminus, wxobj)

    @classmethod
    def fromargs(self, rawargs):

        (args, kwargs) = transit_tools.cleanargs(rawargs)

        ctrldata = args[0].split(",")
        expdata = args[1].split(",")
        annotationPath = args[2]
        output_path = args[3]
        output_file = open(output_path, "w")

        normalization = kwargs.get("n", "TTR")
        samples = int(kwargs.get("s", 10000))
        adaptive = kwargs.get("a", False)
        doHistogram = kwargs.get("h", False)
        replicates = kwargs.get("r", "Sum")
        includeZeros = kwargs.get("iz", False)
        rope = float(kwargs.get("rope", 0.00))
    
        
        LOESS = kwargs.get("l", False)
        ignoreCodon = True
        NTerminus = float(kwargs.get("iN", 0.00))
        CTerminus = float(kwargs.get("iC", 0.00))

        return self(ctrldata,
                expdata,
                annotationPath,
                output_file,
                normalization,
                samples,
                adaptive,
                doHistogram,
                includeZeros,
                rope,
                replicates,
                LOESS,
                ignoreCodon,
                NTerminus,
                CTerminus)



    def Run(self):

        self.transit_message("Starting mcce Method")
        start_time = time.time()
       

        if self.doHistogram:
            histPath = os.path.join(os.path.dirname(self.output.name), transit_tools.fetch_name(self.output.name)+"_histograms")
            if not os.path.isdir(histPath):
                os.makedirs(histPath)
        else:
            histPath = ""
 


        Kctrl = len(self.ctrldata)
        Kexp = len(self.expdata)
        #Get orf data
        self.transit_message("Getting Data")
        if self.normalization != "nonorm":
            self.transit_message("Normalizing using: %s" % self.normalization)


        (data, position) = tnseq_tools.get_data(self.ctrldata + self.expdata)
        (normdata, factors) = norm_tools.normalize_data(data, self.normalization, self.ctrldata + self.expdata, self.annotation_path)

        G_A = tnseq_tools.Genes([], self.annotation_path, ignoreCodon=self.ignoreCodon, nterm=self.NTerminus, cterm=self.CTerminus, data=normdata[:Kctrl], position=position)
        G_B = tnseq_tools.Genes([], self.annotation_path, ignoreCodon=self.ignoreCodon, nterm=self.NTerminus, cterm=self.CTerminus, data=normdata[Kctrl:], position=position)
        
        N = len(G_A)
        muA_list = []; varA_list = [];
        muB_list = []; varB_list = [];
        
        for i in range(N):
            if G_A[i].n > 1:
                A_data = G_A[i].reads.flatten()
                B_data = G_B[i].reads.flatten()
                muA_list.append(numpy.mean(A_data))
                muB_list.append(numpy.mean(B_data))
                varA_list.append(numpy.var(A_data))
                varB_list.append(numpy.var(B_data))
    
        mu0A = numpy.median(muA_list)    
        mu0B = numpy.median(muB_list)    
        s20A = numpy.median(varA_list)
        s20B = numpy.median(varB_list)


        #MCCE
        data = []
        count = 0
        self.progress_range(N)
        for i in range(N):
            count+=1
            if G_A[i].n > 0:
                A_data = G_A[i].reads.flatten()
                B_data = G_B[i].reads.flatten()
            else:
                A_data = numpy.array([0])
                B_data = numpy.array([0])
        

            muA_post, varA_post = self.sample_post(A_data, self.samples, mu0A, s20A, self.k_pi, self.nu_pi)
            muB_post, varB_post = self.sample_post(B_data, self.samples, mu0B, s20B, self.k_pi, self.nu_pi)

            varBA_post = varB_post + varA_post
            muA_post[muA_post<=0] = 0.001
            muB_post[muB_post<=0] = 0.001

            logFC_BA_post = numpy.log2(muB_post/muA_post)


            delta_logFC = logFC_BA_post #- scipy.stats.norm.rvs(self.mu0, self.std0, size=self.samples)
            
            #l_BA, u_BA = self.HDI_from_MCMC(logFC_BA_post, self.alpha)
            l_BA, u_BA = self.HDI_from_MCMC(delta_logFC, self.alpha)


            probROPE = numpy.mean(numpy.logical_and(numpy.logical_and(logFC_BA_post>=0.0-self.rope,  logFC_BA_post<=0.0+self.rope), numpy.logical_and(logFC_BA_post>=l_BA, logFC_BA_post<=u_BA)))/0.95


            bit_BA = not (l_BA <= 0.0 <= u_BA)
 
            if self.doHistogram:
                if len(delta_logFC) > 0:
                    n, bins, patches = plt.hist(delta_logFC, normed=1, facecolor='c', alpha=0.75, bins=100)
                else:
                    n, bins, patches = plt.hist([0], normed=1, facecolor='c', alpha=0.75, bins=100)
                plt.xlabel('Delta Sum')
                plt.ylabel('Probability')
                plt.title('%s - Histogram of Delta Sum' % G_A[i].orf)
                plt.axvline(l_BA, color='r', linestyle='dashed', linewidth=3)
                plt.axvline(u_BA, color='r', linestyle='dashed', linewidth=3)
                plt.axvline(0.00, color='g', linestyle='dashed', linewidth=3)
                plt.grid(True)
                genePath = os.path.join(histPath, G_A[i].orf +".png")
                plt.savefig(genePath)
                plt.clf()


            meanlogFC_BA = numpy.mean(logFC_BA_post)
            post_meanA = numpy.mean(muA_post)
            post_meanB = numpy.mean(muB_post)
            obs_meanA = numpy.mean(A_data)
            obs_meanB = numpy.mean(B_data)
            sumA = numpy.sum(A_data)
            sumB = numpy.sum(B_data)
            obsdiff = obs_meanB - obs_meanA 
            data.append([G_A[i].orf, G_A[i].name, G_A[i].desc, G_A[i].n, obs_meanA, obs_meanB, post_meanA, post_meanB, meanlogFC_BA, probROPE, bit_BA])

            # Update Progress
            text = "Running MCCE Method... %5.1f%%" % (100.0*count/N)
            self.progress_update(text, count)


        #
        self.transit_message("") # Printing empty line to flush stdout 
        #self.transit_message("Performing Benjamini-Hochberg Correction")
        data.sort() 
        #qval = stat_tools.BH_fdr_correction([row[-1] for row in data])
       
 
        self.output.write("#MCCE\n")
        if self.wxobj:
            members = sorted([attr for attr in dir(self) if not callable(getattr(self,attr)) and not attr.startswith("__")])
            memberstr = ""
            for m in members:
                memberstr += "%s = %s, " % (m, getattr(self, m))
            self.output.write("#GUI with: norm=%s, samples=%s, rope=%1.2f, adaptive=%s, histogram=%s, includeZeros=%s, output=%s\n" % (self.normalization, self.samples, self.rope, self.adaptive, self.doHistogram, self.includeZeros, self.output.name))
        else:
            self.output.write("#Console: python %s\n" % " ".join(sys.argv))
        self.output.write("#Control Data: %s\n" % (",".join(self.ctrldata))) 
        self.output.write("#Experimental Data: %s\n" % (",".join(self.expdata))) 
        self.output.write("#Annotation path: %s\n" % (self.annotation_path))
        self.output.write("#Time: %s\n" % (time.time() - start_time))
        self.output.write("# muA-prior: %6.2f\n" % mu0A)
        self.output.write("# muB-prior: %6.2f\n" % mu0B)
        self.output.write("# s2A-prior: %6.2f\n" % s20A)
        self.output.write("# s2B-prior: %6.2f\n" % s20B)
        self.output.write("# ROPE: %3.2f\n" % self.rope)


        self.output.write("#%s\n" % "\t".join(columns))


        for i,row in enumerate(data):
            (orf, name, desc, n, obs_meanA, obs_meanB, meanA, meanB, log2FC, probROPE, bitROPE) = row
            self.output.write("%s\t%s\t%s\t%d\t%5.2f\t%5.2f\t%5.2f\t%5.2f\t%2.2f\t%1.8f\t%s\n" % (orf, name, desc, n, obs_meanA, obs_meanB, meanA, meanB, log2FC, probROPE, bitROPE))
        self.output.close()

        self.transit_message("Adding File: %s" % (self.output.name))
        self.add_file(filetype="MCCE")
        self.finish()
        self.transit_message("Finished mcce Method") 


    def sample_post(self, data, S, mu0, s20, k0, nu0):
        n = len(data)
        if n > 1:
            s2 = numpy.var(data,ddof=1)
        else:
            s2 = s20
        ybar = numpy.mean(data)
        
        kn = k0+n
        nun = nu0+n
        mun = (k0*mu0 + n*ybar)/float(kn)
        s2n = (1.0/nun) * (nu0*s20 + (n-1)*s2 + (k0*n/float(kn))*numpy.power(ybar-mu0,2))
        
        #s2_post = 1.0/scipy.stats.gamma.rvs(nun/2, scale=s2n*nun/2.0, size=S)
        s2_post = 1.0/scipy.stats.gamma.rvs(nun/2.0, scale=2.0/(s2n*nun), size=S)

        min_mu = 0
        max_mu = 1000000
        trunc_a = (min_mu-mun)/numpy.sqrt(s2_post/float(kn))
        trunc_b = (max_mu-mun)/numpy.sqrt(s2_post/float(kn))
        mu_post = scipy.stats.truncnorm.rvs(a=trunc_a, b=trunc_b, loc=mun, scale=numpy.sqrt(s2_post/float(kn)), size=S)
        
        #print S, mu0, s20, k0, nu0
        #print n, s2, ybar, kn, nun, mun, s2n
        #print ""
        #for i in range(S):
        #    #print mu_post[i], s2_post[i]
        #    print mu_post[i]
        
        return (mu_post, s2_post)


    def HDI_from_MCMC(self, posterior_samples, credible_mass=0.95):
        # Computes highest density interval from a sample of representative values,
        # estimated as the shortest credible interval
        # Takes Arguments posterior_samples (samples from posterior) and credible mass (normally .95)
        sorted_points = sorted(posterior_samples)
        ciIdxInc = numpy.ceil(credible_mass * len(sorted_points)).astype('int')
        nCIs = len(sorted_points) - ciIdxInc
        ciWidth = [0]*nCIs
        for i in range(0, nCIs):
            ciWidth[i] = sorted_points[i + ciIdxInc] - sorted_points[i]
        HDImin = sorted_points[ciWidth.index(min(ciWidth))]
        HDImax = sorted_points[ciWidth.index(min(ciWidth))+ciIdxInc]
        return(HDImin, HDImax)



    @classmethod
    def usage_string(self):
        return """python %s mcce <comma-separated .wig control files> <comma-separated .wig experimental files> <annotation .prot_table or GFF3> <output file> [Optional Arguments]
    
        Optional Arguments:
        -s <integer>    :=  Number of samples. Default: -s 10000
        -n <string>     :=  Normalization method. Default: -n TTR
        -h              :=  Output histogram of the permutations for each gene. Default: Turned Off.
        -a              :=  Perform adaptive mcce. Default: Turned Off.
        -iz             :=  Include rows with zero accross conditions.
        --rope          :=  Rope: Region Of Practical Equivalence to zero.
        -l              :=  Perform LOESS Correction; Helps remove possible genomic position bias. Default: Turned Off.
        -iN <float>     :=  Ignore TAs occuring at given fraction of the N terminus. Default: -iN 0.0
        -iC <float>     :=  Ignore TAs occuring at given fraction of the C terminus. Default: -iC 0.0
        """ % (sys.argv[0])




if __name__ == "__main__":

    (args, kwargs) = transit_tools.cleanargs(sys.argv)

    #TODO: Figure out issue with inputs (transit requires initial method name, running as script does not !!!!)

    G = MCCEMethod.fromargs(sys.argv[1:])

    G.console_message("Printing the member variables:")   
    G.print_members()

    print ""
    print "Running:"

    G.Run()


