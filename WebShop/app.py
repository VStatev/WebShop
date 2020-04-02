from Shop import fill, routes, app

if __name__ == '__main__':
    fill.fill_db()
    fill.migrate()
    app.run(host='0.0.0.0', port='5000', ssl_context=('cert.pem','key.pem'))
