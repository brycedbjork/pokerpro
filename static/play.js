/**
 * Created by brycedbjork on 11/30/16.
 */


// when document is ready
$(document).ready(function() {

    // initialize global hand variable
    hand = [];

    // initialize global score variable
    score = {
        "correct": 0,
        "total": 0
    };

    // if start game button pressed, start game
    $("#start-game-button").click(function() {
        render_game();
    });

});