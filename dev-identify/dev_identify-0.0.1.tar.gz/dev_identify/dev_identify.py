import requests
import json
import re
import os.path


class DevIdentify():
    response = None

    @staticmethod
    def email(email):
        '''
        Validate email and make request to devidentify with email

        :param email:
        :return:
        '''
        regex_email = re.compile(
            r"""^(((([a-zA-Z]|\d|[!#$%&'*+\-/=?^_`{|}~]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])+(\.([a-zA-Z]|\d|[!#$%&'*+\-/=?^_`{|}~]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])+)*)|((\x22)((((\x20|\x09)*(\x0d\x0a))?(\x20|\x09)+)?(([\x01-\x08\x0b\x0c\x0e-\x1f\x7f]|\x21|[\x23-\x5b]|[\x5d-\x7e]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(\([\x01-\x09\x0b\x0c\x0d-\x7f]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]))))*(((\x20|\x09)*(\x0d\x0a))?(\x20|\x09)+)?(\x22)))@((([a-zA-Z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-zA-Z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-zA-Z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-zA-Z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.)+(([a-zA-Z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-zA-Z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-zA-Z]|\d|-|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-zA-Z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.?$""")

        if regex_email.match(email):
            data = requests.get('https://api.devidentify.com/{}'.format(email))
            DevIdentify.response = data.json()
        else:
            DevIdentify.response = {"success": False, "error": "Invalid email format"}

        return DevIdentify()

    def save(self, location):
        '''
        Save the fetched image in the local drive

        :param location:
        :return:
        '''
        norm_path = os.path.normpath(location)
        DevIdentify.response['location'] = norm_path
        if DevIdentify.response['success']:
            image = requests.get(re.sub(r'\?sz=500$', '', DevIdentify.response['profile_picture']))
            open(norm_path, 'wb').write(image.content)

        return self

    def toJson(self):
        '''
        Return the result as json

        :return:
        '''
        return json.dumps(self.response)

    def toDict(self):
        '''
        Return the result as dict

        :return:
        '''
        return self.response
