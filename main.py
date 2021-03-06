import re

from flask import Flask, request, redirect, render_template, url_for
#from textblob import TextBlob
from twilio.twiml.messaging_response import MessagingResponse, Message

from castleio import parse_msg
from user import User

app = Flask(__name__)

USERS = {}
# multiple users support
def add_user(name, phone_str):
    user = User(name,phone_str)
    USERS[phone_str] = user

# TEST DATA
add_user("Griffin", "+19132068204")
add_user("Philip", "+15155081003")
USERS["+19132068204"].add_goal("car", 5000)
USERS["+19132068204"].add_goal("bicycle", 200, balance=200)
USERS["+19132068204"].add_goal("vacation", 600, balance=200)
USERS["+15155081003"].add_goal("flamethrower",6900)
# END TEST DATA

def render_twitter_link(reply, link):
    return re.sub(TWITTER_LINK_REGEX,
                  '',
                  reply)

@app.route("/hello",methods=['GET'])
def hello():
    """ respond to basic web request """
    return render_template('index.html')

@app.route("/app",methods=['GET'])
def app_view():
    default_user = USERS["+19132068204"] 
    return render_template('app.html',user=default_user)

@app.route("/form",methods=['GET','POST'])
def handle_form():
    default_user = USERS["+19132068204"] 
    msg = request.form.get('text') or request.args.get('text')
    reply = parse_msg(msg,default_user)
    default_user.add_msg(msg)
    default_user.add_msg(reply, from_user=False)
    return redirect(url_for('app_view'))

@app.route("/",methods=['GET','POST'])
def reply():
    print("got a text!")
    msg = request.form['Body']
    sender = request.form['From']
    user = USERS[sender]
    if not user:
        return
    print(sender)
    print(msg)
    reply = parse_msg(msg,user)
    user.add_msg(msg)
    user.add_msg(reply, from_user=False)
    print(user.messages)
    resp = MessagingResponse()
    resp.message(reply)
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
