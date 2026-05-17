from authlib.integrations.flask_client import OAuth

oauth = OAuth()

def init_oauth(app):
    oauth.init_app(app)
    tenant = app.config.get('MICROSOFT_TENANT_ID', 'common')
    oauth.register(
        name='microsoft',
        client_id=app.config.get('MICROSOFT_CLIENT_ID'),
        client_secret=app.config.get('MICROSOFT_CLIENT_SECRET'),
        server_metadata_url=f'https://login.microsoftonline.com/{tenant}/v2.0/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'},
    )
