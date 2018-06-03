from igamelister.amiga.region import Region


class Publisher:
    def __init__(self, name: str, region: str = None):
        self.name = name
        self._region = region

    @property
    def region(self):
        if self._region is None:
            return Region.Unused
        elif self._region == "Worldwide":
            return Region.Worldwide
        elif self._region == "Argentina":
            return Region.Argentina
        elif self._region == "Armenia":
            return Region.Armenia
        elif self._region == "Australasia":
            return Region.Australasia
        elif self._region == "Australia":
            return Region.Australia
        elif self._region == "Austria":
            return Region.Austria
        elif self._region == "Belgium":
            return Region.Belgium
        elif self._region == "Bosnia-Herzegovina":
            return Region.BosniaHerzegovina
        elif self._region == "Brazil":
            return Region.Brazil
        elif self._region == "Bulgaria":
            return Region.Bulgaria
        elif self._region == "Canada":
            return Region.Canada
        elif self._region == "Croatia":
            return Region.Croatia
        elif self._region == "Czech Republic":
            return Region.CzechRepublic
        elif self._region == "Denmark":
            return Region.Denmark
        elif self._region == "Estonia":
            return Region.Estonia
        elif self._region == "Europe":
            return Region.Europe
        elif self._region == "Finland":
            return Region.Finland
        elif self._region == "France":
            return Region.France
        elif self._region == "Germany":
            return Region.Germany
        elif self._region == "Greece":
            return Region.Greece
        elif self._region == "Hungary":
            return Region.Hungary
        elif self._region == "Iran":
            return Region.Iran
        elif self._region == "Iraq":
            return Region.Iraq
        elif self._region == "Ireland":
            return Region.Ireland
        elif self._region == "Israel":
            return Region.Israel
        elif self._region == "Italy":
            return Region.Italy
        elif self._region == "Jamaica":
            return Region.Jamaica
        elif self._region == "Japan":
            return Region.Japan
        elif self._region == "Liechtenstein":
            return Region.Liechtenstein
        elif self._region == "Mexico":
            return Region.Mexico
        elif self._region == "New Zealand":
            return Region.NewZealand
        elif self._region == "North America":
            return Region.NorthAmerica
        elif self._region == "Norway":
            return Region.Norway
        elif self._region == "Peru":
            return Region.Peru
        elif self._region == "Poland":
            return Region.Poland
        elif self._region == "Portugal":
            return Region.Portugal
        elif self._region == "Rest of Europe":
            return Region.RestOfEurope
        elif self._region == "Rest of the World":
            return Region.RestOfTheWorld
        elif self._region == "Romania":
            return Region.Romania
        elif self._region == "Russia":
            return Region.Russia
        elif self._region == "Serbia":
            return Region.Serbia
        elif self._region == "Slovakia":
            return Region.Slovakia
        elif self._region == "Slovenia":
            return Region.Slovenia
        elif self._region == "South Africa":
            return Region.SouthAfrica
        elif self._region == "Spain":
            return Region.Spain
        elif self._region == "Sweden":
            return Region.Sweden
        elif self._region == "Switzerland":
            return Region.Switzerland
        elif self._region == "The Netherlands":
            return Region.TheNetherlands
        elif self._region == "Turkey":
            return Region.Turkey
        elif self._region == "United Kingdom":
            return Region.UnitedKingdom
        elif self._region == "Uruguay":
            return Region.Uruguay
        elif self._region == "USA":
            return Region.USA
        else:
            return Region.Unknown
