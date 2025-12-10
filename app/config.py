from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
    DATABASE_URL: str ="mysqldb"
    DATABASE_QUERY_ECHO: bool = False
    AUTHJWT_SECRET_KEY: str = ""
    AUTHJWT_ACCESS_COOKIE_KEY: str = ""
    AUTHJWT_REFRESH_COOKIE_KEY: str = ""
    AUTHJWT_COOKIE_CSRF_PROTECT: bool = False
    AUTHJWT_ACCESS_EXPIRE_HOUR: int = 0
    AUTHJWT_REFRESH_EXPIRE_DAY: int = 0
    SESSION_SECRET: str = ""
    model_config = SettingsConfigDict(env_file=".env")
    
config = Config()