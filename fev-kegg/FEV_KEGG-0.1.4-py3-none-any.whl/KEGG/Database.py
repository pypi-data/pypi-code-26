import re
import time
import urllib

from FEV_KEGG.lib.Biopython.KEGG.KGML import KGML_pathway, KGML_parser
import jsonpickle
from FEV_KEGG.KEGG.GENE import Gene
import tqdm
from typing import Set, List, Dict, Iterable, Tuple

from FEV_KEGG.Graph.Elements import GeneID
from FEV_KEGG.KEGG import File, Download, SSDB
import FEV_KEGG.settings as settings
from FEV_KEGG.Util import Parallelism
import concurrent.futures


class NoKnownPathwaysError(ValueError):
    """
    Raised if an organism has no known pathways and is therefore rather useless.
    """

class ImpossiblyOrthologousError(ValueError):
    """
    Raised if trying to find orthologs in an organism using a GeneID from the very same organism.
    """

def getPathwayDescriptions(organismAbbreviation: 'eco') -> Set[str]:
    """
    Get full pathway descriptions for an organism.
    
    Downloads the data from KEGG, if not already present on disk.
    
    Parameters
    ----------
    organismAbbreviation : str
        The organism for which to retrieve all known pathways.
    
    Returns
    -------
    Set[str]
        Set of pathway description lines for given organism.
    
    Raises
    ------
    NoKnownPathwaysError
        If the organism has no known pathways.
    URLError
        If connection to KEGG fails.
    """
    
    fileName = 'organism/' + organismAbbreviation + '/pathway/list'
    
    debugOutput = 'Getting pathway list for ' + organismAbbreviation + ' from '
    
    if File.doesFileExist(fileName):
        
        if settings.verbosity > 1:
            print(debugOutput + 'disk.')
            
        pathwayList = File.readSetFromFileAtOnce(fileName)
    
    else:
        if settings.verbosity > 1:
            print(debugOutput + 'download.')
        
        try:
            pathwayList = Download.downloadPathwayList(organismAbbreviation)
        except urllib.error.HTTPError as exception:
            if isinstance(exception, urllib.error.HTTPError) and exception.code == 404: # organism has no known pathways
                raise NoKnownPathwaysError('The organism \'' + organismAbbreviation + '\' has no known pathways.')
            else:
                raise
        File.writeToFile(pathwayList, fileName)
        
    return pathwayList
    
    
def getPathway(organismAbbreviation: 'eco', pathwayName: '00260') -> KGML_pathway.Pathway:
    """
    Get certain pathway object of an organism.
    
    Downloads the data from KEGG, if not already present on disk.
    
    Parameters
    ----------
    organismAbbreviation : str
        The organism for which to retrieve the pathway.
    pathwayName : str
        The code of the pathway, e.g. '00260'.
    
    Returns
    -------
    KGML_pathway.Pathway
        Pathway object. *None* if pathway does not exist.
    
    Raises
    ------
    URLError
        If connection to KEGG fails.
    """
    
    fileName = 'organism/' + organismAbbreviation + '/pathway/' + pathwayName
    
    debugOutput = 'Getting pathway ' + pathwayName + ' for ' + organismAbbreviation + ' from '
    
    if File.doesFileExist(fileName):
        
        if settings.verbosity > 1:
            print(debugOutput + 'disk.')
            
        fileHandle = File.getFileHandleRead(fileName)
        pathway = KGML_parser.read(fileHandle)
        
    else:
        if settings.verbosity > 1:
            print(debugOutput + 'download.')
        
        try: # certain pathways might not exist as KGML (HTTP error 404), ignore these and return None
            pathwayXml = Download.downloadPathway(organismAbbreviation, pathwayName)
        except urllib.error.HTTPError as exception:
            if isinstance(exception, urllib.error.HTTPError) and exception.code == 404:
                return None
            else:
                raise
            
        File.writeToFile(pathwayXml, fileName)
        pathway = KGML_parser.read(pathwayXml)
    
    return pathway

def getPathwayBulk(organismAbbreviation: 'eco', pathwayNames: Iterable[str]) -> Dict[str, KGML_pathway.Pathway]:
    """
    Get multiple pathway objects of an organism.
    
    Downloads the data from KEGG in bulk, if not already present on disk. This is done in parallel in a thread pool, see :attr:`FEV_KEGG.settings.downloadThreads`.
    
    Parameters
    ----------
    organismAbbreviation : str
        The organism for which to retrieve the pathway.
    pathwayNames : Iterable[str]
        The codes of the pathways, e.g. ['00260', '00530'].
    
    Returns
    -------
    Dict[str, KGML_pathway.Pathway]
        Pathway objects, keyed by their respective pathway name. A pathway object is *None* if the pathway does not exist.
    
    Raises
    ------
    URLError
        If connection to KEGG fails.
    """
    
    # split list into pathways on disk and pathways not downloaded yet
    pathwaysOnDisk = []
    pathwaysToDownload = []
    
    for pathwayName in pathwayNames:
        
        fileName = 'organism/' + organismAbbreviation + '/pathway/' + pathwayName
        
        debugOutput = 'Getting pathway ' + pathwayName + ' from '
        
        if File.doesFileExist(fileName):
        
            if settings.verbosity >= 2:
                print(debugOutput + 'disk.')
            
            pathwaysOnDisk.append(pathwayName)
        
        else:
            if settings.verbosity >= 2:
                print(debugOutput + 'download.')
            
            pathwaysToDownload.append(pathwayName)
    
    
    pathways = dict()
    # get pathways from disk
    for pathwayName in pathwaysOnDisk:
        
        fileName = 'organism/' + organismAbbreviation + '/pathway/' + pathwayName
        
        fileHandle = File.getFileHandleRead(fileName)
        pathway = KGML_parser.read(fileHandle)
        pathways[pathwayName] = pathway
    
    
    # download pathways in bulk
    if len( pathwaysToDownload ) > 0:
        tqdmPosition = Parallelism.getTqdmPosition()
        threadPool = concurrent.futures.ThreadPoolExecutor(Parallelism.getNumberOfThreadsDownload())
        futures = []
        iterator = None
        
        try:
            # query KEGG in parallel
            
            for pathwayToDownload in pathwaysToDownload:
                futures.append( threadPool.submit(_downloadPathway, pathwayToDownload, organismAbbreviation) )
            
            iterator = concurrent.futures.as_completed(futures)
            
            if settings.verbosity >= 1:
                if settings.verbosity >= 2:
                    print( 'Downloading ' + str(len(pathwaysToDownload)) + ' pathways...' )
                iterator = tqdm.tqdm(iterator, total = len(pathwaysToDownload), unit = ' pathways', position = tqdmPosition)
                
            for future in iterator:
                
                result_part = future.result()
                if result_part is not None:
                    pathway = KGML_parser.read(result_part)
                    pathwayName = re.sub('[^0-9]', '', pathway.name)
                    pathways[pathwayName] = pathway
                    
                    fileName = 'organism/' + organismAbbreviation + '/pathway/' + pathwayName
                    File.writeToFile(result_part, fileName)
            
            threadPool.shutdown(wait = False)
            
        except KeyboardInterrupt: # only raised in main thread (once in each process!)
        
            Parallelism.keyboardInterruptHandler(threadPool=threadPool, threadPoolFutures=futures, terminateProcess=True)
            raise
        
        except BaseException:
            
            if Parallelism.isMainThread():
                Parallelism.keyboardInterruptHandler(threadPool=threadPool, threadPoolFutures=futures, silent=True)
            raise
        
        finally:
            
            if iterator is not None: iterator.close()

    return pathways


def _downloadPathway(pathwayName, organismAbbreviation):
    if Parallelism.getShallCancelThreads() is True:
        raise concurrent.futures.CancelledError()
    else:
        try: # certain pathways might not exist as KGML (HTTP error 404), ignore these and return None
            pathwayXml = Download.downloadPathway(organismAbbreviation, pathwayName)
        except urllib.error.HTTPError as exception:
            if isinstance(exception, urllib.error.HTTPError) and exception.code == 404:
                return None
            else:
                raise
        return pathwayXml







def getGene(geneIdString: 'eco:b0004') -> Gene:
    """
    Get certain gene.
    
    Downloads the data from KEGG, if not already present on disk.
    
    Parameters
    ----------
    geneIdString : str
        Unique ID of the gene to be downloaded, represented as a string, including organism abbreviation and gene name, e.g. 'eco:b0004'.
    
    Returns
    -------
    Gene
        Gene object.
    
    Raises
    ------
    HTTPError
        If gene does not exist.
    URLError
        If connection to KEGG fails.
    """
    organismAbbreviation, geneString = geneIdString.split(':')
    fileName = 'organism/' + organismAbbreviation + '/gene/' + geneString
    
    debugOutput = 'Getting gene ' + geneIdString + ' from '
    
    if File.doesFileExist(fileName):
        
        if settings.verbosity >= 2:
            print(debugOutput + 'disk.')
        
        fileContent = File.readStringFromFileAtOnce(fileName)
        gene = Gene(fileContent)

    else:
        if settings.verbosity >= 2:
            print(debugOutput + 'download.')
        
        geneText = Download.downloadGene(geneIdString)
        File.writeToFile(geneText, fileName)
        gene = Gene(geneText)

    return gene


def getGeneBulk(geneIDs: Iterable[GeneID]) -> Dict[GeneID, Gene]:
    """
    Get multiple certain genes.
    
    Downloads the data from KEGG in bulk, if not already present on disk. This is done in parallel in a thread pool, see :attr:`FEV_KEGG.settings.downloadThreads`.
    
    Parameters
    ----------
    geneIDs : Iterable[GeneID]
        Unique IDs of the genes to be downloaded, represented as :class:`FEV_KEGG.Graph.Elements.GeneID` objects.
    
    Returns
    -------
    Dict[GeneID, Gene]
        Each found Gene object, keyed by the GeneID used to search it.
    
    Raises
    ------
    IOError
        If result is too small. Possibly because none of the genes of a download-chunk existed.
    URLError
        If connection to KEGG fails.
    """
    # split list into genes on disk and genes not downloaded yet
    genesOnDisk = []
    genesToDownload = []
    
    for geneID in geneIDs:
        organismAbbreviation = geneID.organismAbbreviation
        geneString = geneID.geneName
        fileName = 'organism/' + organismAbbreviation + '/gene/' + geneString
        
        debugOutput = 'Getting gene ' + str( geneID ) + ' from '
        
        if File.doesFileExist(fileName):
        
            if settings.verbosity >= 2:
                print(debugOutput + 'disk.')
            
            genesOnDisk.append(geneID)
        
        else:
            if settings.verbosity >= 2:
                print(debugOutput + 'download.')
            
            genesToDownload.append(geneID)
    
    
    # get genes from disk
    geneEntries = dict()
    for geneID in genesOnDisk:
        
        organismAbbreviation = geneID.organismAbbreviation
        geneString = geneID.geneName
        fileName = 'organism/' + organismAbbreviation + '/gene/' + geneString
        
        fileContent = File.readStringFromFileAtOnce(fileName)
        gene = Gene(fileContent)
        geneEntries[geneID] = gene
    
    
    # download genes in bulk
    if len( genesToDownload ) > 0:
        geneTextBulk = Download.downloadGeneBulk([x.__str__() for x in genesToDownload])
        geneTexts = re.split('///\n', geneTextBulk)[:-1]
        for geneText in geneTexts:
            
            geneText += '///'
            
            gene = Gene(geneText)
            
            organismAbbreviation = gene.organismAbbreviation
            geneString = gene.number
            
            geneEntries[GeneID(organismAbbreviation + ':' + geneString)] = gene
            
            fileName = 'organism/' + organismAbbreviation + '/gene/' + geneString
            File.writeToFile(geneText, fileName)

    return geneEntries



def getPathwayGeneIDs(organismAbbreviation: 'eco', pathwayName: '00260') -> Set[str]:
    """
    Get all gene ID strings in an organism's pathway, if previously saved.
    
    Parameters
    ----------
    organismAbbreviation : str
        The organism for which to retrieve the pathway.
    pathwayName : str
        The code of the pathway, e.g. '00260'.
    
    Returns
    -------
    Set[str]
        Gene ID strings from a pathway, or *None*, if not previously saved on disk.
    
    Note
    ----
    This requires you to previously call :func:`setPathwayGeneIDs`!
    """
    fileName = 'organism/' + organismAbbreviation + '/pathway/' + pathwayName + '_geneID_list'
    
    debugOutput = 'Getting gene ID list for pathway ' + organismAbbreviation + pathwayName + ' from '
        
    if File.doesFileExist(fileName):
        
        if settings.verbosity > 1:
            print(debugOutput + 'disk.')
        return File.readSetFromFileAtOnce(fileName)
    
    else:
        if settings.verbosity > 1:
            print(debugOutput + 'calculation.')
        return None


def setPathwayGeneIDs(organismAbbreviation: 'eco', pathwayName: '00260', geneIDs: Set[str]):
    """
    Save all gene ID strings in an organism's pathway.
    
    Parameters
    ----------
    organismAbbreviation : str
        The organism for which to retrieve the pathway.
    pathwayName : str
        The code of the pathway, e.g. '00260'.
    geneIDs : Set[str]
        Gene ID strings of the specified organism-specific pathway.
    """
    fileName = 'organism/' + organismAbbreviation + '/pathway/' + pathwayName + '_geneID_list'
    geneIDListString = '\n'.join(geneIDs)
    
    File.writeToFile(geneIDListString, fileName)
    

def getOrganismList() -> List[str]:
    """
    Get list of all organisms known to KEGG.
    
    Returns
    -------
    List[str]
        All organism descriptions known to KEGG.
    
    Raises
    ------
    URLError
        If connection to KEGG fails.
    Returns the list of all known organisms from KEGG.
    """
    fileName = 'organism_list'
    
    debugOutput = 'Getting organism list from '
    
    if File.doesFileExist(fileName):
        
        if settings.verbosity > 1:
            print(debugOutput + 'disk.')
        organismList = File.readListFromFileAtOnce(fileName)
    
    else:
        if settings.verbosity > 1:
            print(debugOutput + 'download.')
        
        organismList = Download.downloadOrganismList()
        File.writeToFile(organismList, fileName)
        organismList = organismList.splitlines()

    return organismList


def getEnzymeEcNumbers(enzymeAbbreviation: 'MiaB') -> List[str]:
    """
    Get EC numbers of an enzyme for the enzyme's abbreviation.
    
    Also works for everything else in the description of an enzyme, not just the abbreviation.
    
    Parameters
    ----------
    enzymeAbbreviation : str
        Part of the enzymes description string.
    
    Returns
    -------
    List[str] or None
        All EC numbers, as strings, for a given enzyme, identified by its abbreviation, from KEGG. Or *None* if no EC numbers could be found.
    
    Raises
    ------
    URLError
        If connection to KEGG fails.
    """
    fileName = 'enzymes/' + enzymeAbbreviation
    
    debugOutput = 'Getting enzyme EC number list for' + enzymeAbbreviation + ' from '
    
    if File.doesFileExist(fileName):
        
        if settings.verbosity > 1:
            print(debugOutput + 'disk.')
        ecNumbers = File.readListFromFileAtOnce(fileName)
        
    else:
        if settings.verbosity > 1:
            print(debugOutput + 'download.')
        
        ecNumbers = Download.downloadEnzymeEcNumbers(enzymeAbbreviation)
        File.writeToFile(ecNumbers, fileName)
        ecNumbers = ecNumbers.splitlines()
    
    if len(ecNumbers) == 0 or (len(ecNumbers) == 1 and len(ecNumbers[0]) <= 2):
        return None
    
    return ecNumbers


def doesOrganismExist(organismAbbreviation: 'eco') -> bool:
    """
    Check whether an organism exists.
    
    Parameters
    ----------
    organismAbbreviation : str
        The abbreviation of the organism to check.
    
    Returns
    -------
    bool
        *True*, if something was downloaded, and thus the organism exists.
        *False*, if the download was empty (400 Bad Request), because this organism does not exist.
    
    Raises
    ------
    URLError
        If connection to KEGG fails.
    """
    folderName = 'organism/' + organismAbbreviation + '/'
    
    debugOutput = 'Getting organism folder ' + organismAbbreviation + ' from '
    
    if File.doesFolderExist(folderName):
        
        if settings.verbosity >= 2:
            print(debugOutput + 'disk.')
        return True            
    
    else:
        if settings.verbosity >= 2:
            print(debugOutput + 'download.')
        
        organismExists = Download.doesOrganismExistDownload(organismAbbreviation)
        
        if organismExists is True:
            
            File.createPath(folderName)
            return True
        
        else:
            
            return False
        
def _doesOrganismExistTuple(organismAbbreviation: 'eco') -> Tuple[str, bool]:
    if Parallelism.getShallCancelThreads() is True:
        raise concurrent.futures.CancelledError()
    else:
        return (organismAbbreviation, doesOrganismExist(organismAbbreviation))

def doesOrganismExistBulk(organismAbbreviations: List[str]) -> List[str]:
    """
    Check whether multiple organisms exist.
    
    This is done in parallel in a thread pool, see :attr:`FEV_KEGG.settings.downloadThreads`.
    
    Parameters
    ----------
    organismAbbreviations : List[str]
        The abbreviations of the organisms to check.
    
    Returns
    -------
    List[str]
        List of organism abbreviations, taken from `organismAbbreviations` for which :func:`doesOrganismExist` would return *True*.
    
    Raises
    ------
    URLError
        If connection to KEGG fails.
    """
    tqdmPosition = Parallelism.getTqdmPosition()
    threadPool = concurrent.futures.ThreadPoolExecutor(Parallelism.getNumberOfThreadsDownload())
    futures = []
    iterator = None
    
    try:
        for organismAbbreviation in organismAbbreviations:
            futures.append( threadPool.submit(_doesOrganismExistTuple, organismAbbreviation) )
        
        iterator = concurrent.futures.as_completed(futures)
        
        if settings.verbosity >= 1:
#             if settings.verbosity >= 2:
            print( 'Checking existance of ' + str(len(organismAbbreviations)) + ' organisms...' )
            iterator = tqdm.tqdm(iterator, total = len(organismAbbreviations), unit = ' organisms', position = tqdmPosition)
        
        existingOrganisms = []
    
        for future in iterator:
            
            doesExistTuple = future.result()
            organismAbbreviation, doesExist = doesExistTuple
            if doesExist is True:
                existingOrganisms.append(organismAbbreviation)
        
        threadPool.shutdown(wait = False)
        
        return existingOrganisms
    
    except KeyboardInterrupt: # only raised in main thread (once in each process!)
        
        Parallelism.keyboardInterruptHandler(threadPool=threadPool, threadPoolFutures=futures, terminateProcess=True)
        raise
    
    except BaseException:
        
        if Parallelism.isMainThread():
            Parallelism.keyboardInterruptHandler(threadPool=threadPool, threadPoolFutures=futures, silent=True)
        raise
        
    finally:
        
        if iterator is not None: iterator.close()

def getOrganismInfo(organismAbbreviation: 'eco', checkExpiration = False) -> str:
    """
    Get organism info.
    
    Parameters
    ----------
    organismAbbreviation : str
        The abbreviation of the organism.
    checkExpiration : bool, optional
        If *True*, check whether the last download of the organism info is older than :attr:`FEV_KEGG.settings.organismInfoExpiration`. If yes, download it again.
        This can be useful when relying upon a current database size for calculating E-values for a :class:`FEV_KEGG.KEGG.SSDB.Match`.
    
    Returns
    -------
    str
        Raw organism info.
    
    Raises
    ------
    ValueError
        If organism with `organismAbbreviation` does not exist.
    URLError
        If connection to KEGG fails.
    """
    fileName = 'organism/' + organismAbbreviation + '/' + 'info'
    
    debugOutput = 'Getting organism info for ' + organismAbbreviation + ' from '
    
    shallDownload = False
    
    if File.doesFileExist(fileName):
        
        if settings.verbosity >= 2:
            print(debugOutput + 'disk.')
        
        organismInfo = File.readStringFromFileAtOnce(fileName)
        
        # remove timestamp
        splitFirstLine = organismInfo.split(sep='\n', maxsplit=1)
        firstLine = splitFirstLine[0]
        organismInfo = splitFirstLine[1]
        
        if checkExpiration:
                
            # check if timestamp is too old
            currentTimestamp = int(time.time())
            lastTimestamp = int(firstLine)
            
            if abs(currentTimestamp - lastTimestamp) > settings.organismInfoExpiration:
                # organism info expired
                shallDownload = True
                if settings.verbosity >= 2:
                    print('Organism info expired. Getting from download again.')
    
    else:
        if settings.verbosity >= 2:
            print(debugOutput + 'download.')
        
        shallDownload = True
    
    
    if shallDownload:
        
        # download and save organism info
        organismInfo = Download.downloadOrganismInfo(organismAbbreviation)
        
        if organismInfo is None:
            raise ValueError('Organism with abbreviation ' + organismAbbreviation + ' does not exist!')
        
        # add timestamp
        currentTimestamp = int(time.time())
        organismInfoWriting = str(currentTimestamp) + '\n' + organismInfo
        
        File.writeToFile(organismInfoWriting, fileName)
    
    return organismInfo
        



def getOrthologsOnlyGeneID(geneID: GeneID, comparisonOrganism: 'Organism or str', eValue: float = settings.defaultEvalue) -> Set[GeneID]:
    """
    Get orthologs for a gene in a certain organism, without metadata.
    
    Parameters
    ----------
    geneID : GeneID
        Gene to use for searching orthologs.
    comparisonOrganism : Organism or str
        Organism to check for orthologs. May be an Organism object or an organism abbreviation string.
    eValue : float, optional
        Statistical expectation value (E-value), below which a sequence alignment is considered significant.
    
    Returns
    -------
    Set[GeneID]
        Set of orthologous genes, using `geneID` to search the genome of `comparisonOrganism`.
        Only matches with an E-value smaller or equal to `eValue` are returned.
        Matches are downloaded from KEGG SSDB.
    
    Raises
    ------
    ImpossiblyOrthologousError
        If `geneID` is from `comparisonOrganism`.
    ValueError
        If any organism does not exist.
    URLError
        If connection to KEGG fails.
    """
    if isinstance(comparisonOrganism, str):
        organismAbbreviation = comparisonOrganism
    else:
        organismAbbreviation = comparisonOrganism.nameAbbreviation
        
    return _filterHomologsBySignificance( _getHomologs(geneID, organismAbbreviation), eValue, onlyGeneID = True)

def getOrthologs(geneID: GeneID, comparisonOrganism: 'Organism or str', eValue: float = settings.defaultEvalue) -> SSDB.Matching:
    """
    Get orthologs for a gene in a certain organism, including metadata.
    
    Parameters
    ----------
    geneID : GeneID
        Gene to use for searching orthologs.
    comparisonOrganism : Organism or str
        Organism to check for orthologs. May be an Organism object or an organism abbreviation string.
    eValue : float, optional
        Statistical expectation value (E-value), below which a sequence alignment is considered significant.
    
    Returns
    -------
    SSDB.Matching
        A matching of orthologs for gene `geneID`, searching the genome of `comparisonOrganism`.
        Only matches with an E-value smaller or equal to `eValue` are returned.
        Matches are downloaded from KEGG SSDB.
    
    Raises
    ------
    ImpossiblyOrthologousError
        If `geneID` is from `comparisonOrganism`.
    ValueError
        If any organism does not exist.
    URLError
        If connection to KEGG fails.
    """
    if isinstance(comparisonOrganism, str):
        organismAbbreviation = comparisonOrganism
    else:
        organismAbbreviation = comparisonOrganism.nameAbbreviation
        
    return _filterHomologsBySignificance( _getHomologs(geneID, organismAbbreviation), eValue, onlyGeneID = False)
    

def getParalogsOnlyGeneID(geneID: GeneID, eValue: float = settings.defaultEvalue) -> Set[GeneID]:
    """
    Get paralogs for a gene, without metadata.
    
    Parameters
    ----------
    geneID : GeneID
        Gene to use for searching paralogs.
    eValue : float, optional
        Statistical expectation value (E-value), below which a sequence alignment is considered significant.
    
    Returns
    -------
    Set[GeneID]
        Set of paralogous genes, using `geneID` to search the genome of the same organism.
        Only matches with an E-value smaller or equal to `eValue` are returned.
        Matches are downloaded from KEGG SSDB.
    
    Raises
    ------
    ValueError
        If any organism does not exist.
    URLError
        If connection to KEGG fails.
    """
           
    return _filterHomologsBySignificance( _getHomologs(geneID, comparisonOrganismString = None), eValue, onlyGeneID = True)

def getParalogs(geneID: GeneID, eValue: float = settings.defaultEvalue) -> SSDB.Matching:
    """
    Get paralogs for a gene, including metadata.
    
    Parameters
    ----------
    geneID : GeneID
        Gene to use for searching paralogs.
    eValue : float, optional
        Statistical expectation value (E-value), below which a sequence alignment is considered significant.
    
    Returns
    -------
    SSDB.Matching
        A matching of paralogous genes, using `geneID` to search the genome of the same organism.
        Only matches with an E-value smaller or equal to `eValue` are returned.
        Matches are downloaded from KEGG SSDB.
    
    Raises
    ------
    ValueError
        If any organism does not exist.
    URLError
        If connection to KEGG fails.
    """
           
    return _filterHomologsBySignificance( _getHomologs(geneID, comparisonOrganismString = None), eValue, onlyGeneID = False)

def _getHomologs(geneID: GeneID, comparisonOrganismString = None) -> SSDB.Matching:
    
    if comparisonOrganismString is None: # looking for paralogs
        fileName = 'organism/' + geneID.organismAbbreviation + '/paralogs/' + geneID.geneName
        debugOutput = 'Getting paralogs for ' + geneID.geneIDString + ' from '
    
    else: # looking for orthologs
        if geneID.organismAbbreviation == comparisonOrganismString:
            raise ImpossiblyOrthologousError('GeneID is from the same Organism I ought to search in. This can never be an ortholog!')
        fileName = 'organism/' + geneID.organismAbbreviation + '/orthologs/' + geneID.geneName + '/' + comparisonOrganismString
        debugOutput = 'Getting orthologs for ' + geneID.geneIDString + ' in ' + comparisonOrganismString + ' from '
    
    
    if File.doesFileExist(fileName):
        
        if settings.verbosity > 1:
            print(debugOutput + 'disk.')
    
    else:
        if settings.verbosity > 1:
            print(debugOutput + 'download.')
        
        # looking for paralog or ortholog?
        if comparisonOrganismString is None: # looking for paralogs
            
            preMatches = Download.downloadParalogs(geneID)
            databaseOrganism = geneID.organismAbbreviation
            
        else: # looking for orthologs
            
            preMatches = Download.downloadOrthologs(geneID, comparisonOrganismString)
            databaseOrganism = comparisonOrganismString
        
        # get length of query sequence
        queryGene = getGene(geneID.geneIDString)
        searchSequenceLength = queryGene.aaseqLength
        
        # add size of database
        organismInfo = getOrganismInfo(databaseOrganism, checkExpiration = True)
        organismGeneEntries = int( re.split('([0-9,]+) entries', organismInfo)[1].replace(',', '') )
        
        # add lengths of result sequences
        matches = []
        for preMatch in preMatches:
            
            # length
            matchedGene = getGene(preMatch.foundGeneIdString)
            sequenceLength = matchedGene.aaseqLength
            
            matches.append( SSDB.Match.fromPreMatch(preMatch, sequenceLength))

        timestamp = int( time.time() )
        
        # create Matching
        matching = SSDB.Matching(geneID, searchSequenceLength, databaseOrganism, organismGeneEntries, matches, timestamp)
        
        # save to file
        jsonpickle.set_encoder_options('simplejson', indent=4)
        File.writeToFile(jsonpickle.encode(matching), fileName)
        
    fileContent = File.readStringFromFileAtOnce(fileName)
    
    matching = jsonpickle.decode(fileContent)
    
    return matching

def _filterHomologsBySignificance(matching: SSDB.Matching, eValue, onlyGeneID = False):
    return _filterHomologsBySignificanceBulk({'0': matching}, eValue, onlyGeneID).get('0')


def getOrthologsBulk(geneIDs: Iterable[GeneID], comparisonOrganism: 'Iterable[Organism] or Iterable[str] or Organism or str', eValue: float = settings.defaultEvalue) -> Dict[GeneID, List[SSDB.Matching]]:
    """
    Get orthologs for genes in a certain organism in bulk, including metadata.
    
    This is done in parallel in a thread pool, see :attr:`FEV_KEGG.settings.downloadThreads`.
    
    Parameters
    ----------
    geneIDs : Iterable[GeneID]
        Genes to use for searching orthologs.
    comparisonOrganism : Iterable[Organism] or Organism or str
        Organism(s) to check for orthologs. May be an organism abbreviation string.
    eValue : float, optional
        Statistical expectation value (E-value), below which a sequence alignment is considered significant.
    
    Returns
    -------
    Dict[GeneID, List[SSDB.Matching]]
        A dictionary of a list of matchings of orthologous genes, using each gene ID from `geneIDs`, searching the genome of each `comparisonOrganism`, keyed by the used gene ID.
        Only matches with an E-value smaller or equal to `eValue` are returned.
        Matches are downloaded from KEGG SSDB.
    
    Raises
    ------
    ImpossiblyOrthologousError
        If any gene ID in `geneIDs` is from `comparisonOrganism`.
    ValueError
        If any organism does not exist.
    URLError
        If connection to KEGG fails.
    """
    if isinstance(comparisonOrganism, str):
        organismAbbreviation = comparisonOrganism
    elif isinstance(comparisonOrganism, Iterable):
        organismAbbreviation = [x if isinstance(x, str) else x.nameAbbreviation for x in comparisonOrganism]
    else:
        organismAbbreviation = comparisonOrganism.nameAbbreviation
    
    orthologousMatchingsDict = _getHomologsBulk(geneIDs, organismAbbreviation)
    
    result = dict()
    
    for geneID, matchingList in orthologousMatchingsDict.items():
        for matching in matchingList:
            tmpDict = dict()
            tmpDict[geneID] = matching
            filteredMatching = _filterHomologsBySignificanceBulk(tmpDict, eValue, onlyGeneID = False)
            if len(filteredMatching[geneID].matches) > 0: # some match survived the E-value filter
                resultMatchingList = result.get(geneID)
                if resultMatchingList is None:
                    result[geneID] = []
                result[geneID].append(filteredMatching[geneID])
    
    return result
        

def getParalogsBulk(geneIDs: Iterable[GeneID], eValue: float = settings.defaultEvalue) -> Dict[GeneID, SSDB.Matching]:
    """
    Get paralogs for genes in bulk, including metadata.
    
    This is done in parallel in a thread pool, see :attr:`FEV_KEGG.settings.downloadThreads`.
    
    Parameters
    ----------
    geneIDs : Iterable[GeneID]
        Genes to use for searching paralogs.
    eValue : float, optional
        Statistical expectation value (E-value), below which a sequence alignment is considered significant.
    
    Returns
    -------
    Dict[GeneID, SSDB.Matching]
        A dictionary of matchings of paralogous genes, using each gene ID from `geneIDs` to search the genome of the same organism, keyed by the used gene ID.
        Only matches with an E-value smaller or equal to `eValue` are returned.
        Matches are downloaded from KEGG SSDB.
    
    Raises
    ------
    ValueError
        If any organism does not exist.
    URLError
        If connection to KEGG fails.
    """
    return _filterHomologsBySignificanceBulk( _getHomologsBulk(geneIDs, comparisonOrganismString = None), eValue, onlyGeneID = False)

def _getHomologsBulk(geneIDs: Iterable[GeneID], comparisonOrganismString = None): # -> Dict[GeneID, List[SSDB.Matching]] (multiple organisms) or Dict[GeneID, SSDB.Match] (single organism string, or paralog)
    
    if comparisonOrganismString is None:
        isParalog = True
    else:
        isParalog = False
    
    # turn a single comparison organism into a list
    if not isinstance(comparisonOrganismString, list):
        comparisonOrganismString = [comparisonOrganismString]
    
    # split list into matchings on disk and matchings not downloaded yet
    matchingsOnDisk = []
    matchingsToDownload = []
    
    for geneID in geneIDs:
        
        for comparisonOrganism in comparisonOrganismString:
        
            if isParalog: # looking for paralogs
                fileName = 'organism/' + geneID.organismAbbreviation + '/paralogs/' + geneID.geneName
                debugOutput = 'Getting paralogs for ' + geneID.geneIDString + ' from '
            
            else: # looking for orthologs                
                if geneID.organismAbbreviation == comparisonOrganism:
                    raise ImpossiblyOrthologousError('GeneID is from the same Organism I ought to search in. This can never be an ortholog!')
                fileName = 'organism/' + geneID.organismAbbreviation + '/orthologs/' + geneID.geneName + '/' + comparisonOrganism
                debugOutput = 'Getting orthologs for ' + geneID.geneIDString + ' in ' + comparisonOrganism + ' from '
            
            
            if File.doesFileExist(fileName):
                
                if settings.verbosity > 1:
                    print(debugOutput + 'disk.')
                    
                matchingsOnDisk.append((geneID, comparisonOrganism))
            
            else:
                if settings.verbosity > 1:
                    print(debugOutput + 'download.')
                
                matchingsToDownload.append((geneID, comparisonOrganism))
    
    
    # get matchings from disk
    matchings = dict()
    for geneID, comparisonOrganism in matchingsOnDisk:
        
        if isParalog: # looking for paralogs
            fileName = 'organism/' + geneID.organismAbbreviation + '/paralogs/' + geneID.geneName
        
        else: # looking for orthologs
            fileName = 'organism/' + geneID.organismAbbreviation + '/orthologs/' + geneID.geneName + '/' + comparisonOrganism

        fileContent = File.readStringFromFileAtOnce(fileName)
        matching = jsonpickle.decode(fileContent, classes=SSDB.Matching)
        
        if isParalog: # looking for paralogs
            matchings[geneID] = matching
        
        else: # looking for orthologs   
            matchingList = matchings.get(geneID)
            if matchingList is None:
                matchings[geneID] = []
            matchings[geneID].append(matching)
    
    # download matchings in bulk
    if len( matchingsToDownload ) > 0:
        
        tqdmPosition = Parallelism.getTqdmPosition()
        threadPool = concurrent.futures.ThreadPoolExecutor(Parallelism.getNumberOfThreadsDownload())
        futures = []
        iterator = None
        
        try:
            # query KEGG SSDB in parallel
            
            for geneID, comparisonOrganism in matchingsToDownload:
                futures.append( threadPool.submit(_getHomologsBulkHelper, geneID, comparisonOrganism) )
            
            iterator = concurrent.futures.as_completed(futures)
            
            if settings.verbosity >= 1:    
                if settings.verbosity >= 2:
                    print( 'Downloading ' + str(len(matchingsToDownload)) + ' matchings...' )
                iterator = tqdm.tqdm(iterator, total = len(matchingsToDownload), unit = ' matchings', position = tqdmPosition)
            
            for future in iterator:
                matching = future.result()
                
                if isParalog:
                    matchings[matching.queryGeneID] = matching
                else:
                    matchingList = matchings.get(matching.queryGeneID)
                    if matchingList is None:
                        matchings[matching.queryGeneID] = []
                    matchings[matching.queryGeneID].append(matching)
            
            threadPool.shutdown(wait = False)
            
        except KeyboardInterrupt: # only raised in main thread (once in each process!)
        
            Parallelism.keyboardInterruptHandler(threadPool=threadPool, threadPoolFutures=futures, terminateProcess=True)
            raise
        
        except BaseException:
            
            if Parallelism.isMainThread():
                Parallelism.keyboardInterruptHandler(threadPool=threadPool, threadPoolFutures=futures, silent=True)
            raise
        
        finally:
            
            if iterator is not None: iterator.close()
    
    return matchings

def _getHomologsBulkHelper(geneID, comparisonOrganismString) -> SSDB.Matching:
    
    if Parallelism.getShallCancelThreads() is True:
        raise concurrent.futures.CancelledError()
    
    preMatches = _downloadHomolog(geneID, comparisonOrganismString)
    
    if comparisonOrganismString is None: # looking for paralogs
        fileName = 'organism/' + geneID.organismAbbreviation + '/paralogs/' + geneID.geneName
        databaseOrganism = geneID.organismAbbreviation
        
    else: # looking for orthologs
        fileName = 'organism/' + geneID.organismAbbreviation + '/orthologs/' + geneID.geneName + '/' + comparisonOrganismString
        databaseOrganism = comparisonOrganismString
    
    if Parallelism.getShallCancelThreads() is True:
        raise concurrent.futures.CancelledError()
    
    # get length of query sequence
    queryGene = getGene(geneID.geneIDString)
    searchSequenceLength = queryGene.aaseqLength
    
    if Parallelism.getShallCancelThreads() is True:
        raise concurrent.futures.CancelledError()
    
    # add size of database
    organismInfo = getOrganismInfo(databaseOrganism, checkExpiration = True)
    organismGeneEntries = int( re.split('([0-9,]+) entries', organismInfo)[1].replace(',', '') )
    
    # add lengths of result sequences
    matches = []
    for preMatch in preMatches:
        
        if Parallelism.getShallCancelThreads() is True:
            raise concurrent.futures.CancelledError()
        
        # length
        matchedGene = getGene(preMatch.foundGeneIdString)
        sequenceLength = matchedGene.aaseqLength
        
        matches.append( SSDB.Match.fromPreMatch(preMatch, sequenceLength))

    timestamp = int( time.time() )
    
    # create Matching
    matching = SSDB.Matching(geneID, searchSequenceLength, databaseOrganism, organismGeneEntries, matches, timestamp)
    
    # save to file
    jsonpickle.set_encoder_options('simplejson', indent=4)
    File.writeToFile(jsonpickle.encode(matching), fileName)
    
    return matching

def _downloadHomolog(geneID, comparisonOrganismString):
    try:
        if comparisonOrganismString is None: #paralog
            return Download.downloadParalogs(geneID)
        else: #ortholog
            return Download.downloadOrthologs(geneID, comparisonOrganismString)
    except urllib.error.HTTPError as exception:
        if isinstance(exception, urllib.error.HTTPError) and exception.code == 404:
            return None
        else:
            raise
    
    

def _filterHomologsBySignificanceBulk(matchings: Dict[GeneID, SSDB.Matching], eValue, onlyGeneID = False):
    """
    Filter sequence alignments by statistical significance.
    
    Parameters
    ----------
    matchings : Dict[GeneID, SSDB.Matching]
        Dictionary of a homolog matching, including homologous gene IDs and statistical data, keyed by the gene ID used to search for homologs.
    eValue : float
        Statistical expectation value (E-value), below which a sequence alignment is considered significant.
    onlyGeneID : bool, optional
        If *True*, return only the set of homologous gene IDs, not the whole matching including statistical data.
    
    Returns
    -------
    Dict[GeneID, SSDB.Matching] or Dict[GeneID, Set[GeneID]]
        `matchings` reduced to the significant sequence alignments, with an E-value below `eValue`.
        If `onlyGeneID` == *True*, `matchings` is further reduced to only contain the homologous gene IDs, not the complete matching.
        
    """
    result = dict()
    
    for geneID, matching in matchings.items():
        
        if onlyGeneID is True:
            # filter non-significant genes
            geneIDs = set()
            
            for match in matching.matches:
                if match.eValue <= eValue:
                    geneIDs.add( match.foundGeneID )
                
            resultPart = geneIDs
        
        else:
            # filter non-significant genes
            validMatches = []
            
            for match in matching.matches:
                if match.eValue <= eValue:
                    validMatches.append(match)
            matching.matches = validMatches
            
            resultPart = matching
        
        result[geneID] = resultPart
    
    return result
        
    
    
    

def getTaxonomyNCBI() -> List[str]:
    """
    Get NCBI taxonomy from KEGG BRITE.
    
    Returns
    -------
    List[str]
        Taxonomy of organisms in KEGG, in special text format, following the NCBI scheme, line by line.
    
    Raises
    ------
    URLError
        If connection to KEGG fails.
    """
    fileName = 'taxonomy/NCBI_raw'
    debugOutput = 'Getting NCBI taxonomy from '
    return _getTaxonomy(fileName, debugOutput, True)


def getTaxonomyKEGG() -> List[str]:
    """
    Get KEGG taxonomy from KEGG BRITE.
    
    Returns
    -------
    List[str]
        Taxonomy of organisms in KEGG, in special text format, following KEGG's own scheme, line by line.
    
    Raises
    ------
    URLError
        If connection to KEGG fails.
    """
    fileName = 'taxonomy/KEGG_raw'
    debugOutput = 'Getting KEGG taxonomy from '
    return _getTaxonomy(fileName, debugOutput, False)
    

def _getTaxonomy(fileName, debugOutput, isNCBI) -> List[str]:
    if File.doesFileExist(fileName):
        
        if settings.verbosity > 1:
            print(debugOutput + 'disk.')
    
    else:
        if settings.verbosity > 1:
            print(debugOutput + 'download.')
        
        if isNCBI:
            organismList = Download.downloadTaxonomyNCBI()
        else:
            organismList = Download.downloadTaxonomyKEGG()
        File.writeToFile(organismList, fileName)
        
    fileContent = File.readListFromFileAtOnce(fileName)

    return fileContent
    