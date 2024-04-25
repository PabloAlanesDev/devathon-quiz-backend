import os

mongo_config = {
    'db': os.environ.get('MONGO_DB', 'db'),
    'host': os.environ.get('MONGO_HOST', 'localhost'),
    'port': os.environ.get('MONGO_PORT', 27017),
}
