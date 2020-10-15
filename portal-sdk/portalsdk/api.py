import json
from enum import Enum
from pprint import pprint

import requests
from base64 import b64decode, b64encode
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_PKCS1_v1_5


class APIRequest:

    def __init__(self, context=None):
        self.context = context

    def execute(self):
        if self.context is not None:
            self.create_default_headers()
            # pprint(self.context)
            try:
                return {
                    APIMethodType.GET: self.__get,
                    APIMethodType.POST: self.__post,
                    APIMethodType.PUT: self.__put
                }.get(self.context.method_type, self.__unknown)()
            except requests.exceptions.ConnectionError as ce:
                print(ce)
                return None
        else:
            raise TypeError('Context cannot be None.')

    def create_bearer_token(self):
        key_der = b64decode(self.context.public_key)
        key_pub = RSA.importKey(key_der)
        cipher = Cipher_PKCS1_v1_5.new(key_pub)
        cipher_text = cipher.encrypt(self.context.api_key.encode('ascii'))
        encrypted_msg = b64encode(cipher_text)

        return encrypted_msg

    def create_default_headers(self):
        self.context.add_header('Authorization', 'Bearer {}'.format(self.create_bearer_token().decode('utf-8')))
        self.context.add_header('Content-Type', 'application/json')
        self.context.add_header('Host', self.context.address)

    def __get(self):
        r = requests.get(self.context.get_url(), params=self.context.get_parameters(), headers=self.context.get_headers())
        print(r)
        return APIResponse(r.status_code, json.loads(r.headers.__str__().replace("'", '"')), json.loads(r.text))

    def __post(self):
        r = requests.post(self.context.get_url(), headers=self.context.get_headers(), json=self.context.get_parameters())
        print(r)
        return APIResponse(r.status_code, json.loads(r.headers.__str__().replace("'", '"')), json.loads(r.text))

    def __put(self):
        print('PUT')
        r = requests.put(self.context.get_url(), headers=self.context.get_headers(), json=self.context.get_parameters())
        print('PUT', r)
        return APIResponse(r.status_code, json.loads(r.headers.__str__().replace("'", '"')), json.loads(r.text))

    def __unknown(self):
        raise Exception('Unknown Method')


class APIResponse(dict):

    def __init__(self, status_code, headers, body):
        super(APIResponse, self).__init__()
        self['status_code']: str = status_code
        self['headers']: dict = headers
        self['body']: dict = body

    @property
    def status_code(self) -> int:
        return self['status_code']

    @status_code.setter
    def status_code(self, status_code: int):
        if type(status_code) is not int:
            raise TypeError('status_code must be a int')
        else:
            self['status_code'] = status_code

    @property
    def headers(self) -> dict:
        return self['headers']

    @headers.setter
    def headers(self, headers: dict):
        if type(headers) is not dict:
            raise TypeError('headers must be a dict')
        else:
            self['headers'] = headers

    @property
    def body(self) -> dict:
        return self['body']

    @body.setter
    def body(self, body: dict):
        if type(body) is not dict:
            raise TypeError('body must be a dict')
        else:
            self['body'] = body


class APIMethodType(Enum):
    GET: int = 0
    POST: int = 1
    PUT: int = 3
    DELETE: int = 4


class APIContext(dict):

    def __init__(self, api_key='', public_key='', ssl=False, method_type=APIMethodType.GET, address='', port=80, path='', headers={}, parameters={}):
        super(APIContext, self).__init__()

        self['api_key']: str = api_key
        self['public_key']: str = public_key
        self['ssl']: bool = ssl
        self['method_type']: Enum = method_type
        self['address']: str = address
        self['port']: int = port
        self['path']: str = path
        self['headers']: dict = headers
        self['parameters']: dict = parameters

    def get_url(self):
        if self.ssl is True:
            return 'https://{}:{}{}'.format(self.address, self.port, self.path)
        else:
            return 'http://{}:{}{}'.format(self.address, self.port, self.path)

    def add_header(self, header, value):
        self['headers'].update({header: value})

    def get_headers(self):
        return self['headers']

    def add_parameter(self, key, value):
        self['parameters'].update({key: value})

    def get_parameters(self):
        return self['parameters']

    @property
    def api_key(self) -> str:
        return self['api_key']

    @api_key.setter
    def api_key(self, api_key: str):
        if type(api_key) is not str:
            raise TypeError('api_key must be a str')
        else:
            self['api_key'] = api_key

    @property
    def public_key(self) -> str:
        return self['public_key']

    @public_key.setter
    def public_key(self, public_key: str):
        if type(public_key) is not str:
            raise TypeError('public_key must be a str')
        else:
            self['public_key'] = public_key

    @property
    def ssl(self) -> bool:
        return self['ssl']

    @ssl.setter
    def ssl(self, ssl: bool):
        if type(ssl) is not bool:
            raise TypeError('ssl must be a bool')
        else:
            self['ssl'] = ssl

    @property
    def method_type(self) -> APIMethodType:
        return self['method_type']

    @method_type.setter
    def method_type(self, method_type: APIMethodType):
        if type(method_type) is not APIMethodType:
            raise TypeError('method_type must be a APIMethodType')
        else:
            self['method_type'] = method_type

    @property
    def address(self) -> str:
        return self['address']

    @address.setter
    def address(self, address: str):
        if type(address) is not str:
            raise TypeError('address must be a str')
        else:
            self['address'] = address

    @property
    def port(self) -> int:
        return self['port']

    @port.setter
    def port(self, port: int):
        if type(port) is not int:
            raise TypeError('port must be a int')
        else:
            self['port'] = port

    @property
    def path(self) -> str:
        return self['path']

    @path.setter
    def path(self, path: str):
        if type(path) is not str:
            raise TypeError('path must be a str')
        else:
            self['path'] = path
