from flask import Flask, request
import pickle, string, random

app = Flask(__name__)

class RoomData:
    def __init__(self, ID, word, guess=''):
        self.ID = ID
        self.word = word
        self.guess = guess

    def __repr__(self):
        return "id: {}, word: {}, guess: {}".format(self.ID, self.word, self.guess)    
  

# room_data schema
# room_id -> 

@app.route('/')
def home():
    return HOME_HTML

HOME_HTML = """
 <html><body>
     <h2>Welcome to Hangman</h2>
     <form action="/propose">
         What's the word that you want the other person to guess? <input type='text' name='word'><br>
         <input type='submit' value='Continue'>
     </form>
      <form action="/guess">
     Enter the room ID that you want to join <input type='text' name='roomid'><br>
     <input type='submit' value='Continue'>
     </form>
 </body></html>
"""

@app.route('/propose')
def greet():
    word = request.args.get('word', '')
    with open('poor-man-db.pickle', 'rb') as pickr:
        room_data = pickle.load(pickr)
        ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 50))
        room = RoomData(ran, word)
        room_data[ran] = room
        print(room_data)
        with open('poor-man-db.pickle', 'wb') as pickw:
            pickle.dump(room_data, pickw)

    return PROPOSAL_HTML.format(ran, word)

PROPOSAL_HTML = """
 <html><body>
     <h2>Your room ID:  {0}</h2>
     <h3>Proposed word: {1}</h3>
 </body></html>
 """

if __name__ == "__main__":
 # Launch the Flask dev server
    app.run(host="localhost", debug=True)

