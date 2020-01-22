# coding=utf-8
from send_email import EmailSender, EmailAccountSettings
from aliyun_sms import AliyunSMS, AliyunAccountSettings
from threading import Thread


class NotificationService(object):
    def __init__(self, account_settings, logger, service_name):
        self.account_settings = account_settings
        self.logger = logger

        email_account_settings = EmailAccountSettings(self.account_settings['EmailAccount'])
        self.emailSender = EmailSender(
            email_account_settings.smtp_server,
            email_account_settings.username,
            email_account_settings.password,
            service_name,
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
        t = Thread(target=self.async_send_email, args=(subject, message,))
        t.start()

    def send_sms(self, message):
        t = Thread(target=self.async_send_sms, args=(message,))
        t.start()

    def async_send_email(self, subject, message):
        try:
            if self.email_receivers:
                self.logger.debug('Start to send Email')
                response = self.emailSender.send(self.email_receivers, subject, message)
                if not response:
                    self.logger.info('The Email has been sent:\n%s' % message)
                else:
                    self.logger.info('The Email has been sent:\n%s\nResponse:\n%s' % (message, response))
        except Exception as ex:
            self.logger.warning('Exception raised during sending email:\n%s' % repr(ex))

    def async_send_sms(self, message):
        try:
            if self.sms_receivers:
                self.logger.debug('Start to send SMS')
                response = self.aliyunSMS.send_sms(message, self.sms_receivers)
                self.logger.info('The SMS has been sent:\n%s\n\nResponse:\n%s' % (message, response))
        except Exception as ex:
            self.logger.warning('Exception raised during sending SMS:\n%s' % repr(ex))
