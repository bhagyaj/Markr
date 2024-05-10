class Config:
    """
    Configuration class for the Flask application.

    Attributes:
        SQLALCHEMY_DATABASE_URI (str): The URI for connecting to the PostgreSQL database.
        SQLALCHEMY_TRACK_MODIFICATIONS (bool): Controls whether Flask-SQLAlchemy
            should track modifications of objects and emit signals.
            Set to False to suppress warnings.
    """
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:root@db/markr?gssencmode=disable'
    SQLALCHEMY_TRACK_MODIFICATIONS = False