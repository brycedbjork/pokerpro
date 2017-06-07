// definitions

// defines the card ranks
// ((card_num - 1) % 13) + 1 = index of rank
var card_ranks = {
	1: "ace",
	2: "2",
	3: "3",
	4: "4",
	5: "5",
	6: "6",
	7: "7",
	8: "8",
	9: "9",
	10: "10",
	11: "jack",
	12: "queen",
	13: "king"
};

// defines the card suits
// Math.floor((card_num - 1) / 13) = index of suit
var card_suits = {
	0: "hearts",
	1: "spades",
	2: "diamonds",
	3: "clubs"
};

// delineates the various hand types
var hand_types = [
	"royal_flush",
	"straight_flush",
	"four_of_a_kind",
	"full_house",
	"flush",
	"straight",
	"three_of_a_kind",
	"two_pair",
	"one_pair"
];

// conversion to pretty text
var hand_type_pretty = {
    "royal_flush": "Royal Flush",
	"straight_flush": "Straight Flush",
	"four_of_a_kind": "Four of a Kind",
	"full_house": "Full House",
	"flush": "Flush",
	"straight": "Straight",
	"three_of_a_kind": "Three of a Kind",
	"two_pair": "Two Pair",
    "one_pair": "One Pair"
};

// function that takes card integer and returns card image file name
function get_card_pic(card_num) {
    var rank = card_ranks[((card_num - 1) % 13) + 1];
    var suit = card_suits[Math.floor((card_num - 1) / 13)];
    return rank + "_of_" + suit + ".png";
}

// function that processes hand variable for displaying
function render_hand() {

    // cancel past ajax requests
    for (var i = 0; i < ajax_requests.length; i++) {
        ajax_requests[i].abort()
    }
    // clear array
    ajax_requests = [];

    // empty hand container
    $("#hand-container").empty();
    // loop through hand
    for (var i = 0; i < hand.length; i++) {
        // create html string
        var html_string = "<div class='hand-icon'>" +
            "<img data-card='" + hand[i] + "' src='../static/card_images/" + get_card_pic(hand[i]) + "' class='hand-icon-image'/>" +
            "<div class='delete-card' data-card='" + hand[i] + "'>Delete</div>" +
            "</div>";
        // add html string to hand container
        $("#hand-container").append(html_string);
    }
    // attach click function
    // if hand card is deleted
    $(".delete-card").click(function() {
        // remove from hand array
        var card = $(this).data("card");
        var card_index = hand.indexOf(card);
        hand.splice(card_index, 1);
        // rerender hand
        render_hand();
    });

    // analyze hand
    ajax_odds("all");
}

// function that prettifies a number
function prettify(number) {
    number *= 1000000;
    number = Math.floor(number);
    number /= 10000;
    var result = number.toString() + "%";
    return result;
}

// function that completes ajax update of odds
function ajax_odds(h_type) {
    // put ajax loader into all odds
    $(".odds-line-probability").html("<img src='/static/ajax-loader.gif' height='18px'/>");
    var request = $.ajax({
        method: "GET",
        url: "/odds/",
        data: {
            cards: JSON.stringify(hand),
            hand_type: h_type
        },
        dataType: "JSON"
    }).done(function (data, textStatus, jqXHR) {
            for (var i = 0; i < Object.keys(data).length; i++) {
                var hand_type = Object.keys(data)[i];
                // add coloring to odds line
                if (data[hand_type] == 1) {
                    $("#odds-line-" + hand_type).css("border", "1px solid #80ff00");
                    $("#odds-line-" + hand_type).css("background-color", "rgba(128, 255, 0, 0.2)");
                }
                else if (data[hand_type] == 0) {
                    $("#odds-line-" + hand_type).css("border", "1px solid #ff4000");
                    $("#odds-line-" + hand_type).css("background-color", "rgba(255, 64, 0, 0.2)");
                }
                else {
                    $("#odds-line-" + hand_type).css("border", "1px solid #cacaca");
                    $("#odds-line-" + hand_type).css("background-color", "transparent");
                }
                // add probability to appropriate odds line
                $("#odds-line-" + hand_type).find(".odds-line-probability").html(prettify(data[hand_type]));
            }

    }).fail(function (jqXHR, textStatus, errorThrown) {

        // log error to browser's console
        console.log(errorThrown.toString());
    });
    ajax_requests.push(request);
}

// function that generates the game via ajax
function ajax_play_odds(h_type) {
    // clear containers
    $("#game-answer-container").empty();
    $("#game-question-container").empty();
    // put ajax loader into play container
    $("#game-play-container").html("<img src='/static/ajax-loader.gif' height='50px'/>");
    $.ajax({
        method: "GET",
        url: "/odds/",
        data: {
            cards: JSON.stringify(hand),
            hand_type: h_type
        },
        dataType: "JSON"
    }).done(function (data, textStatus, jqXHR) {
        // clear play container
        $("#game-play-container").empty();

        // add cards to play container
        // loop through hand
        for (var i = 0; i < hand.length; i++) {
            // create html string
            var html_string = "<div class='game-play-card'>" +
                "<img data-card='" + hand[i] + "' src='../static/card_images/" + get_card_pic(hand[i]) +
                    "' class='game-play-card-image'/>" +
                "</div>";
            // add html string to hand container
            $("#game-play-container").append(html_string);
        }

        // clear game question container
        $("#game-question-container").empty();
        // put appropriate question in
        $("#game-question-container").html("<h3>What are the odds of getting: " + hand_type_pretty[h_type] + "</h3>");

        // clear game answer container
        $("#game-answer-container").empty();

        // choose random number from zero to two to be answer position
        var answer_pos = Math.floor((Math.random() * 3));

        // get pretty correct answer
        var correct_answer = prettify(data[h_type]);

        // generate all answer choices and add to answer container
        for (var i = 0; i < 3; i++) {
            if (i == answer_pos) {
                // if this is the answer position, put the correct answer and add a data tag that says so
                $("#game-answer-container").append("<div class='game-answer-choice btn btn-default' data-answer=1>" +
                    correct_answer + "</div>");
            }
            else {
                // generate false answer
                var false_answer = prettify(Math.random() / 10);
                $("#game-answer-container").append("<div class='game-answer-choice btn btn-default' data-answer=0>" +
                    false_answer + "</div>");
            }
        }

        // attach clicking function to all answer choices
        $(".game-answer-choice").click(function() {
            // check if it is the answer
            var is_answer = $(this).data("answer") == 1;

            // empty all containers except cards
            $("#game-question-container").empty();
            $("#game-answer-container").empty();

            if (is_answer) {
                $("#game-question-container").append("<h2 style='color:green;'>Correct!</h2>");
                // add one to score
                score["correct"]++;
            }
            else {
                $("#game-question-container").append("<h2 style='color:red;'>Incorrect!</h2>");
            }

            // add one to score total
            score["total"]++;

            $("#game-question-container").append("<h3>The odds of getting " + hand_type_pretty[h_type] +
                " with the above cards are " + correct_answer + "</h3>");

            // wait 3 seconds then rerender game
            window.setTimeout(render_game, 3000);
        });


    }).fail(function (jqXHR, textStatus, errorThrown) {

        // log error to browser's console
        console.log(errorThrown.toString());
    });
}

// function that renders the game (largely utilizes ajax_play_game
function render_game() {
    // render score
    $("#score-container").empty();
    $("#score-container").html("<h2><u>Score</u></h2><h3>" + score["correct"] + " / " + score["total"] + "</h3>");

    // clear prior hand
    hand = [];
    // get two unique random cards between 1 and 52
    while (hand.length < 2) {
        // add random card as long as its not already there
        var card = get_random_card();
        if (hand.indexOf(card) < 0) {
            hand.push(card);
        }
    }
    // get a random hand
    var random_hand = get_random_hand();
    // use ajax to generate the rest of the game
    ajax_play_odds(random_hand);


}

// function that gets random card value from 1 to 52
function get_random_card() {
    random = Math.floor((Math.random() * 52) + 1);
    return random;
}

// function that gets random hand
function get_random_hand() {
    var hand_index = Math.floor(Math.random() * 9);
    return hand_types[hand_index];
}