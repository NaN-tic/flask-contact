#This file is part contact app for Flask.
#The COPYRIGHT file at the top level of this repository contains
#the full copyright notices and license terms.

import json
import ConfigParser

from flask import Flask, jsonify, request
from flask.ext.mail import Mail, Message

try:
    import emailvalid
    HAS_EMAILVALID = True
except ImportError:
    HAS_EMAILVALID = False


def get_config():
    '''Get values from cfg file'''
    config = ConfigParser.ConfigParser()
    config.read('config.ini')

    results = {}
    for section in config.sections():
        results[section] = {}
        for option in config.options(section):
            results[section][option] = config.get(section, option)
    return results


def create_app(config=None):
    '''Create Flask APP'''
    cfg = get_config()
    app_name = cfg['flask']['app_name']
    app = Flask(app_name)
    app.config.from_pyfile(config)

    return app


app = create_app('config.cfg')
mail = Mail(app)


@app.route('/', methods=['PUT', 'POST'])
def contact():
    values = {}
    for data in request.json:
        values[data['name']] = data['value']

    if not values.get('email', False):
        return False

    if HAS_EMAILVALID:
        if not emailvalid.check_email(values.get('email')):
            return False

    vals = []
    for key, val in values.items():
        vals.append('%s: %s' % (key, val))

    msg = Message(values.get('subject', 'Contact'))
    msg.sender = app.config.get('MAIL_SENDER')
    msg.recipients = app.config.get('MAIL_RECEPIENTS')
    msg.body = '\n'.join(vals)
    mail.send(msg)

    app.logger.info('Send email')
    app.logger.info(values)

    return jsonify(result=True)

if __name__ == "__main__":
    app.run()
