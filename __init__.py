from flask import Flask

def create_app(test_config=None):        
    app = Flask(__name__)
    app.secret_key = 'sapoazul'

    from . import catalog
    app.register_blueprint(catalog.bp)

    return app