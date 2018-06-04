"""
This module represents the model of all intermediate stages of matches acquired via KEGG SSDB database, partly in conjunction with KEGG GENE.

The methods to actually perform the retrieval are not part of this module. See :mod:`FEV_KEGG.KEGG.Database` and :mod:`FEV_KEGG.KEGG.Download` for these.
"""
import jsonpickle
from typing import Iterable

from FEV_KEGG.Graph.Elements import GeneID
from FEV_KEGG.Statistics import SequenceComparison


class PreMatch(object):
    def __init__(self, foundGeneIdString, swScore, bitScore, identity, overlap):
        """
        A sequence comparison match between two distinct genes, without calculated attributes.
        
        The parameters can be retrieved via `KEGG SSDB <http://www.kegg.jp/ssdb-bin/ssdb_ortholog_view?org_gene=syn:sll1450&org=syn>`_ [1]_.
        
        Parameters
        ----------
        foundGeneIdString : str
            ID of the gene found by SSDB to be a paralog/ortholog, e.g. syn:sll1452.
        swScore : int
            Smith-Waterman score of the match between the gene which was searched for and the found gene specified by `foundGeneIdString`.
        bitScore : float
            Length-normalised `swScore` scaled to bits.
        identity : float
            Percentage of equal amino acids, without substitution.
        overlap : int
            Number of amino acids the found gene sequence overlaps with the gene which was searched for. Maximum is the length of the searched-for gene.
        
        Attributes
        ----------
        self.foundGeneIdString : str
        self.swScore : int
        self.bitScore : float
        self.identity : float
        self.overlap : int
        
        See Also
        --------
        FEV_KEGG.KEGG.Database.getOrthologs : Function to retrieve PreMatches from KEGG SSDB.
        
        References
        __________
        .. [1] Sato et al. (2001), "SSDB: Sequence Similarity Database in KEGG", `<https://www.researchgate.net/publication/254718427_SSDB_Sequence_Similarity_Database_in_KEGG>`_
        """
        self.foundGeneIdString = foundGeneIdString
        self.swScore = swScore
        self.bitScore = bitScore
        self.identity = identity
        self.overlap = overlap

class Match(PreMatch):
    def __init__(self, foundGeneIdString, swScore, bitScore, identity, overlap, length):
        """
        A sequence comparison match between two distinct genes, including calculated attributes.
        
        During creation, `foundGeneIdString` is used to create a GeneID object, saved as `foundGeneID`
        
        Parameters
        __________
        length : int
            Length in amino acids of the found gene. Derived from downloading the gene's information file.
        
        Attributes
        ----------
        self.foundGeneIdString : str
        self.swScore : int
        self.bitScore : float
        self.identity : float
        self.overlap : int
        self.length : int
        self.foundGeneID : :class:`FEV_KEGG.Graph.Elements.GeneID`
        
        See Also
        ________
        PreMatch : Handles all other parameters.
        """
        super().__init__(foundGeneIdString, swScore, bitScore, identity, overlap)
        if length <= 0:
            raise ValueError("Matched sequence can not be of length <= 0.")
        self.length = length
        self.foundGeneID = GeneID(foundGeneIdString)
    
    @classmethod
    def fromPreMatch(cls, preMatch: PreMatch, length):
        """
        Cast a PreMatch object to an object of this class.
        
        During casting, `foundGeneIdString` is used to create a GeneID object, stored as `foundGeneID`. Also, `save` is stored.
        
        Parameters
        __________
        preMatch : PreMatch
            The object to cast into this class' type.
        length : int
            Length in amino acids of the found gene. Derived from downloading the gene's information file.
        
        Note
        ____
        This class method simply casts the PreMatch object, instead of going through creating a new Match object.
        This helps performance and does not significantly impact complexity.
        """
        preMatch.__class__ = cls
        if length <= 0:
            raise ValueError("Matched sequence can not be of length <= 0.")
        preMatch.length = length
        preMatch.foundGeneID = GeneID(preMatch.foundGeneIdString)
        return preMatch

class TransientMatch(Match):
    def __init__(self, foundGeneIdString, swScore, bitScore, identity, overlap, length, eValue):
        """
        A sequence comparison match between two distinct genes, only valid at a certain point in time.
        
        This match is transient, because it is only valid for a certain point in time, because `eValue` changes with the size of the database.
        
        Parameters
        __________
        self.foundGeneIdString : str
        self.swScore : int
        self.bitScore : float
        self.identity : float
        self.overlap : int
        self.length : int
        self.foundGeneID : :class:`FEV_KEGG.Graph.Elements.GeneID`
        eValue : float
            Statistical expectation value for the chance of yielding a match of the same score by pure randomness alone.
        
        Attributes
        ----------
        self.eValue : float
        
        See Also
        ________
        Match : Handles all other parameters.
        """
        super().__init__(foundGeneIdString, swScore, bitScore, identity, overlap, length)
        self.eValue = eValue
    
    @classmethod
    def fromMatch(cls, match: Match, eValue):
        """
        Cast a Match object to an object of this class.
        
        During casting, `eValue` is stored.
        
        Note
        ____
        This class method simply casts the Match object, instead of going through creating a new TransientMatch object.
        This helps performance and does not significantly impact complexity.
        """
        match.__class__ = cls
        match.eValue = eValue
        return match
    

class Matching(object):    
    def __init__(self, queryGeneID: GeneID, queryLength, databaseOrganism, databaseSize, matches: Iterable[Match], timestamp):
        """
        Result of a search for orthologs or paralogs in SSDB, concerning a single target organism.
        
        The E-values for the resulting Matches depend on database size and are therefore only valid at the specified timestamp.
        
        Parameters
        __________
        queryGeneID : GeneID
            ID of the gene to search homologs for, e.g. "syn:sll1450".
        queryLength : int
            Length of the gene product in amino acids.
        databaseOrganism : str
            Organism to search in to find homologs for `queryGeneID`, e.g. "eco".
        databaseSize : int
            Number of genes known to belong to the `databaseOrganism`. This can be queried by `<http://rest.kegg.jp/info/eco>`_, currently yielding "4,498 entries".
        matches : Iterable[Match]
            Iterable of Match objects, one for each match found during the matching.
        timestamp : int
            When was the query run? As UNIX epoch timestamp in seconds.
        
        Attributes
        ----------
        self.queryGeneID : :class:`FEV_KEGG.Graph.Elements.GeneID`
        self.queryLength : int
        
        self.databaseOrganism : str
        self.databaseSize : int
        
        self.timestamp : int
        
        self.matches : List[:class:`TransientMatch`]
        """
        self.queryGeneID = queryGeneID
        self.queryLength = queryLength
        
        self.databaseOrganism = databaseOrganism
        self.databaseSize = databaseSize
        
        self.timestamp = timestamp
        
        transientMatches = []
        
        for match in matches:
            
            eValue = SequenceComparison.getExpectationValue(match.bitScore, queryLength, match.length, databaseSize)
            transientMatches.append( TransientMatch.fromMatch(match, eValue) )
        
        self.matches = transientMatches
        
    def __str__(self):
        """
        Encodes object to "unpickable" JSON.
        
        Returns
        -------
        str
            Object in JSON format, including information to "unpickle" it back into an object.
        """
        jsonpickle.set_encoder_options('simplejson', indent=4)
        return jsonpickle.encode(self)