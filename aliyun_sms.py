# coding=utf-8

import re
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest


class AliyunAccountSettings(object):
    def __init__(self, account_settings):
        self.account_settings = account_settings

    @property
    def access_key(self):
        return self.account_settings['AccessKey']

    @property
    def secret_key(self):
        return self.account_settings['SecretKey']

    @property
    def region_id(self):
        return self.account_settings['RegionId']

    @property
    def sign_name(self):
        return self.account_settings['SignName']

    @property
    def template_code(self):
        return self.account_settings['TemplateCode']


class AliyunSMS(object):
    def __init__(self, access_key, secret_key, region_id='cn-hangzhou'):
        self.access_key = access_key
        self.secret_key = secret_key
        self.region_id = region_id

    def setup(self, sign_name, template_code):
        self.sign_name = sign_name
        self.template_code = template_code

    def send_sms(self, message, phone_numbers):
        # Preprocessing
        message = re.sub(r'[^A-Za-z0-9]', '', message)
        client = AcsClient(self.access_key, self.secret_key, self.region_id)

        request = CommonRequest()
        request.set_accept_format('json')
        request.set_domain('dysmsapi.aliyuncs.com')
        request.set_method('POST')
        request.set_protocol_type('https')
        request.set_version('2017-05-25')
        request.set_action_name('SendSms')

        request.add_query_param('RegionId', self.region_id)
        request.add_query_param('PhoneNumbers', ','.join([str(phone_number) for phone_number in phone_numbers]))
        request.add_query_param('SignName', self.sign_name)
        request.add_query_param('TemplateCode', self.template_code)

        # Notice that the parameter "code" is from the SMS template your created in Aliyun
        # Modify to your own parameter(s) which you are using in the SMS template
        request.add_query_param('TemplateParam', "{\"code\":\"%s\"}" % message)

        response = client.do_action_with_exception(request)
        return response.decode('utf-8')


if __name__ == '__main__':
    access_key = '<your aliyun access key>'
    secret_key = '<your aliyun secret key>'
    sign_name = '<your aliyun SMS sign name>'
    template_code = '<your aliyun SMS template code>'
    aliyun_sms = AliyunSMS(access_key, secret_key)
    aliyun_sms.setup(sign_name, template_code)
    response = aliyun_sms.send_sms('Hello World', [13912345678])
    print(response)
