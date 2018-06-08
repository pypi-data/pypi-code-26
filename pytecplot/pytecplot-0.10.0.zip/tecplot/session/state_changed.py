import collections
import ctypes

from ..tecutil import _tecutil, _tecutil_connector
from .. import tecutil
from ..constant import StateChange
from ..exception import TecplotLogicError


@tecutil.lock()
def _state_changed(what, uniqueid=None, dataset=None, zones=None,
                  variables=None, index=None):
    sv = tecutil.sv
    allocd = []
    try:
        with tecutil.ArgList() as arglist:
            arglist[sv.STATECHANGE] = what
            if uniqueid is not None:
                arglist[sv.UNIQUEID] = ctypes.c_size_t(uniqueid)
            if dataset is not None:
                arglist[sv.DATASETUNIQUEID] = ctypes.c_size_t(dataset)
            if zones:
                zonelist = tecutil.IndexSet(*zones)
                allocd.append(zonelist)
                arglist[sv.ZONELIST] = zonelist
            if variables:
                varlist = tecutil.IndexSet(*variables)
                allocd.append(varlist)
                arglist[sv.VARLIST] = varlist
            if index is not None:
                arglist[sv.INDEX] = index + 1
            _tecutil.StateChangedX(arglist)
    finally:
        for a in allocd:
            a.dealloc()


def zone_added(zone):

    sc_type = StateChange.ZonesAdded
    dataset = zone.dataset.uid
    zone = set([zone.index])

    if _tecutil_connector.suspended:
        sc = _tecutil_connector.state_changes
        if sc_type not in sc:
            sc[sc_type] = {dataset: zone}
        elif dataset not in sc[sc_type]:
            sc[sc_type][dataset] = zone
        else:
            sc[sc_type][dataset] |= zone
        for sc_type in [StateChange.VarsAltered, StateChange.NodeMapsAltered]:
            try:
                del sc[sc_type][dataset][zone]
                if len(sc[sc_type]) == 1:
                    del sc[sc_type]
            except KeyError:
                pass
    else:
        _state_changed(sc_type, dataset=dataset, zones=zone)


def data_altered(zone, variable, index=None):
    if __debug__:
        if zone.dataset != variable.dataset:
            msg = 'Zone and variable are not part of the same dataset.'
            raise TecplotLogicError(msg)

    sc_type = StateChange.VarsAltered
    dataset = zone.dataset.uid
    zone = zone.index
    variable = variable.index

    if _tecutil_connector.suspended:
        index = set([index])
        sc = _tecutil_connector.state_changes
        try:
            if zone not in sc[StateChange.ZonesAdded][dataset]:
                raise KeyError
        except KeyError:
            if sc_type not in sc:
                sc[sc_type] = {dataset: {zone: {variable: index}}}
            elif dataset not in sc[sc_type]:
                sc[sc_type][dataset] = {zone: {variable: index}}
            elif zone not in sc[sc_type][dataset]:
                sc[sc_type][dataset][zone] = {variable: index}
            elif variable not in sc[sc_type][dataset][zone]:
                sc[sc_type][dataset][zone][variable] = index
            elif sc[sc_type][dataset][zone][variable] != set([None]):
                if index == set([None]):
                    sc[sc_type][dataset][zone][variable] = set([None])
                else:
                    sc[sc_type][dataset][zone][variable] |= index
    else:
        _state_changed(sc_type, dataset=dataset, zones=[zone],
                       variables=[variable], index=index)


def connectivity_altered(zone):

    sc_type = StateChange.NodeMapsAltered
    dataset = zone.dataset.uid
    zone = set([zone.index])

    if _tecutil_connector.suspended:
        sc = _tecutil_connector.state_changes
        try:
            if zone.isdisjoint(sc[StateChange.ZonesAdded][dataset]):
                raise KeyError
        except KeyError:
            if sc_type not in sc:
                sc[sc_type] = {dataset: zone}
            elif dataset not in sv[sc_type]:
                sv[sc_type][dataset] = zone
            else:
                sv[sc_type][dataset] |= zone
    else:
        _state_changed(sc_type, dataset=dataset, zones=zone)


def _emit_state_changes(state_changes):
    for sc_type, info in state_changes.items():
        if sc_type in (StateChange.ZonesAdded, StateChange.NodeMapsAltered):
            for dataset, zones in info.items():
                _state_changed(sc_type, dataset=dataset, zones=zones)
        elif sc_type == StateChange.VarsAltered:
            for dataset in info:
                for zone in info[dataset]:
                    for variable in info[dataset][zone]:
                        for index in info[dataset][zone][variable]:
                            _state_changed(sc_type, dataset=dataset,
                                           zones=[zone], variables=[variable],
                                           index=index)

'''
class StateChange(Enum):
    VarsAltered               =  0
    VarsAdded                 =  1
    ZonesDeleted              =  2
    ZonesAdded                =  3
    NodeMapsAltered           =  4
    FrameDeleted              =  5
    #NewTopFrame              =  6  /* deprecated: use NewActiveFrame and/or FrameOrderChange */
    Style                     =  7
    DataSetReset              =  8
    NewLayout                 =  9
    #CompleteReset            = 10  /* deprecated: no longer broadcast */
    LineMapAssignment         = 11
    ContourLevels             = 12
    ModalDialogLaunch         = 13
    ModalDialogDismiss        = 14
    QuitTecplot               = 15
    ZoneName                  = 16
    VarName                   = 17
    LineMapName               = 18
    LineMapAddDeleteOrReorder = 19
    View                      = 20
    ColorMap                  = 21
    ContourVar                = 22
    Streamtrace               = 23
    NewAxisVariables          = 24
    MouseModeUpdate           = 25
    PickListCleared           = 26
    PickListGroupSelect       = 27
    PickListSingleSelect      = 28
    PickListStyle             = 29
    JournalReset              = 30
    UnsuspendInterface        = 31
    SuspendInterface          = 32
    DataSetLockOn             = 33
    DataSetLockOff            = 34
    Text                      = 35
    Geom                      = 36
    DataSetTitle              = 37
    DrawingInterrupted        = 38
    PrintPreviewLaunch        = 39
    PrintPreviewDismiss       = 40
    AuxDataAdded              = 41
    AuxDataDeleted            = 42
    AuxDataAltered            = 43
    VarsDeleted               = 44
    TecplotIsInitialized      = 45
    ImageExported             = 46
    VariableLockOn            = 47
    VariableLockOff           = 48
    PageDeleted               = 49
    NewTopPage                = 50
    NewActiveFrame            = 51
    FrameOrderChanged         = 52
    NewUndoState              = 53
    MacroFunctionListChanged  = 54
    AnimationStart            = 55
    AnimationEnd              = 56
    MacroRecordingStarted     = 57
    MacroRecordingEnded       = 58
    MacroRecordingCanceled    = 59
    ZoneSolutionTimeAltered   = 60
    LayoutAssociation         = 61
    CopyView                  = 62
    ColorMapDeleted           = 63
    OpenLayout                = 64
    MacroLoaded               = 65
    PerformingUndoBegin       = 66
    PerformingUndoEnd         = 67
'''
