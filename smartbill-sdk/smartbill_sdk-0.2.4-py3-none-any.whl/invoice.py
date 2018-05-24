import json
import requests

class InvoiceSmartBill(object):

    def create_client(self, name_client, country_client, vat_code_client=None, is_tax_payer_client=None,
                      address_client=None, city_client=None, email_client=None, save_to_db_client=None):

        if save_to_db_client is None:
            save_to_db_client = self.save_to_db

        return {"name": name_client,
                "vatCode": vat_code_client,
                "isTaxPayer": is_tax_payer_client,
                "address": address_client,
                "city": city_client,
                "country": country_client,
                "email": email_client,
                "saveToDb": save_to_db_client
                }

    def create_product(self, name_product, code, measuring_unit_name, quantify, price,
                       is_tax_included, tax_name, tax_percentage, is_service, currency=None, is_discount=False,
                       save_to_db_product=None, use_stock=None, ware_house_name=None):
        if use_stock is None:
            use_stock = self.use_stock

        if save_to_db_product is None:
            save_to_db_product = self.save_to_db

        if currency is None:
            currency = self.currency

        product = {"name": name_product,
                   "isDiscount": is_discount,
                   "code": code,
                   "measuringUnitName": measuring_unit_name,
                   "currency": currency,
                   "quantity": quantify,
                   "price": price,
                   "isTaxIncluded": is_tax_included,
                   "taxName": tax_name,
                   "taxPercentage": tax_percentage,
                   "isService": is_service,
                   "saveToDb": save_to_db_product
                   }
        if not is_service:
            if use_stock:
                product.update({'warehouseName':ware_house_name})
        return product

    def create_partial_payment(self, value, payment_series=None, type='Alta incasare', is_cash=False):
        return {'value': value,
                'paymentSeries': payment_series,
                'type': type,
                'isCash':is_cash}

    def create_all_payment(self, products, *args, **kwargs):
        value_all = 0

        for product in products:
            if product['isTaxIncluded']:
                value_all += product['quantity'] * product['price']
            else:
                value_all += product['quantity'] * product['price'] * float(product['taxPercentage'] + 100)/100
        return self.create_partial_payment(value_all, **kwargs)

    def create_invoice(self, client, products, issue_date, currency=None, series_number=None, is_draft=False,
                       due_date=None, delivery_date=None, use_stock=None, payment=None):

        if use_stock is None:
            use_stock = self.use_stock

        if currency is None:
            currency = self.currency

        if series_number is None:
            series_number = self.get_series()['list'][0]['name']

        data = {"companyVatCode": self.smartbill_ciff,
                "client": client,
                "issueDate": issue_date,
                "seriesName": series_number,
                'currency': currency,
                "isDraft": is_draft,
                "dueDate": due_date,
                "deliveryDate": delivery_date,
                "products": products,
                'useStock': use_stock,
                'payment': payment,
              }
        data = json.dumps(data)
        response = requests.post(f"{self.base_url}/invoice", headers=self.headers, data=data)
        return response.json()

    def get_invoice(self, series, nr):
        params = {'cif': self.smartbill_ciff,
                  'seriesname': series,
                  'number': nr}
        response = requests.get(f"{self.base_url}/invoice/pdf", headers=self.headers, params=params)
        return response

    def get_invoice_paymentstatus(self, series, nr):
        params = {'cif': self.smartbill_ciff,
                  'seriesname': series,
                  'number': nr}
        response = requests.get(f"{self.base_url}/invoice/paymentstatus", headers=self.headers, params=params)
        return response.json()

    def cancel_invoice(self, series, nr):
        params = {'cif': self.smartbill_ciff,
                  'seriesname': series,
                  'number': nr}
        response = requests.put(f"{self.base_url}/invoice/cancel", headers=self.headers, params=params)
        return response.json()

    def restore_invoice(self, series, nr):
        params = {'cif': self.smartbill_ciff,
                  'seriesname': series,
                  'number': nr}
        response = requests.put(f"{self.base_url}/invoice/restore", headers=self.headers, params=params)
        return response.json()
