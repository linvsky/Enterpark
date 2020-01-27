# coding=utf-8
import time
from send_email import EmailSender, EmailAccountSettings
from aliyun_sms import AliyunSMS, AliyunAccountSettings
from aws_sns import AwsSNS, AwsAccountSettings
from threading import Thread


class NotificationService(object):
    def __init__(self, account_settings, logger, service_name):
        self.account_settings = account_settings
        self.logger = logger

        email_account_settings = EmailAccountSettings(self.account_settings['EmailAccount'])
        self.email_sender = EmailSender(
            email_account_settings.smtp_server,
            email_account_settings.username,
            email_account_settings.password,
            service_name,
            email_account_settings.from_email
        )

        aliyun_account_settings = AliyunAccountSettings(self.account_settings['AliyunAccount'])
        self.aliyun_sms = AliyunSMS(
            aliyun_account_settings.access_key,
            aliyun_account_settings.secret_key,
            aliyun_account_settings.region_id
        )
        self.aliyun_sms.setup(
            aliyun_account_settings.sign_name,
            aliyun_account_settings.template_code
        )

        aws_account_settings = AwsAccountSettings(self.account_settings['AwsAccount'])
        self.aws_sns = AwsSNS(
            aws_account_settings.access_key,
            aws_account_settings.secret_key,
            aws_account_settings.region_name
        )
        self.aws_sns_topic = aws_account_settings.topic_arn

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
        timestamp = int(time.time())
        try:
            if self.email_receivers:
                self.logger.debug('Start to send Email (timestamp: %s):\n%s\n' % (timestamp, message))
                response = self.email_sender.send(self.email_receivers, subject, message)
                if not response:
                    self.logger.info('The Email has been sent (timestamp: %s)\n' % timestamp)
                else:
                    self.logger.info('The Email has been sent (timestamp: %s):\nResponse:\n%s\n'
                                     % (timestamp, response))
        except Exception as ex:
            self.logger.warning('Exception raised during sending email (timestamp: %s):\n%s\n'
                                % (timestamp, repr(ex)))

            try:
                self.logger.info('Try to send message via aws SNS (timestamp: %s)\n' % timestamp)
                response = self.aws_sns.send_message(self.aws_sns_topic, subject, message)
                self.logger.info('The message has been sent via aws SNS (timestamp: %s):\nResponse:\n%s\n'
                                 % (timestamp, response))
            except Exception as ex2:
                self.logger.warning('Exception raised during sending message (timestamp: %s):\n%s\n'
                                    % (timestamp, repr(ex2)))

    def async_send_sms(self, message):
        timestamp = int(time.time())
        try:
            if self.sms_receivers:
                self.logger.debug('Start to send SMS (timestamp: %s)\n' % timestamp)
                response = self.aliyun_sms.send_sms(message, self.sms_receivers)
                self.logger.info('The SMS has been sent (timestamp: %s):\n%s\n\nResponse:\n%s\n' %
                                 (timestamp, message, response))
        except Exception as ex:
            self.logger.warning('Exception raised during sending SMS (timestamp: %s):\n%s\n' % (timestamp, repr(ex)))
