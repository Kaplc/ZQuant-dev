import json
from json import JSONDecodeError
import logging
import requests
from .__version__ import __version__
from sdk.binance_sdk.binance.error import ClientError, ServerError
from sdk.binance_sdk.binance.lib.utils import get_timestamp
from sdk.binance_sdk.binance.lib.utils import cleanNoneValue
from sdk.binance_sdk.binance.lib.utils import encoded_string
from sdk.binance_sdk.binance.lib.utils import check_required_parameter
from sdk.binance_sdk.binance.lib.authentication import hmac_hashing, rsa_signature


class API(object):
    """API base class

    Keyword Args:
        base_url (str, optional): the API base url, useful to switch to testnet, etc. By default it's https://api.binance.com
        timeout (int, optional): the time waiting for server response, number of seconds. https://docs.python-requests.org/en/master/user/advanced/#timeouts
        proxies (obj, optional): Dictionary mapping protocol to the URL of the proxy. e.g. {'https': 'http://1.2.3.4:8080'}
        show_limit_usage (bool, optional): whether return limit usage(requests and/or orders). By default, it's False
        show_header (bool, optional): whether return the whole response header. By default, it's False
        private_key (str, optional): RSA private key for RSA authentication
        private_key_pass(str, optional): Password for PSA private key

        关键字Args:
        base_url（str，optional）：API基本url，用于切换到测试网等。默认情况下，它是https://api.binance.com
        timeout（int，optional），用于等待服务器响应的时间，秒数。https://docs.python-requests.org/en/master/user/advanced/#timeouts
        proxies（obj，optional）：到代理URL的字典映射协议。例如｛'https':'http:1.2.3.4:8080'｝
        show_limit_usage（bool，optional）：是否返回限制使用（请求和或订单）。默认情况下，它是False
        show_header（bool，optional）：是否返回整个响应标头。默认情况下，它是False
        private_key（str，optional）：用于RSA身份验证的RSA私钥
        private_key_pass（str, optional）：用于PSA私钥的密码
    """

    def __init__(
            self,
            api_key=None,
            api_secret=None,
            base_url=None,
            timeout=None,
            proxies=None,
            show_limit_usage=False,
            show_header=False,
            private_key=None,
            private_key_pass=None,
    ):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url
        self.timeout = timeout
        self.proxies = None
        self.show_limit_usage = False
        self.show_header = False
        self.private_key = private_key
        self.private_key_pass = private_key_pass
        self.session = requests.Session()  # 创建session对象
        self.session.headers.update(  # 更新session请求头
            {
                "Content-Type": "application/json;charset=utf-8",
                "User-Agent": "binance-connector/" + __version__,
                "X-MBX-APIKEY": api_key,
            }
        )

        if show_limit_usage is True:
            self.show_limit_usage = True

        if show_header is True:
            self.show_header = True

        if type(proxies) is dict:  # 初始化代理URL协议映射
            self.proxies = proxies

        self._logger = logging.getLogger(__name__)
        return

    def query(self, url_path, payload=None):
        """发送请求返回响应"""
        return self.send_request("GET", url_path, payload=payload)

    def limit_request(self, http_method, url_path, payload=None):
        """
        limit request is for those endpoints require API key in the header
        调用那些需要在请求头中包含 API 密钥的接口
        """

        check_required_parameter(self.api_key, "api_key")  # 检查是否设置了 API 密钥
        return self.send_request(http_method, url_path, payload=payload)  # 发送请求返回data

    def sign_request(self, http_method, url_path, payload=None):
        """payload带签名发送请求"""
        if payload is None:
            payload = {}
        payload["timestamp"] = get_timestamp()  # 生成毫秒时间戳
        query_string = self._prepare_params(payload)  # 编码转换 %40 <=> @
        payload["signature"] = self._get_sign(query_string)  # 生成签名
        return self.send_request(http_method, url_path, payload)  # 发送请求返回data

    def limited_encoded_sign_request(self, http_method, url_path, payload=None):
        """This is used for some endpoints has special symbol in the url.
        In some endpoints these symbols should not encoded
        - @
        - [
        - ]

        so we have to append those parameters in the url
        带签名url的发送请求
        """
        if payload is None:
            payload = {}
        payload["timestamp"] = get_timestamp()
        query_string = self._prepare_params(payload)
        url_path = (
                url_path + "?" + query_string + "&signature=" + self._get_sign(query_string)
        )
        return self.send_request(http_method, url_path)

    def send_request(self, http_method, url_path, payload=None):
        """发送请求并接受响应"""
        if payload is None:
            payload = {}
        url = self.base_url + url_path
        self._logger.debug("url: " + url)
        params = cleanNoneValue(  # 清除字典中值为 None 的键值对
            {
                "url": url,
                "params": self._prepare_params(payload),
                "timeout": self.timeout,
                "proxies": self.proxies,
            }
        )
        response = self._dispatch_request(http_method)(**params)  # 发送请求返回response对象
        self._logger.debug("raw response from server:" + response.text)
        self._handle_exception(response)  # 响应状态码的处理

        try:
            data = response.json()
        except ValueError:
            data = response.text
        result = {}  # 构建空字典

        if self.show_limit_usage:  # 提取usage到空字典
            limit_usage = {}
            for key in response.headers.keys():
                key = key.lower()
                if (
                        key.startswith("x-mbx-used-weight")
                        or key.startswith("x-mbx-order-count")
                        or key.startswith("x-sapi-used")
                ):
                    limit_usage[key] = response.headers[key]
            result["limit_usage"] = limit_usage

        if self.show_header:  # 提取响应头
            result["header"] = response.headers

        if len(result) != 0:  # 提取data
            result["data"] = data
            return result
        # 不需要提取数据直接返回
        return data

    def _prepare_params(self, params):
        """编码转换 %40 <=> @"""
        return encoded_string(cleanNoneValue(params))

    def _get_sign(self, payload):
        """RSA/hash签名"""
        if self.private_key:  # 有私钥
            return rsa_signature(self.private_key, payload, self.private_key_pass)  # 对 payload 进行 RSA 签名
        return hmac_hashing(self.api_secret, payload)  # 对 payload 进行哈希处理

    def _dispatch_request(self, http_method):
        """返回对应请求方法"""
        return {
            "GET": self.session.get,
            "DELETE": self.session.delete,
            "PUT": self.session.put,
            "POST": self.session.post,
        }.get(http_method, "GET")  # 无对应默认使用"GET"发送请求并返回response

    def _handle_exception(self, response):
        """请求响应状态码的处理"""
        status_code = response.status_code
        if status_code < 400:  # 小于 400，表示请求成功，直接返回
            return
        if 400 <= status_code < 500:  # 状态码在 400 到 500 之间，表示客户端错误，尝试解析响应的文本内容为 JSON 格式，并抛出 ClientError 异常。
            try:
                err = json.loads(response.text)
            except JSONDecodeError:
                raise ClientError(
                    status_code, None, response.text, None, response.headers  # 异常中包含了状态码、错误码、错误信息、响应头和错误数据等信息
                )
            error_data = None
            if "data" in err:
                error_data = err["data"]
            raise ClientError(
                status_code, err["code"], err["msg"], response.headers, error_data
            )
        raise ServerError(status_code, response.text)  # 状态码大于等于 500，表示服务器错误，抛出 ServerError 异常
