import re
import os
from os.path import dirname, join, exists
from torito_prototype.entity.config import Config, ProxyConfig, BridgeConfig
from datetime import datetime
from returns.result import Result, Success, Failure


entryPattern = re.compile(
    r"(?P<directive>UseBridges |Bridge |HTTPProxy |HTTPProxyAuthenticator |HTTPSProxy |HTTPSProxyAuthenticator |Socks4Proxy |Socks5Proxy |Socks5ProxyUsername |Socks5ProxyPassword )(?P<args>.*)"
)

class TorrcRepository:
    path: str
    backUpPath: str

    def __init__(self, path: str, backUpDirName: str):
        # ファイルが存在するかチェック
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
                
        # バックアップを格納するディレクトリを作成
        if not exists(join(dirname(path), backUpDirName)):
            os.makedirs(join(dirname(path), backUpDirName))
            
        # ディレクトリパス取得
        backUpPath = join(dirname(path), backUpDirName, f"{datetime.now().strftime('%Y%m%d%H%M%S')}_torrc")
        
        self.path = path
        self.backUpPath = backUpPath

    def backup(self) -> Result[None, Exception]:
        try:
            with open(self.path, "r") as f:
                with open(self.backUpPath, "w") as b:
                    b.write(f.read())
            return Success(None)
        except Exception as e:
            return Failure(e)

    def load(self) -> Result[Config, Exception]:

        try:
            with open(self.path, "r") as f:
                # インデックスを付与する
                lines = enumerate(f.readlines(), start=1)
        except Exception as e:
            return Failure(e)

        tmp = {
            "UseBridges": False,
            "Bridge": [],
            "HTTPProxy": [],
            "HTTPProxyAuthenticator": [],
            "HTTPSProxy": [],
            "HTTPSProxyAuthenticator": [],
            "Socks4Proxy": [],
            "Socks5Proxy": [],
            "Socks5ProxyUsername": [],
            "Socks5ProxyPassword": [],
            "others": []
        }

        for _, line in lines:
            match = entryPattern.match(line)
            if match is None:
                thisLine = line.strip()
                if thisLine == "### This file was generated by torito_prototype ###" or thisLine == "### End of generated ###":
                    continue

                tmp["others"].append(thisLine)
                continue

            directive = match.group("directive").strip()
            args = match.group("args").strip()

            match directive:
                case "UseBridges":
                    tmp["UseBridges"] = True if args == "1" else False
                case "Bridge":
                    tmp["Bridge"].append(args)
                case "HTTPProxy":
                    tmp["HTTPProxy"].append(args)
                case "HTTPProxyAuthenticator":
                    tmp["HTTPProxyAuthenticator"].append(args)
                case "HTTPSProxy":
                    tmp["HTTPSProxy"].append(args)
                case "HTTPSProxyAuthenticator":
                    tmp["HTTPSProxyAuthenticator"].append(args)
                case "Socks4Proxy":
                    tmp["Socks4Proxy"].append(args)
                case "Socks5Proxy":
                    tmp["Socks5Proxy"].append(args)
                case "Socks5ProxyUsername":
                    tmp["Socks5ProxyUsername"].append(args)
                case "Socks5ProxyPassword":
                    tmp["Socks5ProxyPassword"].append(args)


        try: 
            config = Config(
                useBridge=tmp["UseBridges"],
                bridgeConfig=BridgeConfig(bridgeParams=tmp["Bridge"]),
                proxyConfig=ProxyConfig(
                    HTTPProxyParams=tmp["HTTPProxy"],
                    HTTPProxyAuthenticatorParams=tmp["HTTPProxyAuthenticator"],
                    HTTPSProxyParams=tmp["HTTPSProxy"],
                    HTTPSProxyAuthenticatorParams=tmp["HTTPSProxyAuthenticator"],
                    Socks4ProxyParams=tmp["Socks4Proxy"],
                    Socks5ProxyParams=tmp["Socks5Proxy"],
                    Socks5ProxyUsernameParams=tmp["Socks5ProxyUsername"],
                    Socks5ProxyPasswordParams=tmp["Socks5ProxyPassword"]
                ),
                others=tmp["others"]
            )

            return Success(config)
        except Exception as e:
            return Failure(e)
        
    def save(self, config: Config) -> Result[None, Exception]:
        try:
            with open(self.path, "w") as f:

                f.write("### This file was generated by torito_prototype ###\n")
                if config.useBridge:
                    f.write("UseBridges 1\n")

                if config.bridgeConfig.bridgeParams:
                    f.write("\n".join([f"Bridge {bridgeParam}" for bridgeParam in config.bridgeConfig.bridgeParams]) + "\n")

                if config.proxyConfig.HTTPProxyParams:
                    f.write("\n".join([f"HTTPProxy {HTTPProxyParam}" for HTTPProxyParam in config.proxyConfig.HTTPProxyParams]) + "\n")
                if config.proxyConfig.HTTPProxyAuthenticatorParams:
                    f.write("\n".join([f"HTTPProxyAuthenticator {HTTPProxyAuthenticatorParam}" for HTTPProxyAuthenticatorParam in config.proxyConfig.HTTPProxyAuthenticatorParams]) + "\n")
                if config.proxyConfig.HTTPSProxyParams:
                    f.write("\n".join([f"HTTPSProxy {HTTPSProxyParam}" for HTTPSProxyParam in config.proxyConfig.HTTPSProxyParams]) + "\n")
                if config.proxyConfig.HTTPSProxyAuthenticatorParams:
                    f.write("\n".join([f"HTTPSProxyAuthenticator {HTTPSProxyAuthenticatorParam}" for HTTPSProxyAuthenticatorParam in config.proxyConfig.HTTPSProxyAuthenticatorParams]) + "\n")
                if config.proxyConfig.Socks4ProxyParams:
                    f.write("\n".join([f"Socks4Proxy {Socks4ProxyParam}" for Socks4ProxyParam in config.proxyConfig.Socks4ProxyParams]) + "\n")
                if config.proxyConfig.Socks5ProxyParams:
                    f.write("\n".join([f"Socks5Proxy {Socks5ProxyParam}" for Socks5ProxyParam in config.proxyConfig.Socks5ProxyParams]) + "\n")
                if config.proxyConfig.Socks5ProxyUsernameParams:
                    f.write("\n".join([f"Socks5ProxyUsername {Socks5ProxyUsernameParam}" for Socks5ProxyUsernameParam in config.proxyConfig.Socks5ProxyUsernameParams]) + "\n")
                if config.proxyConfig.Socks5ProxyPasswordParams:
                    f.write("\n".join([f"Socks5ProxyPassword {Socks5ProxyPasswordParam}" for Socks5ProxyPasswordParam in config.proxyConfig.Socks5ProxyPasswordParams]) + "\n")

                f.write("### End of generated ###\n")
                
                f.write("\n".join(config.others))
        except Exception as e:
            return Failure(e)
        
        return Success(None)