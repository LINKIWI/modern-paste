var toggleHeaderStyle = function() {
    var header = $('.mp-header');
    var titleText = $('.mp-header span');
    var linksText = $('.mp-header a');

    if ($(window).scrollTop() > 0) {
        header.css('background-color', '#edf1f2');
        titleText.css('color', '#242424');
        linksText.css('color', '#242424');
    } else {
        header.css('background-color', 'transparent');
        titleText.css('color', '#edf1f2');
        linksText.css('color', '#edf1f2');
    }
};


$(document).ready(function() {
    $(window).on('scroll', toggleHeaderStyle);
});
