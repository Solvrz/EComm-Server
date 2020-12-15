import hashlib
import hmac
import os
import smtplib
from email.message import EmailMessage

import razorpay
from flask import Flask, jsonify, request
from flask_cors import CORS
from pyfcm import FCMNotification

testing = True

if testing:
    creds = {"key": "rzp_test_3XFNUiX9RPskxm", "id": "p9idhjrcBmr2FFvthVa56HeI"}
else:
    # TODO: Put Merchant Key & ID Here
    creds = {"key": "", "id": ""}


client = razorpay.Client(auth=(creds["key"], creds["id"]))
client.set_app_details({"title": "Suneel Printers", "version": "1.0.0+1"})

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
<img src="https://firebasestorage.googleapis.com/v0/b/suneelprinters37.appspot.com/o/Logo.png?alt=media&token=21acff59-dc39-411b-a881-f4dac1da5173", class="center" width="12%">
<div id="card">"""


@app.route("/")
def running_check():
    return "The Server is running"


@app.route("/payment_init", methods=["POST"])
def payment_init():
    args = request.get_json()

    response = client.order.create(
        data={
            "amount": args["amount"],
            "currency": "INR",
            "receipt": args["order_id"],
            "payment_capture": 1,
        }
    )

    return response


@app.route("/payment_verify", methods=["POST"])
def payment_verify():
    args = request.get_json()

    signature = hmac.new(
        bytes(creds["id"], "latin-1"),
        msg=bytes((args["order_id"] + "|" + args["payment_id"]), "latin-1"),
        digestmod=hashlib.sha256,
    ).hexdigest()

    if signature == args["signature"]:
        return jsonify({"sucessful": True})
    else:
        return jsonify({"sucessful": False})


@app.route("/order", methods=["POST"])
def send_order():
    args = request.get_json()

    FCMNotification(
        api_key="AAAAZSeYoWE:APA91bEowBkZ0QHPPZnG_GkMWWGToAAnRV1qL5Rv2Yn5iaiIMcJ90Wex5TcIoV_Fd98MS_qGpS7jfmbLKtRoTq08pE4QhKd-RDcehpDTcuWICQh-akydH40UjTdOcavQrcP_1RxqVH0w"
    ).notify_topic_subscribers(
        topic_name="orders",
        message_title="New Order has been Placed",
        message_body="An Order has been Placed, Please check the Orders Section of the app for more details of the order",
    )

    message = EmailMessage()

    message["From"] = "orders.suneelprinters@gmail.com"
    message["Bcc"] = ["orders.suneelprinters@gmail.com", f"{args['email']}"]
    message["Subject"] = f"Order Placed by {args['name']}"

    message.add_header("Content-Type", "text/html")
    message.set_payload(
        f"""{mail_structure}<p style = 'font-size:12px; text-align : left;'>Hey {args['name']} <br> Greetings from Suneel Printers! <br><br> This is to confirm your order with Sunil Printers. </p>
            <p style="font-size: 24px; font-weight: bold; text-align: center;">ORDER DETAILS</p>

            <table>
                <tr>
                    <th class="lefty">Customer Name:</th>
                    <td class="righty">{args['name']}</td>
                </tr>
                <tr>
                    <th class="lefty">Phone Number:</th>
                    <td class="righty">{args['phone']}</td>
                </tr>
                <tr>
                    <th class="lefty">Payment Mode:</th>
                    <td class="righty">{args['payment_mode']}</td>
                </tr>
                <tr>
                    <th class="lefty">Shipping Address:</th>
                    <td class="righty" width="50%">{args['address']}</td>
                </tr>
            </table>

            <table class="product">
                <tr>
                    <th class="lefty">PRODUCT </th>
                    <th class="righty">QUANTITY</th>
                    <th class="righty" width="40%">PRICE</th>
                </tr>
                    {args['product_list']}
                <tr>
                <th colspan="2" style="border-top: 1px solid black; text-align: left;">TOTAL:</th>
                <th style="border-top: 1px solid black" class="righty">{args['price']}</th>
                </tr>
            </table>

            <p style = 'font-size:12px; text-align : center;'>Your order will be delivered soon. </p>
            <p style = 'font-size:18px; text-align : center;'> Thanks for Shopping with us!</p>

            </div>

            <a href="https://www.facebook.com/pages/category/Business-Service/Suneel-printers-1602910586637429/" target="_blank">
            <img src="https://simplesharebuttons.com/images/somacro/facebook.png" alt="Facebook" width="5%" class="center" />
            </a>
            </body>
        </html>"""
    )

    mail_server = smtplib.SMTP_SSL("smtp.gmail.com")

    mail_server.login("orders.suneelprinters@gmail.com", "SuneelPrinters37")
    mail_server.send_message(message)
    mail_server.quit()

    return "Successful"


@app.route("/request", methods=["POST"])
def send_request():
    args = request.get_json()

    FCMNotification(
        api_key="AAAAZSeYoWE:APA91bEowBkZ0QHPPZnG_GkMWWGToAAnRV1qL5Rv2Yn5iaiIMcJ90Wex5TcIoV_Fd98MS_qGpS7jfmbLKtRoTq08pE4QhKd-RDcehpDTcuWICQh-akydH40UjTdOcavQrcP_1RxqVH0w"
    ).notify_topic_subscribers(
        topic_name="orders",
        message_title="New Order has been Placed",
        message_body="An Order has been Placed, Please check the Orders Section of the app for more details of the order",
    )

    message = EmailMessage()

    message["From"] = "orders.suneelprinters@gmail.com"
    message["Bcc"] = ["orders.suneelprinters@gmail.com", f"{args['email']}"]
    message["Subject"] = f"Order Placed by {args['name']}"

    message.add_header("Content-Type", "text/html")
    message.set_payload(
        f"""{mail_structure}<p style = 'font-size:12px; text-align : left;'>Hey {args['name']} <br> Greetings from Suneel Printers! <br><br> This is to confirm your order with Sunil Printers. </p>
            <p style="font-size: 24px; font-weight: bold; text-align: center;">ORDER DETAILS</p>

            <table>
                <tr>
                    <th class="lefty">Customer Name:</th>
                    <td class="righty">{args['name']}</td>
                </tr>
                <tr>
                    <th class="lefty">Phone Number:</th>
                    <td class="righty">{args['phone']}</td>
                </tr>
            </table>

            <p style = font-size:18px; font-weight:bold;>ORDERS:</p>
            <ul><li>{args['order_list']}</li></ul>
            
            <p style = 'font-size:12px; text-align : center;'>You will soon recieve a call from us</p>
            <p style = 'font-size:18px; text-align : center;'> Thanks for Shopping with us!</p>
            
            </div>

            <a href="https://www.facebook.com/pages/category/Business-Service/Suneel-printers-1602910586637429/" target="_blank">
            <img src="https://simplesharebuttons.com/images/somacro/facebook.png" alt="Facebook" width="5%" class="center" />
            </a>
            </body>
        </html>"""
    )

    mail_server = smtplib.SMTP_SSL("smtp.gmail.com")

    mail_server.login("orders.suneelprinters@gmail.com", "SuneelPrinters37")
    mail_server.send_message(message)
    mail_server.quit()
    return "Successful"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
