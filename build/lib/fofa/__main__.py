import base64
import copy
import csv
import re
import shutil
from dataclasses import dataclass
from warnings import simplefilter

import requests
from beautifultable import BeautifulTable as Table

simplefilter(action='ignore', category=FutureWarning)

DEBUG = False

WEB_SITE = 'https://fofa.info'
BASE_API_URL = 'https://fofa.info/api/v1'

def fofa_request(url: str):
    try:
        results = requests.get(url).json()
    except ConnectionError as e:
        errmsg = 'ConnectionError : %s' % url
        return {'error': True, 'errmsg': errmsg}
    except Exception as e:
        errmsg = 'ConnectionUnknowError : %s' % url
        # print(e)
        return {'error': True, 'errmsg': errmsg}
    else:
        return results

def kw_is_support(kw: str, submodel=False):
    if submodel:
        if '&&' == kw or '||' == kw:
            return True

        _x = []
        # =
        ret0 = re.match(r"^\w+$", kw)
        _x.append(ret0)
        ret0 = re.match(r"^\w+=$", kw)
        _x.append(ret0)
        ret0 = re.match(r"^\w+==$", kw)
        _x.append(ret0)

        ret0 = re.match(r"^\(\w+$", kw)
        _x.append(ret0)
        ret0 = re.match(r"^\(\w+=$", kw)
        _x.append(ret0)
        ret0 = re.match(r"^\(\w+==$", kw)
        _x.append(ret0)

        ret0 = re.match(r"^\w+\)$", kw)
        _x.append(ret0)
        ret0 = re.match(r"^\w+=\)$", kw)
        _x.append(ret0)
        ret0 = re.match(r"^\w+==\)$", kw)
        _x.append(ret0)

        ret0 = re.match(r"^\(\w+\)$", kw)
        _x.append(ret0)
        ret0 = re.match(r"^\(\w+=\)$", kw)
        _x.append(ret0)
        ret0 = re.match(r"^\(\w+==\)$", kw)
        _x.append(ret0)

        # !=
        ret0 = re.match(r"^\w+!=$", kw)
        _x.append(ret0)
        ret0 = re.match(r"^\(\w+!=$", kw)
        _x.append(ret0)
        ret0 = re.match(r"^\w+!=\)$", kw)
        _x.append(ret0)
        ret0 = re.match(r"^\(\w+!=\)$", kw)
        _x.append(ret0)

        # *= (title=&&*header='x-wingback'&&port!=)
        ret0 = re.match(r"^\*\w+=\S+$", kw)
        _x.append(ret0)
        ret0 = re.match(r"^\(\*\w+=\S+$", kw)
        _x.append(ret0)
        ret0 = re.match(r"^\*\w+=\S+\)$", kw)
        _x.append(ret0)
        ret0 = re.match(r"^\(\*\w+=\S+\)$", kw)
        _x.append(ret0)

        # *!= (title=&&*header='x-wingback'&&port!=)
        ret0 = re.match(r"^\*\w+!=\S+$", kw)
        _x.append(ret0)
        ret0 = re.match(r"^\(\*\w+!=\S+$", kw)
        _x.append(ret0)
        ret0 = re.match(r"^\*\w+!=\S+\)$", kw)
        _x.append(ret0)
        ret0 = re.match(r"^\(\*\w+!=\S+\)$", kw)
        _x.append(ret0)

        for x in _x:
            if x:
                return True
        return False
    else:
        if re.match(r"^\(", kw) or re.match(r"^\*", kw):
            return True
        elif re.match(r"^\W+", kw) or re.match(r"\W+$", kw):
            return False
        else:
            return True


def keywork_to_base64(kw: str):
    search_keyword_base64 = str(base64.b64encode(kw.encode('utf8')), encoding='utf8')
    if DEBUG:
        log.run_debug(text=f'qbase64    : {search_keyword_base64}')

    for k, v in URL_SPEC.items():
        search_keyword_base64 = search_keyword_base64.replace(k, v)  # base64??????????????????URL?????????
    if DEBUG:
        log.run_debug(text=f'qbase64(c) : {search_keyword_base64}')

    return search_keyword_base64


def init_table(header):
    max_width = shutil.get_terminal_size()[0]
    table = Table(maxwidth=max_width)
    # table.set_style(Table.STYLE_BOX_ROUNDED)
    table.set_style(Table.STYLE_COMPACT)

    table_header = header
    table.columns.header = table_header
    table.columns.alignment = Table.ALIGN_LEFT
    return table


def _fmt_print_level1(text: str, maxlen: int):
    if text is None or len(text) == 0:
        return ' ' * maxlen
    if len(text) > maxlen:
        tmp_text = ''
        while True:
            if len(text) > maxlen:
                tmp_text = tmp_text + text[0:maxlen] + '\n'
                text = text[maxlen:]
            else:
                tmp_text = tmp_text + text
                break
        return tmp_text
    else:
        return _fmt_print_level0(text=text, maxlen=maxlen)


def _fmt_print_level0(text: str, maxlen: int):
    if text is None or len(text) == 0:
        return ' ' * maxlen
    if len(text) < maxlen:
        return text + str(' ' * (maxlen - len(text)))
    elif len(text) == maxlen:
        return text
    else:
        return text[0:maxlen - 3] + '...'


def _format_print(text, split_len=100, force=False, space=False):
    if force:
        if text is None:
            return ' ' * split_len
        if len(text) > split_len:
            tmp_text = ''
            while True:
                if len(text) > split_len:
                    tmp_text = tmp_text + text[0:split_len] + '\n'
                    text = text[split_len:]
                else:
                    tmp_text = tmp_text + text
                    break
            return tmp_text
        else:
            if space:
                return text + str(' ' * (split_len - len(text)))
            else:
                return text
    else:
        if text is None:
            return text
        if len(text) > split_len:
            return text[0:split_len - 3] + '...'
        elif len(text) == split_len:
            return text
        else:
            return text + ' ' * (split_len - len(text))

def special_characte(text):
    _characte = ['\r', '\n', '\t']
    if isinstance(text, bytes):
        return text
    for characte in _characte:
        text = text.replace(characte, ' ')
    return ' '.join(text.split())

from termcolor import colored, cprint
from rich import print as rprint

class _Log():
    SPACE_STRING = ' ' * 2

    def warn(self, text):
        cprint(text=self.SPACE_STRING + color.yellow(text=text))
    def error(self, text):
        cprint(text=self.SPACE_STRING + color.red(text))
    def tip(self, text):
        cprint(text=self.SPACE_STRING + color.blue(text))
    def info(self, text):
        cprint(text=self.SPACE_STRING + color.white(text))
    def run_error(self, text):
        pri = '[-] '
        cprint(text=self.SPACE_STRING + color.red(pri) + text)
    def run_info(self, text):
        pri = '[+] '
        cprint(text=self.SPACE_STRING + color.green(pri) + text)
    def run_debug(self, text):
        pri = '[#] '
        cprint(text=self.SPACE_STRING + color.blue(pri) + text)
    def run_base(self, text):
        pri = '[*] '
        cprint(text=self.SPACE_STRING + color.white(pri) + text)


class _Color():

    def red(self, text):
        return colored(text=text, color='red', attrs=['bold'])
    def green(self, text):
        return colored(text=text, color='green')
    def yellow(self, text):
        return colored(text=text, color='yellow')
    def blue(self, text):
        return colored(text=text, color='blue')
    def magenta(self, text):
        return colored(text=text, color='magenta')
    def cyan(self, text):
        return colored(text=text, color='cyan')
    def white(self, text):
        return colored(text=text, color='white')

log = _Log()
color = _Color()

URL_SPEC = {
    '%': "%25",
    '+': "%2B",
    '/': "%2F",
    '?': "%3F",
    '#': "%23",
    '&': "%26",
    '=': "%3D"
}

import json, os
from hashlib import scrypt as _scrypt
from platform import system as _system
from Cryptodome.Cipher import AES

class AuthStorage:
    def __init__(self) -> None:
        file_name = '.enc.dat'
        ptf = _system()
        if ptf == 'Windows':
            dir = os.environ.get('APPDATA')
            pwd = '11002299338844775566'
            self.file = dir + '\\' + file_name
        elif ptf == 'Linux' or ptf == 'Darwin':
            dir = os.environ.get('HOME')
            pwd = 'A1B2C3D4E5F6G7I8J9K0'
            self.file = dir + '/' + file_name
        else:
            dir = '/temp'
            pwd = '10110111001001000'
            self.file = dir + '/' + file_name

        self.password = bytes(pwd, encoding='UTF-8')

    salt = b'5Q\xf5M\xbd\xe2\x87\xa8U\xa5Wy\xde3\xf8z\xd0\xec\xed\xf5\xb8\xd3\x97PT,!65X%\x10'

    def enc(self, enc_dat: str):
        key = _scrypt(self.password, salt=self.salt, n=2 ** 14, r=8, p=1, dklen=32)
        cipher = AES.new(key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(enc_dat)
        try:
            file_out = open(self.file, "wb")
        except Exception as e:
            print(f' open file error. {e}')
            return False
        [file_out.write(x) for x in (cipher.nonce, tag, ciphertext)]
        file_out.close()
        return True

    #####
    def un_enc(self):

        if os.path.exists(self.file):
            pass
        else:
            return False

        try:
            file_in = open(self.file, "rb")
        except Exception as e:
            print(f' open file error. {e}')
            return False
        nonce, tag, ciphertext = [file_in.read(x) for x in (16, 16, -1)]
        file_in.close()

        key = _scrypt(self.password, salt=self.salt, n=2 ** 14, r=8, p=1, dklen=32)
        cipher = AES.new(key, AES.MODE_GCM, nonce)
        try:
            data = cipher.decrypt_and_verify(ciphertext=ciphertext, received_mac_tag=tag)
        except Exception as e:
            print(f" {e}")
            return
        dat = json.loads(data.decode('UTF-8'))
        # rprint(dat.items()) 
        return dat

# ----------------------
# ??????????????????
class _SearchSyntax(object):

    def __init__(self) -> None:
        self.syntax_data = {}
        self.support_syntax_fields = self.Syntax()
        for syntax_fields in dir(self.support_syntax_fields):
            if syntax_fields.startswith('__') and syntax_fields.endswith('__'):
                pass
            else:
                data = {syntax_fields: getattr(self.support_syntax_fields, syntax_fields)}
                self.syntax_data.update(data)

    @dataclass
    class Syntax(object):
        # ????????? web, domain, cloud, host, area, fingerprint, daterange, other, is, ip, port
        titles = ['title="beijing"', '????????????????????????', '-', 'website']
        header = ['header="elastic"', '???http???????????????elastic???', '-', 'website']
        body = ['body="??????????????????"', '???html???????????????????????????????????????', '-', 'website']
        fid = ['fid="sSXXGNUO2FefBTcCLIT/2Q=="', '???????????????????????????,(????????????????????????)', '-', 'website']
        domain = ['domain="qq.com"', '?????????????????????qq.com?????????', '-', 'domain']
        icp = ['icp="???ICP???030173???"', '????????????????????????ICP???030173???????????????,(????????????????????????)', '-', 'website']
        js_name = ['js_name="js/jquery.js"', '???????????????????????????js/jquery.js?????????,(????????????????????????)', '-', 'website']
        js_md5 = ['js_md5="82ac3f14327a8b7ba49baa208d4eaa15"', '??????js???????????????????????????', '-', 'website']
        cname = ['cname="ap21.inst.siteforce.com"', '??????cname???"ap21.inst.siteforce.com"?????????', '-', 'domain']
        cname_domain = ['cname_domain="siteforce.com"', '??????cname?????????siteforce.com????????????', '-', 'domain']
        cloud_name = ['cloud_name="Aliyundun"', '?????????????????????????????????', '-', 'cloud']
        icon_hash = ['icon_hash="-247388890"', '??????????????? icon ?????????', '++', 'website']
        host = ['host=".gov.cn"', '???url????????????.gov.cn???,(????????????host????????????)', '-', 'domain']
        port = ['port="6379"', '???????????????6379??????????????????', '-', 'port']
        ip = ['ip="1.1.1.1"', '???ip??????????????????1.1.1.1????????????,(????????????ip????????????)', '-', 'website']
        ip1 = ['ip="220.181.111.1/24"', '??????IP??????220.181.111.1??????C????????????', '-', 'ip']
        status_code = ['status_code="402"', '???????????????????????????402????????????,(????????????????????????)', '-', 'website']
        protocol = ['protocol="quic"', '??????quic????????????.????????????????????????,(???????????????????????????????????????)', '-', 'port']
        country = ['country="CN"', '??????????????????(??????)?????????', '-', 'area']
        region = ['region="Xinjiang"', '??????????????????????????????', '-', 'area']
        city = ['city="??r??mqi"', '???????????????????????????', '-', 'area']
        cert = ['cert="baidu"', '????????????(https??????imaps???)?????????baidu?????????', '-', 'cert']
        cert_subject = ['cert.subject="Oracle Corporation"', '????????????????????????Oracle Corporation?????????', '-', 'cert']
        cert_issuer = ['cert.issuer="DigiCert"', '????????????????????????DigiCert Inc?????????', '-', 'cert']
        cert_is_valid = ['cert.is_valid=true', '????????????????????????.true??????,false??????', '++', 'cert']
        jarm = ['jarm="2ad...83e81"', '??????JARM??????', '-', 'fingerprint']
        banner = ['banner="users" && protocol="ftp"', '??????FTP???????????????users???????????????', '-', 'fingerprint']
        type = ['type="service"', '????????????????????????,(??????subdomain???service??????)', '-', 'fingerprint']
        os = ['os="centos"', '??????CentOS??????', '-', 'fingerprint']
        server = ['server=="Microsoft-IIS/10"', '??????IIS 10?????????', '-', 'fingerprint']
        app = ['app="Microsoft-Exchange"', '??????Microsoft-Exchange??????', '-', 'fingerprint']
        after = ['after="2017" && before="2017-10-01"', '?????????????????????', '-', 'daterange']
        asn = ['asn="19551"', '????????????asn?????????', '-', 'area']
        org = ['org="LLC Baxet"', '????????????org(??????)?????????', '-', 'area']
        base_protocol = ['base_protocol="udp"', '????????????udp???????????????', '-', 'port']

        is_fraud = ['is_fraud=false', '????????????/????????????', '++', 'is']
        is_honeypot = ['is_honeypot=false', '??????????????????', '++', 'is']
        is_ipv6 = ['is_ipv6=true', '??????ipv6?????????(?????????true???false)', '-', 'ip']
        is_domain = ['is_domain=true', '?????????????????????(?????????true???false)', '-', 'is']
        is_cloud = ['is_cloud=true', '?????????????????????????????????', '-', 'is']

        port_size = ['port_size="6"', '??????????????????????????????"6"?????????', '+', 'port']
        port_size_gt = ['port_size_gt="6"', '??????????????????????????????"6"?????????', '+', 'port']
        port_size_lt = ['port_size_gt="12"', '??????????????????????????????"12"?????????', '+', 'port']

        ip_ports = ['ip_ports="80,161"', '??????????????????80???161?????????ip??????,(???ip????????????????????????)', '-', 'ip']
        ip_country = ['ip_country="CN"', '???????????????ip??????,(???ip????????????????????????)', '-', 'ip']
        ip_region = ['ip_region="Zhejiang"', '????????????????????????ip??????,(???ip????????????????????????)', '-', 'ip']
        ip_city = ['ip_city="Hangzhou"', '?????????????????????ip??????,(???ip????????????????????????)', '-', 'ip']
        ip_after = ['ip_after="2021-03-18"', '??????2021-03-18?????????ip??????,(???ip????????????????????????)', '-', 'ip']
        ip_before = ['ip_before="2019-09-09"', '??????2019-09-09?????????ip??????,(???ip????????????????????????)', '-', 'ip']

    def synax_print(self):
        header = ['Syntax', 'Desc', 'Permission', 'Type']
        table = init_table(header=header)
        syntax_data = {}
        for k, v in self.syntax_data.items():
            search_ = syntax_data.setdefault(v[-1], [])
            search_.append(v)

        i = 0
        for k, v in syntax_data.items():
            for syntanField in v:
                if i == 0:
                    data = [color.white(syntanField[0]), color.white(syntanField[1]), color.white(syntanField[2]),
                            color.white(syntanField[3])]
                if i == 1:
                    data = [color.cyan(syntanField[0]), color.cyan(syntanField[1]), color.cyan(syntanField[2]),
                            color.cyan(syntanField[3])]
                if i == 2:
                    data = [color.green(syntanField[0]), color.green(syntanField[1]), color.green(syntanField[2]),
                            color.green(syntanField[3])]
                if i == 3:
                    data = [color.red(syntanField[0]), color.red(syntanField[1]), color.red(syntanField[2]),
                            color.red(syntanField[3])]
                if i == 4:
                    data = [color.yellow(syntanField[0]), color.yellow(syntanField[1]), color.yellow(syntanField[2]),
                            color.yellow(syntanField[3])]
                table.rows.append(data)

            i = i + 1
            if i == 5:
                i = 0
        # rprint(self.syntax_data)
        print("????????????????????????,????????????,html??????,http?????????,url???????????????: ")
        print("????????????????????????????????????????????????????????????????????????????????????")
        print('''??????==?????????????????????,????????????????????????,????????????qq.com??????host,?????????domain=="qq.com"''')
        print()
        print(color.red('????????????'))
        print(' =      ?????????=""??????????????????????????????????????????????????????')
        print(' ==     ???????????????==""??????????????????????????????????????????')
        print(' &&     ???')
        print(' ||     ??????')
        print(' !=     ????????????!=""?????????????????????????????????')
        print(' ~=     ????????????????????????(??????????????????,?????????body)')
        print(' ()     ???????????????????????????????????????????????????')
        print()
        print('''
?????????????????? ??? && || !=?????????,???:
title="powered by" && title!="discuz"
body="content=WordPress" || (header="X-Wingback" && header="/xmlrpc.php" && body="/wp-includes/") && host="gov.cn" 
    ''')
        print('?????????????????????????????????????????????,??????:https://fofa.info/ ???????????? ??????')
        print()
        print(table)

        pass

# ----------------------
# ??????????????????
# ????????????API?????????
# ????????????
@dataclass
class _SeachAPIParameter(object):
    querykw: str = None  # ????????????????????????
    qbase64: str = None  # ??????querykw ?????????base64
    fields: str = 'ip,port,protocol,host,domain,os,server,banner,header,title,city,country,longitude,latitude'  # ??????1
    page: int = 1  # ???????????????
    size: int = 100  # ???????????????????????????100???
    full: bool = False  # ?????????????????????????????????????????? True ?????????????????????
    fields_list = ['ip', 'port', 'protocol', 'country', 'country_name', 'region', 'city', 'longitude', 'latitude',
                   'as_number', 'as_organization', 'host', 'domain', 'os', 'server', 'icp', 'title', 'jarm', 'banner',
                   'header', 'cert', 'body', 'fid', 'structinfo']

# ???????????????????????????
class _SearchAPI(object):
    FIELDS = _SeachAPIParameter()
    SET_FIELDS = FIELDS.__dict__

    def __init__(self) -> None:
        self.SEARCH_FIELDS = {}
        self._register_fields()

        self.VIP3_SUPPORT_SEARCH_FILEDS = list(self.SEARCH_FIELDS.keys())  # +++ ???????????????????????????????????????????????????
        self.VIP2_SUPPORT_SEARCH_FILEDS = copy.deepcopy(self.VIP3_SUPPORT_SEARCH_FILEDS)  # ++ ???????????????????????????????????????????????????
        self.VIP2_SUPPORT_SEARCH_FILEDS.remove('body')
        self.VIP2_SUPPORT_SEARCH_FILEDS.remove('fid')
        self.VIP2_SUPPORT_SEARCH_FILEDS.remove('structinfo')

    def _search_fields(self, keywork, desc, permission, fmt_color):
        k = self.SEARCH_FIELDS.setdefault(keywork, {})
        k['desc'] = desc
        k['permission'] = permission
        k['color'] = fmt_color

    def _register_fields(self):
        self._search_fields('ip', desc='ip??????', permission='-', fmt_color='red')
        self._search_fields('port', desc='??????', permission='-', fmt_color='red')
        self._search_fields('protocol', desc='?????????', permission='-', fmt_color='red')

        self._search_fields('country', desc='????????????', permission='-', fmt_color='green')
        self._search_fields('country_name', desc='?????????', permission='-', fmt_color='green')
        self._search_fields('region', desc='??????', permission='-', fmt_color='green')
        self._search_fields('city', desc='??????', permission='-', fmt_color='green')
        self._search_fields('longitude', desc='???????????? ' + color.green('??????'), permission='-', fmt_color='green')
        self._search_fields('latitude', desc='???????????? ' + color.green('??????'), permission='-', fmt_color='green')

        self._search_fields('as_number', desc='asn??????', permission='-', fmt_color='yellow')
        self._search_fields('as_organization', desc='asn??????', permission='-', fmt_color='yellow')

        self._search_fields('host', desc='?????????', permission='-', fmt_color='magenta')
        self._search_fields('domain', desc='??????', permission='-', fmt_color='magenta')
        self._search_fields('os', desc='????????????', permission='-', fmt_color='magenta')

        self._search_fields('server', desc='??????server', permission='-', fmt_color='white')
        self._search_fields('icp', desc='icp?????????', permission='-', fmt_color='white')
        self._search_fields('title', desc='????????????', permission='-', fmt_color='white')
        self._search_fields('jarm', desc='jarm ??????', permission='-', fmt_color='white')

        self._search_fields('banner', desc='?????? banner', permission='-', fmt_color='red')
        self._search_fields('header', desc='?????? banner', permission='-', fmt_color='red')
        self._search_fields('cert', desc='??????', permission='-', fmt_color='white')
        self._search_fields('body', desc='??????????????????', permission='+++', fmt_color='cyan')
        self._search_fields('fid', desc='??????????????????', permission='+++', fmt_color='cyan')

        self._search_fields('structinfo', desc='??????????????? (???????????????????????????elastic???mongodb)', permission='+++', fmt_color='cyan')

    def field_print(self):

        table_header = ['?????????', '??????', '??????']
        table = init_table(header=table_header)

        for k, v in self.SEARCH_FIELDS.items():
            if v['color'] == 'red':
                k = color.red(k)
            elif v['color'] == 'green':
                k = color.green(k)
            elif v['color'] == 'yellow':
                k = color.yellow(k)
            elif v['color'] == 'magenta':
                k = color.magenta(k)
            elif v['color'] == 'white':
                k = color.white(k)
            elif v['color'] == 'cyan':
                k = color.cyan(k)
            else:
                k = color.white(k)

            if v['permission'] == '+++':
                permission = color.red(v['permission'])
            else:
                permission = v['permission']
            table.rows.append([k, v['desc'], permission])

        table.rows.header = [str(id) for id in range(0, len(table.rows))]
        print(table)

    def show_fields(self):
        max_width = shutil.get_terminal_size()[0]
        max_display = int(max_width / 2)
        header = ['Parameter', 'Required', 'Type', 'Value', 'Description']
        table = init_table(header=header)
        table.rows.append(
            [color.red('querykw'), color.red('Yes'), 'str', _format_print(self.FIELDS.querykw, max_display, force=True),
             '??????????????????base64?????????qbase64??????'])
        table.rows.append(
            ['qbase64', 'no', 'str', _format_print(self.FIELDS.qbase64, max_display), '??????qbase64?????????,querykw????????????'])
        table.rows.append(['fields', 'no', 'str', self.FIELDS.fields, '??????host,ip,port'])
        table.rows.append(['page', 'no', 'int', color.green(self.FIELDS.page), '????????????????????????,?????????????????????'])
        table.rows.append(['size', 'no', 'int', color.green(self.FIELDS.size), f'???????????????(defau:100, max:10,000)'])
        table.rows.append(['full', 'no', 'bool', color.red(str(self.FIELDS.full)), '????????????(false:1??????, true:all)'])
        print()
        print(table)
        print()


class ApiSearch(_SearchAPI):
    VIEW_DATA = None
    ID = None

    def __init__(self, email: str, key: str) -> None:
        super().__init__()
        self.email = email
        self.key = key
        self.data = None
        self.data_other = {'size': None, 'page': None, 'mode': None, 'query': None}

        self.search_api_base = f"{BASE_API_URL}/search/all?"
        self.auth = 'email=%s&key=%s' % (email, key)

        # self.userinfo = ApiUserInfo(email=email, key=key)._api_user_acc() # ????????????????????????
        self.userinfo = {'vip_level': 2}
        if self.userinfo:
            self.vip_level = self.userinfo['vip_level']
            if self.vip_level == 3:
                self.VIP_SUPPORT_SEARCH_FILEDS = copy.deepcopy(self.VIP3_SUPPORT_SEARCH_FILEDS)
            else:
                self.VIP_SUPPORT_SEARCH_FILEDS = copy.deepcopy(self.VIP2_SUPPORT_SEARCH_FILEDS)
        else:
            pass

    def set_fields(self, size_next=False, size_page=False, **kw):
        unsupport = []

        for k, v in kw.items():
            if k not in self.SET_FIELDS:
                unsupport.append(k)
            if unsupport:
                log.error(f" set fields error,unspport keyword! {','.join(unsupport)}")
                return

            if k == 'querykw':
                self.SET_FIELDS['qbase64'] = keywork_to_base64(v)
                self.SET_FIELDS[k] = v
            elif k == 'qbase64':
                self.SET_FIELDS['querykw'] = None
                self.SET_FIELDS[k] = v
            elif k == 'size' and size_next:
                self.SET_FIELDS[k] = int(v) + 50
            elif k == 'page' and size_page:
                self.SET_FIELDS[k] = int(v) + 1
            elif k == 'fields':
                _unsp = []
                for field_dat in v.split(','):
                    if field_dat not in self.FIELDS.fields_list:
                        _unsp.append(field_dat)
                if _unsp:
                    log.error(f" unspport fields keyword! {','.join(_unsp)}")
                    return
                self.SET_FIELDS[k] = v
            else:
                self.SET_FIELDS[k] = v
            log.error(f" set search {k} => {self.SET_FIELDS[k]}")

    def export(self, file):

        if not self.data:
            log.error(f" search results is empty....")
            return
        try:
            f = open(file, 'w', encoding='utf-8')
        except Exception as e:
            log.error(f" {e}")
            return
        with f:
            writer = csv.writer(f)
            writer.writerow(self.VIP_SUPPORT_SEARCH_FILEDS)
            for row in self.data:
                writer.writerow(row)
            log.info(f" export data success. {file}")

    def set_fields_default(self):
        self.FIELDS.fields = 'ip,port,protocol,host,domain,os,server,banner,header,title,city,country,longitude,latitude'
        log.error(f' set search fields => {self.FIELDS.fields}')

    def set_fields_normal(self):
        self.FIELDS.fields = 'ip,port,os,jarm,cert,banner,header,server,country,title,as_organization'
        log.error(f' set search fields => {self.FIELDS.fields}')

    def search(self, kw: str = None):
        if kw:
            self.FIELDS.querykw = kw
            self.FIELDS.qbase64 = keywork_to_base64(kw=kw)
        if not self.FIELDS.qbase64:
            log.error(f" search keyword is None....")
            return

        qbase64 = "&qbase64=%s" % self.FIELDS.qbase64
        fields = "&fields=%s" % ','.join(self.VIP_SUPPORT_SEARCH_FILEDS)  # ??????????????????????????????????????????????????????
        page = "&page=%s" % str(self.FIELDS.page)
        size = "&size=%s" % str(self.FIELDS.size)
        if self.FIELDS.full:
            full = "&full=true"
        else:
            full = "&full=false"

        url = self.search_api_base + self.auth + qbase64 + fields + page + size + full
        if DEBUG:
            log.run_debug(text=f'requestURL : {url}')
        results = fofa_request(url=url)
        if 'results' in results:
            self.data = results['results']
            self.data_other['size'] = results['size']
            self.data_other['page'] = results['page']
            self.data_other['mode'] = results['mode']
            self.data_other['query'] = results['query']
            self.last()
        if results['error']:
            log.error(results['errmsg'])
            return
        if DEBUG:
            rprint(results)
        return results

    def last(self):
        if not self.data:
            log.error(' no data.....')
            return
        self._fmt_search_results()

    def _fmt_search_results(self):
        results = copy.deepcopy(self.data)
        display_fileds = copy.deepcopy(self.FIELDS.fields).split(',')
        unsupport = list(set(display_fileds).difference(self.VIP_SUPPORT_SEARCH_FILEDS))
        if unsupport:
            log.error(f" unsupport fileds. {','.join(unsupport)}")
            return

        table = init_table(header=display_fileds)
        table.columns.alignment = Table.ALIGN_CENTER

        table1 = init_table(header=self.VIP_SUPPORT_SEARCH_FILEDS)  # ???????????????????????????????????????

        fields_dic = {}
        for fileds in display_fileds:
            fields_dic[fileds] = self.VIP_SUPPORT_SEARCH_FILEDS.index(fileds)

        for res in results:
            ## ??????????????????
            res[self.VIP_SUPPORT_SEARCH_FILEDS.index('banner')] = bytes(
                res[self.VIP_SUPPORT_SEARCH_FILEDS.index('banner')], encoding='utf-8')
            res[self.VIP_SUPPORT_SEARCH_FILEDS.index('header')] = bytes(
                res[self.VIP_SUPPORT_SEARCH_FILEDS.index('header')], encoding='utf-8')
            table1.rows.append(res)
            #
            fmt_res = []
            for k, v in fields_dic.items():
                res[v] = special_characte(res[v])

                if k == 'banner' or k == 'header':
                    if res[v]:
                        bt_data = _fmt_print_level0(str(res[v].decode('utf-8')), maxlen=20)
                        bt_data = bytes(bt_data, encoding='utf-8')
                        fmt_res.append(bt_data)
                    else:
                        fmt_res.append('-')
                elif k == 'title':
                    fmt_res.append(_fmt_print_level0(res[v], maxlen=30))
                elif k == 'city':
                    fmt_res.append(_fmt_print_level0(res[v], maxlen=15))
                elif k == 'server':
                    fmt_res.append(_fmt_print_level0(res[v], maxlen=35))
                elif k == 'ip':
                    fmt_res.append(_fmt_print_level0(res[v], maxlen=16))
                elif k == 'host' or k == 'domain':
                    fmt_res.append(_fmt_print_level0(res[v], maxlen=35))
                elif k == 'as_organization':
                    fmt_res.append(_fmt_print_level0(res[v], maxlen=25))
                elif k == 'jarm' or k == 'cert' or k == 'body' or k == 'fid' or k == 'structinfo':
                    if not res[v]:
                        fmt_res.append('-')
                        continue

                    data = res[v]
                    if len(display_fileds) <= 5:
                        if k == 'body' or k == 'cert':
                            data = _fmt_print_level0(res[v], maxlen=50)
                            data = bytes(data, encoding='utf-8')
                            fmt_res.append(data)
                        else:
                            fmt_res.append(res[v])
                    elif len(display_fileds) > 5 and len(display_fileds) <= 11:
                        if k == 'body' or k == 'cert':
                            data = _fmt_print_level0(res[v], maxlen=30)
                            data = bytes(data, encoding='utf-8')
                            fmt_res.append(data)
                        else:
                            fmt_res.append(res[v])
                    else:
                        if res[v]:
                            fmt_res.append(_fmt_print_level0(res[v], maxlen=3))
                else:
                    if res[v]:
                        fmt_res.append(res[v])
                    else:
                        fmt_res.append('-')
            table.rows.append(fmt_res)

        if 'ip' in table.columns.header:
            table.rows.sort('ip')
            table1.rows.sort('ip')
        table.rows.header = [str(id) for id in range(0, len(table.rows))]  # ???????????????????????????
        table1.rows.header = [str(id) for id in range(0, len(table.rows))]  # ????????????????????????id
        self.VIEW_DATA = table1
        rprint(table)
        print()
        rprint(
            f"size && page : {self.data_other['size']} && {self.data_other['page']} , mode : {self.data_other['mode']}")
        rprint(f"query syntax : {self.data_other['query']}")

    def _id(self, id):
        try:
            id = int(id)
        except:
            log.error(' id must be numeric...')
            return
        if not self.VIEW_DATA:
            log.error(f" no data from search resultes...")
            return
        if len(self.VIEW_DATA.rows) - 1 >= id:
            id_details = list(self.VIEW_DATA.rows[id])
            return id_details
        else:
            log.error(f" ID index out of range.")
            return

    def _cover(self, kw: str, kwd: str, support_get_fields_other: dict, data: list):
        ret_data = []

        start_flag = False
        if kwd.startswith('('):
            kwd = kwd[1:]
            start_flag = True
        end_flag = False
        if kwd.endswith(')'):
            end_flag = True
            kwd = kwd[0:-1]

        if kw in kwd:
            t = kwd.split(kw)[0]
        else:
            t = kwd

        index = support_get_fields_other.get(t, -999)
        if index == -999:
            log.error(f" {t} -> not found in support list.")
            return
        index_vaule = data[index]
        if not index_vaule or index_vaule == '-':
            log.error(f" {t} -> {index_vaule} is None.")
            return

        if kw == '!!!!':
            kw = '='

        try:
            index_vaule = int(index_vaule)
            st = f"{t}{kw}{index_vaule}"
        except Exception as e:
            index_vaule = str(index_vaule)
            if t == 'ip' or t == 'jarm' or t == 'domain' or t == 'os' or t == 'icp' or t == 'org' or t == 'city':
                st = f"{t}{kw}{index_vaule}"
            elif t == 'host':
                from urllib.parse import urlsplit
                if index_vaule.startswith('http'):
                    val = urlsplit(index_vaule).netloc.split(':')[0]
                else:
                    val = index_vaule.split(':')[0]
                st = f"{t}{kw}{val}"
            else:
                st = f"{t}{kw}'{index_vaule}'"

        if start_flag and end_flag:
            ret_data.append('(' + st + ')')
        elif start_flag:
            ret_data.append('(' + st)
        elif end_flag:
            ret_data.append(st + ')')
        else:
            ret_data.append(st)

        return ''.join(ret_data)

    def get_ip_from_id(self, id):
        data = self._id(id=id)
        if data:
            return data[0]
        else:
            return None

    def get_searchkw_from_id(self, id, kw: str):
        data = self._id(id=id)
        # data = ['104.21.57.125', '443', 'https', '', '', '', '', '0.000000', '0.000000', '13335', 'CLOUDFLARENET', 'https://www.teslahunt.io', 'teslahunt.io', '', 'cloudflare', '', 'Real-time alerting &amp; monitoring for Tesla inventories | Tesla Hunt', '', b'', b'HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\nAge: 6\r\nAlt-Svc: h3=":443"; ma=86400, h3-29=":443"; ma=86400\r\nCache-Control: public, max-age=120\r\nCf-Cache-Status: DYNAMIC\r\nCf-Ray: 74c8fe064ff8d041-SJC\r\nConnection: keep-alive\r\nContent-Type: text/html; charset=utf-8\r\nDate: Sun, 18 Sep 2022 09:18:05 GMT\r\nNel: {"success_fraction":0,"report_to":"cf-nel","max_age":604800}\r\nReport-To: {"endpoints":[{"url":"https:\\/\\/a.nel.cloudflare.com\\/report\\/v3?s=7vquZebooMWL%2Bw5od4uT4Uc6NKZw%2Bvxr4YWeU6yxFFXsP6u9uJXSbfr%2F70bcQ1VD3%2FKonnfGvuylj%2FOhUhkdO2x%2FS3p%2Fti73jLdPVFDSWkCdUzEp5Qrfl1VMl0kFP3yMyjh0"}],"group":"cf-nel","max_age":604800}\r\nServer: cloudflare\r\nStrict-Transport-Security: max-age=63072000\r\nX-Matched-Path: /\r\nX-Powered-By: Next.js\r\nX-Vercel-Cache: HIT\r\nX-Vercel-Id: sfo1::sfo1::gv4n4-1663492685821-b8fc9e7e1c16\r\n', 'Version:  v3\nSerial Number: 1586355641409089235842258967545119341\nSignature Algorithm: ECDSA-SHA256\n\nIssuer:\n  Country: US\n  Organization: Cloudflare, Inc.\n  CommonName: Cloudflare Inc ECC CA-3\n\nValidity:\n  Not Before: 2022-06-07 00:00 UTC\n  Not After : 2023-06-06 23:59 UTC\n\nSubject:\n  Country: US\n  Province: California\n  Locality: San Francisco\n  Organization: Cloudflare, Inc.\n  CommonName: sni.cloudflaressl.com\n\nSubject Public Key Info:\n  Public Key Algorithm: ECDSA\n  Public Key:\n    DE:B2:5F:0E:E0:F2:FB:69:00:B1:CA:8F:23:03:CE:EB:\n    4E:11:05:2F:46:52:CC:77:3D:9E:BE:E9:86:B1:20:0B:\n    EF:72:12:84:CD:D4:7F:AD:71:71:35:4E:4A:DC:49:5B:\n    57:A1:85:4C:D2:69:11:4C:97:06:FA:E7:0F:5F:1A:D4\n\nAuthority Key Identifier:\n  A5:CE:37:EA:EB:B0:75:0E:94:67:88:B4:45:FA:D9:24:10:87:96:1F\n\nSubject Key Identifier:\n  23:79:6A:F6:0A:12:67:EB:87:BC:E9:10:20:77:41:55:29:81:61:45\n\nCRL Distribution Points:\n  http://crl3.digicert.com/CloudflareIncECCCA-3.crl\n  http://crl4.digicert.com/CloudflareIncECCCA-3.crl\n\nBasic Constraints:\n  CA : false\n  Path Length Constraint: UNLIMITED\n\nOCSP Server:\n  http://ocsp.digicert.com\n\nIssuing Certificate URL:\n  http://cacerts.digicert.com/CloudflareIncECCCA-3.crt\n\nKey Usage:\n  Digital Signature\n\nExtended Key Usage:\n  Server Auth\n  Client Auth\n\nDNS Names:\n  sni.cloudflaressl.com\n  *.teslahunt.io\n  teslahunt.io\n\nCertificate Signature Algorithm: ECDSA-SHA256\nCertificate Signature:\n  30:45:02:20:12:77:1A:DC:5A:97:68:AA:0C:86:35:8F:\n  FB:77:18:A7:06:D2:98:B6:6B:AF:93:35:42:61:BB:55:\n  EE:64:82:0B:02:21:00:CE:B8:8A:5D:9C:3A:AA:2B:DF:\n  4E:39:9B:C5:AF:CB:F8:DC:F2:93:F9:53:EC:78:E6:03:\n  F2:18:F0:71:23:DC:99']
        if not data:
            return
        support_get_fields = {'ip': (0, None), 'port': (1, None), 'protocol': (2, None),
                              'country': (3, None), 'region': (5, None), 'city': (6, None), 'as_number': (9, 'asn'),
                              'as_organization': (10, 'org'),
                              'host': (11, None), 'domain': (12, None), 'os': (13, None), 'server': (14, None),
                              'icp': (15, None), 'title': (16, None), 'jarm': (17, None)}

        fields_data = list(support_get_fields.keys())
        support_get_fields_other = {}
        for k in fields_data:
            if k == 'as_number':
                alias = 'asn'
            elif k == 'as_organization':
                alias = 'org'
            else:
                alias = k
            support_get_fields_other[alias] = self.VIP_SUPPORT_SEARCH_FILEDS.index(k)
        # {'ip' : 0, 'port' : 1 ...}
        # test_str = "ip==&&port||jarm!=&&(*header='X-Wingback')||os="
        # kw = test_str

        print(f" id.x support list : {color.red(', '.join(list(support_get_fields_other.keys())))}")
        if not kw_is_support(kw=kw):
            log.error(f" unsupport syntax! -> {kw} ")
            log.error(" ????????????: ==, !=, &&, || ()??? show syntax ????????????????????????")
            log.error(" ????????????: *, *??????????????????????????????&&???||??????????????????.")
            print()
            log.error(" ??????(input): ????????? id.x ????????????????????????(id.x ??????????????? sch view id). ????????????????????????")
            log.error(" input -> (ip==&&port||jarm!=)&&(*header='X-Wingback')||os=")
            print()
            log.error(" logic -> (ip==id.ip&&port=id.port||jarm!=id.jarm)&&(header='X-Wingback')&&os=id.os")
            log.error(
                " ouput => (ip==1.116.158.77&&port=3389||jarm!=2ad2ad16d2ad2ad22c2ad2ad2ad2adfd9c9d14e4f4f67f94f0359f8b28f532)&&(header='X-Wingback')||os=windows 10")
            return

        kwds = re.split(r'(&&|\|\|)', kw)
        ret_data = []  # ??????????????????????????????????????????

        for kwd in kwds:
            if not kw_is_support(kw=kwd, submodel=True):
                log.error(f' sub syntax error : {kw}')
                log.error(" unsupport syntax!")
                log.error(" ????????????: ==, !=, &&, || ()??? show syntax ????????????????????????")
                log.error(" ????????????: *, *??????????????????????????????&&???||??????????????????.")
                log.error(" ??????: (ip==&&port||jarm!=)&&(*header='X-Wingback')||os=")
                log.error(" (ip==id.ip&&port=id.port||jarm!=id.jarm)&&(header='X-Wingback')&&os=id.os")
                log.error(" ????????? id.x ????????????????????????. ?????????????????????????????????")
                return

            if kwd == '&&' or kwd == '||':
                if kwd == '&&':
                    ret_data.append('&&')
                    continue
                else:
                    ret_data.append('||')
                    continue

            dat = ''
            if '*' in kwd:
                dat = kwd.replace('*', '')
            elif '==' in kwd:
                dat = self._cover('==', kwd, support_get_fields_other, data)
            elif '!=' in kwd:
                dat = self._cover('!=', kwd, support_get_fields_other, data)
            elif '=' in kwd:
                dat = self._cover('=', kwd, support_get_fields_other, data)
            else:
                dat = self._cover('!!!!', kwd, support_get_fields_other, data)

            ret_data.append(dat)

        if None in ret_data:
            print(ret_data)
            return
        else:
            print(''.join(ret_data))
            return ''.join(ret_data)

    def get_search_kw(self):
        if self.FIELDS.querykw:
            return self.FIELDS.querykw
        else:
            log.error(' not found search querykw...')
            return

    def view(self, id=None, cert=False):
        if not self.VIEW_DATA:
            log.error(f" search results...c")
            return

        id = str(id)
        _details = []
        _details_header = ['fields']
        if id:
            temp = []
            for _id in id.split(','):
                if _id in temp:
                    continue

                _detail = self._id(id=_id)
                if _detail:
                    _details.append((_detail, _id))
                    _details_header.append('<' + 'ID' + ' ' + _id + '>')
                else:
                    return
                temp.append(_id)
        else:
            return

        # rprint(_details)
        # return
        data = {}
        for id_details_t in _details:
            id_details = id_details_t[0]
            id_number = id_details_t[1]

            # id_details = self._id(id=id)
            index = 0
            for field in self.VIP_SUPPORT_SEARCH_FILEDS:
                _field = data.setdefault(field, [])
                if isinstance(id_details[index], bytes):
                    _id_details_dat = str(id_details[index].decode('utf-8'))
                    if field == 'banner' and "\\x0" in _id_details_dat or _id_details_dat.startswith("\\x"):
                        _field.append((id_details[index], id_number))
                    else:
                        _field.append((str(id_details[index].decode('utf-8')), id_number))
                else:
                    _field.append((id_details[index], id_number))
                index = index + 1

        table = init_table(header=_details_header)
        table_cert = init_table(header=_details_header)

        _cert_rows_data = ['cert']
        # view id cert model
        if cert:
            _cert_dats = []
            cert_dats = data['cert']
            for cert_dat_t in cert_dats:
                cert_dat = cert_dat_t[0]
                if not cert_dat:
                    cert_dat = '-'
                _cert_dats.append(cert_dat)
            _cert_rows_data.extend(_cert_dats)
            # rprint(_cert_rows_data)
            table_cert.rows.append(_cert_rows_data)
            rprint(table_cert)
            return

        for key, rows_data in data.items():
            _rows_data = [key]

            for v1 in rows_data:
                v = v1[0]
                id_numb = v1[1]
                # view id <model>
                if not v:
                    v = '-'
                v = special_characte(v)
                if key == 'cert' and v != '-':
                    v = f'<see details command : sch view <{id_numb}> cert>'
                elif key == 'cert' and v == '-':
                    v = '-'
                _rows_data.append(v)

            table.rows.append(_rows_data)
            # rprint(_rows_data)
        rprint(table)


#######
@dataclass
class _StatsAPIParameter(object):
    querykw: str = None  # ????????????????????????
    qbase64: str = None  # ??????querykw ?????????base64
    fields_list = ['protocol', 'domain', 'port', 'title', 'os', 'server', 'country', 'as_number', 'as_organization',
                   'asset_type', 'fid', 'icp']
    fields: str = ','.join(fields_list)  # fields_list??????????????????????????????

# ??????fields???????????????
class _StatsApi(object):
    FIELDS = _StatsAPIParameter()

    def __init__(self) -> None:
        self.SEARCH_FIELDS = {}
        self._register_fields()

    def _search_fields(self, keywork, desc, permission, fmt_color):
        k = self.SEARCH_FIELDS.setdefault(keywork, {})
        k['desc'] = desc
        k['permission'] = permission
        k['color'] = fmt_color

    def _register_fields(self):
        self._search_fields(keywork='protocol', desc='??????', permission='-', fmt_color='red')
        self._search_fields(keywork='domain', desc='??????', permission='-', fmt_color='red')
        self._search_fields(keywork='port', desc='??????', permission='-', fmt_color='red')
        self._search_fields(keywork='title', desc='http ??????', permission='-', fmt_color='green')
        self._search_fields(keywork='os', desc='????????????', permission='-', fmt_color='red')
        self._search_fields(keywork='server', desc='http server??????', permission='-', fmt_color='red')
        self._search_fields(keywork='country', desc='?????????????????????', permission='-', fmt_color='yellow')
        self._search_fields(keywork='as_number', desc='asn??????', permission='-', fmt_color='yellow')
        self._search_fields(keywork='as_organization', desc='asn??????', permission='-', fmt_color='yellow')
        self._search_fields(keywork='asset_type', desc='????????????', permission='-', fmt_color='cyan')
        self._search_fields(keywork='fid', desc='fid ??????', permission='-', fmt_color='magenta')
        self._search_fields(keywork='icp', desc='icp????????????', permission='-', fmt_color='magenta')

    def field_print(self):
        table_header = ['?????????', '??????', '??????']
        table = init_table(header=table_header)

        for k, v in self.SEARCH_FIELDS.items():
            if v['color'] == 'red':
                k = color.red(k)
            elif v['color'] == 'green':
                k = color.green(k)
            elif v['color'] == 'yellow':
                k = color.yellow(k)
            elif v['color'] == 'magenta':
                k = color.magenta(k)
            elif v['color'] == 'white':
                k = color.white(k)
            elif v['color'] == 'cyan':
                k = color.cyan(k)
            else:
                k = color.white(k)
            table.rows.append([k, v['desc'], v['permission']])

        table.rows.header = [str(id) for id in range(0, len(table.rows))]
        print(table)

    def show_fields(self):
        max_width = shutil.get_terminal_size()[0]
        max_display = int(max_width / 4)
        header = ['Parameter', 'Required', 'Type', 'Value', 'Description']
        table = init_table(header=header)
        table.rows.append(
            [color.red('querykw'), color.red('Yes'), 'str', _format_print(self.FIELDS.querykw, max_display, force=True),
             '??????????????????base64?????????qbase64??????'])
        table.rows.append(
            ['qbase64', 'no', 'str', _format_print(self.FIELDS.qbase64, max_display), '????????????querykw????????????base64??????'])
        table.rows.append(['fields', 'no', 'str', self.FIELDS.fields, '???????????????????????????????????????. ???#3'])
        print()
        print(table)
        print()


class ApiStats(_StatsApi):

    def __init__(self, email: str, key: str) -> None:
        super().__init__()
        self.search_statistics_api = f"{BASE_API_URL}/search/stats?"
        self.user = "&email=%s&key=%s" % (email, key)
        self.data = None

    def stats(self, querykw: str):
        '''
        ???????????????????????????,????????????????????????,?????????????????????????????????5??????????????????????????????????????? 5???/???
        '''
        # curl -X GET "https://fofa.info/api/v1/search/stats?fields=title&qbase64=dGl0bGU9IueZvuW6piI%3D&email=your_email&key=your_key"
        self.FIELDS.querykw = querykw
        self.FIELDS.qbase64 = keywork_to_base64(querykw)

        fields = "fields=%s" % self.FIELDS.fields
        qbase64 = "&qbase64=%s" % self.FIELDS.qbase64

        search_statistics_url = "%s%s%s%s" % (self.search_statistics_api, fields, qbase64, self.user)

        results = fofa_request(url=search_statistics_url)

        if results['error']:
            log.error(results['error'])
            return None
        else:
            if 'aggs' in results:
                self.data = results['distinct'], results['aggs'], results['lastupdatetime']
                self._fmt_search_results()

    def _fmt_search_results(self):
        results = copy.deepcopy(self.data)

        distinct = results[0]
        aggs = results[1]
        lastupdatetime = results[2]

        header = ['field_tye', 'data 1', 'data 2', 'data 3', 'data 4', 'data 5']
        table = init_table(header=header)

        for field, field_datas in aggs.items():
            if not field_datas:
                continue
            d = [color.yellow(field)]
            i = 0
            for field_data in field_datas:
                count = str(field_data['count'])
                name = special_characte(str(field_data['name']))
  
                if len(count) < 6:
                    count = count + ' ' * (6 - len(count))

                d.append('  ' + color.red(count) + ' <-  ' + name + '  ')
                i = i + 1
            for _ in range(5 - i):
                d.append(' ')
            table.rows.append(d)
        print(f'lastupdatetime : {color.red(lastupdatetime)} , distinct : {distinct}')
        print(f'query syntax   : {color.red(self.FIELDS.querykw)}')
        print(table)

    def last(self):
        if not self.data:
            log.error(f' stats no data.....')
            return
        self._fmt_search_results()

    def set_fields(self, fields: str):
        if fields == 'all':
            self.FIELDS.fields = ','.join(self.FIELDS.fields_list)
            log.error(f" stat set fields => {self.FIELDS.fields}")
            return
        unsupport = []
        for field in fields.split(','):
            if field not in self.FIELDS.fields_list:
                unsupport.append(field)
        if unsupport:
            log.error(f" stats unsupport fields.....{','.join(unsupport)}")
            return
        self.FIELDS.fields = fields
        log.error(f" stat set fields => {fields}")


######
@dataclass
class _HostAPIParameter(object):
    host: str = None
    detail = True  # ??????????????????

class _HostAPI(object):
    FIELDS = _HostAPIParameter()

    def __init__(self) -> None:
        pass
    def show_fields(self):
        max_width = shutil.get_terminal_size()[0]
        max_display = int(max_width / 4)
        header = ['Parameter', 'Required', 'Type', 'Value', 'Description']
        table = init_table(header=header)
        table.rows.append(
            [color.red('host'), color.red('Yes'), 'str', _format_print(self.FIELDS.host, max_display, force=True),
             'host?????????ip,?????????????????????IP??????'])
        table.rows.append(
            ['detail', 'no', 'bool', _format_print(str(self.FIELDS.detail), max_display), '??????????????????????????????,??????True'])
        print()
        print(table)
        print()


class ApiHost(_HostAPI):
    def __init__(self, email: str, key: str) -> None:
        super().__init__()
        self.user = "email=%s&key=%s" % (email, key)
        self.data = None

    def host(self, host: str):
        '''???????????????????????????,??????????????????,host?????????ip,?????????????????????IP??????????????????????????????????????? 1s/???
        '''
        # curl -X GET "https://fofa.info/api/v1/host/78.48.50.249?email=your-email&key=your-key"
        host_aggs_details_api = f"{BASE_API_URL}/host/{host}?"

        self.FIELDS.host = host
        if self.FIELDS.detail:
            detail = "&detail=true"
        else:
            detail = "&detail=false"
        url = "%s%s%s" % (host_aggs_details_api, self.user, detail)

        results = fofa_request(url=url)
        if results['error']:
            log.error(results['error'])
            return {}
        else:
            self.data = results
            self._fmt_search_results()
            return results

    def set_fields(self, host: str):
        self.FIELDS.host = host
        log.error(f' Host set fields host => {host}')

    def last(self):
        if not self.data:
            log.error(" host not data...")
            return
        self._fmt_search_results()

    def _fmt_search_results(self):
        results = copy.deepcopy(self.data)

        header = ['ip', 'port', 'protocol', 'product', 'category', 'level', 'sort_hard_code']
        table = init_table(header=header)

        host = results['host']
        ip = results['ip']
        asn = results['asn']
        org = results['org']
        country_name = results['country_name']
        country_code = results['country_code']
        ports = results['ports']
        update_time = results['update_time']

        i = True
        for port_details in ports:
            table_row_date = []
            if i:
                table_row_date.append(ip)
                i = False
            else:
                table_row_date.append('*')

            if 'port' in port_details:
                table_row_date.append(port_details['port'])
            else:
                table_row_date.append('-')

            if 'protocol' in port_details:
                table_row_date.append(port_details['protocol'])
            else:
                table_row_date.append('-')

            if 'products' in port_details:
                for product in port_details['products']:
                    if 'product' in product:
                        table_row_date.append(product['product'])
                    else:
                        table_row_date.append('-')

                    if 'category' in product:
                        table_row_date.append(product['category'])
                    else:
                        table_row_date.append('-')

                    if 'level' in product:
                        if product['level'] == 5:
                            table_row_date.append('?????????')
                        elif product['level'] == 4:
                            table_row_date.append('?????????')
                        elif product['level'] == 3:
                            table_row_date.append('?????????')
                        elif product['level'] == 2:
                            table_row_date.append('?????????')
                        elif product['level'] == 1:
                            table_row_date.append('?????????')
                        elif product['level'] == 0:
                            table_row_date.append('???????????????')
                        else:
                            table_row_date.append('unknow??????')
                        # table_row_date.append(product['level'])
                    else:
                        table_row_date.append('-')

                    if 'sort_hard_code' in product:
                        if product['sort_hard_code'] == 1:
                            table_row_date.append('??????')
                        else:
                            table_row_date.append('?????????')
                        # table_row_date.append(product['sort_hard_code'])
                    else:
                        table_row_date.append('-')
            else:
                table_row_date.append('-')
                table_row_date.append('-')
                table_row_date.append('-')
                table_row_date.append('-')
            table.rows.append(table_row_date)
        print(f"update_time  : {color.red(update_time)}")
        print(f"host         : {host}")
        if 'domain' in results:
            print(f"domain       : {color.red(', '.join(results['domain']))}")
        print(
            f"country_name : {color.green(country_name)} , country_code : {color.green(country_code)} , org : {color.green(org)} , asn : {color.green(asn)}")
        rprint(table)
        # rprint(results)

######
class ApiUserInfo():
    def __init__(self, email: str, key: str) -> None:
        self.account_api_base = f"{BASE_API_URL}/info/my?"
        self.auth = "email=%s&key=%s" % (email, key)

        self.user_url = "%s%s" % (self.account_api_base, self.auth)

    def _api_user_acc(self, init=False):
        results = fofa_request(url=self.user_url)
        if DEBUG:
            rprint(results)

        if results['error']:
            if init:
                return results
            else:
                log.error(results['errmsg'])
                return

        return results

    def userinfo(self):
        max_width = shutil.get_terminal_size()[0]
        fmt_with = int(max_width / 4)
        userinfo = self._api_user_acc()
        if not userinfo:
            return

        header = []
        data = []
        for k, v in userinfo.items():
            if k == 'error' or k == 'avatar' or k == 'message':
                continue
            else:
                header.append(k)
                # data.append(str(v))
                v = str(v)
                if len(v) < fmt_with and k == 'email':
                    data.append(_format_print(v, split_len=fmt_with, force=True, space=True))
                elif len(v) < fmt_with and k == 'username':
                    data.append(_format_print(v, split_len=fmt_with, force=True, space=True))
                else:
                    data.append(v)

        table = init_table(header=header)
        table.rows.append(data)

        print()
        rprint(table)
        print()
        rprint(f" social_avatar  : {userinfo['avatar']}")
        if userinfo['message']:
            rprint(f" message : {userinfo['message']}")

########
from dataclasses import dataclass
from prompt_toolkit.application import run_in_terminal
from prompt_toolkit.key_binding import KeyBindings

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import NestedCompleter

from prompt_toolkit.styles import Style

cmd = {
    'last': None,
    'show': {'syntax': None},
    'sch': {'id': None,
            'show': {'fields': None, 'options': None},
            'set': {
                'size': None,
                'page': None,
                'full': {
                    'True': None,
                    'False': None
                },
                'fields': {'to': {'default': None, 'normal': None}}
            },
            'export': None
            },
    'view': None,
    'host': {'sch': {'id': None},
             'show': {'options': None},
             'get': {'last': None}
             },
    'stats': {'sch': {'kw': None},
              'show': {'options': None},
              'set': {'fields': {'to': {'all': None}}},
              'get': {'last': None}
              },
    'userinfo': None
}

_session = PromptSession()


@dataclass
class PromptCharter:
    banner: str = color.red('      Search for some interesting information from fofa search engine.')
    default_style_color = {'moduls': '#FF0000',  # fofa red
                           'prompt': '#FFFFFF',  # > white
                           'prompt_char': '#7CFC00'}
    style: Style = Style.from_dict(style_dict=default_style_color)
    prompt_str = ['cli', 'fofa.info/api', '>']
    cmd_json = cmd

    def __post_init__(self):
        self._prompt = ('class:prompt', f'{self.prompt_str[0]} search(')
        self._prompt_modu = ('class:moduls', f'{self.prompt_str[1]}')
        self._prompt_char = ('class:prompt', f') {self.prompt_str[2]} ')

        self.prompt = [self._prompt, self._prompt_modu, self._prompt_char]
        self.completer = NestedCompleter.from_nested_dict(self.cmd_json)


class Cli:
    def __init__(self, fofa, bindings: KeyBindings, prompt: PromptCharter) -> None:
        self.bindings = bindings
        self.prompt = prompt
        self.core = Core(search=fofa[0], userinfo=fofa[1], stats=fofa[2], host=fofa[3])

    def start(self):
        while True:
            try:
                text = _session.prompt(self.prompt.prompt,
                                       auto_suggest=AutoSuggestFromHistory(),
                                       is_password=False, completer=self.prompt.completer, key_bindings=self.bindings,
                                       style=self.prompt.style)
            except KeyboardInterrupt:
                print(color.red('goodbay...'))
                exit(1)
            text = text.split()
            if text:
                self.core.run(text=text)

class RegisterCommand(object):
    @dataclass
    class ObjCmd:
        desc: str
        exp: str
        arg = {}
        keyshot: bool

        def __post_init__(self):
            self.arg['strlen'] = len(self.exp)

            self.arg['arglen']: int = len(self.exp.split())  # search set fields <....>
            self.arg['argindex']: dict = {}
            self.arg['argstr']: dict = {}
            i = 0
            for tempalte in self.exp.split():
                if self.keyshot:
                    self.arg['arglen'] = -999
                if tempalte.startswith('<') and tempalte.endswith('>'):
                    self.arg['argindex'][str(i)] = tempalte
                else:
                    self.arg['argstr'][str(i)] = tempalte
                i = i + 1

    def __init__(self, grp_name=None) -> None:
        self.command_all = {}
        self.command = {}
        if not grp_name:
            grp_name = 'Base Command'
        self.grp = self.command.setdefault(grp_name, {})

        self.grpObj = {}
        self.format_indent = 10

    def get_format_indent(self):
        return self.format_indent

    def formt_help(self):
        if self.grpObj:
            for k, obj in self.grpObj.items():
                self.command.update(obj.command)
                if self.get_format_indent() < obj.get_format_indent():
                    self.format_indent = obj.get_format_indent()
            self.grpObj = {}
        for k, v in self.command.items():
            print()
            print(f' {k}:')
            for sub_k, sub_v in v.items():
                padd_len = self.format_indent - len(sub_k)
                rprint('  %s%s  %s' % (sub_k, padd_len * ' ', sub_v['desc']))
        print()

    def add_group(self, grp):
        if grp == 'Base Command':
            return
        cmdObj = RegisterCommand(grp_name=grp)
        self.grpObj[grp] = cmdObj
        return cmdObj

    def add_cmd(self, exp, desc, keyshot=False):
        cmd = self.ObjCmd(desc=desc, exp=exp, keyshot=keyshot)
        cmd_data = self.grp.setdefault(exp, {})
        cmd_data['exp'] = cmd.exp  # sch show options / sch view <1> cert
        cmd_data['desc'] = cmd.desc  # xxxxxxxx
        cmd_data['arg'] = {}
        cmd_data['arg']['strlen'] = cmd.arg['strlen']
        cmd_data['arg']['arglen'] = cmd.arg['arglen']
        cmd_data['arg']['argindex'] = cmd.arg['argindex']
        cmd_data['arg']['argstr'] = cmd.arg['argstr']

        if self.format_indent < cmd_data['arg']['strlen']:
            self.format_indent = cmd_data['arg']['strlen']

    def parse_input(self, texts: list):
        arglen = len(texts)

        if self.grpObj:
            self.command_all.update(self.grp)
            for k, registerCommand in self.grpObj.items():
                self.command_all.update(registerCommand.grp)
                self.command.update(registerCommand.command)

        for option in self.command_all.values():
            flag = True
            if arglen == option['arg']['arglen']:
                # rprint(option)
                for index, date in option['arg']['argstr'].items():
                    if texts[int(index)] == date:
                        pass
                    else:
                        flag = False
                if flag:
                    # print(f"input  ->  {' '.join(texts)}")
                    # print(f"parse  ->  {option['exp']}")

                    text_arg = []
                    for arg_index in option['arg']['argindex'].keys():
                        text_arg.append(texts[int(arg_index)])
                    return option['exp'], tuple(text_arg)
                    break
                else:
                    pass
            else:
                pass


###
class Core(object):
    def __init__(self, search=None, host=None, stats=None, userinfo=None) -> None:
        self.fofa_search_obj: ApiSearch = search
        self.fofa_host_obj: ApiHost = host
        self.stats_obj: ApiStats = stats
        self.userinfo_obj: ApiUserInfo = userinfo
        self.syantx = _SearchSyntax()

        self.register_Command_obj = self._command_register()

    def _command_register(self):
        base = RegisterCommand(grp_name='Global commands')
        base.add_cmd(exp='show syntax', desc='?????????????????????????????????#2. ?????????: ctrl + \\')
        base.add_cmd(exp='exit', desc='????????????.')
        base.add_cmd(exp='help', desc='??????????????????.')
        base.add_cmd(exp='?', desc='??????????????????.')

        pro_init = base.add_group(grp='re-init app command')
        pro_init.add_cmd(exp='re-init email <email> key <key>', desc='re-init processes.')

        keyshot = base.add_group(grp='Keyshot support')
        keyshot.add_cmd(exp='<c-\\>', desc='show syntax, ???????????????.', keyshot=True)
        keyshot.add_cmd(exp='<c-l>', desc='last, ???????????????', keyshot=True)
        keyshot.add_cmd(exp='<c-k>', desc='sch set fields to normal, ???????????????', keyshot=True)
        keyshot.add_cmd(exp='<c-j>', desc='sch set fields to default, ???????????????', keyshot=True)
        keyshot.add_cmd(exp='<c-i>', desc='sch set size <num+50>, ???????????????,????????????size???50', keyshot=True)
        keyshot.add_cmd(exp='<c-u>', desc='sch set page <num+1>, ???????????????,????????????page???1', keyshot=True)
        keyshot.add_cmd(exp='<c-d>', desc='sch set size/page <100>/<1> , ???????????????,??????size/page????????????', keyshot=True)
        keyshot.add_cmd(exp='<c-p>', desc='stats sch kw, ???????????????', keyshot=True)
        keyshot.add_cmd(exp='<c-y>', desc='sch <syntax...>, ???????????????.??????????????????????????????????????????.', keyshot=True)

        search = base.add_group(grp='Search Command')
        search.add_cmd(exp='sch <syntax...>', desc='??????????????????,????????????????????????.(????????????????????????#2)')
        search.add_cmd(exp='sch id <id> <ip==&&port||jarm!=...>', desc='??????????????????id????????????????????????????????????(????????????).')
        search.add_cmd(exp='sch set size <num>', desc='?????????????????????????????????????????????. ?????????: ctrl + i')
        search.add_cmd(exp='sch set page <num>', desc='????????????????????????. ?????????: ctrl + u')
        search.add_cmd(exp='sch set full <True/False>', desc='????????????????????????????????????. (True:????????????,False:????????????).')

        search.add_cmd(exp='sch show fields', desc='??????????????????????????????,?????????????????????????????????????????????????????????(????????????), body,fid,structinfo??????.#1.')
        search.add_cmd(exp='sch show options', desc='???????????????????????????????????????.size, page, full, fileds?????????.')

        search_s = base.add_group(grp='Search res-related commands')
        search_s.add_cmd(exp='sch export <"d:\\files.csv">', desc='?????????????????????????????????. "d:\\files.csv"')
        search_s.add_cmd(exp='sch set fields <ip,port,os...>',
                       desc='?????????????????????????????????(??????:ctrl + j/k , ctrl + l).??????????????????????????????#1 ???https://fofa.info/api. ??????1')
        search_s.add_cmd(exp='sch set fields to normal',
                       desc='?????????????????????????????????(?????????: ctrl + k).??????<ip,port,os,jarm,cert,banner,header,server,country,title,as_organization>.')
        search_s.add_cmd(exp='sch set fields to default',
                       desc='??????(?????????: ctrl + j).??????<ip,port,protocol,host,domain,os,server,banner,header,title,city,country,longitude,latitude>.')
        search_s.add_cmd(exp='last', desc='????????????sch <syntax...> ???????????????????????????. ?????????: ctrl + l')
        search_s.add_cmd(exp='view <id>', desc='?????????????????????<id1,id2,id3...>????????????????????????.')
        search_s.add_cmd(exp='view <id> cert', desc='?????????????????????<id1,id2,id3...>??????????????????<??????>??????????????????.')

        host = base.add_group(grp='Host Aggs Command')
        host.add_cmd(exp='host <host/ip>', desc='????????????????????????,??????????????????,??????????????????,?????????????????????IP??????.')
        host.add_cmd(exp='host sch id <id_num>', desc='??????search??????????????????id?????????ip?????????????????????????????????.')
        host.add_cmd(exp='host show options', desc='??????host?????????????????????????????????.')
        host.add_cmd(exp='host get last', desc='?????????????????????????????????????????????.')

        stats = base.add_group(grp='Stats Aggs Command')
        stats.add_cmd(exp='stats <syntax...>', desc='????????????????????????,??????????????????,????????????????????????,??????????????????????????????5??????..???#2')
        stats.add_cmd(exp='stats sch kw', desc='??????search ????????????????????????????????????????????????.?????????: ctrl + p')
        stats.add_cmd(exp='stats show fields', desc='?????????????????????????????????????????????#3.')
        stats.add_cmd(exp='stats set fields <os,fid,icp...>', desc='????????????????????????????????????,??????????????????????????????????????????#3.')
        stats.add_cmd(exp='stats set fields to all', desc='????????????????????????????????????????????????????????????????????????#3.')
        stats.add_cmd(exp='stats show options', desc='????????????????????????????????????????????????.')
        stats.add_cmd(exp='stats get last', desc='???????????????????????????????????????.')

        userinfo = base.add_group(grp='User Command')
        userinfo.add_cmd(exp='info', desc='??????????????????.')
        return base

    def run(self, text):
        args = self.register_Command_obj.parse_input(text)

        if not args:
            if text[0] == 'sch':
                kw = ['id', 'set', 'show', 'view', 'export']
                args = ('sch <syntax...>', (' '.join(text[1:]),))
                for k1 in kw:
                    if f'sh {k1}' == ' '.join(text):
                        log.error(f" unknow input : {' '.join(text)}")
                        return

                    if re.match(f'^sch {k1}', ' '.join(text)):
                        if re.match(r"^sch id \d+ \S", ' '.join(text)):
                            args = ('sch id <id> <ip==&&port||jarm!=...>', (text[2], ' '.join(text[3:]),))
                            break
                        log.error(f" unknow input : {' '.join(text)}")
                        return
            elif text[0] == 'stats':
                kw = ['sch', 'set', 'show', 'get']
                for k1 in kw:
                    if f'sh {k1}' == ' '.join(text):
                        log.error(f" unknow input : {' '.join(text)}")
                        return

                    if re.match(f'^stats {k1}', ' '.join(text)):
                        log.error(f" unknow input : {' '.join(text)}")
                        return
                args = ('stats <syntax...>', (' '.join(text[1:]),))
            else:
                log.error(f" unknow input : {' '.join(text)}")
                return

        kw = args[0]
        arg = args[1]

        # print(kw, arg)
        if kw == 'show syntax':
            self.syantx.synax_print()

        if kw == 'help' or kw == '?':
            self.register_Command_obj.formt_help()
        if kw == 'exit':
            print(color.red('goodbay...'))
            exit(1)

        if kw == 're-init email <email> key <key>':
            _email = arg[0]
            _key = arg[1]
            _info = ApiUserInfo(email=_email, key=_key)._api_user_acc(init=True)
            if _info['error']:
                print(' re-initialization ' + color.red('failed') + f".{_info['errmsg']}")
            else:
                _b_data = bytes(json.dumps({'email': _email, 'key': _key}), encoding='UTF-8')

                _auth = AuthStorage()
                _auth.enc(enc_dat=_b_data)
                print(' re-initialization ' + color.green('succeeded') + '.')

        if kw == 'last':
            self.fofa_search_obj.last()
        if kw == 'sch <syntax...>':
            self.fofa_search_obj.search(kw=arg[0])
        if kw == 'sch id <id> <ip==&&port||jarm!=...>':
            dat = self.fofa_search_obj.get_searchkw_from_id(id=arg[0], kw=arg[1])
            if dat:
                self.fofa_search_obj.search(kw=dat)
        if kw == 'sch set size <num>':
            self.fofa_search_obj.set_fields(**{'size': arg[0]})
        if kw == 'sch set page <num>':
            self.fofa_search_obj.set_fields(**{'page': arg[0]})
        if kw == 'sch set full <True/False>':
            if arg[0] == 'true':
                flag = True
            elif arg[0] == 'false':
                flag = False
            else:
                flag = False
            self.fofa_search_obj.set_fields(**{'full': flag})
        if kw == 'sch show fields':
            self.fofa_search_obj.field_print()
        if kw == 'sch set fields <ip,port,os...>':
            self.fofa_search_obj.set_fields(**{'fields': arg[0]})
        if kw == 'sch set fields to default':
            self.fofa_search_obj.set_fields_default()
        if kw == 'sch set fields to normal':
            self.fofa_search_obj.set_fields_normal()
        if kw == 'sch show options':
            self.fofa_search_obj.show_fields()

        if kw == 'view <id>':
            self.fofa_search_obj.view(id=arg[0])
        if kw == 'view <id> cert':
            self.fofa_search_obj.view(id=arg[0], cert=True)
        if kw == 'sch export <"d:\\files.csv">':
            self.fofa_search_obj.export(file=arg[0])

        if kw == 'host <host/ip>':
            self.fofa_host_obj.host(host=arg[0])
        if kw == 'host sch id <id_num>':
            ip = self.fofa_search_obj.get_ip_from_id(arg[0])
            if ip:
                self.fofa_host_obj.host(host=ip)
        if kw == 'host show options':
            self.fofa_host_obj.show_fields()
        if kw == 'host get last':
            self.fofa_host_obj.last()

        if kw == 'stats <syntax...>':
            self.stats_obj.stats(arg[0])
        if kw == 'stats sch kw':
            queryKW = self.fofa_search_obj.get_search_kw()
            if queryKW:
                self.stats_obj.stats(queryKW)
        if kw == 'stats show fields':
            self.stats_obj.field_print()
        if kw == 'stats set fields <os,fid,icp...>':
            self.stats_obj.set_fields(arg[0])
        if kw == 'stats set fields to all':
            self.stats_obj.set_fields('all')
        if kw == 'stats show options':
            self.stats_obj.show_fields()
        if kw == 'stats get last':
            self.stats_obj.last()

        if kw == 'info':
            self.userinfo_obj.userinfo()

def main():
    email = None
    key = None

    import argparse
    parser = argparse.ArgumentParser(description='Command-line interaction tools for fofa.info.',
                                     epilog="emmmm......")
    parser.add_argument('--init', nargs=2, metavar=('email', 'key'), help='init processes first.')
    args = parser.parse_args()

    _init_args = args.init
    if _init_args:
        _email = _init_args[0]
        _key = _init_args[1]
        userinfo = ApiUserInfo(email=_email, key=_key)
        _info = userinfo._api_user_acc(init=True)
        if _info['error']:
            print(' initialization ' + color.red('failed') + f".{_info['errmsg']}")
            exit()
        else:
            auth = {}
            auth['email'] = _email
            auth['key'] = _key
            data = bytes(json.dumps(auth), encoding='UTF-8')

            _auth = AuthStorage()
            _auth.enc(enc_dat=data)
            print(' initialization ' + color.green('succeeded') + '.')
            exit()
    else:
        auth = AuthStorage()
        _dat = auth.un_enc()

        if not _dat:
            print(color.red(' initialize the program first.'))
            exit()

        email = _dat.get('email', None)
        key = _dat.get('key', None)

    search = ApiSearch(email=email, key=key)
    userinfo = ApiUserInfo(email=email, key=key)
    stats = ApiStats(email=email, key=key)
    host = ApiHost(email=email, key=key)

    fofa = (search, userinfo, stats, host)

    syntax = _SearchSyntax()
    default_prompt = PromptCharter()

    print()
    print(default_prompt.banner)
    print()

    bindings = KeyBindings()  

    @bindings.add('c-\\')
    def _(event):
        def _SearchSyntax():
            syntax.synax_print()

        print()
        run_in_terminal(_SearchSyntax)

    @bindings.add('c-l')
    def _(event, fofa=search):
        def _get_search_last():
            fofa.last()

        print()
        run_in_terminal(_get_search_last)

    @bindings.add('c-k')
    def _(event, fofa=search):
        def _set_search_fields_normal():
            fofa.set_fields_normal()

        print()
        run_in_terminal(_set_search_fields_normal)

    @bindings.add('c-j')
    def _(event, fofa=search):
        def _set_search_fields_default():
            fofa.set_fields_default()

        print()
        run_in_terminal(_set_search_fields_default)

    @bindings.add('c-i')
    def _(event, fofa=search):
        def _set_search_size_50():
            size = fofa.FIELDS.size
            fofa.set_fields(size_next=True, **{'size': size})

        print()
        run_in_terminal(_set_search_size_50)

    @bindings.add('c-u')
    def _(event, fofa=search):
        def _set_search_page():
            page = fofa.FIELDS.page
            fofa.set_fields(size_page=True, **{'page': page})

        print()
        run_in_terminal(_set_search_page)

    @bindings.add('c-d')
    def _(event, fofa=search):
        def _set_search_all_default():
            page = 1
            size = 100
            fofa.set_fields(**{'page': page, 'size': size})

        print()
        run_in_terminal(_set_search_all_default)

    @bindings.add('c-p')
    def _(event, stats=stats, fofa=search):
        def _get_stats_from_search_syntax():
            qew = fofa.FIELDS.querykw
            if qew is None:
                log.error(' search querykw is <None>.')
                return
            stats.stats(qew)

        print()
        run_in_terminal(_get_stats_from_search_syntax)

    @bindings.add('c-y')
    def _(event, fofa=search):
        def _research():
            qew = fofa.FIELDS.querykw
            if qew is None:
                log.error(' search querykw is <None>.')
                return
            fofa.search(qew)

        print()
        run_in_terminal(_research)

    c = Cli(fofa=fofa, bindings=bindings, prompt=default_prompt)
    c.start()

import sys
if __name__ == '__main__':
    sys.exit(main())
