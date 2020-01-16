# coding=utf-8
import os, logging, time, datetime, sys
import collections
import simplejson
from interpark_api import InterparkAPI
from notification_service import NotificationService


class InterparkMonitor(object):
    def __init__(self, interpark_api, noti_service, logger):
        self.interpark_api = interpark_api
        self.noti_service = noti_service
        self.logger = logger
        self.last_ticket_matrix = {}
        self.interval = 0

    def run(self):
        do_sms_notify = False
        do_email_notify = False
        short_messages = []
        start_time = datetime.datetime.now()
        last_output_time = start_time

        expected_goods_list = []
        for goods_name, goods_code in self.interpark_api.goods_codes.items():
            if not goods_code in self.interpark_api.ignored_goods_codes:
                expected_goods_list.append(goods_name)

        start_msg = 'Enterpark is checking tickets for %s\n' % ', '.join(expected_goods_list)
        start_msg += 'SMS Receivers  : %s\n' % ', '.join(self.noti_service.sms_receivers)
        start_msg += 'Email Receivers: %s\n' % ', '.join(self.noti_service.email_receivers)
        self.logger.info(start_msg)

        self.noti_service.send_email('Enterpark is Now Running', start_msg)

        while True:
            try:
                ticket_matrix, seat_names = self.get_ticket_matrix()
            except Exception as ex:
                self.logger.error('Exception raised during requesting ticket info (will retry):\n%s' % repr(ex))
                self.interpark_api.reset()
                time.sleep(self.interval)
                continue

            if not self.last_ticket_matrix:
                self.last_ticket_matrix = ticket_matrix

            for goods_name, ticket_status in ticket_matrix.items():
                if not goods_name in self.last_ticket_matrix:
                    self.logger.warning('Unexpected ticket type found: %s' % goods_name)
                    continue

                for seat_grade, remain_count in ticket_status.items():
                    if not seat_grade in self.last_ticket_matrix[goods_name]:
                        do_sms_notify = True
                        do_email_notify = True
                        short_message = '%s Added %s %s' % (goods_name, seat_names[seat_grade], remain_count)
                        short_messages.append(short_message)
                    elif remain_count > self.last_ticket_matrix[goods_name][seat_grade]:
                        do_sms_notify = True
                        do_email_notify = True
                        added_count = int(remain_count) - int(self.last_ticket_matrix[goods_name][seat_grade])
                        short_message = '%s %s Add %s' % (goods_name, seat_names[seat_grade], added_count)
                        short_messages.append(short_message)
                    elif remain_count < self.last_ticket_matrix[goods_name][seat_grade]:
                        do_sms_notify = False
                        do_email_notify = True
                        subbed_count = int(self.last_ticket_matrix[goods_name][seat_grade]) - int(remain_count)
                        short_message = '%s %s Sub %s' % (goods_name, seat_names[seat_grade], subbed_count)
                        short_messages.append(short_message)

            ticket_summary = InterparkMonitor.print_ticket_matrix(ticket_matrix, seat_names)
            self.last_ticket_matrix = ticket_matrix

            if do_sms_notify:
                for short_message in short_messages:
                    self.noti_service.send_sms(short_message)
                do_sms_notify = False

            if do_email_notify:
                long_message = 'Highlights:\n%s\n\n%s' % ('\n'.join(short_messages), ticket_summary)
                self.noti_service.send_email('Tickets Changed', long_message)
                do_email_notify = False
                short_messages.clear()

            if not do_sms_notify and not do_email_notify:
                current_time = datetime.datetime.now()
                report_time_delta = current_time - start_time
                output_time_delta = current_time - last_output_time

                if report_time_delta.days == 1:
                    subject = 'Tickets Daily Report %s' % time.strftime('%x', current_time.timetuple())
                    self.noti_service.send_email(subject, ticket_summary)
                    start_time = current_time

                if output_time_delta.seconds > 120:
                    self.logger.info('Tickets Log per 2 minutes\n%s' % ticket_summary)
                    last_output_time = current_time

            time.sleep(self.interval)

    @staticmethod
    def print_ticket_matrix(ticket_matrix, seat_names):
        summary = ''
        header = 'Type'
        for seat_grade, seat_name in seat_names.items():
            header += '\t%s' % seat_name
        summary += header + '\n'

        for goods_name, ticket_status in ticket_matrix.items():
            row = goods_name
            for seat_grade, seat_remain_count in ticket_matrix[goods_name].items():
                row += '\t%s' % seat_remain_count

            summary += row + '\n'
        return summary

    def get_ticket_matrix(self):
        place_code = self.interpark_api.place_code
        language_type = self.interpark_api.language_type
        goods_codes = self.interpark_api.goods_codes
        ignored_goods_codes = self.interpark_api.ignored_goods_codes
        ticket_matrix = collections.OrderedDict()
        seat_names = {}
        for goods_name, goods_code in goods_codes.items():
            if goods_code in ignored_goods_codes:
                continue

            ticket_matrix[goods_name] = {}

            play_date = self.interpark_api.get_play_date(goods_code, place_code, language_type)
            time.sleep(self.interval)

            play_seq = self.interpark_api.get_play_seq(goods_code, place_code, play_date, language_type)
            time.sleep(self.interval)

            seat_status_list = self.interpark_api.get_seat_status_list(goods_code, place_code, play_seq, language_type)
            time.sleep(self.interval)

            for seat_status in seat_status_list:
                ticket_matrix[goods_name][seat_status['SeatGrade']] = seat_status['RemainCnt']
                seat_names[seat_status['SeatGrade']] = seat_status['SeatGradeName']

        return ticket_matrix, seat_names


def setup_logger(file_log_folder, logger_name):
    logging.getLogger("requests").setLevel(logging.WARNING)
    logger = logging.getLogger(logger_name)
    logger_formatter = logging.Formatter('%(asctime)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    logger.setLevel(logging.DEBUG)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(logger_formatter)
    stdout_handler.encoding = 'utf-8'
    time_string = time.strftime('%Y-%m-%d %H.%M.%S', time.localtime(time.time()))

    if not os.path.exists(file_log_folder):
        os.makedirs(file_log_folder)
    log_filename = os.path.join(file_log_folder, '%s.log' % time_string)
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logger_formatter)
    file_handler.encoding = 'utf-8'
    logger.addHandler(stdout_handler)
    logger.addHandler(file_handler)
    return logger


if __name__ == '__main__':
    current_folder = os.path.split(__file__)[0]
    logger = setup_logger(os.path.join(current_folder, 'Logs'), 'Enterpark')

    interpark_parameters_filepath = os.path.join(current_folder, 'InterparkParameters.json')
    with open(interpark_parameters_filepath, mode='r') as interpark_parameters_file:
        interpark_parameters = simplejson.load(interpark_parameters_file, encoding='utf-8')
        logger.debug(interpark_parameters)

    if not interpark_parameters:
        logger.error('Failed to load Interpark parameters from %s' % interpark_parameters_filepath)
        exit()

    account_settings_filepath = os.path.join(current_folder, 'AccountSettings.json')
    with open(account_settings_filepath, mode='r') as account_settings_file:
        account_settings = simplejson.load(account_settings_file, encoding='utf-8')
        logger.debug(account_settings)

    if not account_settings:
        logger.error('Failed to load account settings from %s' % account_settings_filepath)
        exit()

    try:
        interpark_api = InterparkAPI(interpark_parameters)
        noti_service = NotificationService(account_settings, logger, 'Enterpark')
        interpark_monitor = InterparkMonitor(interpark_api, noti_service, logger)
        interpark_monitor.run()
    except Exception as ex:
        logger.error('Critical exception raised:\n%s' % repr(ex))
        noti_service.send_email('Enterpark Encountered An Error',
                                'Please notice that Enterpark encountered a fatal error and will exit immediately.')
    finally:
        logger.error('Enterpark will exit')
