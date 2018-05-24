class Bank:
    def __init__(self, name, slug, code, segment_position_identifier=None, segment_identifier_length=1, segment_header_identifier_name=None):
        self.name = name
        self.slug = slug
        self.code = code
        self.available_segments = dict()
        self.segment_position_identifier = segment_position_identifier
        self.segment_identifier_length = segment_identifier_length
        self.segment_header_identifier_name = segment_header_identifier_name
    
    def set_segment(self, segment_name, segment_class, payment_types=dict(), segment_alias=None):
        params = dict(
            segment_name = segment_name,
            segment_class = segment_class,
            payment_types = payment_types,
        )

        if segment_alias:
            params['segment_alias'] = segment_alias
        else:
            params['segment_alias'] = segment_name
        
        self.available_segments[segment_name] = params
    
    def get_file_header(self):
        pass
    
    def get_file_footer(self):
        pass

    def get_segment(self, segment):
        pass
    
    def get_payment_segment(self, payment_type):
        for segment_name, segment_dict in self.available_segments.items():
            if payment_type in [*segment_dict['payment_types']]:
                return segment_dict
        raise Exception('Payment Type not Found')
    
    def identify_payment_segment(self, payment_line, payment_header_line):
        # check segment position identifier and segment header identifier name
        if not self.segment_position_identifier or not self.segment_header_identifier_name:
            return None
        
        # for each available segment...
        for segment_name, segment_data in self.available_segments.items():
            # ... check if payment line has segment alias
            if payment_line[self.segment_position_identifier:(self.segment_position_identifier + self.segment_identifier_length)] == segment_data['segment_alias']:
                # get segment class
                segment_class = segment_data['segment_class']

                # get segment class header
                segment_header = segment_class().header

                # fill segment header from payment header line
                segment_header.set_attributes_from_line(payment_header_line)

                for type_name, type_value in segment_data['payment_types'].items():
                    if type_value is None:
                        return segment_data
                    elif type_value == segment_header.attributes[self.segment_header_identifier_name].value:
                        return segment_data
