from pg_cnab240.banks.bank import Bank
from pg_cnab240.banks.itau.file_header import FileHeader
from pg_cnab240.banks.itau.file_footer import FileFooter
from pg_cnab240.banks.itau.segments.A import SegmentA, SegmentANF
from pg_cnab240.banks.itau.segments.J import SegmentJ


class itau(Bank):
    def __init__(self):
        super().__init__('Itaú', 'itau', 341, 13, 1, 'payment_way')
        super().set_segment('J', SegmentJ, {
            'slip': '30',
            'other_bank_slip': '31',
        })
        super().set_segment('A', SegmentA, {
            'cc': '01',
            'admin_check': '02',
            'doc': '03',
            'poupanca': '05',
            'ccd': '06',
            'docd': '07',
            'normal_darf': '16',
            'simple_darf': '18',
            'gps': '17',
            'city_taxs': '19',
            'darj': '21',
            'gare': '22',
            'ipva': '25',
            'dpvat': '27',
            'billing_title': '30',
            'billing_title_other_bank': '31',
            'fiscal_note': '32',
            'fgts': '35',
            'ted': '41',
            'tedd': '43',
            'gnre': '91',
        })
        super().set_segment('ANF', SegmentANF, {
            'nf': None,
        }, 'A')
    
    def get_file_header(self):
        file_header = FileHeader()
        file_header.set_bank(self)
        return file_header
    
    def get_file_footer(self):
        file_footer = FileFooter()
        file_footer.set_bank(self)
        return file_footer
    
    def get_company_document_id(self, document_type):
        if document_type == 'cnpj':
            return 2
        return 1 # cpf
