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
 * Show the requested splash.
 *
 * @param splash A JQuery object of the splash to reveal.
 */
modernPaste.universal.SplashController.showSplash = function(splash) {
    splash.css('visibility', 'visible');
    splash.css('opacity', 0.6);
};

/**
 * Hide the requested splash.
 *
 * @param splash A JQuery object of the splash to hide.
 */
modernPaste.universal.SplashController.hideSplash = function(splash) {
    splash.css('opacity', 0);
    setTimeout(function() {
        splash.css('visibility', 'hidden');
    }.bind(this), 600);
};

/**
 * Hide the loading splash.
 */
modernPaste.universal.SplashController.hideLoadingSplash = function() {
    modernPaste.universal.SplashController.hideSplash(this.loadingSplash);
};


$(document).ready(function() {
    new modernPaste.universal.SplashController();
});
