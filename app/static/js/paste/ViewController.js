goog.provide('modernPaste.paste.ViewController');

goog.require('modernPaste.universal.AlertController');
goog.require('modernPaste.universal.CommonController');
goog.require('modernPaste.universal.URIController');


/**
 * This controller handles loading paste information into the paste view page via an AJAX call.
 * @constructor
 */
modernPaste.paste.ViewController = function() {
    // Metadata
    this.pasteId = $('#paste-id').data('paste-id');

    // Page elements
    this.pasteLoadSplash = $('.paste-load-splash');
    this.spinner = $('.paste-load-splash .spinner');

    // Paste UI elements
    this.rawPasteContents = $('.raw-paste-contents');
    this.pasteTitle = $('.paste-header .paste-title');
    this.pasteLanguage = $('.paste-header .paste-language');
    this.pastePosterUsername = $('.paste-header .paste-poster-username');
    this.pastePostTime = $('.paste-header .paste-post-time');
    this.pasteExpiryTimeContainer = $('.paste-expiry-time-container');
    this.pasteExpiryTime = $('.paste-header .paste-expiry-time');
    this.pasteViews = $('.paste-header .paste-views');
    this.passwordProtectionNotice = $('.password-protected');
    this.pastePasswordField = $('.password-protected .paste-password-field');
    this.passwordSubmitButton = $('.password-protected .password-submit-button');

    // Paste header links
    this.pasteDownloadLink = $('.paste-header .paste-download-link');
    this.pasteDownloadContent = $('.paste-view-container .paste-download-content');
    this.pasteForkContainer = $('.paste-header .paste-fork-container');

    modernPaste.paste.ViewController.loadPaste.bind(this)();

    this.passwordSubmitButton.on('click', modernPaste.paste.ViewController.verifyPastePassword.bind(this));
    this.pasteDownloadLink.on('click', modernPaste.paste.ViewController.downloadPasteAsFile.bind(this));
};

/**
 * Begin loading the specified paste, then initialize all the UI elements on success or display an error.
 */
modernPaste.paste.ViewController.loadPaste = function() {
    $.ajax({
        'method': 'POST',
        'url': modernPaste.universal.URIController.uris.PasteDetailsURI,
        'contentType': 'application/json',
        'data': JSON.stringify({
            'paste_id': this.pasteId
        })
    })
    .done(modernPaste.paste.ViewController.initializePasteDetails.bind(this))
    .fail(modernPaste.paste.ViewController.handlePasteLoadFail.bind(this));
};

/**
 * Update all UI elements on the page with the paste details.
 */
modernPaste.paste.ViewController.initializePasteDetails = function(data) {
    this.passwordProtectionNotice.fadeOut('fast');

    this.pasteTitle.text(data.details.title);
    this.pasteLanguage.text(data.details.language.toUpperCase());
    this.pastePostTime.text(modernPaste.paste.ViewController.convertUnixTimestamp(data.details.post_time));
    this.pastePosterUsername.text(data.details.poster_username.toUpperCase());
    this.pasteViews.text(data.details.views);
    if (data.details.expiry_time === null) {
        this.pasteExpiryTimeContainer.hide();
    } else {
        this.pasteExpiryTime.text(modernPaste.paste.ViewController.convertUnixTimestamp(data.details.expiry_time));
    }
    this.rawPasteContents.text(data.details.contents);

    this.pasteContents = CodeMirror.fromTextArea(
        this.rawPasteContents[0],
        {
            'autofocus': true,
            'lineNumbers': true,
            'viewportMargin': Infinity,
            'lineWrapping': true,
            'mode': data.details.language.toLowerCase(),
            'readOnly': 'nocursor'  // Prevent editing of paste when viewing it
        }
    );

    modernPaste.universal.SplashController.hideSplash(this.pasteLoadSplash);
};

/**
 * The paste could fail to load on first attempt either because the paste is password-protected, and returns an
 * authentication error when attempting to access it without a password, or because of an undefined server or client
 * side error.
 */
modernPaste.paste.ViewController.handlePasteLoadFail = function(data) {
    if (data.responseJSON.failure === 'password_mismatch_failure') {
        // In the event that we need to present the password prompt, we should hide only the spinner and not the splash,
        // in order to preserve a faded white backdrop for the password prompt.
        this.spinner.fadeOut();
        this.passwordProtectionNotice.fadeIn('fast');
        // We should also immediately disable the paste fork link in the UI.
        // It is insecure to allow a password-protected paste to be forked.
        this.pasteForkContainer.hide();
    } else {
        modernPaste.universal.SplashController.hideSplash(this.pasteLoadSplash);
        modernPaste.universal.AlertController.displayErrorAlert('The details for this paste couldn\'t be loaded. Please try again later.');
    }
};

/**
 * If the paste is password-secured, try to get the paste details again with authentication.
 * Handle success and failure appropriately.
 */
modernPaste.paste.ViewController.verifyPastePassword = function(evt) {
    evt.preventDefault();

    this.passwordSubmitButton.prop('disabled', true);
    $.ajax({
        'method': 'POST',
        'url': modernPaste.universal.URIController.uris.PasteDetailsURI,
        'contentType': 'application/json',
        'data': JSON.stringify({
            'paste_id': this.pasteId,
            'password': this.pastePasswordField.val()
        })
    })
    .done(modernPaste.paste.ViewController.initializePasteDetails.bind(this))
    .fail(modernPaste.paste.ViewController.displayPasswordFailure.bind(this));
};

/**
 * Display an error if password authentication fails.
 */
modernPaste.paste.ViewController.displayPasswordFailure = function() {
    this.passwordSubmitButton.prop('disabled', false);
    modernPaste.universal.AlertController.displayErrorAlert('The password supplied is incorrect.');
};

/**
 * Convert a UNIX timestamp into a human-readable date format.
 *
 * @param unixTimestampString UNIX timestamp as a string (e.g. not parsed as an integer)
 * @returns {string} A representation of the date e.g. January 14, 2016 5:43 PM
 */
modernPaste.paste.ViewController.convertUnixTimestamp = function(unixTimestampString) {
    // It's extremely frustrating that Date doesn't expose this via a public interface.
    var monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    var date = new Date(parseInt(unixTimestampString, 10)*1000);
    // It would also be nice if Javascript had a formalized method of formatting strings
    return monthNames[date.getMonth()].toUpperCase() + ' ' + date.getDate() + ', ' + date.getFullYear() + ' ' + ((date.getHours() + 11) % 12 + 1) + ':' + date.getMinutes() + ' ' + (date.getHours() >= 12 ? 'PM' : 'AM');
};

/**
 * Download the contents of the paste as a file with the appropriate file extension.
 */
modernPaste.paste.ViewController.downloadPasteAsFile = function(evt) {
    evt.preventDefault();

    var fileExtension = modernPaste.universal.CommonController.getFileExtensionForType(this.pasteLanguage.text());
    this.pasteDownloadContent.attr('download', this.pasteTitle.text() + fileExtension);
    this.pasteDownloadContent.attr('href', 'data:text/plain;base64,' + window.btoa(this.pasteContents.getValue()));
    this.pasteDownloadContent[0].click();
};


$(document).ready(function() {
    new modernPaste.paste.ViewController();
});
