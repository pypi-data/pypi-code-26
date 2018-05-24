#!/usr/bin/env python

headers = "WRT;WLV;WST;WSO;DVS;TEMP;PMRES"
raw_data = ["111.35897;72.383331;38.975636;0.0000000;5.69523834E-02;8.3000002;1.3910484",
            "123.99798;80.925438;43.516457;0.0000000;0.12485714;8.7500000;1.6017523",
            "128.22073;84.300674;45.214600;0.0000000;0.15404762;-7.1499996;0.55252564",
            "128.22073;84.300674;45.214600;0.0000000;0.15647618;3.4000001;1.1479926",
            "128.22073;84.300674;45.214600;0.0000000;0.17847620;6.5500002;1.4281162",
            "153.02798;113.16146;58.116299;0.0000000;0.24814285;7.7500000;1.9849979",
            "168.40706;134.48489;67.464432;0.0000000;0.27128565;-2.5000000;1.1256766",
            "168.79504;135.14352;67.803787;0.0000000;0.30457136;1.0500000;1.4455550",
            "169.27014;136.08443;68.344070;0.0000000;0.33757135;7.4000001;2.2576878",
            "211.83162;238.56105;135.54535;0.0000000;0.39976186;3.2500000;2.7386796",
            "215.23181;249.13504;144.83624;0.0000000;0.47080943;12.900000;5.5654893",
            "257.93060;389.41046;283.97189;0.0000000;0.53342855;2.0500002;4.0368190",
            "299.75705;526.21100;519.57135;0.0000000;0.63933337;21.150000;21.500204",
            "410.67249;880.49255;1645.3977;0.0000000;0.77252388;12.100000;23.414831",
            "495.00140;1102.7692;3192.3433;0.0000000;0.87857145;11.850000;35.527500",
            "544.23639;1143.2697;4697.2012;227.33698;0.99214298;22.549999;97.201683",
            "575.41620;1069.3918;4732.9390;2415.8425;1.1477001;13.850000;62.727901",
            "577.34735;1009.2563;4732.9390;3996.4629;1.3361501;24.049999;140.34402",
            "554.48444;872.58844;4545.5146;5203.7261;1.5659001;19.950001;109.02146",
            "453.05417;576.92432;3714.0168;5883.3008;1.7616501;19.549999;95.027321",
            "370.17822;132.01065;3034.6218;5941.8218;1.9223001;14.800000;56.437428"]
class Container(object):
    pass

header_names = headers.split(";")
respiration_testdata = []
for strline in raw_data:
    vline = strline.split(";")
    c = Container()
    for hname, value in zip(header_names, vline):
        setattr(c, hname, float(value))
    respiration_testdata.append(c)
