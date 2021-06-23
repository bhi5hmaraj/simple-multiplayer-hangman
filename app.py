from flask import Flask, request, render_template, redirect, session
from flask_session import Session
from tinydb import TinyDB, Query
import json

import string
import random

app = Flask(__name__)

MAX_TRIES = 6

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
db = TinyDB('room-data-db.json')


class RoomData:
    def __init__(self, room_id, word, guess=''):
        self.room_id = room_id
        self.word = word
        self.guess = guess

    def to_JSON(self):
        return json.loads(json.dumps(self, default=lambda o: o.__dict__))

    def __repr__(self):
        return "[room_id: {}, word: {}, guess: {}]".format(self.room_id, self.word, self.guess)


@app.route('/')
def home():
    session["room_id"] = None
    return HOME_HTML


@app.route('/propose')
def propose():
    print("session ", session, session["room_id"])
    word = request.args.get('word', '')
    Room = Query()
    ran = ''.join(random.choices(
        string.ascii_uppercase + string.digits, k=5))
    room = RoomData(ran, word)
    db.insert(room.to_JSON())
    print(db.all())
    return PROPOSAL_HTML.format(ran, word)


@app.route('/guess', methods=["POST", "GET"])
def guess():
    r_id = session.get("room_id")
    Room = Query()
    print("session ", session)

    if r_id:
        room_data = db.search(Room.room_id == r_id)[0]
        print(room_data)
        l = request.args.get('guessletter', '')
        ret = ''
        updated_guess = room_data['guess'] + l
        word = room_data['word']

        if (set(word).issubset(set(updated_guess))):
            ret = WIN_HTML.format(word)
        elif len(updated_guess) == MAX_TRIES:   # Last try
            db.remove(Room.room_id == r_id)
            ret = GAME_OVER_HTML.format(word)
        else:
            masked_word = ' - '.join(
                map(lambda ch: ch if ch in updated_guess else '?', word))
            db.update({'guess': updated_guess}, Room.room_id == r_id)
            ret = GUESS_HTML.format(
                r_id, masked_word, MAX_TRIES - len(updated_guess), updated_guess)

        return ret

    if request.method == "POST":    # First time
        session["room_id"] = request.form.get("roomid")
        room_data = db.search(Room.room_id == session["room_id"])[0]
        return GUESS_HTML.format(session["room_id"], ' - '.join(('?' * len(room_data['word']))), MAX_TRIES, '')


HOME_HTML = """
 <html><body>
     <h2>Welcome to Hang<a href="https://eige.europa.eu/publications/gender-sensitive-communication/challenges/invisibility-and-omission/do-not-use-man-neutral-term">Human</a></h2>
     <form action="/propose">
         What's the word that you want the other person to guess? <input type='text' name='word'><br>
         <input type='submit' value='Start'>
     </form>
      <form action="/guess" method="POST">
     Enter the room ID that you want to join <input type='text' name='roomid'><br>
     <input type='submit' value='Join'>
     </form>
 </body></html>
"""


PROPOSAL_HTML = """
 <html><body>
     <h2>Your room ID:  {0}</h2>
     <h3>Proposed word: {1}</h3>
 </body></html>
 """

GUESS_HTML = """
<html><body>
     <h2>Your room ID:  {0}</h2>
     <h3>Current status of the word: {1}</h3>
     <h3>Number of tries left: {2}</h3>
     <h3>Previous Guesses: {3}</h3>
     <form action="/guess">
     Enter a letter: <input type='text' name='guessletter'><br>
     <input type='submit' value='guess'>
     </form>
 </body></html>
"""

GAME_OVER_HTML = """
<html><body>
<h2>You have exceeded the number of tries, the word is: {0}</h2>
<h3>Click the button below to start a new game</h3>
<form action="/">
    <input type='submit' value='Reset'>
</form>
</body></html>
"""

WIN_HTML = """
<html><body>
<h2>Congrats! You've guessed the word ({0}) correctly.</h2>
<h3>Click the button below to start a new game</h3>
<form action="/">
    <input type='submit' value='Reset'>
</form>
</body></html>
"""

if __name__ == "__main__":
 # Launch the Flask dev server
    # app.run(host="localhost", debug=True)
    app.run(port=5000, debug=True)
