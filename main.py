from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from flask_restful import reqparse
from smtplib import SMTP, SMTPException
from email.message import EmailMessage

app = Flask(__name__)
api = Api(app)


parser = reqparse.RequestParser()
parser.add_argument("host", type=str)
parser.add_argument("port", type=int)
parser.add_argument("tls", type=bool)
parser.add_argument("username", type=str)
parser.add_argument("password", type=str)
parser.add_argument("from", type=str)
parser.add_argument("to", type=str)
parser.add_argument("subject", type=str)
parser.add_argument("content", type=str)


def mk_msg(toaddr, fromaddr, subj, content):
    msg = EmailMessage()
    msg["To"] = toaddr
    msg["From"] = fromaddr
    msg["Subject"] = subj
    if content is not None:
        msg.set_content(content)
    return msg


class SendEmail(Resource):
    def post(self):
        args = parser.parse_args(strict=True)

        for key, msg in [
            ("host", "no host provided"),
            ("username", "no username provided"),
            ("to", "no 'to' address"),
            ("from", "no 'from' address"),
        ]:
            if args[key] is None:
                return msg, 400

        # just assume we will want TLS (for obvious reasons)
        port = 587 if args["port"] is None else args["port"]
        use_tls = args["tls"] is not False

        try:
            with SMTP(host=args["host"], port=port) as s:
                if use_tls:
                    s.starttls()
                s.login(args["username"], args["password"])
                msg = mk_msg(
                    args["to"],
                    args["from"],
                    args["subject"],
                    args["content"],
                )
                s.send_message(msg)
                return "send successful", 201
        except SMTPException as e:
            return str(e), 400
        
class ReceiveAlert(Resource):
    def post(self):
        args = parser.parse_args(strict=False)
        print(args)


api.add_resource(SendEmail, "/send")
api.add_resource(ReceiveAlert, "/alert")


if __name__ == "__main__":
    app.run(debug=True)