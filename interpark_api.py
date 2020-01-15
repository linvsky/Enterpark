# coding=utf-8
import os
import simplejson
import collections
import requests
from bs4 import BeautifulSoup


class InterparkAPI(object):
    base_url = 'http://ticket.globalinterpark.com/Global/Play/Goods/GoodsInfoXml.asp'

    def __init__(self, interpark_parameters):
        self.interpark_parameters = interpark_parameters

    @property
    def default_headers(self):
        return {
            "Accept": "text/javascript, text/html, application/xml, text/xml, */*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
            "X-Prototype-Version": "1.6.1",
            "X-Requested-With": "XMLHttpRequest"
        }

    @property
    def place_code(self):
        return self.interpark_parameters['PlaceCode']

    @property
    def language_type(self):
        return self.interpark_parameters['LanguageType']

    @property
    def goods_codes(self):
        return self.interpark_parameters['GoodsCode']

    @property
    def ignored_goods_codes(self):
        return self.interpark_parameters['IgnoredGoodsCode']

    def reset(self):
        session = requests.session()
        session.keep_alive = False

    def get_play_date(self, goods_code, place_code, language_type):
        parameters = {
            'Flag': 'PlayDate',
            'GoodsCode': goods_code,
            'PlaceCode': place_code,
            'LanguageType': language_type,
            'OnlyDeliver': '',
            'DelyDay': '',
            'ExpressDelyDay': ''
        }
        response = requests.get(InterparkAPI.base_url, parameters, headers=self.default_headers, timeout=30)
        response.raise_for_status()
        response_text = response.text
        response_soup = BeautifulSoup(response_text, 'lxml-xml')
        play_date = response_soup.find('PlayDate').get_text()
        return play_date

    def get_play_seq(self, goods_code, place_code, play_date, language_type):
        parameters = {
            'Flag': 'PlaySeq',
            'GoodsCode': goods_code,
            'PlaceCode': place_code,
            'PlayDate': play_date,
            'LanguageType': language_type
        }
        response = requests.get(InterparkAPI.base_url, parameters, headers=self.default_headers, timeout=30)
        response.raise_for_status()
        response_text = response.text
        response_soup = BeautifulSoup(response_text, 'lxml-xml')
        play_seq = response_soup.find('PlaySeq').get_text()
        return play_seq

    def get_seat_status_list(self, goods_code, place_code, play_seq, language_type):
        parameters = {
            'Flag': 'RemainSeat',
            'GoodsCode': goods_code,
            'PlaceCode': place_code,
            'PlaySeq': play_seq,
            'LanguageType': language_type
        }
        response = requests.get(InterparkAPI.base_url, parameters, headers=self.default_headers, timeout=30)
        response.raise_for_status()
        response_text = response.text
        response_soup = BeautifulSoup(response_text, 'lxml-xml')

        seat_status_list = []
        for seat_status_soup in response_soup.find_all('Table'):
            seat_status = {}
            for tag in seat_status_soup.children:
                seat_status[tag.name] = tag.text
            seat_status_list.append(seat_status)

        return seat_status_list


if __name__ == '__main__':
    current_folder = os.path.split(__file__)[0]
    interpark_parameters_filepath = os.path.join(current_folder, 'InterparkParameters.json')
    with open(interpark_parameters_filepath, mode='r') as interpark_parameters_file:
        interpark_parameters = simplejson.load(interpark_parameters_file, encoding='utf-8')

    if not interpark_parameters:
        exit()

    interpark_api = InterparkAPI(interpark_parameters)
    place_code = interpark_api.place_code
    language_type = interpark_api.language_type
    goods_codes = interpark_api.goods_codes
    ignored_goods_codes = interpark_api.ignored_goods_codes
    ticket_matrix = collections.OrderedDict()
    seat_names = {}
    for goods_name, goods_code in goods_codes.items():
        if goods_code in ignored_goods_codes:
            continue

        ticket_matrix[goods_name] = {}

        play_date = interpark_api.get_play_date(goods_code, place_code, language_type)
        play_seq = interpark_api.get_play_seq(goods_code, place_code, play_date, language_type)
        seat_status_list = interpark_api.get_seat_status_list(goods_code, place_code, play_seq, language_type)

        for seat_status in seat_status_list:
            ticket_matrix[goods_name][seat_status['SeatGrade']] = seat_status['RemainCnt']
            seat_names[seat_status['SeatGrade']] = seat_status['SeatGradeName']

    header = 'Ticket'
    for seat_grade, seat_name in seat_names.items():
        header += '\t%s' % seat_name
    print(header)

    for goods_name, ticket_status in ticket_matrix.items():
        row = goods_name
        for seat_grade, seat_remain_count in ticket_matrix[goods_name].items():
            row += '\t%s' % seat_remain_count

        print(row)
