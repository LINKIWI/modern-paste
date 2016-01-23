goog.provide('modernPaste.misc.APIDocumentationController');

goog.require('modernPaste.universal.URIController');


/**
 * This controller handles UI elements on the API documentation page.
 *
 * @constructor
 */
modernPaste.misc.APIDocumentationController = function() {
    this.apiListing = $('.api-listing');
    this.apiDocumentation = $('.api-documentation-container');

    hljs.initHighlightingOnLoad();
    modernPaste.misc.APIDocumentationController.toggleApiListingVisibility.bind(this)();

    $('a').on('click', modernPaste.misc.APIDocumentationController.animateAnchorJump);
    $(window).scroll(modernPaste.misc.APIDocumentationController.lockApiListing.bind(this));
    $(window).resize(modernPaste.misc.APIDocumentationController.toggleApiListingVisibility.bind(this));
};

/**
 * Toggle the visibility of the API listing on the right side of the page depending on the width of the device's screen.
 */
modernPaste.misc.APIDocumentationController.toggleApiListingVisibility = function() {
    var width = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
    width > 1400 ? this.apiListing.show() : this.apiListing.hide();
};

/**
 * Animate the scrolling when the user clicks a link in the API listing box.
 */
modernPaste.misc.APIDocumentationController.animateAnchorJump = function() {
    $('html, body').animate({
        'scrollTop': $( $.attr(this, 'href') ).offset().top
    }, {
        'duration': 1000,
        'easing': 'easeOutQuint'
    });
};

/**
 * Stick the API listing to the page if the user has scrolled past the main header.
 */
modernPaste.misc.APIDocumentationController.lockApiListing = function() {
    $(window).scrollTop() > this.apiDocumentation.offset().top - 140 ?
        this.apiListing.addClass('stick') : this.apiListing.removeClass('stick');
};


$(document).ready(function() {
    new modernPaste.misc.APIDocumentationController();
});
