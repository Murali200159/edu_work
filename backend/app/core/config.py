from pydantic_settings import BaseSettings
from urllib.parse import quote_plus

class Settings(BaseSettings):
    PROJECT_NAME: str = "EduProva Backend"
    
    # Database Settings targeting SQL Server on AWS RDS
    DB_HOST: str
    DB_PORT: str = "1433"
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DRIVER_NAME: str = "ODBC Driver 18 for SQL Server"
    
    # CORS Settings
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:5173", 
        "http://localhost:3000", 
        "http://127.0.0.1:5173", 
        "http://16.112.203.49:5173", 
        "http://16.112.203.49"
    ]
    
    # JWT Settings
    SECRET_KEY: str = "EduProva_Default_Secret_Key_Change_Me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    @property
    def get_database_url(self) -> str:
        """Constructs the database connection string from available ODBC drivers."""
        import pyodbc
        available_drivers = pyodbc.drivers()
        
        # Priority for Driver Selection
        if "ODBC Driver 18 for SQL Server" in available_drivers:
            final_driver = "ODBC Driver 18 for SQL Server"
        elif "ODBC Driver 17 for SQL Server" in available_drivers:
            final_driver = "ODBC Driver 17 for SQL Server"
        else:
            final_driver = "SQL Server" # Universal fallback

        # Encode password to safely handle special characters in connection string
        encoded_password = quote_plus(self.DB_PASSWORD)
        
        # Format the SQL Server connection string using pyodbc
        driver_param = final_driver.replace(" ", "+")
        base_url = f"mssql+pyodbc://{self.DB_USER}:{encoded_password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?driver={driver_param}"
        
        # ODBC Driver 18 requires encryption for production (default in 18+) but Driver 17 can also use it
        # We append AWS-recommended encryption parameters
        ssl_params = "&Encrypt=yes&TrustServerCertificate=yes"
        
        # If using old 'SQL Server' driver, we must NOT use the modern SSL parameters
        if final_driver == "SQL Server":
            return base_url

        return f"{base_url}{ssl_params}"

    class Config:
        env_file = ".env"

settings = Settings()
