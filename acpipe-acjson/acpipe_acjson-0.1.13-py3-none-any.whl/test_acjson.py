import copy
import sys
import unittest
import acpipe_acjson.acjson as ac


class TestAcjsonRetype(unittest.TestCase):
    """ retype function testing"""
    def test_retype_bool(self):
        self.assertTrue(type(ac.retype(False)) == bool)
        self.assertTrue(type(ac.retype(True)) == bool)
        self.assertTrue(type(ac.retype("False")) == bool)
        self.assertTrue(type(ac.retype("True")) == bool)

    def test_retype_int(self):
        self.assertTrue(type(ac.retype(0)) == int)
        self.assertTrue(type(ac.retype("0")) == int)

    def test_retype_real(self):
        self.assertTrue(type(ac.retype(0.1)) == float)
        self.assertTrue(type(ac.retype("0.1")) == float)
        self.assertTrue(type(ac.retype("0E-1")) == float)

    def test_retype_complex(self):
        self.assertTrue(type(ac.retype(1+1j)) == complex)
        self.assertTrue(type(ac.retype("1+1j")) == complex)

    def test_retype_string(self):
        self.assertTrue(type(ac.retype("bue")) == str)


class TestAcjsonEscoor(unittest.TestCase):
    def test_escoor(self):
        d_acjson = ac.acbuild(
            s_runid="abc",
            s_runtype="testacjson",
            s_welllayout="2x2",
            ti_spotlayout=(1,2,3)
        )
        es_coor = set([str(i) for i in range(1,25)])
        self.assertEqual(ac.escoor(d_acjson), es_coor)


class TestAcjsonIcoormax(unittest.TestCase):
    def test_icoormax(self):
        d_acjson = ac.acbuild(
            s_runid="abc",
            s_runtype="testacjson",
            s_welllayout="2x2",
            ti_spotlayout=(1,2,3)
        )
        self.assertEqual(ac.icoormax(d_acjson), 24)


class TestAcjsonIspotmax(unittest.TestCase):
    def test_ispotmax(self):
        self.assertEqual(ac.ispotmax((1,2,3)), 6)
        self.assertEqual(ac.ispotmax((3,3,3)), 9)


class TestAcjsonIspot(unittest.TestCase):
    def test_ispot(self):
        self.assertEqual(ac.ispot(i_yy=2, i_xx=2, ti_spotlayout=(1,2,3)), 3)
        self.assertEqual(ac.ispot(i_yy=2, i_xx=2, ti_spotlayout=(3,3,3)), 5)


class TestAcjsonXy2icoor(unittest.TestCase):
    def test_xy2icoor(self):
        i_coor = ac.xy2icoor(
            i_y=2,
            i_x=2,
            s_welllayout="4x4",
            i_yy=2,
            i_xx=2,
            ti_spotlayout=(4,4,4,4)
        )
        self.assertEqual(i_coor, 86)


class TestAcjsonRelabel(unittest.TestCase):
    def test_relable(self):
        s_acid = "testacjson-xyz_ac.json"
        # build
        d_acjson = ac.acbuild(
            s_runid="abc",
            s_runtype="testacjson",
            s_welllayout="2x2",
            ti_spotlayout=(1,2,3)
        )
        self.assertNotEqual(d_acjson["acid"], s_acid)
        self.assertIsNone(d_acjson["log"])
        # relable
        ac.acrelabel(
            s_runid="xyz",
            s_log="relable",
            d_iacjson=d_acjson,
            s_runtype="testacjson")
        self.assertEqual(d_acjson["acid"], s_acid)
        self.assertEqual(d_acjson["log"], "relable")


class TestAcjsonBuild(unittest.TestCase):
    """ basic acjson methods unittest """
    def test_acbuild_well(self):
        # ok
        d_okwell = {
            "acid": "testacjson-abc_ac.json",
            "runtype": "testacjson",
            "runid": "abc",
            "welllayout": "2x2",
            "spotlayout": (1,),
            "log": None,
            "1": {
                "endpoint": None,
                "perturbation": None,
                "sample": None,
                "ixi": "1x1",
                "iixii": "1_1x1_1",
                "sxi": "Ax1"
            },
            "2": {
                "endpoint": None,
                "perturbation": None,
                "sample": None,
                "ixi": "1x2",
                "iixii": "1_1x2_1",
                "sxi": "Ax2"
            },
            "3": {
                "endpoint": None,
                "perturbation": None,
                "sample": None,
                "ixi": "2x1",
                "iixii": "2_1x1_1",
                "sxi": "Bx1"
            },
            "4": {
                "endpoint": None,
                "perturbation": None,
                "sample": None,
                "ixi": "2x2",
                "iixii": "2_1x2_1",
                "sxi": "Bx2"
            }
        }
        # build
        d_buildwell = ac.acbuild(
            s_runid="abc",
            s_runtype="testacjson",
            s_welllayout="2x2",
        )
        # assert
        self.assertEqual(d_okwell, d_buildwell)


    def test_acbuild_spot(self):
        # ok
        d_okspot = {
            "acid": "testacjson-abc_ac.json",
            "runtype": "testacjson",
            "runid": "abc",
            "welllayout": "1x1",
            "spotlayout": (1,2),
            "log": None,
            "1": {
                "endpoint": None,
                "perturbation": None,
                "sample": None,
                "ixi": "1x1",
                "iixii": "1_1x1_1",
                "sxi": "Ax1"
            },
            "2": {
                "endpoint": None,
                "perturbation": None,
                "sample": None,
                "ixi": "1x1",
                "iixii": "1_2x1_1",
                "sxi": "Ax1"
            },
            "3": {
                "endpoint": None,
                "perturbation": None,
                "sample": None,
                "ixi": "1x1",
                "iixii": "1_2x1_2",
                "sxi": "Ax1"
            }
        }
        # build
        d_buildspot = ac.acbuild(
            s_runid="abc",
            s_runtype="testacjson",
            s_welllayout="1x1",
            ti_spotlayout=(1,2)
        )
        # assert
        self.assertEqual(d_okspot, d_buildspot)


class TestAcjsonFuseAxisRecord(unittest.TestCase):
    def test_acfuseaxisrecord(self):
        # ok
        d_okfuseaxis = {
            "acid": "testacjson-abc_ac.json",
            "runtype": "testacjson",
            "runid": "abc",
            "welllayout": "1x1",
            "spotlayout": (1,),
            "log": None,
            "1": {
                "endpoint": None,
                "perturbation": None,
                "sample": {
                    "abc" : {
                        "conc": None ,
                        "concUnit": None,
                        "timeBegin": None,
                        "timeEnd": None,
                        "timeUnit": "infinity"
                    },
                    "def" : {
                        "conc": None ,
                        "concUnit": None,
                        "timeBegin": None,
                        "timeEnd": None,
                        "timeUnit": None
                    }
                },
                "ixi": "1x1",
                "iixii": "1_1x1_1",
                "sxi": "Ax1"
            }
        }
        # build
        d_acjson = ac.acbuild(
            s_runid="abc",
            s_runtype="testacjson",
            s_welllayout="1x1",
        )
        d_record = {"abc": copy.deepcopy(ac.d_RECORD)}
        ac.acfuseaxisrecord(
            d_acjson=d_acjson,
            s_coor="1",
            s_axis="sample",
            d_record=d_record
        )
        d_record["abc"].update({"timeUnit": "infinity"})
        ac.acfuseaxisrecord(
            d_acjson=d_acjson,
            s_coor="1",
            s_axis="sample",
            d_record=d_record,
            s_ambiguous="update",
        )
        d_record = {"def": copy.deepcopy(ac.d_RECORD)}
        ac.acfuseaxisrecord(
            d_acjson=d_acjson,
            s_coor="1",
            s_axis="sample",
            d_record=d_record
        )
        # assert
        self.assertEqual(d_okfuseaxis, d_acjson)

class TestAcjsonFuseWellRecord(unittest.TestCase):
    def test_acfusewellrecord(self):
        # ok
        d_okfusewell = {
            "acid": "testacjson-abc_ac.json",
            "runtype": "testacjson",
            "runid": "abc",
            "welllayout": "1x1",
            "spotlayout": (1,),
            "log": None,
            "1": {
                "endpoint": {
                    "end1" : {
                        "conc": None ,
                        "concUnit": None,
                        "timeBegin": None,
                        "timeEnd": None,
                        "timeUnit": None
                    },
                    "end2" : {
                        "conc": None ,
                        "concUnit": None,
                        "timeBegin": None,
                        "timeEnd": None,
                        "timeUnit": None
                    },
                },
                "perturbation": {
                    "pertu1" : {
                        "conc": None ,
                        "concUnit": None,
                        "timeBegin": None,
                        "timeEnd": None,
                        "timeUnit": None
                    },
                    "pertu2" : {
                        "conc": None ,
                        "concUnit": None,
                        "timeBegin": None,
                        "timeEnd": None,
                        "timeUnit": None
                    },
                },
                "sample": {
                    "sam1" : {
                        "conc": None ,
                        "concUnit": None,
                        "timeBegin": None,
                        "timeEnd": None,
                        "timeUnit": None
                    },
                    "sam2" : {
                        "conc": None ,
                        "concUnit": None,
                        "timeBegin": None,
                        "timeEnd": None,
                        "timeUnit": None
                    },
                },
                "ixi": "1x1",
                "iixii": "1_1x1_1",
                "sxi": "Ax1"
            },
        }
        # build
        d_acjson = ac.acbuild(
            s_runid="abc",
            s_runtype="testacjson",
            s_welllayout="1x1",
        )
        d_rec1 = {
            "endpoint": {"end1": copy.deepcopy(ac.d_RECORD)},
            "perturbation": { "pertu1": copy.deepcopy(ac.d_RECORD) },
            "sample": {"sam1": copy.deepcopy(ac.d_RECORD)}
        }
        d_rec2 = {
            "endpoint": {"end2": copy.deepcopy(ac.d_RECORD)},
            "perturbation": { "pertu2": copy.deepcopy(ac.d_RECORD) },
            "sample": {"sam2": copy.deepcopy(ac.d_RECORD)}
        }
        ac.acfusewellrecord(
            d_acjson=d_acjson,
            s_coor="1",
            d_record=d_rec1
        )
        ac.acfusewellrecord(
            d_acjson=d_acjson,
            s_coor="1",
            d_record=d_rec2
        )
        # assert
        self.assertEqual(d_okfusewell, d_acjson)

class TestAcjsonFuseRepeatRecord(unittest.TestCase):
    def setUp(self):
        self.d_major = ac.acbuild(
            s_runid="abc",
            s_runtype="testacjson",
            s_welllayout="2x2",
        )
        self.d_minor = ac.acbuild(
            s_runid="abc",
            s_runtype="testacjson",
            s_welllayout="2x1",
        )
        d_record = {"zero": copy.deepcopy(ac.d_RECORD)}
        d_record["zero"].update({"timeUnit": "infinity"})
        ac.acfuseaxisrecord(
            d_acjson=self.d_minor,
            s_coor="1",
            s_axis="sample",
            d_record=d_record,
            s_ambiguous="update",
        )
        d_record = {"one": copy.deepcopy(ac.d_RECORD)}
        d_record["one"].update({"timeUnit": "eternety"})
        ac.acfuseaxisrecord(
            d_acjson=self.d_minor,
            s_coor="2",
            s_axis="sample",
            d_record=d_record,
            s_ambiguous="update",
        )

    def test_acfuserepeat0011(self):
        # ok
        d_ok0011 = {
            'welllayout': '2x2',
            'spotlayout': (1,),
            'log': None,
            'runid': 'abc',
            'runtype': 'testacjson',
            'acid': 'testacjson-abc_ac.json',
            '1': {
                'endpoint': None,
                'perturbation': None,
                'sample': {
                    'zero': {
                        'conc': None,
                        'concUnit': None,
                        'timeBegin': None,
                        'timeEnd': None,
                        'timeUnit': 'infinity'
                    }
                },
                'ixi': '1x1',
                'iixii': '1_1x1_1',
                'sxi': 'Ax1'
            },
            '2': {
                'endpoint': None,
                'perturbation': None,
                'sample': {
                    'zero': {
                        'conc': None,
                        'concUnit': None,
                        'timeBegin': None,
                        'timeEnd': None,
                        'timeUnit': 'infinity'
                    }
                },
                'ixi': '1x2',
                'iixii': '1_1x2_1',
                'sxi': 'Ax2'
            },
            '3': {
                'endpoint': None,
                'perturbation': None,
                'sample': {
                    'one': {
                        'conc': None,
                        'concUnit': None,
                        'timeBegin': None,
                        'timeEnd': None,
                        'timeUnit': 'eternety'}
                },
                'ixi': '2x1',
                'iixii': '2_1x1_1',
                'sxi': 'Bx1'
            },
            '4': {
                'endpoint': None,
                'perturbation': None,
                'sample': {
                    'one': {
                        'conc': None,
                        'concUnit': None,
                        'timeBegin': None,
                        'timeEnd': None,
                        'timeUnit': 'eternety'
                    }
                },
                'ixi': '2x2',
                'iixii': '2_1x2_1',
                'sxi': 'Bx2'
            }
        }
        # build
        d_0011 = ac.acfuserepeat0011(
            d_acjsonmajor=self.d_major,
            d_acjsonminor=self.d_minor,
            b_deepcopy=True,
        )
        # assert
        self.assertEqual(d_ok0011, d_0011)

    def test_acfuserepeat0101(self):
        # ok
        d_ok0101 = {
            'welllayout': '2x2',
            'spotlayout': (1,),
            'log': None,
            'runid': 'abc',
            'runtype': 'testacjson',
            'acid': 'testacjson-abc_ac.json',
            '1': {
                'endpoint': None,
                'perturbation': None,
                'sample': {
                    'zero': {
                        'conc': None,
                        'concUnit': None,
                        'timeBegin': None,
                        'timeEnd': None,
                        'timeUnit': 'infinity'
                    }
                },
                'ixi': '1x1',
                'iixii': '1_1x1_1',
                'sxi': 'Ax1'
            },
            '2': {
                'endpoint': None,
                'perturbation': None,
                'sample': {
                    'one': {
                        'conc': None,
                        'concUnit': None,
                        'timeBegin': None,
                        'timeEnd': None,
                        'timeUnit': 'eternety'
                    }
                },
                'ixi': '1x2',
                'iixii': '1_1x2_1',
                'sxi': 'Ax2'
            },
            '3': {
                'endpoint': None,
                'perturbation': None,
                'sample': {
                    'zero': {
                        'conc': None,
                        'concUnit': None,
                        'timeBegin': None,
                        'timeEnd': None,
                        'timeUnit': 'infinity'}
                },
                'ixi': '2x1',
                'iixii': '2_1x1_1',
                'sxi': 'Bx1'
            },
            '4': {
                'endpoint': None,
                'perturbation': None,
                'sample': {
                    'one': {
                        'conc': None,
                        'concUnit': None,
                        'timeBegin': None,
                        'timeEnd': None,
                        'timeUnit': 'eternety'
                    }
                },
                'ixi': '2x2',
                'iixii': '2_1x2_1',
                'sxi': 'Bx2'
            }
        }
        # build
        d_0101 = ac.acfuserepeat0101(
            d_acjsonmajor=self.d_major,
            d_acjsonminor=self.d_minor,
            b_deepcopy=True,
        )
        # assert
        self.assertEqual(d_ok0101, d_0101)


class TestAcjsonFuseObject(unittest.TestCase):
    def test_acfuseobject(self):
        # ok
        d_okobj = {
            'acid': 'acpipe_acjson-testrun_ac.json',
            'runid': 'testrun',
            'runtype':'acpipe_acjson',
            'welllayout': '1x1',
            'spotlayout': (1,),
            'log': 'testacjson-sam_ac.json; testacjson-pertu_ac.json; testacjson-end_ac.json | acfuseacobj > acpipe_acjson-testrun_ac.json',
            '1': {
                'endpoint': {
                    'end': {
                        'conc': None,
                        'concUnit': None,
                        'timeBegin': None,
                        'timeEnd': None,
                        'timeUnit': None
                    }
                },
                'perturbation': {
                    'pertu': {
                        'conc': None,
                        'concUnit': None,
                        'timeBegin': None,
                        'timeEnd': None,
                        'timeUnit': None
                    }
                },
                'sample': {
                    'sam': {
                        'conc': None,
                        'concUnit': None,
                        'timeBegin': None,
                        'timeEnd': None,
                        'timeUnit': None
                    }
                },
                'ixi': '1x1',
                'iixii': '1_1x1_1',
                'sxi': 'Ax1'
            }
        }
        # build
        d_acjson = ac.acbuild(
            s_runid="abc",
            s_runtype="testacjson",
            s_welllayout="1x1",
        )
        # build sam
        d_record = {"sam": copy.deepcopy(ac.d_RECORD)}
        d_sam = ac.acfuseaxisrecord(
            d_acjson=d_acjson,
            s_coor="1",
            s_axis="sample",
            d_record=d_record,
            b_deepcopy=True,
        )
        d_sam = ac.acrelabel(
            s_runid="sam",
            s_log=d_sam["log"],
            d_iacjson=d_sam,
            s_runtype=d_sam["runtype"],
            b_deepcopy=True,
        )
        # build pertu
        d_record = {"pertu": copy.deepcopy(ac.d_RECORD)}
        d_pertu = ac.acfuseaxisrecord(
            d_acjson=d_acjson,
            s_coor="1",
            s_axis="perturbation",
            d_record=d_record,
            b_deepcopy=True,
        )
        d_pertu = ac.acrelabel(
            s_runid="pertu",
            s_log=d_pertu["log"],
            d_iacjson=d_pertu,
            s_runtype=d_pertu["runtype"],
            b_deepcopy=True,
        )
        # build end
        d_record = {"end": copy.deepcopy(ac.d_RECORD)}
        d_end = ac.acfuseaxisrecord(
            d_acjson=d_acjson,
            s_coor="1",
            s_axis="endpoint",
            d_record=d_record,
            b_deepcopy=True,
        )
        d_end = ac.acrelabel(
            s_runid="end",
            s_log=d_end["log"],
            d_iacjson=d_end,
            s_runtype=d_end["runtype"],
            b_deepcopy=True,
        )
        # fuse
        d_fuseobj = ac.acfuseobject(
            s_runid="testrun",
            d_acjsonsample=d_sam,
            d_acjsonperturbation=d_pertu,
            d_acjsonendpoint=d_end,
        )
        # assert
        self.assertEqual(d_okobj, d_fuseobj)


class TestAcjsonXray(unittest.TestCase):
    def test_xray(self):
        # ok
        d_okxray = {
            'acid': 'testacjson-abc_ac.json',
            'runid': 'abc',
            'runtype': 'testacjson',
            'welllayout': '1x1',
            'spotlayout': (1,),
            'log': None,
            '1': {
                'endpoint': None,
                'perturbation': '[list]',
                'sample': {
                    'zzz': {
                        'conc': 'value',
                        'concUnit': 'value',
                        'timeBegin': 'value',
                        'timeEnd': 'value',
                        'timeUnit': 'value'}
                },
                'ixi': '1x1',
                'iixii': '1_1x1_1',
                'sxi': 'Ax1'
            }
        }
        # build
        d_acjson = ac.acbuild(
            s_runid="abc",
            s_runtype="testacjson",
            s_welllayout="1x1",
        )
        d_record = {"zzz": copy.deepcopy(ac.d_RECORD)}
        d_record["zzz"].update({"conc": 1})
        d_record["zzz"].update({"concUnit": True})
        d_record["zzz"].update({"timeBegin": 1.1})
        d_record["zzz"].update({"timeEnd": 1+1j})
        d_record["zzz"].update({"timeUnit": "eternety"})
        ac.acfuseaxisrecord(
            d_acjson=d_acjson,
            s_coor="1",
            s_axis="sample",
            d_record=d_record,
        )
        l_record = [1, 2, 3, 4, "my", "life", "is", "a", "list"]
        ac.acfuseaxisrecord(
            d_acjson=d_acjson,
            s_coor="1",
            s_axis="perturbation",
            d_record=l_record,
        )
        d_xray = ac.xray(d_acjson)
        # assert
        self.assertEqual(d_okxray, d_xray)


class TestAcjsonFuse4To1(unittest.TestCase):
    pass

class TestAcjson2Tsv(unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()
