import hashlib
import hmac
import json
import os
import smtplib
from email.message import EmailMessage

import razorpay
import yaml
from firebase_admin import credentials, initialize_app, messaging
from flask import Flask, jsonify, request
from flask_cors import CORS

testing = False

# TODO: Update These
name = "EComm"
logo = "https://firebasestorage.googleapis.com/v0/b/ecomm37.appspot.com/o/Logo.png?alt=media&token=21acff59-dc39-411b-a881-f4dac1da5173"


with open("../firebase.json") as f:
    data = json.load(f)

    if data["private_key_id"] == "":
        data["private_key_id"] = os.environ.get("ECOMM_FIREBASE_ID")
        data["private_key"] = os.environ.get("ECOMM_FIREBASE_KEY1").replace(
            r"\n", "\n"
        ) + os.environ.get("ECOMM_FIREBASE_KEY2").replace(r"\n", "\n")

    initialize_app(credentials.Certificate(data))


creds = yaml.safe_load(open("../creds.yaml"))

smtp_email = creds["email"]
smtp_pass = creds["pass"]

if testing:
    razorpay_creds = creds["razorpay_test"]
else:
    razorpay_creds = creds["razorpay_prod"]

client = razorpay.Client(auth=(razorpay_creds["key"], razorpay_creds["id"]))
client.set_app_details({"title": name, "version": "1.0.0+1"})

app = Flask(__name__)
CORS(app)


mail_structure = f"""
<!DOCTYPE html>
<html>
    <head>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
        <style>
            body {{
            background-color: #F0F0F0;
            font-family: sans-serif;
            }}
            #card {{
            background-color: white;
            padding: 4px 32px 32px 32px;
            margin-top: 12px;
            }}
            .lefty {{
            text-align: left;
            }}
            .righty {{
            text-align: right;
            }}
            .center {{
            display: block;
            margin-left: auto;
            margin-right: auto;
            }}
            table.product td, table.product th {{
            padding-right: 10px;
            padding-left: 10px;
            padding-top: 6px;
            padding-bottom: 6px;
            }}
            table.product th {{
            border-bottom: 1px solid black;
            }}
            table {{
            width: 100%;
            border-collapse: collapse;
            }}
            table.product {{
            margin-top: 18px;
            }}
            .fa {{
            padding: 16px;
            font-size: 16px;
            width: 16px;
            text-align: center;
            text-decoration: none;
            margin: 5px 2px;
            border-radius: 50%;
            }}
            .fa-facebook {{
            margin-top: 12px;
            background: #666;
            color: white;
            }}
        </style>
    </head>
<body>
<img src="{logo}", class="center" width="12%">
<div id="card">"""


@app.route("/")
def running_check():
    return "The Server is running"


@app.route("/payment_init", methods=["POST"])
def payment_init():
    args = request.args

    response = client.order.create(
        data={
            # TODO: Change This
            "currency": "INR",
            "amount": args.get("amount"),
            "receipt": args.get("order_id"),
            "payment_capture": 1,
        }
    )

    return response


@app.route("/payment_verify", methods=["POST"])
def payment_verify():
    args = request.get_json()

    signature = hmac.new(
        bytes(razorpay_creds["id"], "latin-1"),
        msg=bytes((args["order_id"] + "|" + args["payment_id"]), "latin-1"),
        digestmod=hashlib.sha256,
    ).hexdigest()

    if signature == args["signature"]:
        return jsonify({"sucessful": True})
    else:
        return jsonify({"sucessful": False})


@app.route("/order", methods=["POST"])
def send_order():
    args = request.args

    messaging.send(
        messaging.Message(
            notification=messaging.Notification(
                title="New Order has been Placed",
                body="An Order has been Placed, Please check the Orders Section of the app for more details of the order",
            ),
            topic="orders",
        )
    )

    message = EmailMessage()

    message["From"] = smtp_email
    message["Bcc"] = [smtp_email, f"{args.get('email')}"]
    message["Subject"] = f"Order Placed by {args.get('email')}"

    message.add_header("Content-Type", "text/html")
    message.set_payload(
        f"""{mail_structure}<p style = 'font-size:12px; text-align : left;'>Hey {args.get('name')} <br> Greetings from {name}! <br><br> This is to confirm your order with {name}. </p>
            <p style="font-size: 24px; font-weight: bold; text-align: center;">ORDER DETAILS</p>

            <table>
                <tr>
                    <th class="lefty">Customer Name:</th>
                    <td class="righty">{args.get('name')}</td>
                </tr>
                <tr>
                    <th class="lefty">Phone Number:</th>
                    <td class="righty">{args.get('phone')}</td>
                </tr>
                <tr>
                    <th class="lefty">Payment Mode:</th>
                    <td class="righty">{args.get('payment_mode')}</td>
                </tr>
                <tr>
                    <th class="lefty">Shipping Address:</th>
                    <td class="righty" width="50%">{args.get('address')}</td>
                </tr>
            </table>

            <table class="product">
                <tr>
                    <th class="lefty">PRODUCT </th>
                    <th class="righty">QUANTITY</th>
                    <th class="righty" width="40%">PRICE</th>
                </tr>
                    {args.get('product_list')}
                <tr>
                <th colspan="2" style="border-top: 1px solid black; text-align: left;">TOTAL:</th>
                <th style="border-top: 1px solid black" class="righty">{args.get('price')}</th>
                </tr>
            </table>

            <p style = 'font-size:12px; text-align : center;'>Your order will be delivered soon. </p>
            <p style = 'font-size:18px; text-align : center;'> Thanks for Shopping with us!</p>

            </div>

            </a>
            </body>
        </html>"""
    )

    mail_server = smtplib.SMTP_SSL("smtp.gmail.com")

    mail_server.login(smtp_email, smtp_pass)
    mail_server.send_message(message)
    mail_server.quit()

    return "Successful"


if __name__ == "__main__":
    app.run(debug=testing)
