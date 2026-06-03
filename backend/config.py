from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    '''
    Store and validation environment data
    '''
    
    DB_HOST: str
    DB_NAME: str
    DB_PORT: int
    DB_USERNAME: str
    DB_PASS: str
    BOT_TOKEN: str

    @property
    def DB_URL(self):
        """Get Database URL"""

        # postgresql+asyncpg://USER:PASSWORD@HOST:PORT/DATABASE
        return f"postgresql+asyncpg://{self.DB_USERNAME}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
