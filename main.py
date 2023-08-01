from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from flask_restful import reqparse, inputs
from smtplib import SMTP, SMTPException
from email.message import EmailMessage
import json

from data.constants import *

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()

parser.add_argument("_check_name", type=str)
parser.add_argument("_message", type=str)
parser.add_argument("_time", type=str)
parser.add_argument("engine_host", type=str)

def mk_msg(toaddr, fromaddr, subj, content):
    msg = EmailMessage()
    msg["To"] = toaddr
    msg["From"] = fromaddr
    msg["Subject"] = subj
    if content is not None:
        msg.set_content(content)
    return msg

def send_email(check, messageBody, host):
    try:
        with SMTP(host=SMTP_HOST, port=SMTP_PORT) as s:
            if USE_TLS:
                s.starttls()
            s.login(SMTP_USER, SMTP_PASS)
            msg = mk_msg(
                ', '.join(RECIPIENTS),
                f'{SMTP_FROM} <{SMTP_USER}>',
                f'{check} en {host}',
                messageBody,
            )
            s.send_message(msg, SMTP_USER)
            return "Message sent", 201
    except SMTPException as e:
        return str(e), 400
        
class HandleAlert(Resource):
    def post(self):
        args = parser.parse_args(strict=False)

        for key, msg in [
            ("_check_name", "no check provided"),
            ("_message", "no message provided"),
            ("_time", "no time provided"),
            ("engine_host", "no host provided"),
        ]:
            if args[key] is None:
                return msg, 400
            
        messageBody = f'{args["_message"]} a las {inputs.datetime_from_iso8601(args["_time"]).astimezone()}.'

        with open('./data/history.log', 'a') as file:
            file.write(messageBody)
        
        if (SMTP_HOST is not None and SMTP_HOST != "") and (SMTP_USER is not None and SMTP_USER != "") and (SMTP_PASS is not None and SMTP_PASS != "") and (SMTP_FROM is not None and SMTP_FROM != "") and (SMTP_PORT is not None) and (USE_TLS is not None) and (RECIPIENTS is not None and SMTP_HOST != []):
            send_email(args["_check_name"], messageBody, args["engine_host"])

api.add_resource(HandleAlert, "/alert")

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=3000)