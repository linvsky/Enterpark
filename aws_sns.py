# coding=utf-8
import boto3


class AwsAccountSettings(object):
    def __init__(self, account_settings):
        self.account_settings = account_settings

    @property
    def access_key(self):
        return self.account_settings['AccessKey']

    @property
    def secret_key(self):
        return self.account_settings['SecretKey']

    @property
    def region_name(self):
        return self.account_settings['RegionName']

    @property
    def topic_arn(self):
        return self.account_settings['TopicARN']


class AwsSNS(object):
    def __init__(self, access_key, secret_key, region_name):
        self.sns = boto3.client(service_name='sns', region_name=region_name, use_ssl=False,
                                aws_access_key_id=access_key,
                                aws_secret_access_key=secret_key)

    def send_SMS(self, phone_number, message):
        response = self.sns.publish(PhoneNumber=str(phone_number), Message=message)
        return response

    def send_message(self, topic_arn, subject, message):
        response = self.sns.publish(TopicArn=topic_arn, Message=message, Subject=subject)
        return response


if __name__ == '__main__':
    import os, simplejson

    current_folder = os.path.split(__file__)[0]
    account_settings_filepath = os.path.join(current_folder, 'AccountSettings.json')
    with open(account_settings_filepath, mode='r') as account_settings_file:
        account_settings = simplejson.load(account_settings_file, encoding='utf-8')
        if account_settings:
            aws_account_settings = AwsAccountSettings(account_settings['AwsAccount'])
            aws_sns = AwsSNS(
                aws_account_settings.access_key,
                aws_account_settings.secret_key,
                aws_account_settings.region_name
            )
            aws_sns_topic = aws_account_settings.topic_arn
            response = aws_sns.send_message(aws_sns_topic, 'Test Mail', 'This is a test mail.')
            print(response)
