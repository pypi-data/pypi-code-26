from pydoc import locate
from datetime import datetime
from pg_cnab240.payment import Payment
import os
import random


class File:
    def __init__(self, bank, company=None, payments=[]):
        self.company = company
        self.payments = payments

        self.bank = self.import_bank(bank)
        self.header = self.import_header()
        self.footer = self.import_footer()
        self.body = []
        self.lots_quantity = 1
        self.lines = []
        self.line_cursor = 0
    
    def import_bank(self, bank):
        bankClassFile =  locate('pg_cnab240.banks.' + bank + '.' + bank)
        bankClass = getattr(bankClassFile, bank)
        return bankClass()

    def import_header(self):
        return self.bank.get_file_header()
    
    def import_footer(self):
        return self.bank.get_file_footer()
    
    def verify(self):
        if self.header is None or self.footer is None:
            raise Exception('Header and Footer cannot be None')
        return True
    
    def add_payment(self, payment):
        self.payments.append(payment)
    
    def process_payments(self):
        for payment in self.payments:
            register_number = 1
            
            # get bank payment segment
            payment_segment = self.bank.get_payment_segment(payment.get_attribute('type'))
            segment = payment_segment['segment_class']()

            # set bank and company
            segment.set_bank(self.bank)
            segment.set_company(self.company)

            # attr payment attributes
            segment_data = payment.attributes
            segment_data['payment_way'] = payment_segment['payment_types'][payment.get_attribute('type')]
            
            # set custom segment attributes
            segment_data['lot_code'] = self.lots_quantity
            segment_data['register_number'] = register_number
            segment.set_data(segment_data)

            # check header
            if hasattr(segment, 'get_header_line'):
                self.body.append(segment.get_header_line())
            
            self.body.append(segment.to_line())

            # check footer
            if hasattr(segment, 'get_footer_line'):
                self.body.append(segment.get_footer_line())

            # increment lots_quantity
            self.lots_quantity += 1

    def generate(self, file_path=None, file_name=None):
        self.verify()

        # add header line
        self.lines.append(self.header.to_line())

        # process payments
        self.process_payments()

        for line in self.body:
            self.lines.append(line)

        # populate footer
        self.footer.set_data(dict(
            lots_quantity = self.lots_quantity - 1,
            registers_quantity = ((self.lots_quantity - 1) * 3) + 2,
        ))

        # add footer line
        self.lines.append(self.footer.to_line())

        if file_path:
            return self.save_file(file_path, file_name)

        return True
    
    def read_file_content(self, file_content=""):
        if not file_content:
            raise Exception('File content cannot be empty.')
        
        # split file in lines
        self.lines = file_content.splitlines()

        line_index = 0
        payment_header_line = None
        for line in self.lines:
            if line_index == 0:
                # header
                self.header.set_attributes_from_line(line)
                if hasattr(self.header, 'extract_company'):
                    self.company = self.header.extract_company()
            elif line_index == (len(self.lines) - 1):
                # footer
                self.footer.set_attributes_from_line(line)
                pass
            else:
                # payments
                if line[8] == 'C':
                    payment_header_line = line
                if line[8] != 'C' and line[8] != ' ':
                    # get payment segment data
                    payment_segment_data = self.bank.identify_payment_segment(line, payment_header_line)
                    if not payment_segment_data:
                        raise Exception('Cannot identify payment segment: ' + payment_header_line + ', ' + line)
                    
                    # get segment class
                    segment_class = payment_segment_data['segment_class']
                    payment_segment = segment_class()
                    payment_segment.set_attributes_from_line(line)
                    
                    payment = Payment()
                    for attr_name, attr_value in payment_segment.get_dict().items():
                        payment.set_attribute(attr_name, attr_value)
                    
                    self.payments.append(payment)
            
            line_index += 1
    
    def get_content(self):
        content = ""
        for line in self.lines:
            if content:
                content += "\n"
            content += line
        return content
    
    def save_file(self, file_path, file_name):
        # check file name
        if not file_name:
            file_name = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S_") + str(random.randint(0, 10000) * 5) + '.rem'
        
        file_full_path = os.path.join(file_path, file_name)
        f = open(file_full_path, 'w')
        f.write(self.get_content())
        f.close()

        return file_full_path
    
    def next_line(self, append_line_break=False):
        if self.line_cursor > (len(self.lines) - 1):
            return None
        
        line = ""

        if append_line_break and self.line_cursor > 0:
            line += "\n"
        
        line += self.lines[self.line_cursor]
        
        self.line_cursor += 1
        return line
    
    def read(self, file_content):
        self.verify()
        pass
