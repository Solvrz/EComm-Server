from email.message import EmailMessage
import smtplib
import os
import flask
from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route("/")
def test_server():
    return "I Am Working!!!"


@app.route("/order_confirmation")
def order_confirmation():
    args = request.args

    message = EmailMessage()
    sender = "orders.suneelprinters@gmail.com"
    recipient = args["email"]

    message["From"] = sender
    message["To"] = recipient

    message["Subject"] = "Order Confirmation from Sunil Printers"

    message.set_content(
        f"Dear {args['customer']}\nGreetings from Sunil Printers!\n\nThis is to confirm that your order for a {args['productName']} costing Rs. {args['price']} is placed."
        f"It would be shortly delivered to the following address\n\n {args['address']}\n\n Thanks for Shopping with us!"
    )

    mail_server = smtplib.SMTP_SSL("smtp.gmail.com")
    mail_server.login("orders.suneelprinters@gmail.com", "SuneelPrinters37")
    mail_server.send_message(message)
    mail_server.quit()

    return "Successful"


@app.route("/order_request", methods=["POST"])
def order_request():
    message = EmailMessage()

    message["From"] = "orders.suneelprinters@gmail.com"
    message["To"] = "orders.suneelprinters@gmail.com"
    message["Subject"] = f"Order Placed by {request.form['customer']}"

    message.set_content(
        f"""<!DOCTYPE html>
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
        <div id="card">
            <p style="font-size: 24px; font-weight: bold; text-align: center;">ORDER DETAILS</p>
            <table>
                <tr>
                    <th class="lefty">Customer Name:</th>
                    <td class="righty">{request.form['name']}</td>
                </tr>
                <tr>
                    <th class="lefty">Phone Number:</th>
                    <td class="righty">{request.form['phone']}</td>
                </tr>
                <tr>
                    <th class="lefty">Shipping Address:</th>
                    <td class="righty" width="50%">{request.form['address']}</td>
                </tr>
            </table>
            <table class="product">
                <tr>
                    <th class="lefty">PRODUCT NAME</th>
                    <th class="righty">QUANTITY</th>
                    <th class="righty" width="40%">PRICE</th>
                </tr>
                    {request.form['product_list']}
                <tr>
                <th colspan="2" style="border-top: 1px solid black; text-align: left;">TOTAL:</th>
                <th style="border-top: 1px solid black" class="righty">{request.form['price']}</th>
                </tr>
            </table>
        </div>
        <a href="http://www.facebook.com/" target="_blank">
                <img src="https://simplesharebuttons.com/images/somacro/facebook.png" alt="Facebook" width="4%" class="center" />
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

