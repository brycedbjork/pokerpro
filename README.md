# pokerpro

**Bryce Bjork,
Yale Class of 2020**

Video Presentation: https://youtu.be/lcENtXAL07Q

Poker Pro is a Flask web application. The web application is composed of three main pages.
The first page is Home, which includes a brief description of poker, the project, and poker hands.

The second page is Learn, which is an interactive page that allows users to pick a hand up to five cards,
and see the probability of certain combinations update in real time.
Learn is intended to educate users on the probabilities of certain outcomes, given the selected hands.
This is partially because it is just cool to know those odds and partially because it is preparation for the next page: Play.

Play is the third page of the Flask web application, and it is an odds-estimation game.
After reading through the instructions, users must click "Start Game!" to begin.
On clicking "Start Game!", the game is rendered, showing the user two cards, a question, and three choices.
The two cards are randomly selected.
The question is of the format "What are the odds of getting:" + randomly selected outcome.
The three choices are generated such that one is the correct odds, and the other two are randomly generated.
The user must select which of the choices they think is correct, and they are told after selection whether or not they were right.
Ideally, this game trains users to more accurately estimate the probability of certain poker outcomes.

It is important to note that my game processes the probabilities of 5 card combinations (not 7 card as in Texas Hold'em)

Regarding the Flask implementation...
````
export FLASK_APP=main.py
flask run
````


Details on the project as a whole...
* static includes all static files (css, js, images, etc.)
* templates includes the html templates that Flask uses
* archive includes old files that were used during development
    * I saved these because I thought it might be interesting to look at some of my past attempts (specifically back_attempt1.py)
* the back-end of this flask application is contained in back.py (application.py includes the line: from back import *)
* poker.db (the sqlite database file that allows the app to function) has been exclueded from Github because it is too large
    * back.py includes the function used to build this database file
