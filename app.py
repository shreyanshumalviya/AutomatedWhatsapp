import threading

from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

app = Flask(__name__)
i = 0
stock = []

callback_done = threading.Event()


# Create a callback on_snapshot function to capture changes
def on_snapshot(doc_snapshot, changes, read_time):
    stock.clear()
    for doc in doc_snapshot:
        stock.append(doc.to_dict())
    callback_done.set()


def get_database():
    cred = credentials.Certificate("google-services.json")
    default_app = firebase_admin.initialize_app(cred)
    db = firestore.client(default_app)
    stock_ref = db.collection(u'stock')
    for doc in stock_ref.stream():
        stock.append(doc.to_dict())
    print(stock.__len__())
    # Watch the document
    doc_watch = stock_ref.on_snapshot(on_snapshot)


def get_items(_name):
    name = _name
    items = []
    for i in range(0, name.__len__() - 3):
        if i % 2 == 0:
            name = name[0:-1]
        else:
            name = name[1:]
        for item in stock:
            if item["name"].upper().__contains__(name):
                items.append(item)
        if not items.__len__() == 0:
            return items
    for i in range(0, name.__len__() - 1):
        name = name[0:-1]
        for item in stock:
            if item["name"].upper().__contains__(name):
                items.append(item)
        if not items.__len__() == 0:
            return items
        name = _name


def find_match(request_):
    at_location = request_.find("STOCK ")
    return request_[at_location + 6:]


get_database()


@app.route("/")
def hello():
    items = "<h1>"
    for item in stock:
        items = items + item["name"] + "      " + str(item["stock"]) + "<br><br>"

    items=items+"</h1>"
    return """
    <html><body>
    <h3>Whatsapp "join bush-planned" to +1 415 523-8886</h3>
    """ + items + "</body></html>"


@app.route("/sms", methods=['POST'])
def sms_reply():
    print("Requested")
    """Respond to incoming calls with a single text message"""
    msg = request.form.get('Body')
    msg = msg.upper()
    # create reply
    item_name = find_match(msg)
    resp = MessagingResponse()
    items = get_items(item_name)
    ans = ''
    if items is None:
        resp.message(f"No match for {item_name}\n ensure spelling and try again.")
    else:
        for item in items:
            ans = ans + f'\n{item["name"]} - {item["stock"]}'
        resp.message(ans)
    return str(resp)


if __name__ == "__main__":
    app.run(debug=True)


class Items(object):
    def __init__(self, item_name, item_spec, stock):
        self.item_name = item_name
        self.item_spec = item_spec
        self.stock = stock

    def __repr__(self):
        return (
            f'City(\
                    item_name={self.item_name}, \
                    item_spec={self.item_spec}, \
                    stock={self.stock}\
                )'
        )
