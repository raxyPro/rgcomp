import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('MYSQL_URL', 'mysql+pymysql://rcc:900@localhost/rcpro')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
