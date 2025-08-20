import yaml

class Config:
    def __init__(self, data):
        self._data = data or {}

    def get_database_url(self):
        db = self._data.get('database', {})
        if not db:
            return None
        user = db.get('user')
        password = db.get('password')
        host = db.get('host', 'pipeline-postgres')
        port = db.get('port', 5432)
        name = db.get('name', 'pipeline_db')
        return f"postgresql://{user}:{password}@{host}:{port}/{name}"

    def get_api_config(self):
        return self._data.get('api', {})

    def get_microsoft_graph_config(self):
        return self._data.get('microsoft_graph', {})

    def get_logging_config(self):
        return self._data.get('logging', {})

def get_config():
    with open('jobs/config.yaml', 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f) or {}
    return Config(data)
