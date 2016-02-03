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

var controlIntroFontSize = function() {
    var height = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;
    var text = $('.intro .intro-text .i-wish');
    height < 700 ? text.css('font-size', '40px') : text.css('font-size', '72px');
};


$(document).ready(function() {
    $(window).on('scroll', toggleHeaderStyle);
    $(window).on('resize', controlIntroFontSize);
});
