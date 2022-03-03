from distutils.log import debug
from pydantic import BaseSettings


class Settings(BaseSettings):
    debug: bool = False
    root_path: str = ''

    mail_username: str
    mail_password: str
    mail_from: str
    mail_port: int
    mail_server: str
    mail_tls: bool
    mail_ssl: bool
    use_credentials: bool
    validate_certs: bool

    class Config:
        env_file = '.env'
