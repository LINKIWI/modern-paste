goog.provide('modernPaste.universal.SplashController');


/**
 * This controller handles hiding the splash when the page has finished loading.
 *
 * @constructor
 */
modernPaste.universal.SplashController = function() {
    Pace.options = {
        'ajax': false
    };

    this.loadingSplash = $('#loading-splash');

    Pace.on('done', modernPaste.universal.SplashController.hideLoadingSplash.bind(this));
};

/**
 * Hide the loading splash.
 */
modernPaste.universal.SplashController.hideLoadingSplash = function() {
    this.loadingSplash.css('opacity', 0);
    setTimeout(function() {
        this.loadingSplash.css('visibility', 'hidden');
    }.bind(this), 600);
};


$(document).ready(function() {
    new modernPaste.universal.SplashController();
});