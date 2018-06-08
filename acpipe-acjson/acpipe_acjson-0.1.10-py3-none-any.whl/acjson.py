# python stadard library
import copy
import csv
import importlib
import json
import re
import sys

# const
ts_ABC = (
    None, "A", "B", "C", "D", "E", "F", "G", "H", "I",
    "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S",
    "T", "U", "V", "W", "X", "Y", "Z")

ts_ACAXIS = (
    "sample",
    "perturbation",
    "endpoint")

ts_NOTCOOR = (
    "acid",
    "runid",
    "runtype",
    "log",
    "welllayout",
    "spotlayout")

ts_COORSYS = (
    "ixi",
    "iixii",
    "sxi",
    "iWell",
    "iSpot"
)

d_WELL = {
    "sample" : None,
    "perturbation" : None,
    "endpoint": None,
    "sxi" : None,
    "ixi" : None,
    "iixii": None,
    "iWell": None,
    "iSpot": None,
}

d_RECORD = {
    "conc": None ,
    "concUnit": None,
    "cultType": None,
    "timeBegin": None,
    "timeEnd": None,
    "timeUnit": None}

d_RECORDLONG = {
    "manufacture": None,
    "catalogNu": None,
    "batch": None,
    "conc": None ,
    "concUnit": None,
    "cultType": None,
    "timeBegin": None,
    "timeEnd": None,
    "timeUnit": None}

# record addons
d_SET ={
    "recordSet": None}

d_EXTERNALID ={
    "externalId": None}

d_SAMPLE = {
    "passageOrigin": None,
    "passageUsed": None}

d_MICROSCOPE = {
    "micChannel": None,  # microscopy channel
    "wavelengthNm": None}  # nominal_excitation

d_PRIMANTIBODY = {
    "hostOrganism": None,
    "isotype": None}

d_SECANTIBODY = {
    "hostOrganism": None,
    "targetOrganism": None,
    "isotype": None,
    "dye": None}

# leafs
es_LEAF = {
    "acid",
    "runtype",
    "runid",
    "log",
    "welllayout",
    "spotlayout",
    "sxi",
    "ixi",
    "iixii",
    "iWell",
    "iSpot",
    "recordSet",
    "manufacture",
    "catalogNu",
    "batch",
    "conc",
    "concUnit",
    "timeBegin",
    "timeEnd",
    "timeUnit",
    "cultType",
    "externalId",
    "passageOrigin",
    "passageUsed",
    "micChannel",
    "wavelengthNm",
    "hostOrganism",
    "targetOrganism",
    "isotype"}

es_DATAFRAMELEAF = copy.deepcopy(es_LEAF)
es_DATAFRAMELEAF.discard("acid")
es_DATAFRAMELEAF.discard("runtype")
es_DATAFRAMELEAF.discard("log")
es_DATAFRAMELEAF.add("runCollapsed")
es_DATAFRAMELEAF.add("axisCollapsed")
es_DATAFRAMELEAF.add("recordSetCollapsed")
es_DATAFRAMELEAF.discard("manufacture")
es_DATAFRAMELEAF.discard("catalogNu")
es_DATAFRAMELEAF.discard("batch")
es_DATAFRAMELEAF.add("longRecord")

# 96 well to 384 well
dii_96A1 = {
    1:1, 2:3, 3:5, 4:7, 5:9, 6:11, 7:13, 8:15, 9:17, 10:19, 11:21, 12:23,
    13:49, 14:51, 15:53, 16:55, 17:57, 18:59, 19:61, 20:63, 21:65, 22:67, 23:69, 24:71,
    25:97, 26:99, 27:101, 28:103, 29:105, 30:107, 31:109, 32:111, 33:113, 34:115, 35:117, 36:119,
    37:145, 38:147, 39:149, 40:151, 41:153, 42:155, 43:157, 44:159, 45:161, 46:163, 47:165, 48:167,
    49:193, 50:195, 51:197, 52:199, 53:201, 54:203, 55:205, 56:207, 57:209, 58:211, 59:213, 60:215,
    61:241, 62:243, 63:245, 64:247, 65:249, 66:251, 67:253, 68:255, 69:257, 70:259, 71:261, 72:263,
    73:289, 74:291, 75:293, 76:295, 77:297, 78:299, 79:301, 80:303, 81:305, 82:307, 83:309, 84:311,
    85:337, 86:339, 87:341, 88:343, 89:345, 90:347, 91:349, 92:351, 93:353, 94:355, 95:357, 96:359,
}

dii_96A2 = {
    1:2, 2:4, 3:6, 4:8, 5:10, 6:12, 7:14, 8:16, 9:18, 10:20, 11:22, 12:24,
    13:50, 14:52, 15:54, 16:56, 17:58, 18:60, 19:62, 20:64, 21:66, 22:68, 23:70, 24:72,
    25:98, 26:100, 27:102, 28:104, 29:106, 30:108, 31:110, 32:112, 33:114, 34:116, 35:118, 36:120,
    37:146, 38:148, 39:150, 40:152, 41:154, 42:156, 43:158, 44:160, 45:162, 46:164, 47:166, 48:168,
    49:194, 50:196, 51:198, 52:200, 53:202, 54:204, 55:206, 56:208, 57:210, 58:212, 59:214, 60:216,
    61:242, 62:244, 63:246, 64:248, 65:250, 66:252, 67:254, 68:256, 69:258, 70:260, 71:262, 72:264,
    73:290, 74:292, 75:294, 76:296, 77:298, 78:300, 79:302, 80:304, 81:306, 82:308, 83:310, 84:312,
    85:338, 86:340, 87:342, 88:344, 89:346, 90:348, 91:350, 92:352, 93:354, 94:356, 95:358, 96:360,
}

dii_96B1 = {
    1:25, 2:27, 3:29, 4:31, 5:33, 6:35, 7:37, 8:39, 9:41, 10:43, 11:45, 12:47,
    13:73, 14:75, 15:77, 16:79, 17:81, 18:83, 19:85, 20:87, 21:89, 22:91, 23:93, 24:95,
    25:121, 26:123, 27:125, 28:127, 29:129, 30:131, 31:133, 32:135, 33:137, 34:139, 35:141, 36:143,
    37:169, 38:171, 39:173, 40:175, 41:177, 42:179, 43:181, 44:183, 45:185, 46:187, 47:189, 48:191,
    49:217, 50:219, 51:221, 52:223, 53:225, 54:227, 55:229, 56:231, 57:233, 58:235, 59:237, 60:239,
    61:265, 62:267, 63:269, 64:271, 65:273, 66:275, 67:277, 68:279, 69:281, 70:283, 71:285, 72:287,
    73:313, 74:315, 75:317, 76:319, 77:321, 78:323, 79:325, 80:327, 81:329, 82:331, 83:333, 84:335,
    85:361, 86:363, 87:365, 88:367, 89:369, 90:371, 91:373, 92:375, 93:377, 94:379, 95:381, 96:383,
}

dii_96B2 = {
    1:26, 2:28, 3:30, 4:32, 5:34, 6:36, 7:38, 8:40, 9:42, 10:44, 11:46, 12:48,
    13:74, 14:76, 15:78, 16:80, 17:82, 18:84, 19:86, 20:88, 21:90, 22:92, 23:94, 24:96,
    25:122, 26:124, 27:126, 28:128, 29:130, 30:132, 31:134, 32:136, 33:138, 34:140, 35:142, 36:144,
    37:170, 38:172, 39:174, 40:176, 41:178, 42:180, 43:182, 44:184, 45:186, 46:188, 47:190, 48:192,
    49:218, 50:220, 51:222, 52:224, 53:226, 54:228, 55:230, 56:232, 57:234, 58:236, 59:238, 60:240,
    61:266, 62:268, 63:270, 64:272, 65:274, 66:276, 67:278, 68:280, 69:282, 70:284, 71:286, 72:288,
    73:314, 74:316, 75:318, 76:320, 77:322, 78:324, 79:326, 80:328, 81:330, 82:332, 83:334, 84:336,
    85:362, 86:364, 87:366, 88:368, 89:370, 90:372, 91:374, 92:376, 93:378, 94:380, 95:382, 96:384,
}

# error handling
with open(
        "{}/error.json".format(
            list(importlib.util.find_spec(
                "acpipe_acjson"
            ).submodule_search_locations)[0]
        )) as f_json:  # type: ignore
    ds_error = json.load(f_json)


# function
def retype(o_value):
    """
    input:
        o_value: value in any built-in data type.

    output:
        o_value: value transfomed into most likely
        best possible built-in data type.

    description:
      transform string into best possible other data type.
    """
    if not((type(o_value) == bool) or (o_value is None)):
        # if not a number
        if not((type(o_value) == float) \
               or (type(o_value) == int) \
               or (type(o_value) == complex)):
            # strip
            o_value = str(o_value)
            o_value = o_value.strip()
            # number
            if re.fullmatch("[-|+|0-9|.|e|E|j|(|)]+", o_value):
                # complex
                if re.search("j", o_value):
                    try:
                        o_value = complex(o_value)
                    except ValueError:
                        pass  # still a string
                # float
                elif re.search("[.|e|E]", o_value):
                    try:
                        o_value = float(o_value)
                    except ValueError:
                        pass  # still a string
                # integer
                else:
                    try:
                        o_value = int(o_value)
                    except ValueError:
                        pass  # still a string
            # boolean
            elif (o_value in ('TRUE','True','true')):
                o_value = True
            elif (o_value in ('FALSE','False','false')):
                o_value = False
            elif (o_value in ('NONE','None','none','Null','Null','null')):
                o_value = None
            # a real string, complex, float or integer
            else:
                pass
    # output
    return(o_value)


def escoor(d_iacjson):
    """
    input:
        d_iacjson: acjson.
    output:
        es_coor: acjson's coordinate key set.
    description:
        give back the acjson's coordinate key set.
    """
    es_coor = set(d_iacjson.keys())
    [es_coor.remove(s_notcoor) for s_notcoor in ts_NOTCOOR]
    return(es_coor)


def icoormax(d_iacjson):
    """
    input:
        d_iacjson: acjson.
    output:
        i_coor: max coorinate as integer.
    description:
        give back the acjson obj max coordinate as integer.
    """
    i_coor = None
    es_coor = escoor(d_iacjson)
    li_coor = [int(s_coor) for s_coor in es_coor]
    i_coor = max(li_coor)
    return(i_coor)


def ispotmax(ti_spotlayout):
    """
    input:
        ti_spotlayout: sport layout tuple of integers.
        e.g (1,2,3) for a pyramide or (3,3,3) for a square.
    output:
        i_spotmax: total number of spots.
    description:
        translate ti_spotlayout definition tuple into max spot coordinate.
    """
    i_spotmax = 0
    for i_spot in ti_spotlayout:
        i_spotmax += i_spot
    return(i_spotmax)


def ispot(i_yy, i_xx, ti_spotlayout):
    """
    input:
        i_yy: y axis sport coordinate.
        i_xx: x axis sport coordinate.
        ti_spotlayout: spot layout tuple.

    output:
        i_spot: i spot coordinate.

    descrioption:
        translate yy xx spot coordinate into i sport coordinat.
    """
    i_spot = 0
    for i_spotrow in ti_spotlayout[0:(i_yy-1)]:
        i_spot += i_spotrow
    i_spot += i_xx
    return(i_spot)


def xy2icoor(i_y, i_x, s_welllayout, i_yy=1, i_xx=1, ti_spotlayout=(1,)):
    """
    input:
        i_y: y axis well coordinate.
        i_x: x axis well coordinate.
        s_welllayout: well layout string.
        i_yy: y axis spot coordinate. default 1.
        i_xx: x axis spot coordinate. default 1.
        ti_spotlayout: spot layout tuple of integers.
        default is one spot per well (1,).
    output:
        i_coor: acjson i coordinate.
    description:
        translate acjson xy coordinate into i cordinate.
    """
    i_coor = None
    # process
    ls_coor = s_welllayout.split("x")
    i_ymax = int(ls_coor[0])  # not really used
    i_xmax = int(ls_coor[1])  # used
    i_spotmax = ispotmax(ti_spotlayout=ti_spotlayout)
    i_spot = ispot(i_yy=i_yy, i_xx=i_xx, ti_spotlayout=ti_spotlayout)
    i_coor = ((i_y - 1) * i_xmax * i_spotmax) + ((i_x - 1) * i_spotmax) + i_spot
    # output
    return(i_coor)


def acrelabel(s_runid, s_log, d_iacjson, s_runtype, b_deepcopy=False):
    """
    input:
        runid: unique run identifier.
        s_log: log string.
        d_iacjson: acjson.
        runtype: pipeline module name. (e.g. acflow)
        b_deepcopy: specify if the input d_acjson is really copied in memory
            or just called by reference and manipulated by this subroutine.
            boolean. default is False.

    output:
        d_iacjson: updated acjson

    description:
        update acjson's runid, runtype, acid and s_log
    """
    # get copy or reference
    if (b_deepcopy):
        d_iacjson =  copy.deepcopy(d_iacjson)
    # process
    s_acid = "{}-{}_ac.json".format(s_runtype, s_runid)
    d_iacjson.update({"runid": s_runid})
    d_iacjson.update({"runtype": s_runtype})
    d_iacjson.update({"acid": s_acid})
    d_iacjson.update({"log": s_log})
    # output
    return(d_iacjson)


def acbuild(s_runid, s_runtype, s_welllayout, ti_spotlayout=(1,), s_log=None):
    """
    input:
        s_runid: unique run identifier.
        s_runtype: pipeline module name. (e.g. acflow)
        s_welllayout: well layout string.
            + 0x0: not_yet_specified or not_available
            + 1x1: 1 Well Tube or Petridish
            + 1x4: 4 Wellplate one row
            + 2x2: 4 Wellplate two rows
            + 2x3: 6 Wellpalte
            + 2x4: 8 Wellplate
            + 8x12: 96 Wellplate
            + 16x24: 384 Wellplate
        ti_spotlayout: spotl layout tuple of integers.
            for example (1,2,3) for a pyramide
            or (3,3,3) for a 3x3 square
            or (1,2,1) for a trapezoid.
            default is one spot per well (1,).
        s_log: optional log entry, default None.
    output:
        dd_acjson: acjson dictionary of dictionary object.

    description:
        generate acjson object simply by welllayout and spot layout definition.
    """
    # initiate acjson dictionary
    dd_acjson = {
        "welllayout" : s_welllayout,
        "spotlayout" : ti_spotlayout,
        "log" : s_log,
        "runid": s_runid,
        "runtype": s_runtype,
    }
    dd_acjson.update({"acid": "{}-{}_ac.json".format(s_runtype, s_runid)})

    # initiate other vaiables
    s_ymax,s_xmax = s_welllayout.split("x")
    i_ymax = int(s_ymax)
    i_xmax = int(s_xmax)
    i_coor = 1

    # get skeleton
    i_well = 0
    for i_y in range(1, i_ymax + 1):
        for i_x in range(1, i_xmax + 1):
            i_well += 1
            i_spot = 0
            for i_yspot in range(1, len(ti_spotlayout) + 1):
                for i_xspot in range(1, ti_spotlayout[i_yspot-1] + 1):
                    i_spot += 1
                    d_thewell = copy.deepcopy(d_WELL)
                    d_thewell.update(
                        {"ixi": "{}x{}".format(i_y, i_x)}
                    )
                    d_thewell.update(
                        {"iixii": "{}_{}x{}_{}".format(
                            i_y, i_yspot, i_x, i_xspot
                        )}
                    )
                    d_thewell.update({"iWell": i_well})
                    d_thewell.update({"iSpot": i_spot})
                    if (i_y <= len(ts_ABC)):
                        d_thewell.update(
                            {"sxi":"{}x{}".format(ts_ABC[i_y],i_x)}
                        )
                    dd_acjson.update({str(i_coor): d_thewell})
                    # next
                    i_coor += 1
    # output
    return(dd_acjson)


# acjson fusion
def acfuseaxisrecord(
        d_acjson,
        s_coor,
        s_axis,
        d_record,
        s_ambiguous="break",
        b_deepcopy=False):
    """
    input:
        d_acjson: acjson object.

        s_coor: coordinate to be updated.

        s_axis: axis on the coordinate to be updated.

        d_record: gent record.

        s_ambiguous: what to do if at the coordinate and axis
            specified location already a record of this element exist.
            possible values are: break, timeseries, update, jump.
            defalt value is break.
            the acjson format can handle batch, fed and continous culture type.
            timeseries will sum up ambiguous batch culture type elements,
            if unit, timebegin and timeend is compatible.

        b_deepcopy: specify if the input d_acjson is really copied in memory
            or just called by reference and manipulated by this subroutine.
            boolean. default is False.
    output:
        d_acjson: updated acjson object

    description:
        update acjson with a coordinate and axis specific record.
    """
    # get copy or reference
    if (b_deepcopy):
        d_acjson =  copy.deepcopy(d_acjson)
    # update record at related acjson coordinat
    d_set = d_acjson[s_coor][s_axis]
    if (d_set is None):
        d_set = d_record
    else:
        for s_element, o_source in d_record.items():
            # element exists
            try:
                d_set[s_element]
                # element is differnt
                if (o_source != d_set[s_element]) \
                   and (s_ambiguous == "break"):
                    sys.exit(ds_error["acfuserecord_break"].format(
                        s_coor,
                        s_axis,
                        s_element,
                        d_set[s_element],
                        o_source
                        )
                    )
                elif (o_source != d_set[s_element]) \
                     and (s_ambiguous == "update"):
                    d_set.update({s_element : o_source})
                elif (o_source != d_set[s_element]) \
                     and (s_ambiguous == "timeseries"):
                    # check for none
                    for d_content in (d_set[s_element], o_source):
                        for _, o_content in d_content.items():
                            if (o_content is None):
                                sys.exit(
                                    ds_error["acfuserecord_none"].format(
                                        s_coor,
                                        s_axis,
                                        s_element,
                                        d_set[s_element],
                                        o_source
                                    )
                                )
                    # check for compatible units
                    if (o_source["concUnit"] != d_set[s_element]["concUnit"]) or \
                       (o_source["timeUnit"] != d_set[s_element]["timeUnit"]):
                        sys.exit(
                            ds_error["acfuserecord_unit"].format(
                                s_coor,
                                s_axis,
                                s_element,
                                d_set[s_element],
                                o_source
                            )
                        )
                    # get set time series
                    # conc
                    lr_conc_set = d_set[s_element]["conc"]
                    if (type(lr_conc_set) != list):
                        lr_conc_set = [lr_conc_set]
                    # cultType
                    ls_culttype_set = d_set[s_element]["cultType"]
                    if (type(ls_culttype_set) != list):
                        ls_culttype_set = [ls_culttype_set]
                    # time begin
                    lr_timebegin_set = d_set[s_element]["timeBegin"]
                    if (type(lr_timebegin_set) != list):
                        lr_timebegin_set = [lr_timebegin_set]
                    # time end
                    lr_timeend_set = d_set[s_element]["timeEnd"]
                    if (type(lr_timeend_set) != list):
                        lr_timeend_set = [lr_timeend_set]
                    # get  source time series
                    # conc
                    lr_conc_source = o_source["conc"]
                    if (type(lr_conc_source) != list):
                        lr_conc_source = [lr_conc_source]
                    # conc
                    ls_culttype_source = o_source["cultType"]
                    if (type(ls_culttype_source) != list):
                        ls_culttype_source = [ls_culttype_source]
                    # time begin
                    lr_timebegin_source = o_source["timeBegin"]
                    if (type(lr_timebegin_source) != list):
                        lr_timebegin_source = [lr_timebegin_source]
                    # time end
                    lr_timeend_source = o_source["timeEnd"]
                    if (type(lr_timeend_source) != list):
                        lr_timeend_source = [lr_timeend_source]
                    # check for serie leng consistency
                    if (len(lr_timebegin_set) != len(lr_timeend_set)) or \
                       (len(lr_timebegin_set) != len(lr_conc_set)) or \
                       (len(lr_timebegin_set) != len(ls_culttype_set)) or \
                       (len(lr_timebegin_source) != len(lr_timeend_source)) or \
                       (len(lr_timebegin_source) != len(lr_conc_source)) or \
                       (len(lr_timebegin_source) != len(ls_culttype_source)):
                        sys.exit(
                            ds_error["acfuserecord_lenconcculttime"].format(
                                s_coor,
                                s_axis,
                                s_element,
                                d_set[s_element],
                                o_source
                            )
                        )
                    # merge series
                    er_loop_timebegin = set(lr_timebegin_source)
                    er_loop_timebegin.union(set(lr_timebegin_set))
                    lr_loop_timebegin = list(er_loop_timebegin)
                    lr_loop_timebegin.sort()
                    lr_timebegin = []
                    lr_timeend = []
                    lr_conc = []
                    ls_culttype = []
                    for r_timebegin in lr_loop_timebegin:
                        # set
                        i_index_set = None
                        try:
                            i_index_set = lr_timebegin_set.index(r_timebegin)
                            s_culttype_set = ls_culttype_set[i_index_set]
                            # check culttype
                            if (s_culttype_set not in {"batch","fed","continuous"}):
                                sys.exit(
                                    ds_error["acfuserecord_culttype"].format(
                                        s_coor,
                                        s_axis,
                                        s_element,
                                        d_set[s_element],
                                        o_source
                                    )
                                )
                        except KeyError:
                            pass
                        # source
                        i_index_source = None
                        try:
                            i_index_source = lr_timebegin_source.index(r_timebegin)
                            s_culttype_source = ls_culttype_source[i_index_source]
                            # check culttype
                            if (s_culttype_source not in {"batch","fed","continuous"}):
                                sys.exit(
                                    ds_error["acfuserecord_culttype"].format(
                                        s_coor,
                                        s_axis,
                                        s_element,
                                        d_set[s_element],
                                        o_source
                                    )
                                )
                        except KeyError:
                            pass
                        # update output
                        if not (i_index_set is None) and not (i_index_source is None):
                            if (s_culttype_set == "batch") and \
                               (s_culttype_source == "batch"):
                                # batch (set and source)
                                lr_timebegin.append(r_timebegin)
                                ls_culttype.append(s_culttype_set)
                                lr_conc.append(lr_conc_set[i_index_set] + lr_conc_source[i_index_source])
                                lr_timeend.append(lr_timeend_set[i_index_set])
                                if (lr_timeend_set[i_index_set] != lr_timeend_source[i_index_source]):
                                    sys.exit(
                                        ds_error["acfuserecord_timeend"].format(
                                            s_coor,
                                            s_axis,
                                            s_element,
                                            d_set[s_element],
                                            o_source
                                        )
                                    )
                            elif (s_culttype_set == "batch") and \
                               ((s_culttype_source == "fed") or (s_culttype_source == "continous")):
                                # batch (set)
                                ls_culttype.append(s_culttype_set)
                                lr_conc.append(lr_conc_set[i_index_set])
                                lr_timeend.append(lr_timeend_set[i_index_set])
                                # fed or continuous (source)
                                ls_culttype.append(s_culttype_source)
                                lr_conc.append(lr_conc_source[i_index_source])
                                lr_timeend.append(lr_timeend_source[i_index_source])
                            elif ((s_culttype_set == "fed") or (s_culttype_set == "continous")) and \
                                 (s_culttype_source == "batch"):
                                # batch (source)
                                ls_culttype.append(s_culttype_source)
                                lr_conc.append(lr_conc_source[i_index_source])
                                lr_timeend.append(lr_timeend_source[i_index_source])
                                # fed or continuous (set)
                                ls_culttype.append(s_culttype_set)
                                lr_conc.append(lr_conc_set[i_index_set])
                                lr_timeend.append(lr_timeend_set[i_index_set])
                            elif ((s_culttype_set == "fed") or (s_culttype_set == "continous")) and \
                                 ((s_culttype_source == "fed") or (s_culttype_source == "continous")):
                                sys.exit(
                                    ds_error["acfuserecord_fedcontinuous"].format(
                                        s_coor,
                                        s_axis,
                                        s_element,
                                        d_set[s_element],
                                        o_source
                                    )
                                )
                        elif not (i_index_set is None):
                            # batch or fed or continuous (set only)
                            ls_culttype.append(s_culttype_set)
                            lr_conc.append(lr_conc_set[i_index_set])
                            lr_timeend.append(lr_timeend_set[i_index_set])
                        elif not (i_index_source is None):
                            # batch or fed or continuous (source only)
                            ls_culttype.append(s_culttype_source)
                            lr_conc.append(lr_conc_source[i_index_source])
                            lr_timeend.append(lr_timeend_source[i_index_source])
                        else:
                            sys.exit(
                                ds_error["acfuserecord_sourcecode"].format(
                                    s_coor,
                                    s_axis,
                                    s_element,
                                    d_set[s_element],
                                    o_source
                                )
                            )
                    # update set
                    if len(lr_timebegin) == 1:
                        lr_timebegin = lr_timebegin[-1]
                        lr_timeend = lr_timeend[-1]
                        lr_conc = lr_conc[-1]
                        ls_culttype = ls_culttype[-1]
                    d_set[s_element]["timeBegin"] = lr_timebegin
                    d_set[s_element]["timeEnd"] = lr_timeend
                    d_set[s_element]["conc"] = lr_conc
                    d_set[s_element]["cultType"] = ls_culttype
                # element is the same or s_ambiguous is jump
                else:
                    pass
            # element does not exist
            except KeyError:
                d_set.update({s_element : o_source})
    # output
    d_acjson[s_coor].update({s_axis : d_set})
    return(d_acjson)


def acfusewellrecord(
        d_acjson,
        s_coor,
        d_record,
        s_ambiguous="break",
        b_deepcopy=False):
    """
    input:
        d_acjson: acjson object.

        s_coor: coordinate to be updated.

        d_record: gent record.

        s_ambiguous: what to do if at the coordinate and axis
            specified location already a record of this element exist.
            possible values are: break, timeseries, update, jump.
            defalt value is break.
            the acjson format can handle batch, fed and continous culture type.
            timeseries will sum up ambiguous batch culture type elements,
            if unit, timebegin and timeend is compatible.

        b_deepcopy: specify if d_acjson is really copied in memory
            or just called by reference. boolean.
            default is False.
    output:
        d_acjson: updated acjson object

    description:
        update acjson with a coordinate and axis specific record.
    """
    # get copy
    if (b_deepcopy):
        d_acjson = copy.deepcopy(d_acjson)
    # update axis
    if (d_record["sample"] != None):
        d_acjson = acfuseaxisrecord(
            d_acjson=d_acjson,
            s_coor=s_coor,
            s_axis="sample",
            d_record=d_record["sample"],
            s_ambiguous=s_ambiguous,
            b_deepcopy=b_deepcopy)
    if (d_record["perturbation"] != None):
        d_acjson = acfuseaxisrecord(
            d_acjson=d_acjson,
            s_coor=s_coor,
            s_axis="perturbation",
            d_record=d_record["perturbation"],
            s_ambiguous=s_ambiguous,
            b_deepcopy=b_deepcopy)
    if (d_record["endpoint"] != None):
        d_acjson = acfuseaxisrecord(
            d_acjson=d_acjson,
            s_coor=s_coor,
            s_axis="endpoint",
            d_record=d_record["endpoint"],
            s_ambiguous=s_ambiguous,
            b_deepcopy=b_deepcopy)
    # upadte well layer elements
    ls_element = list(d_record.keys())
    ls_element.pop(ls_element.index("sample"))
    ls_element.pop(ls_element.index("perturbation"))
    ls_element.pop(ls_element.index("endpoint"))
    for s_coorsys in ts_COORSYS:
        try:
            ls_element.pop(ls_element.index(s_coorsys))
        except ValueError:
            pass
    # other elements
    for s_element in ls_element:
        # element exists
        try:
            o_source = d_record[s_element]
            # element is differnt
            if (o_source != d_acjson[s_coor][s_element]) \
               and (s_ambiguous == "break") or (s_ambiguous == "timeseries"):
                # bue: i break as well by timeseries.
                # it is hard to say how with an other acjson format element
                # should be deal as timeseries.
                sys.exit(ds_error["acfuserecord_break"].format(
                    s_coor,
                    s_axis,
                    s_element,
                    d_acjson[s_coor][s_element],
                    o_source
                ))
            elif (o_source != d_acjson[s_coor][s_element]) \
                 and (s_ambiguous == "update"):
                d_acjson[s_coor].update({s_element : o_source})
            # element is the same or s_ambiguous is jump
            else:
                pass
        # element does not exist
        except KeyError:
            d_acjson[s_coor].update({s_element : d_record[s_element]})
    # output
    return(d_acjson)


def acfuserepeat0011(
        d_acjsonmajor,
        d_acjsonminor,
        s_ambiguous="break",
        b_deepcopy=False):
    """
    input:
        d_acjsonmajor: main acjson. if deepcopy is False,
            then this acjson will be modified!

        d_acjsonminor: mainor acjson which will be fused to the major one.

        s_ambiguous: what to do if at the coordinate and axis
            specified location already a record of this record exist.
            possible values are: break, timeseries, update, jump.
            defalt value is break.
            the acjson format can handle batch, fed and continous culture type.
            timeseries will sum up ambiguous batch culture type elements,
            if unit, timebegin and timeend is compatible.

        b_deepcopy: specify if d_acjsonmajor is really copied in memory
            or just called by reference. boolean.
            default is False.
    output:
        d_acjson: updated acjson object
    """
    #print("acfuseRepeat0011: processing {} {}".format(
    #    d_acjsonmajor["acid"],
    #    d_acjsonminor["acid"]
    #))
    # get copy
    if (b_deepcopy):
        d_acjsonmajor = copy.deepcopy(d_acjsonmajor)
    # get max coordinate
    i_majorcoormax = icoormax(d_acjsonmajor)
    i_minorcoormax = icoormax(d_acjsonminor)
    # is minor coordinate multiple of major coordinate
    if ((i_majorcoormax % i_minorcoormax) != 0):
        sys.exit(ds_error["acfuserepeat"].format(
            i_minorcoormax,
            i_majorcoormax,
            (i_majorcoormax % i_minorcoormax)
        ))
    else:
        i_totalfraction = int(i_majorcoormax / i_minorcoormax)

    # per minor coodinate
    i_majorcoor = 1
    for i_minorcoor in range(1, (i_minorcoormax + 1)):
        # per self fraction
        for i_fraction in range(1, (i_totalfraction + 1)):
            # per well
            d_acjsonmajor = acfusewellrecord(
                d_acjson=d_acjsonmajor,
                s_coor=str(i_majorcoor),
                d_record=d_acjsonminor[str(i_minorcoor)],
                s_ambiguous=s_ambiguous,
                b_deepcopy=b_deepcopy
            )
            # increment self coordinate
            i_majorcoor += 1
    # output
    return(d_acjsonmajor)


def acfuserepeat0101(
        d_acjsonmajor,
        d_acjsonminor,
        s_ambiguous="break",
        b_deepcopy=False):
    """
    input:
        d_acjsonmajor: main acjson. if deepcopy is False,
            then this acjson will be modified!

        d_acjsonminor: mainor acjson which will be fused to the major one.

        s_ambiguous: what to do if at the coordinate and axis
            specified location already a record of this record exist.
            possible values are: break, timeseries, update, jump.
            defalt value is break.
            the acjson format can handle batch, fed and continous culture type.
            timeseries will sum up ambiguous batch culture type elements,
            if unit, timebegin and timeend is compatible.

        b_deepcopy: specify if d_acjsonmajor is really copied in memory
            or just called by reference. boolean.
            default is False.
    output:
        d_acjson: updated acjson object
    """
    #print("acfuseRepeat0101: processing {} {}".format(
    #    d_acjsonmajor["acid"],
    #    d_acjsonminor["acid"]
    #))
    # get copy
    if (b_deepcopy):
        d_acjsonmajor = copy.deepcopy(d_acjsonmajor)
    # get max coordinate
    i_majorcoormax = icoormax(d_acjsonmajor)
    i_minorcoormax = icoormax(d_acjsonminor)
    # is minor coordinate a multiple of major coordinate
    if ((i_majorcoormax % i_minorcoormax) != 0):
        sys.exit(ds_error["acfuserepeat"].format(
                i_minorcoormax,
                i_majorcoormax,
                (i_majorcoormax % i_minorcoormax)
            ))
    else:
        i_totalfraction = int(i_majorcoormax / i_minorcoormax)

    # per major fraction
    i_majorcoor = 1
    for i_fraction in range(1, (i_totalfraction + 1)):
        # per acjson coordiante
        for i_minorcoor in range(1, (i_minorcoormax + 1)):
            # per well
            d_acjsonmajor = acfusewellrecord(
                d_acjson=d_acjsonmajor,
                s_coor=str(i_majorcoor),
                d_record=d_acjsonminor[str(i_minorcoor)],
                s_ambiguous=s_ambiguous,
                b_deepcopy=b_deepcopy
            )
            # increment self coordinate
            i_majorcoor += 1
    # output
    return(d_acjsonmajor)


def acfuseobject(
        s_runid,
        d_acjsonsample=None,
        d_acjsonperturbation=None,
        d_acjsonendpoint=None,
        s_runtype="acpipe_acjson"):
    """
    input:
        s_runid: unique run identifier.

        d_acjsonsample: sample acsjon object. default is None.
        d_acjsonperturbation: perturbation acjson object. default is None.
        d_acjsonendpoint: endpoint acjson object. default is None.

        s_runtype: pipeline module name. default is acpipe_acjson.

    output:
        d_acjson: updated acjson object

    description:
        0011 fuses sample, perturbation and endpoint acjson object
        into one resulting acjson object
    """
    d_oacjson = None
    i_coormax = 0
    s_welllayout = None
    # sample
    if (d_acjsonsample != None):
        if (i_coormax < icoormax(d_acjsonsample)):
            i_coormax = icoormax(d_acjsonsample)
            s_welllayout = d_acjsonsample["welllayout"]
            ti_spotlayout = d_acjsonsample["spotlayout"]
            s_acidsample = d_acjsonsample["acid"]
        else:
            s_acidsample = 'None'
    # perturbation
    if (d_acjsonperturbation != None):
        if (i_coormax < icoormax(d_acjsonperturbation)):
            i_coormax = icoormax(d_acjsonperturbation)
            s_welllayout = d_acjsonperturbation["welllayout"]
            ti_spotlayout = d_acjsonperturbation["spotlayout"]
            s_acidperturbation = d_acjsonperturbation["acid"]
        else:
            s_acidperturbation = 'None'
    # endpoint
    if (d_acjsonendpoint != None):
        if (i_coormax < icoormax(d_acjsonendpoint)):
            i_coormax = icoormax(d_acjsonendpoint)
            s_welllayout = d_acjsonendpoint["welllayout"]
            ti_spotlayout = d_acjsonendpoint["spotlayout"]
            s_acidendpoint = d_acjsonendpoint["acid"]
        else:
            s_acidendpoint = 'None'
    # get output acjson
    d_oacjson = acbuild(
        s_welllayout=s_welllayout,
        ti_spotlayout = ti_spotlayout,
        s_runid=s_runid,
        s_runtype=s_runtype
    )
    d_oacjson.update({"log": "{}; {}; {} | acfuseacobj > {}".format(
        s_acidsample,
        s_acidperturbation,
        s_acidendpoint,
        d_oacjson["acid"])}
    )
    # fuse sample
    if (d_acjsonsample != None):
        acfuserepeat0011(
            d_acjsonmajor=d_oacjson,
            d_acjsonminor=d_acjsonsample,
            s_ambiguous="break",
            b_deepcopy=False)
    # fuse perturbation
    if (d_acjsonperturbation != None):
        acfuserepeat0011(
            d_acjsonmajor=d_oacjson,
            d_acjsonminor=d_acjsonperturbation,
            s_ambiguous="break",
            b_deepcopy=False)
    # fuse endpoint
    if (d_acjsonendpoint != None):
        acfuserepeat0011(
            d_acjsonmajor=d_oacjson,
            d_acjsonminor=d_acjsonendpoint,
            s_ambiguous="break",
            b_deepcopy=False)
    # output
    return(d_oacjson)


def acfuse4to1(
        s_runid,
        ld_acjsonminor,
        ld_map=[dii_96A1, dii_96A2, dii_96B1, dii_96B2],
        s_ambiguous="break",
        s_owelllayout="16x24",
        s_runtype="acpipe_acjson"):
    """
    input:
        s_runid: unique run identifier.

        ld_acjsonminor: ordered list (A1, A2, B1, B2)
            of 4 x 96 wellplate acjson objects.

        ld_map: ordered list of 4 x 96 wellplate to 384 wellplate
            mapping dictionaries. mapping dictionaries are constats.

        s_ambiguous: what to do if at the coordinate and axis
            specified location already a record of this element exist.
            possible values are: break, timeseries, update, jump.
            defalt value is break.
            the acjson format can handle batch, fed and continous culture type.
            timeseries will sum up ambiguous batch culture type elements,
            if unit, timebegin and timeend is compatible.

        s_owelllayout: output acjson well layout string.
            default is the string for a 384 well plate.

        s_runtype: pipeline module name. default is acpipe_acjson.

    output:
        d_oacjson: 384 well acjson object,
        fused out of 4 x 96 well acjson objects.

    description:
        fuses 4 x 96 well plates into one 384 well plate.
        this is quite stanadard and commonly done by a pipette robot.
    """
    # check input
    if (len(ld_acjsonminor) != len(ld_map)):
       sys.exit(ds_error["acfuse4to1"].format(len(ld_acjsonminor), len(ld_map)))
    # generate output
    d_oacjson = acbuild(
        s_welllayout=s_owelllayout,
        s_runid=s_runid,
        s_runtype=s_runtype)
    # map
    s_log = None
    for d_map in ld_map:
        d_acjsonminor = ld_acjsonminor.pop(0)
        for i_key,i_value in d_map.items():
            d_record = d_acjsonminor[str(i_key)]
            d_oacjson = acfusewellrecord(
                d_acjson=d_oacjson,
                s_coor=str(i_value),
                d_record=d_record,
                s_ambiguous=s_ambiguous,
                b_deepcopy=False)
        # handle log
        if (s_log is None):
            s_log = d_acjsonminor["acid"]
        else:
            s_log +=  "; {}".format( d_acjsonminor["acid"])
    # return
    s_log += " | acfuse4to1 > {}".format(d_oacjson["acid"])
    d_oacjson.update({"log" : s_log})
    return(d_oacjson)

# acdiff
# get all diffent coordinates from two acjson dictionaryes

# basic manupulations
def count_record(d_acjson, d_record=None, ts_axis=ts_ACAXIS):
    """
    input:
        d_acjson: acjson dictionary

        d_record: gent record. if None, all records weill be counted.

        ts_axis: tuple of ac axis which should be searched for the record.

    output:
        i_count: number of popped records

    description:
        counts all or the number of the given record in an acjson dict.
    """
    i_count=0
    # process
    for s_axis in ts_axis:
        for s_coor, o_well in d_acjson.items():
            if not (s_coor in ts_NOTCOOR):
                if not (o_well[s_axis] is None):
                    i_count += len(o_well[s_axis])
    # output
    return(i_count)


def record_in_acjson(d_acjson, d_record, ts_axis=ts_ACAXIS, b_leaf_intersection=False, b_recordset_major=False):
    """
    input:
        d_acjson: acjson dictionary

        d_record: gent record

        ts_axis: tuple of ac axis which should be searched for the record.

        b_leaf_intersection: if True then the function check only for the leafs
            that intersect in d_record and d_acjson record. if False then the
            function will check the whole dict. missing leafes will cause
            not found.
            default is False.

        b_recordset_major: if True then the recordset is only checked for its
            major part of the recordset name, the part befor the first dash.

    output:
        b_found: boolen states if record was found in acjson

    description:
      scans acjson along the specifed axis for the given record.
      returns True if record could be detected, False otherwise.
    """
    b_found = False
    # procss
    print(f"search: {d_record}")
    for s_coor, o_well in d_acjson.items():
        if (b_found):
            break
        elif not (s_coor in ts_NOTCOOR):
            for s_axis in ts_axis:
                if (b_found):
                    break
                if not (o_well[s_axis] is None):
                    for s_gent, d_acjsonrecord in o_well[s_axis].items():
                        if (b_found):
                            break
                        #print(f"check coordinate {s_coor} axis {s_axis} for {s_gent}")
                        try:
                            d_therecord = d_record[s_gent]
                            if (b_recordset_major):
                                d_acjsonrecord = copy.deepcopy(d_acjsonrecord)
                                d_therecord = copy.deepcopy(d_record[s_gent])
                                try:
                                    d_acjsonrecord["recordSet"] = d_acjsonrecord["recordSet"].split("-")[0]
                                except KeyError:
                                    pass
                                try:
                                    d_therecord["recordSet"] = d_therecord["recordSet"].split("-")[0]
                                except KeyError:
                                    pass
                            if (b_leaf_intersection):
                                b_leaf_ok = True
                                es_leaf = set(d_therecord.keys()).intersection(set(d_acjsonrecord.keys()))
                                for s_leaf in es_leaf:
                                    if (b_found):
                                        break
                                    try:
                                        if (d_therecord[s_leaf] != d_acjsonrecord[s_leaf]):
                                            b_leaf_ok = False
                                            break
                                    except KeyError:
                                        pass
                                if (b_leaf_ok):
                                    b_found = True
                                    break
                            else:
                                if (d_therecord == d_acjsonrecord):
                                    b_found = True
                                    break
                        except KeyError:
                            pass
    # output
    if (b_found):
        print(f"found.\n")
    else:
        print(f"missing.\n")
    return(b_found)


def list_uniq_record(d_acjson, ts_axis=ts_ACAXIS):
    """
    input:
        d_acjson: acjson dictionary

        ts_axis: tuple of ac axis which should be searched for records.

    output:
        ld_gentrecord: list of uniq gent records

    description:
        give a list of all unique records, found along the specifed ac axis,
        in the the acjson object.
    """
    ld_gentrecord = []
    # process
    for s_axis in ts_axis:
        for s_coor, o_well in d_acjson.items():
            if not(s_coor in ts_NOTCOOR):
                if not (o_well[s_axis] is None):
                    for s_gent, d_record in o_well[s_axis].items():
                        b_missing = True
                        for d_gentrecord in ld_gentrecord:
                            s_uniq = list(d_gentrecord.keys())[0]
                            if (s_gent == s_uniq) and (d_record == d_gentrecord[s_uniq]):
                                b_missing = False
                                break
                        if (b_missing):
                            ld_gentrecord.append({s_gent: d_record})
    # output
    return(ld_gentrecord)


def list_uniq_recordset(d_acjson, ts_axis=ts_ACAXIS, b_major=True):
    """
    input:
        d_acjson: acjson dictionary

        ts_axis: tuple of ac axis which should be searched for recordsets.

        b_major: focus on major set. split possible minor part after first dash away.

    output:
        ls_recordset: list of recordsets

    description:
        give a unique list of all recordSet entries , found along the specifed ac axis,
        in the acjson object.
    """
    es_recordset = set()
    # process
    for s_axis in ts_axis:
        for s_coor, o_well in d_acjson.items():
            if not(s_coor in ts_NOTCOOR):
                if not (o_well[s_axis] is None):
                    for s_gent, d_record in o_well[s_axis].items():
                        try:
                            s_recordset = d_record["recordSet"]
                            if (b_major):
                                s_recordset = s_recordset.split("-")[0]
                        except (KeyError, TypeError ):
                            # bue 20180216: Type Error is because of
                            # acjson2dataframetsv stacked axis None hack.
                            print(
                                ds_error["list_uniq_recordset_norecord"].format(
                                    d_record
                                )
                            )
                            s_recordset = "None"
                        # update recordset set
                        es_recordset.add(s_recordset)
    # output
    return(sorted(list(es_recordset)))


def max_record(d_acjson, ts_axis=ts_ACAXIS, s_recordset=None, b_major=None):
    """
    input:
        d_acjson: acjson dictionary.

        ts_axis: tuple of assay coordinate axis from which information is extracted.
            valid axis are sample, perturbation and endpoint.

        s_recordset:  recordSet or major recordSet from which information is extracted.
            s_recordset = None search the entire axis independent from recordSet membership.
            default is None.

        b_major: focus on major set. split possible minor part after first dash away.
            b_major = None searches with regex ^s_recordset.
            default is None.

    output:
        i_max_record: input realted maximal record count.

    description:
        get maximal ac axis and recordset related recordcount in this d_acjson object.
    """
    # process
    i_max_record = 0
    for s_axis in ts_axis:
        i_axismax_record = 0
        for s_coor, o_well in d_acjson.items():
            if not(s_coor in ts_NOTCOOR):
                if not (o_well[s_axis] is None):
                    i_coormax_record = 0
                    for s_gent, d_record in o_well[s_axis].items():
                        s_therecordset = d_record["recordSet"]
                        # update corr max record count
                        if (s_recordset is None):
                            i_coormax_record += 1
                        elif not (s_recordset is None) and \
                             (b_major is None) and \
                             (re.search("^{}".format(s_recordset), s_therecordset)):
                            i_coormax_record += 1
                        elif not (s_recordset is None) and \
                             (b_major) and \
                             (s_recordset.split("-")[0] == s_therecordset.split("-")[0]):
                              i_coormax_record += 1
                        elif not (s_recordset is None) and \
                             not (b_major) and \
                             (s_recordset == s_therecordset):
                              i_coormax_record += 1
                        else:
                              pass # nop
                    # update axis max record count
                    if (i_coormax_record > i_axismax_record):
                        i_axismax_record = i_coormax_record
        # update acjson max record count
        if (i_axismax_record > i_max_record):
            i_max_record = i_axismax_record
    # output
    return(i_max_record)


def pop_record(
        d_acjson,
        d_record,
        ts_axis=ts_ACAXIS,
        b_leaf_intersection=False,
        b_recordset_major=False
    ):
    """
    input:
        d_acjson: acjson dictionary

        d_record: gent record

        ts_axis: tuple of ac axis which should be searched for the record.

        b_leaf_intersection: if True then the function check only for the leafs
            that intersect in d_record and d_acjson record. if False then the
            function will check the whole dict. missing leafes will cause
            not found.
            default is False.

        b_recordset_major: if True then the recordset is only checked for its
            major part of the recordset name, the part befor the first dash.
    output:
        d_pop: poped acjson

    description:
        pops the given record from the acjson dict.
    """
    d_pop = copy.deepcopy(d_acjson)
    # process
    print(f"pop: {d_record}")
    for s_coor, o_well in d_acjson.items():
        if not (s_coor in ts_NOTCOOR):
            for s_axis in ts_axis:
                if not (o_well[s_axis] is None):
                    for s_gent, d_acjsonrecord in o_well[s_axis].items():
                        #print(f"check coordinate {s_coor} axis {s_axis} for {s_gent}")
                        try:
                            d_therecord = d_record[s_gent]
                            if (b_recordset_major):
                                d_acjsonrecord = copy.deepcopy(d_acjsonrecord)
                                d_therecord = copy.deepcopy(d_record[s_gent])
                                try:
                                    d_acjsonrecord["recordSet"] = d_acjsonrecord["recordSet"].split("-")[0]
                                except KeyError:
                                    pass
                                try:
                                    d_therecord["recordSet"] = d_therecord["recordSet"].split("-")[0]
                                except KeyError:
                                    pass
                            if (b_leaf_intersection):
                                b_leaf_ok = True
                                es_leaf = set(d_therecord.keys()).intersection(set(d_acjsonrecord.keys()))
                                for s_leaf in es_leaf:
                                    try:
                                        if (d_therecord[s_leaf] != d_acjsonrecord[s_leaf]):
                                            b_leaf_ok = False
                                            break
                                    except KeyError:
                                        pass
                                if (b_leaf_ok):
                                    # pop
                                    d_pop[s_coor][s_axis].pop(s_gent)
                            elif (d_therecord == d_acjsonrecord):
                                # pop
                                d_pop[s_coor][s_axis].pop(s_gent)
                        except KeyError:
                            pass
    # output
    return(d_pop)


def pop_ac(
        d_acjson,
        d_acrecord,
        ts_axis=ts_ACAXIS,
        b_leaf_intersection=False,
        b_recordset_major=False,
        s_error=None
    ):
    '''
    input:
        d_acjson: acjson dictionary from whom the records specified in
            d_acrecord will be popped.

        d_acrecord: acjson dictionary which spercifes the records
            that will be poped from d_acpop.

        ts_axis: tuple of ac axis which should be searched for the record.

        b_leaf_intersection: if True then the function check only for the leafs
            that intersect in d_record and d_acjson record. if False then the
            function will check the whole dict. missing leafes will cause
            not found.
            default is False.

        b_recordset_major: if True then the recordset is only checked for its
            major part of the recordset name, the part befor the first dash.

        s_error: error string.

    output tuple:
        d_acjson: popped d_acjson

        s_error: error string.

    description:
        pops all records speified in d_acrecord from d_acjson.
    '''
    # for each record
    for d_record in list_uniq_record(
            d_acrecord,
            ts_axis=ts_axis
        ):
        # check and pop each record
        if (record_in_acjson(
                d_record=d_record,
                d_acjson=d_acjson,
                ts_axis=ts_axis,
                b_leaf_intersection=b_leaf_intersection,
                b_recordset_major=b_recordset_major,
            )):
            d_acjson = pop_record(
                d_record=d_record,
                d_acjson=d_acjson,
                ts_axis=ts_axis,
                b_leaf_intersection=b_leaf_intersection,
                b_recordset_major=b_recordset_major,
            )
        elif (s_error is None):
            s_error = "Error @ pop_ac :\n{}".format(
                ds_error['pop_ac'].format(d_acrecord['acid'], ts_axis, d_record, d_acrecord['acid'])
            )
        else:
            s_error = "{}\n{}".format(
                s_error,
                ds_error['pop_ac'].format(d_acrecord['acid'], ts_axis, d_record, d_acrecord['acid'])
            )
    # output
    return(d_acjson, s_error)


# xray
def xray(d_acjson, s_opath="./"):
    """
    input: d_acjson: acjson dictionary object.

    output: d_skeleton: acjson skeleton dictionary object and file.

    description:
        returns the dictionary skeleton object and file of the acjson object.
        the acjson with out content.
    """
    # clone
    d_skeleton = copy.deepcopy(d_acjson)
    # x ray
    print("\nxray {}".format(d_acjson["acid"]))
    for s_coor, d_well in d_skeleton.items():
        if (s_coor not in ts_NOTCOOR):
            print("process coordinate {}".format(s_coor))
            # well layer
            for s_axis, o_branch in d_well.items():
                # branch layer none case
                print("process coordinate {} axis {}".format(s_coor, s_axis))
                if (o_branch is None) or (s_axis in {"ixi","iixii","sxi"}):
                    pass
                # branch layer dict case
                elif (type(o_branch) == dict):  # (s_axis in ts_ACAXIS)
                    # twig layer
                    for s_twig, o_leaf in o_branch.items():
                        print("process coordinate {} axis {} gent {}".format(s_coor, s_axis, s_twig))
                        # twig layer none case
                        if (o_branch is None):
                            pass
                        # twig layer dict case
                        elif (type(o_leaf) == dict):
                            # leaf layer
                            for s_key, o_value in o_leaf.items():
                                if (o_value is None):
                                    pass
                                elif (type(o_value) == dict):
                                    o_leaf[s_key] = "{dict}"
                                elif (type(o_value) == list) \
                                     or (type(o_value) == tuple):
                                    o_leaf[s_key] = "[list]"
                                else:
                                    o_leaf[s_key] = "value"
                        # twig layer list case
                        elif (type(o_leaf) == list) or (type(o_leaf) == tuple):
                            o_branch[s_twig] = "[list]"
                        # twig layer other case
                        else:
                            o_branch[s_twig] = "value"
                # branch layer list case
                elif (type(o_branch) == list) or (type(o_branch) == tuple):
                    d_skeleton[s_coor][s_axis] = "[list]"
                # branch layer other case
                else:
                    d_skeleton[s_coor][s_axis] = "value"

    # output json file
    with open(s_opath + "xray-" + d_skeleton["acid"], "w") as f_json:
        json.dump(d_skeleton, f_json, indent=4, sort_keys=True)
    # return
    return(d_skeleton)


# tsv
def acjson2layouttsv(
        d_acjson,
        ts_axis=ts_ACAXIS,
        es_leaf=es_LEAF,
        s_mode="short",
        b_wellborder=False,
        s_delimiter="\t",
        s_opath="./"
    ):
    """
    input:
        d_acjson: acjson object.

        ts_axis: tuple of acaxis from which information is extracted.

        es_leaf: set of strings which for s_mode="long" specifies what contet
            for each gent should be given out.

        s_mode: mode specifies how coordinate records should be condensed
            for the tsv output. valid modes are short and long.
            default mode is short.
            the short mode will solely give out the key
            the long mode will give back key and alphabetically sorted record.

        b_wellborder: put space between wells.
            this especcialy helpfull for spotted array layouts.
            default setting is False.

        s_delimiter: file delimiter. default is \t (tab).

        s_opath: output path. default is current working directory.

    output:
        file.tsv: axis and recordset related tab separated value layout file.
        ls_pathfile: list of path to and tsv file name.

    description:
        transfor acjson axis into a human readable tab separated vale file.
    """
    ls_pathfile = []

    # loop through axis
    for s_axis in ts_axis:

        # loop through mayor recordset of each axis
        for s_majorrecordset in list_uniq_recordset(d_acjson, ts_axis=(s_axis,), b_major=True):

            # reset found
            b_found = False

            # get wellplate matrix
            print("\n{}\naxis: {}\nmajor_record: {}".format(d_acjson["acid"], s_axis, s_majorrecordset))

            # get wellplate matrix
            ll_matrix = []
            i_coor = 0
            i_past_y_well = 0
            i_past_x_well = 0
            i_past_y_spot = 0
            i_past_x_spot = -1

            # loop through well rows
            for i_y_well in range(int(d_acjson["welllayout"].split("x")[0])):
                # loop through spot rows
                for i_y_spot in range(len(d_acjson["spotlayout"])):
                    # loop through well columns
                    l_vector = []
                    for i_x_well in range(int(d_acjson["welllayout"].split("x")[1])):
                        # loop through spot columns
                        for i_x_spot in range(d_acjson["spotlayout"][i_y_spot]):
                            # get next coordinate
                            if (i_x_spot == i_past_x_spot + 1) and \
                               (i_y_spot == i_past_y_spot) and \
                               (i_x_well == i_past_x_well) and \
                               (i_y_well == i_past_y_well):
                                # next spot column in same well
                                print("next spot column in same well")
                                i_coor += 1
                                i_past_x_spot = i_x_spot
                            elif (i_x_spot == 0) and \
                                 (i_y_spot == i_past_y_spot) and \
                                 (i_x_well == i_past_x_well + 1) and \
                                 (i_y_well == i_past_y_well):
                                # next well column in same well row
                                print("next well column in same well row")
                                # i_coor + number of spots per well excluding the particular row in the well + 1
                                i_coor += 1
                                for i_yspot , i_xspot in enumerate(d_acjson["spotlayout"]):
                                    if (i_yspot != i_y_spot):
                                        i_coor += i_xspot
                                i_past_x_spot = i_x_spot
                                i_past_x_well = i_x_well
                            elif (i_x_spot == 0) and \
                                 (i_y_spot == i_past_y_spot + 1) and \
                                 (i_x_well == 0) and \
                                 (i_y_well == i_past_y_well):
                                # next spot row in same well row
                                # i_coor -  (number_of_spots_per_well * (number_of_well_column - 1) - 1)
                                i_coor = i_coor - (sum(d_acjson["spotlayout"]) * (int(d_acjson["welllayout"].split("x")[1]) -1) -1)
                                i_past_x_spot = i_x_spot
                                i_past_y_spot = i_y_spot
                                i_past_x_well = i_x_well
                            elif (i_x_spot == 0) and \
                                 (i_y_spot == 0) and \
                                 (i_x_well == 0) and \
                                 (i_y_well == i_past_y_well + 1):
                                # next well row first sopt first well column
                                print("next well row first well column")
                                i_coor += 1
                                i_past_x_spot = i_x_spot
                                i_past_y_spot = i_y_spot
                                i_past_x_well = i_x_well
                                i_past_y_well = i_y_well
                            else:
                                # error: strange coordinate looping
                                sys.exit(
                                    ds_error["acjson2layouttsv"].format(
                                        i_past_x_spot,
                                        i_x_spot,
                                        i_past_y_spot,
                                        i_y_spot,
                                        i_past_x_well,
                                        i_x_well,
                                        i_past_y_well,
                                        i_y_well
                                    )
                                )

                            # reset extracted coordinate information
                            s_content = None

                            # none case
                            if (d_acjson[str(i_coor)][s_axis] is None):
                                s_content = "None"

                            # short case
                            elif (s_mode == "short"):
                                for s_gent, d_spec in sorted(d_acjson[str(i_coor)][s_axis].items()):
                                    # check recordset
                                    if (s_majorrecordset is "None") or re.search("^{}".format(s_majorrecordset), d_spec['recordSet']):
                                        # get data
                                        if (s_content is None):
                                            s_content = s_gent
                                        else:
                                            s_content += " + {}".format(s_gent)

                            # long case
                            elif (s_mode == "long"):
                                for s_gent, d_spec in sorted(d_acjson[str(i_coor)][s_axis].items()):
                                    # check recordset
                                    if (s_majorrecordset is "None") or re.search("^{}".format(s_majorrecordset), d_spec['recordSet']):
                                        # get data
                                        d_content = {s_key: o_value for s_key, o_value in d_spec.items() if s_key in es_leaf}
                                        if (s_content is None):
                                            s_content = "{} {}".format(s_gent, json.dumps(d_content))
                                        else:
                                            s_content += " + {} {}".format(s_gent, json.dumps(d_content))

                            # unknowen case
                            else:
                                sys.exit(ds_error["unknown_mode"].format(s_mode))

                            # check if information could be extracted
                            if not (b_found) and not (s_content is None):
                                b_found = True

                            # pack information into list
                            l_vector.append(s_content)

                            # screen output
                            print("{} {}_{}x{}_{} {}:\t{}".format(i_coor, i_y_well, i_y_spot, i_x_well, i_x_spot, s_axis, s_content))

                        # column well boarder
                        if (b_wellborder):
                             l_vector.append("")
                    # pack information vector into matrix
                    ll_matrix.append(l_vector)
                # row well boarder
                if (b_wellborder):
                    ll_matrix.append([])

            # write matrix to tsv file
            if (b_found):
                print("\nthe Matrix: {}\n".format(ll_matrix))
                s_pathfile = "{}{}".format(
                    s_opath,
                    d_acjson["acid"].replace(
                        "_ac.json",
                        "layouttsv_{}_{}_{}.tsv".format(s_axis, s_majorrecordset, s_mode)
                    )
                )
                with open(s_pathfile, "w", newline="") as f_csv:
                    o_writer = csv.writer(f_csv, delimiter=s_delimiter)
                    o_writer.writerows(ll_matrix)
                # output
                ls_pathfile.append(s_pathfile)

    # return
    return(ls_pathfile)


def acjson2dataframetsv(
        d_acjson,
        es_dfleaf=es_DATAFRAMELEAF,
        b_stacked=False,
        s_delimiter="\t",
        s_opath="./"
    ):
    """
        d_acjson: acjson object.
        es_leaf: set of strings which for s_mode="long" specifies what contet
            for each gent should be given out.
        s_mode: mode specifies how coordinate records should be condensed
        s_delimiter: file delimiter. default is \t (tab).
        s_opath: output path. default is current working directory.
    """
    ls_header = []
    b_header = True

    # base header gent
    ls_leaf_gent = []
    for s_leaf in ("recordSet", "ExternalId", "cultType", "conc", "concUnit", "timeBegin", "timeEnd", "timeUnit"):
        ls_leaf_gent.append(s_leaf)

    # base header sample
    ls_leaf_sample = copy.deepcopy(ls_leaf_gent)
    ls_leaf_sample.insert(1, "sample")
    for s_leaf in ("longRecord", "passageOrigin", "passageUsed"):
        if (s_leaf in es_dfleaf):
            ls_leaf_sample.append(s_leaf)

    # base header perturation
    # bue 20180312 about GallId and PinId: maybe sample and entpoints could be
    # spotted too. however, at the moment we only spot perturbation reagenties.
    # i am happy to add GallId and PinID to sample and endpoint too, if needed.
    ls_leaf_perturbation = copy.deepcopy(ls_leaf_gent)
    ls_leaf_perturbation.insert(1, "perturbation")
    for s_leaf in ("longRecord", "GallId", "PinId"):
        if (s_leaf in es_dfleaf):
            ls_leaf_perturbation.append(s_leaf)

    # base header endpoint
    ls_leaf_endpoint = copy.deepcopy(ls_leaf_gent)
    ls_leaf_endpoint.insert(1, "endpoint")
    for s_leaf in ("longRecord", "GallId", "PinId", "micChannel", "wavelengthNm", "hostOrganism", "targetOrganism", "isotype"):
        if (s_leaf in es_dfleaf):
            ls_leaf_endpoint.append(s_leaf)

    # generate output file
    if (b_stacked):
        s_mode = "stacked"
    else:
        s_mode = "unstacked"

    s_pathfile = "{}{}".format(
        s_opath,
        d_acjson["acid"].replace(
            "_ac.json",
            "dataframetsv_{}.tsv".format(s_mode)
        )
    )
    with open(s_pathfile, "w", newline="") as f:
        f.write("")

    # loop through acjson
    for i_enum, (s_coor, d_coor) in enumerate(d_acjson.items()):
        print(f"\nprocess acjson coordinate {i_enum}/{len(d_acjson)} coordinate {s_coor} ...")
        if (s_coor not in ts_NOTCOOR):
            l_datalayer_preaxis = []  # one unstacked datarow, more stacked datarows

            # acjson level
            for s_leaf in ("runid", "welllayout", "spotlayout"):
                if (s_leaf in es_dfleaf):
                    # data leaf
                    l_datalayer_preaxis.append(d_acjson[s_leaf])
                    # header
                    if (b_header):
                        ls_header.append(s_leaf)

            # preaxis level part 1
            for s_leaf in ("sxi", "ixi", "iixii", "iWell", "iSpot"):
                if (s_leaf in es_dfleaf):
                    # data leaf
                    l_datalayer_preaxis.append(d_acjson[s_coor][s_leaf])
                    # header
                    if (b_header):
                        ls_header.append(s_leaf)

            # coor leaf
            l_datalayer_preaxis.append(s_coor)
            # header
            if (b_header):
                ls_header.append("coor")

            # preaxis level part 2
            if ("runCollapsed" in es_dfleaf):
                # runCollapsed leaf
                s_runcollapsed = None
                for s_axis in ts_ACAXIS:
                    try:
                        for s_gent in d_acjson[s_coor][s_axis].keys():
                            if (s_runcollapsed is None):
                                s_runcollapsed = s_gent
                            else:
                                s_runcollapsed += " + {}".format(s_gent)
                    except AttributeError:
                        # bue 20180110: none case
                        pass
                l_datalayer_preaxis.append(s_runcollapsed)
                # header
                if (b_header):
                    ls_header.append("runCollapsed")

            # stacked
            if (b_stacked):

                # bue 20180216: this is a hack!
                # if an axis is None add {"None": None} that each loop get executed
                d_acjson_manipu = copy.deepcopy(d_acjson)
                for s_axis in ts_ACAXIS:
                    if (d_acjson_manipu[s_coor][s_axis] == None):
                        d_acjson_manipu[s_coor][s_axis] = {"None": None}

                # loop through sample axis recordsets
                for s_majorrecordset_sample in list_uniq_recordset(d_acjson_manipu, ts_axis=("sample",), b_major=True):

                    #++ loop through all sample ++
                    for s_sample, d_record_sample in d_acjson_manipu[s_coor]["sample"].items():
                        # if sample axis None or member the major record set
                        if (s_majorrecordset_sample is "None") or \
                            (d_record_sample["recordSet"].split("-")[0] == s_majorrecordset_sample):

                            # empty data layer
                            l_datalayer_sample = []

                            # sample axis not None
                            if (d_record_sample != None):

                                # sample axis level
                                if ("axisCollapsed" in es_dfleaf):
                                    # axisCollapsed leaf
                                    s_axiscollapsed = None
                                    for s_gent in d_acjson[s_coor]["sample"].keys():
                                        if (s_axiscollapsed is None):
                                            s_axiscollapsed = s_gent
                                        else:
                                            s_axiscollapsed += " + {}".format(s_gent)
                                    l_datalayer_sample.append(s_axiscollapsed)
                                    # header
                                    if (b_header):
                                        ls_header.append("sample-axisCollapsed")

                                # sample recordset level
                                if ("recordSetCollapsed" in es_dfleaf):
                                    # recordSetCollapsed leaf
                                    s_recordsetcollapsed = None
                                    for s_gent, d_record in d_acjson[s_coor]["sample"].items():
                                        if (s_majorrecordset_sample is "None") or \
                                           (d_record["recordSet"].split("-")[0] == s_majorrecordset_sample):
                                            if (s_recordsetcollapsed is None):
                                                s_recordsetcollapsed = s_gent
                                            else:
                                                s_recordsetcollapsed += " + {}".format(s_gent)
                                    l_datalayer_sample.append(s_recordsetcollapsed)
                                    # header
                                    if (b_header):
                                        ls_header.append("sample-recordSetCollapsed")

                                # real
                                for s_leaf in ls_leaf_sample:

                                    # sample leaf
                                    if (s_leaf == "sample"):
                                        l_datalayer_sample.append(s_sample)
                                        # header
                                        if (b_header):
                                            ls_header.append("sample")  # "sample-recordset-sample"
                                    # other leafs
                                    else:
                                        # longRecord leaf
                                        if (s_leaf == "longRecord"):
                                            try:
                                                l_datalayer_sample.append(
                                                    "{}-{}-{}-{}".format(
                                                        s_sample,
                                                        d_acjson[s_coor]["sample"][s_sample]["manufacture"] ,
                                                        re.sub("[^a-zA-Z0-9]", "", d_acjson[s_coor]["sample"][s_sample]["catalogNu"]),
                                                        re.sub("[^a-zA-Z0-9]", "", d_acjson[s_coor]["sample"][s_sample]["batch"]),
                                                    ))
                                            except KeyError:
                                                l_datalayer_sample.append(None)
                                        # list
                                        elif (s_leaf in {"passageOrigin", "passageUsed"}):
                                            try:
                                                l_datalayer_sample.append(str(d_acjson[s_coor]["sample"][s_sample][s_leaf]))
                                            except KeyError:
                                                l_datalayer_sample.append(None)
                                        # other leafs
                                        else:
                                            try:
                                                l_datalayer_sample.append(d_acjson[s_coor]["sample"][s_sample][s_leaf])
                                            except KeyError:
                                                l_datalayer_sample.append(None)
                                        # header
                                        if (b_header):
                                            ls_header.append("sample-{}".format(s_leaf))

                            #++ loop through perturbation axis recordsets ++#
                            for s_majorrecordset_perturbation in list_uniq_recordset(d_acjson_manipu, ts_axis=("perturbation",), b_major=True):
                                # loop through all perturbation
                                for s_perturbation, d_record_perturbation in d_acjson_manipu[s_coor]["perturbation"].items():
                                    # if perturbation axis None or perturbation member the major record set
                                    if (s_majorrecordset_perturbation is "None") or \
                                        (d_record_perturbation["recordSet"].split("-")[0] == s_majorrecordset_perturbation):

                                        # empty data layer
                                        l_datalayer_perturbation = []

                                        # perturbationaxis axis not None
                                        if (d_record_perturbation != None):

                                            # perturbation axis level
                                            if ("axisCollapsed" in es_dfleaf):
                                                # axisCollapsed leaf
                                                s_axiscollapsed = None
                                                for s_gent in d_acjson[s_coor]["perturbation"].keys():
                                                    if (s_axiscollapsed is None):
                                                        s_axiscollapsed = s_gent
                                                    else:
                                                        s_axiscollapsed += " + {}".format(s_gent)
                                            l_datalayer_perturbation.append(s_axiscollapsed)
                                            # header
                                            if (b_header):
                                                ls_header.append("perturbation-axisCollapsed")

                                            # recordset level
                                            if ("recordSetCollapsed" in es_dfleaf):
                                                # recordSetCollapsed leaf
                                                s_recordsetcollapsed = None
                                                for s_gent, d_record in d_acjson[s_coor]["perturbation"].items():
                                                    if (s_majorrecordset_perturbation is "None") or \
                                                       (d_record["recordSet"].split("-")[0] == s_majorrecordset_perturbation):
                                                        if (s_recordsetcollapsed is None):
                                                            s_recordsetcollapsed = s_gent
                                                        else:
                                                            s_recordsetcollapsed += " + {}".format(s_gent)
                                                l_datalayer_perturbation.append(s_recordsetcollapsed)
                                                # header
                                                if (b_header):
                                                    ls_header.append("perturbation-recordSetCollapsed")


                                            # real
                                            for s_leaf in ls_leaf_perturbation:
                                                # perturbation leaf
                                                if (s_leaf == "perturbation"):
                                                    l_datalayer_perturbation.append(s_perturbation)
                                                    # header
                                                    if (b_header):
                                                        ls_header.append("perturbation")
                                                # other leafs
                                                else:
                                                    # longRecord leaf
                                                    if (s_leaf == "longRecord"):
                                                        try:
                                                            l_datalayer_perturbation.append(
                                                                "{}-{}-{}-{}".format(
                                                                    s_perturbation,
                                                                    d_acjson[s_coor]["perturbation"][s_perturbation]["manufacture"] ,
                                                                    re.sub("[^a-zA-Z0-9]", "", d_acjson[s_coor]["perturbation"][s_perturbation]["catalogNu"]),
                                                                    re.sub("[^a-zA-Z0-9]", "", d_acjson[s_coor]["perturbation"][s_perturbation]["batch"]),
                                                                ))
                                                        except KeyError:
                                                            l_datalayer_perturbation.append(None)
                                                    # other leafs
                                                    else:
                                                        try:
                                                            l_datalayer_perturbation.append(d_acjson[s_coor]["perturbation"][s_perturbation][s_leaf])
                                                        except KeyError:
                                                            l_datalayer_perturbation.append(None)
                                                    # header
                                                    if (b_header):
                                                        ls_header.append("perturbation-{}".format(s_leaf))

                                        #++ loop through endpoint axis recordsets ++#
                                        for s_majorrecordset_endpoint in list_uniq_recordset(d_acjson_manipu, ts_axis=("endpoint",), b_major=True):
                                            # loop through all endpoint
                                            for s_endpoint, d_record_endpoint in d_acjson_manipu[s_coor]["endpoint"].items():
                                                # if endpoint axis None or endpoint member the major record set
                                                if (s_majorrecordset_endpoint is "None") or \
                                                    (d_record_endpoint["recordSet"].split("-")[0] == s_majorrecordset_endpoint):

                                                    # empty data layer
                                                    l_datalayer_endpoint = []

                                                    # perturbationaxis axis not None
                                                    if (d_record_endpoint != None):

                                                        # endpoint axis level
                                                        if ("axisCollapsed" in es_dfleaf):
                                                            # axisCollapsed leaf
                                                            s_axiscollapsed = None
                                                            for s_gent in d_acjson[s_coor]["endpoint"].keys():
                                                                if (s_axiscollapsed is None):
                                                                    s_axiscollapsed = s_gent
                                                                else:
                                                                    s_axiscollapsed += " + {}".format(s_gent)
                                                            l_datalayer_endpoint.append(s_axiscollapsed)
                                                            # header
                                                            if (b_header):
                                                                ls_header.append("endpoint-axisCollapsed")

                                                        # recordset level
                                                        if ("recordSetCollapsed" in es_dfleaf):
                                                            # recordSetCollapsed leaf
                                                            s_recordsetcollapsed = None
                                                            for s_gent, d_record in d_acjson[s_coor]["endpoint"].items():
                                                                if (s_majorrecordset_endpoint is "None") or \
                                                                   (d_record["recordSet"].split("-")[0] == s_majorrecordset_endpoint):
                                                                    if (s_recordsetcollapsed is None):
                                                                        s_recordsetcollapsed = s_gent
                                                                    else:
                                                                        s_recordsetcollapsed += " + {}".format(s_gent)
                                                            l_datalayer_endpoint.append(s_recordsetcollapsed)
                                                            # header
                                                            if (b_header):
                                                                ls_header.append("endpoint-recordSetCollapsed")

                                                        # real
                                                        for s_leaf in ls_leaf_endpoint:
                                                            # endpoint leaf
                                                            if (s_leaf == "endpoint"):
                                                                l_datalayer_endpoint.append(s_endpoint)
                                                                # header
                                                                if (b_header):
                                                                    ls_header.append("endpoint")
                                                            # other leafs
                                                            else:
                                                                # longRecord leaf
                                                                if (s_leaf == "longRecord"):
                                                                    try:
                                                                        l_datalayer_endpoint.append(
                                                                            "{}-{}-{}-{}".format(
                                                                                s_endpoint,
                                                                                d_acjson[s_coor]["endpoint"][s_endpoint]["manufacture"] ,
                                                                                re.sub("[^a-zA-Z0-9]", "", d_acjson[s_coor]["endpoint"][s_endpoint]["catalogNu"]),
                                                                                re.sub("[^a-zA-Z0-9]", "", d_acjson[s_coor]["endpoint"][s_endpoint]["batch"]),
                                                                            ))
                                                                    except KeyError:
                                                                        l_datalayer_endpoint.append(None)
                                                                # other leafs
                                                                else:
                                                                    try:
                                                                        l_datalayer_endpoint.append(d_acjson[s_coor]["endpoint"][s_endpoint][s_leaf])
                                                                    except KeyError:
                                                                        l_datalayer_endpoint.append(None)
                                                                # header
                                                                if (b_header):
                                                                    ls_header.append("endpoint-{}".format(s_leaf))

                                                    #++ update datastack ++#
                                                    print(f"stacked processed: {s_sample} {s_perturbation} {s_endpoint}")
                                                    ll_dataframe = []
                                                    # header
                                                    if (b_header):
                                                        ll_dataframe.append(ls_header)
                                                        b_header = False
                                                    # data
                                                    l_datalayer = copy.deepcopy(l_datalayer_preaxis)
                                                    l_datalayer.extend(l_datalayer_sample)
                                                    l_datalayer.extend(l_datalayer_perturbation)
                                                    l_datalayer.extend(l_datalayer_endpoint)
                                                    ll_dataframe.append(l_datalayer)
                                                    # append to file
                                                    with open(s_pathfile, "a", newline="") as f_csv:
                                                        o_writer = csv.writer(f_csv, delimiter=s_delimiter)
                                                        o_writer.writerows(ll_dataframe)

            # unstacked
            else:
                l_datalayer = copy.deepcopy(l_datalayer_preaxis)

                # axis level
                for s_axis in ts_ACAXIS:
                    if ("axisCollapsed" in es_dfleaf) and (d_acjson[s_coor][s_axis] != None):
                        # axisCollapsed leaf
                        s_axiscollapsed = None
                        try:
                            for s_gent in d_acjson[s_coor][s_axis].keys():
                                if (s_axiscollapsed is None):
                                    s_axiscollapsed = s_gent
                                else:
                                    s_axiscollapsed += " + {}".format(s_gent)
                        except AttributeError:
                            # bue 20180110: none case
                            pass
                        l_datalayer.append(s_axiscollapsed)
                        # header
                        if (b_header):
                            ls_header.append("{}-axisCollapsed".format(s_axis))

                    # record level of one axis
                    ls_majorrecordset = list_uniq_recordset(d_acjson, ts_axis=(s_axis,), b_major=True)

                    # loop through recordsets
                    for s_majorrecordset in ls_majorrecordset:

                        # recordset level
                        if ("recordSetCollapsed" in es_dfleaf):
                            # recordSetCollapsed leaf
                            s_recordsetcollapsed = None
                            try:
                                for s_gent, d_record in d_acjson[s_coor][s_axis].items():
                                    if (s_majorrecordset is "None") or \
                                       (d_record["recordSet"].split("-")[0] == s_majorrecordset):
                                        if (s_recordsetcollapsed is None):
                                            s_recordsetcollapsed = s_gent
                                        else:
                                            s_recordsetcollapsed += " + {}".format(s_gent)
                            except AttributeError:
                                # bue 20180110: none case
                                pass
                            l_datalayer.append(s_recordsetcollapsed)
                            # header
                            if (b_header):
                                ls_header.append("{}-{}-recordSetCollapsed".format(s_axis, s_majorrecordset))

                        # get max sample perturbation endpoints for that record of an axis
                        i_max_gent = max_record(d_acjson, ts_axis=(s_axis,), s_recordset=s_majorrecordset, b_major=True)

                        # loop through gents of a record of an axis filter by major record sets
                        i_gent = 0
                        for s_gent, d_record in d_acjson[s_coor][s_axis].items():
                            if (s_majorrecordset is "None") or (d_record["recordSet"].split("-")[0] == s_majorrecordset):
                                i_gent += 1

                                # case of sample
                                if (s_axis == "sample"):
                                    # real
                                    ls_leaf = ls_leaf_sample
                                    for s_leaf in ls_leaf:
                                        # sample leaf
                                        if (s_leaf == "sample"):
                                            l_datalayer.append(s_gent)
                                            # header
                                            if (b_header):
                                                ls_header.append("{}-{}-{}".format(s_axis, s_majorrecordset, i_gent))
                                        # other leafs
                                        else:
                                            # longRecord leaf
                                            if (s_leaf == "longRecord"):
                                                try:
                                                    l_datalayer.append(
                                                        "{}-{}-{}-{}".format(
                                                            s_gent,
                                                            d_acjson[s_coor][s_axis][s_gent]["manufacture"] ,
                                                            re.sub("[^a-zA-Z0-9]", "", d_acjson[s_coor][s_axis][s_gent]["catalogNu"]),
                                                            re.sub("[^a-zA-Z0-9]", "", d_acjson[s_coor][s_axis][s_gent]["batch"]),
                                                        ))
                                                except KeyError:
                                                    l_datalayer.append(None)
                                            # list
                                            elif (s_leaf in {"passageOrigin", "passageUsed"}):
                                                try:
                                                    l_datalayer.append(str(d_acjson[s_coor][s_axis][s_gent][s_leaf]))
                                                except KeyError:
                                                    l_datalayer.append(None)
                                            # other leafs
                                            else:
                                                try:
                                                    l_datalayer.append(d_acjson[s_coor][s_axis][s_gent][s_leaf])
                                                except KeyError:
                                                    l_datalayer.append(None)
                                            # header
                                            if (b_header):
                                                ls_header.append("{}-{}-{}-{}".format(s_axis, s_majorrecordset, i_gent, s_leaf))

                                # case off perturbation
                                elif (s_axis == "perturbation"):
                                    # real
                                    ls_leaf = ls_leaf_perturbation
                                    for s_leaf in ls_leaf:
                                        # perturbation leaf
                                        if (s_leaf == "perturbation"):
                                            l_datalayer.append(s_gent)
                                            # header
                                            if (b_header):
                                                ls_header.append("{}-{}-{}".format(s_axis, s_majorrecordset, i_gent))
                                        # other leafs
                                        else:
                                            # longRecord leaf
                                            if (s_leaf == "longRecord"):
                                                try:
                                                    l_datalayer.append(
                                                        "{}-{}-{}-{}".format(
                                                            s_gent,
                                                            d_acjson[s_coor][s_axis][s_gent]["manufacture"] ,
                                                            re.sub("[^a-zA-Z0-9]", "", d_acjson[s_coor][s_axis][s_gent]["catalogNu"]),
                                                            re.sub("[^a-zA-Z0-9]", "", d_acjson[s_coor][s_axis][s_gent]["batch"]),
                                                        ))
                                                except KeyError:
                                                    l_datalayer.append(None)
                                            # other leafs
                                            else:
                                                try:
                                                    l_datalayer.append(d_acjson[s_coor][s_axis][s_gent][s_leaf])
                                                except KeyError:
                                                    l_datalayer.append(None)
                                            # header
                                            if (b_header):
                                                ls_header.append("{}-{}-{}-{}".format(s_axis, s_majorrecordset, i_gent, s_leaf))

                                # case off endpoint
                                elif (s_axis == "endpoint"):
                                    # real
                                    ls_leaf = ls_leaf_endpoint
                                    for s_leaf in ls_leaf:
                                        # endpoint leaf
                                        if (s_leaf == "endpoint"):
                                            l_datalayer.append(s_gent)
                                            # header
                                            if (b_header):
                                                ls_header.append("{}-{}-{}".format(s_axis, s_majorrecordset, i_gent))
                                        # other leafs
                                        else:
                                            # longRecord leaf
                                            if (s_leaf == "longRecord"):
                                                try:
                                                    l_datalayer.append(
                                                        "{}-{}-{}-{}".format(
                                                            s_gent,
                                                            d_acjson[s_coor][s_axis][s_gent]["manufacture"] ,
                                                            re.sub("[^a-zA-Z0-9]", "", d_acjson[s_coor][s_axis][s_gent]["catalogNu"]),
                                                            re.sub("[^a-zA-Z0-9]", "", d_acjson[s_coor][s_axis][s_gent]["batch"]),
                                                        ))
                                                except KeyError:
                                                    l_datalayer.append(None)
                                            # other leafs
                                            else:
                                                try:
                                                    l_datalayer.append(d_acjson[s_coor][s_axis][s_gent][s_leaf])
                                                except KeyError:
                                                    l_datalayer.append(None)
                                            # header
                                            if (b_header):
                                                ls_header.append("{}-{}-{}-{}".format(s_axis, s_majorrecordset, i_gent, s_leaf))
                                else:
                                    sys.exit(ds_error["unknown_acxis"].format(s_axis, ts_ACAXIS))

                        # empty
                        for i_empty in range(i_gent, i_max_gent):
                            i_empty += 1
                            # data
                            for s_leaf in ls_leaf:
                                l_datalayer.append(None)
                                # header
                                if (b_header):
                                    ls_header.append("{}-{}-{}-{}".format(s_axis, s_majorrecordset, i_empty, s_leaf))

                # update data stack
                ll_dataframe = []
                # header
                if (b_header):
                    b_header = False
                    ll_dataframe.append(ls_header)
                # data
                ll_dataframe.append(l_datalayer)
                # append matrix to tsv file
                with open(s_pathfile, "a", newline="") as f_csv:
                    o_writer = csv.writer(f_csv, delimiter=s_delimiter)
                    o_writer.writerows(ll_dataframe)
                # display output
                print(f"unstacked processed: {l_datalayer}")

    # output
    return(s_pathfile)


'''
if __name__ == "__main__":
    # this code is only executed if file is run as script
    # will not be executed if imported as library
    # kind of develpment and pre test code
    pass
'''
