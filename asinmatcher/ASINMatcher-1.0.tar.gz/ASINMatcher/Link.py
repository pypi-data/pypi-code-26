import Region, Check_Url, Check_pattern


class Link:
    def __init__(self, link_string):
        self._link_string = link_string
        self._is_valid = False
        self._region = ''
        self._id = ''
        self._id_type = ''

# region get methods
    def get_valid(self):
        return self._is_valid

    def get_region(self):
        return self._region

    def get_id(self):
        return self._id

    def get_id_type(self):
        return self._id_type
# end region


# region set methods
    def _set_is_valid(self):
        self._is_valid = Check_pattern.check_url_pattern(self._link_string) and Check_Url.check_url(self._link_string)

    def _set_region(self):
        if self._is_valid:
            try:
                link_list = self._link_string.split('/')
                region_string = link_list[2]
                self._region = Region.region_dict[region_string.split('.')[-1].upper()]
            except:
                self._region = ''

    def _set_id(self):
        if self._is_valid:
            try:
                link_list = self._link_string.split('/')
                if 'dp' in link_list:
                    self._id = link_list[link_list.index('dp') + 1]
                elif 'gp' in link_list:
                    self._id = link_list[link_list.index('gp') + 2]
                else:
                    self._id = link_list[link_list.index('d') + 3]
            except:
                self. _id = ''

    # depends on product id
    def _set_id_type(self):
        if self._is_valid and self._id != '':
            prod_id = self._id
            try:
                if (len(prod_id) == 10 or len(prod_id) == 13) and re.match(r'[0-9]+', prod_id):
                    self._id_type = "ISBN"
                elif len(prod_id) == 10 and re.match(r'[A-Z0-9]', prod_id):
                    self._id_type = "ASIN"
            except:
                self._id_type = ''

    def set_details(self):
        self._set_is_valid()
        self._set_region()
        self._set_id()
        self._set_id_type()
# end region
