/**
 * Created by brycedbjork on 11/30/16.
 */


// when document is ready
$(document).ready(function() {

    // initialize hand variable
    hand = [];

    // generate card icon selector
    for (var i = 1; i <= 52; i++) {
        // create html string
        var html_string = "<div class='card-icon'>" +
            "<img data-card='" + i + "' src='../static/card_images/" + get_card_pic(i) + "' class='card-icon-image'/>" +
            "</div>";
        // add html string to icon container
        $("#card-icon-container").append(html_string);
        // if we have finished a suit, insert line break
        if (i % 13 == 0) {
            $("#card-icon-container").append("<br/>");
        }
    }

    // if card is selected, add it to hand_container div
    $(".card-icon").click(function() {
        // get card value
        var card = $(this).find(".card-icon-image").data("card");
        // check if card already in hand and if hand is not already full
        if (hand.indexOf(card) < 0 && hand.length < 5) {
            // add card
            hand.push(card);
            render_hand();
        }
    });

    // generate odds visual
    for (var i = 0; i < hand_types.length; i++) {
        var html_string = "<div class='odds-line' id='odds-line-" + hand_types[i] + "'>" +
            "<div class='odds-line-hand-type'>" + hand_type_pretty[hand_types[i]] + "</div>" +
            "<div class='odds-line-probability'></div>" +
            "</div>";
        $("#odds-container").append(html_string);
    }

    // initialize ajax requests array
    ajax_requests = [];

    // render no card odds
    ajax_odds("all");

});