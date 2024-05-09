class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:root@db/markr?gssencmode=disable'
    SQLALCHEMY_TRACK_MODIFICATIONS = False