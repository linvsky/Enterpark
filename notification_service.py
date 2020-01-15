# coding=utf-8
from send_email import EmailSender, EmailAccountSettings
from aliyun_sms import AliyunSMS, AliyunAccountSettings


class NotificationService(object):
    def __init__(self, account_settings, logger):
        self.account_settings = account_settings
        self.logger = logger

        email_account_settings = EmailAccountSettings(self.account_settings['EmailAccount'])
        self.emailSender = EmailSender(
            email_account_settings.smtp_server,
            email_account_settings.username,
            email_account_settings.password,
            'Enterpark',
            email_account_settings.from_email
        )

        aliyun_account_settings = AliyunAccountSettings(self.account_settings['AliyunAccount'])
        self.aliyunSMS = AliyunSMS(
            aliyun_account_settings.access_key,
            aliyun_account_settings.secret_key,
            aliyun_account_settings.region_id
        )
        self.aliyunSMS.setup(
            aliyun_account_settings.sign_name,
            aliyun_account_settings.template_code
        )

    @property
    def email_receivers(self):
        return self.account_settings['EmailReceivers']

    @property
    def sms_receivers(self):
        return self.account_settings['SMSReceivers']

    def send_email(self, subject, message):
        try:
            response = self.emailSender.send(self.email_receivers, subject, message)
            if not response:
                self.logger.info('This Email has been sent:\n%s' % message)
            else:
                self.logger.info('This Email has been sent:\n%s\nResponse:\n%s' % (message, response))
        except Exception as ex:
            self.logger.warning('Exception raised during sending email:\n%s' % repr(ex))

    def send_sms(self, message):
        try:
            response = self.aliyunSMS.send_sms(message, self.sms_receivers)
            self.logger.info('This SMS has been sent:\n%s\n\nResponse:\n%s' % (message, response))
        except Exception as ex:
            self.logger.warning('Exception raised during sending SMS:\n%s' % repr(ex))
