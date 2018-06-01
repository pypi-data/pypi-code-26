import re
import json

class Convertor(object):

    def gais2json(self, records=[], rec_beg='', spec_fields=None):
        """ Convert GAIS record to JSON format.  
        {records} is an array of 'field-value' pairs.
        """

        if not rec_beg or not rec_beg.strip():
            raise ValueError('rec_beg cannot be empty value.')
        elif not isinstance(records, list):
            raise ValueError('records is an array of \'field-value\' pairs.')
        else:
            items = []
            data = {}
            prev_field = ""		# previous field, for multiple lines content

            regex_field = re.compile(r'^@[\w\.]+:')
            for rec in records:
                if re.match('^' + rec_beg + '$', rec):
                    if data:
                        items.append(data)
                    data = {}
                    prev_field = ""
                elif regex_field.search(rec):
                    # GAIS format: @{field}:{content}
                    field = re.sub('[@:]', '', regex_field.search(rec).group(0))

                    # 不指定欄位 or field in spec_fields
                    if not spec_fields or field in spec_fields:
                        prev_field = field
                        content = rec.split('@' + field + ':')[1]

                        # if content is a JSON string, convert to JSON object
                        try:
                            content = json.loads(content)
                        except ValueError:
                            pass

                        """
                        nested object, 最多2層
                        @data.body => {"data": {"body": "..."}}
                        @data.location.lat => {"data": {"location": {"lat": 123}}}
                        @data.info.location.lat => VauleError
                        """
                        if '.' in field:
                            nested_key = field.split('.')
                            length = len(nested_key)
    
                            # Initialize
                            if nested_key[0] not in data:
                                data[nested_key[0]] = {}

                            if length == 2:
                                data[nested_key[0]][nested_key[1]] = content
                            elif length == 3:
                                if nested_key[1] not in data[nested_key[0]]:
                                    data[nested_key[0]][nested_key[1]] = {}

                                data[nested_key[0]][nested_key[1]][nested_key[2]] = content
                            else:
                                raise ValueError('Wrong field name. (%s)' % field)
                        else:
                            data[field] = content
                    else:
                        # 指定欄位 and field not in spec_fields, append to previous field
                        print('*** Not in spec field ***\nfield: %s\nprev_field:%s' % (field, prev_field))

                        if '.' in prev_field:
                            nested_key = prev_field.split('.')
                            length = len(nested_key)

                            if length == 2:
                                new_content = str(data[nested_key[0]][nested_key[1]]) + '\n' + str(rec)
                                data[nested_key[0]][nested_key[1]] = new_content
                            elif length == 3:
                                new_content = str(data[nested_key[0]][nested_key[1]][nested_key[2]]) + '\n' + str(rec)
                                data[nested_key[0]][nested_key[1]][nested_key[2]] = new_content
                        else:
                            new_content = str(data[prev_field]) + '\n' + str(rec)
                            data[prev_field] = new_content
                        
                elif rec.strip():
                    # Not empty line, append to previous field
                    if '.' in prev_field:
                        nested_key = prev_field.split('.')
                        length = len(nested_key)

                        if length == 2:
                            new_content = str(data[nested_key[0]][nested_key[1]]) + '\n' + str(rec)
                            data[nested_key[0]][nested_key[1]] = new_content
                        elif length == 3:
                            new_content = str(data[nested_key[0]][nested_key[1]][nested_key[2]]) + '\n' + str(rec)
                            data[nested_key[0]][nested_key[1]][nested_key[2]] = new_content
                    else:
                        new_content = str(data[prev_field]) + '\n' + str(rec)
                        data[prev_field] = new_content

            # Last one record
            if data:
                items.append(data)
            return items

    def json2gais(self, records):
        """ Convert JSON object to GAIS record. 
        {records} is an object or a list of object.
        """

        if not isinstance(records, list) and not isinstance(records, dict):
            raise ValueError('records must be an object or a list of objects')
        elif isinstance(records, dict):
            records = [records]
        
        rec_beg = "@GAIS:"
        gais_rec = ""
        for rec in records:
            gais_rec += rec_beg + '\n'

            # First level
            keys_1st = rec.keys()
            for key1 in keys_1st:
                # Nested, second level
                if isinstance(rec[key1], dict):
                    keys_2nd = rec[key1].keys()
                    for key2 in keys_2nd:
                        # Nested, third level
                        if isinstance(rec[key1][key2], dict):
                            keys_3rd = rec[key1][key2].keys()
                            for key3 in keys_3rd:
                                # Nested, fourth level, convert to JSON string
                                if isinstance(rec[key1][key2][key3], dict):
                                    gais_rec += '@' + key1 + '.' + key2 + '.' + key3 + ':' + json.dumps(rec[key1][key2][key3]) + '\n'
                                else:
                                    gais_rec += '@' + key1 + '.' + key2 + '.' + key3 + ':' + str(rec[key1][key2][key3]) + '\n'
                        else:
                            gais_rec += '@' + key1 + '.' + key2 + ':' + str(rec[key1][key2]) + '\n'
                else:
                    gais_rec += '@' + key1 + ':' + str(rec[key1]) + '\n'
            
        return gais_rec
    