goog.provide('modernPaste.paste.PostController');

goog.require('modernPaste.universal.URIController');
goog.require('modernPaste.universal.AlertController');


/**
 * This controller handles all events related to the paste post page.
 *
 * @constructor
 */
modernPaste.paste.PostController = function() {
    this.alert = $('#alert');

    this.moreOptionsContainer = $('.more-options-container');
    this.moreOptionsArrow = $('.more-options-container .arrow');
    this.moreOptionsLink = $('.more-options-container .more-options-link');
    this.languageSelector = $('.language-selector');
    this.dateTimePicker = $('#date-time-picker');
    this.pastePassword = $('.more-options-container .paste-password');
    this.codeMirrorContainer = $('#paste-contents');
    this.lineCounter = $('#footer').find('.statistics-section .line-count');
    this.characterCounter = $('#footer').find('.statistics-section .character-count');
    this.pasteDownloadLink = $('#footer').find('.submit-section .paste-download-link');
    this.pasteDownloadContent = $('#footer').find('.submit-section .paste-download-content');
    this.pasteTitle = $('.paste-title-container').find('.paste-title');
    this.submitButton = $('#footer').find('.submit-section .submit-button');
    this.pasteSubmitSplash = $('.paste-submit-splash');

    this.dateTimePicker.datetimepicker({});
    this.pasteContents = CodeMirror(
        this.codeMirrorContainer[0],
        {
            'autofocus': true,
            'lineNumbers': true,
            'viewportMargin': Infinity,
            'mode': ''  // Start with plain text mode by default
        }
    );

    this.moreOptionsLink.on('click', modernPaste.paste.PostController.handleMoreOptionLinkClick.bind(this));
    this.languageSelector.on('change', modernPaste.paste.PostController.handleLanguageSelectorChange.bind(this));
    this.pasteContents.on('change', modernPaste.paste.PostController.handlePasteContentsChange.bind(this));
    this.pasteDownloadLink.on('click', modernPaste.paste.PostController.handlePasteDownloadLinkClick.bind(this));
    this.submitButton.on('click', modernPaste.paste.PostController.handleSubmitButtonClick.bind(this));
};

/**
 * Reveal/hide options for expiration time and paste password.
 */
modernPaste.paste.PostController.handleMoreOptionLinkClick = function(evt) {
    evt.preventDefault();

    if (this.moreOptionsContainer.css('height') === '25px') {
        // More options are hidden
        this.moreOptionsArrow.css('transform', 'rotate(-90deg)');
        this.moreOptionsContainer.css('height', '170px');
    } else {
        // More options are visible
        this.moreOptionsArrow.css('transform', 'rotate(90deg)');
        this.moreOptionsContainer.css('height', '25px');
    }
};

/**
 * Change the syntax highlighting when the paste language is changed.
 */
modernPaste.paste.PostController.handleLanguageSelectorChange = function(evt) {
    evt.preventDefault();

    this.pasteContents.setOption('mode', this.languageSelector.val().toLowerCase());
};

/**
 * Update the line and character count whenever there is a change to the text region.
 */
modernPaste.paste.PostController.handlePasteContentsChange = function(evt) {
    this.lineCounter.text(this.pasteContents.lineCount());
    this.characterCounter.text(this.pasteContents.getValue().length);
};

/**
 * When the user clicks the paste download button, capture the contents of the current paste and put it into a link
 * with a data:text/plain href attribute. Then, simulate a click on that link to download its contents.
 */
modernPaste.paste.PostController.handlePasteDownloadLinkClick = function(evt) {
    evt.preventDefault();

    this.pasteDownloadContent.attr('download', this.pasteTitle.text() + '.txt');
    this.pasteDownloadContent.attr('href', 'data:text/plain;base64,' + window.btoa(this.pasteContents.getValue()));
    this.pasteDownloadContent[0].click();  // Why can't I use .click() on a JQuery <a> object with a download attribute?
};

/**
 * When the user clicks the submit button, visually indicate submission progress, then submit an AJAX request
 * to submit the actual paste.
 */
modernPaste.paste.PostController.handleSubmitButtonClick = function(evt) {
    evt.preventDefault();

    this.submitButton.prop('disabled', true);
    this.pasteSubmitSplash.css('visibility', 'visible');
    this.pasteSubmitSplash.css('opacity', 0.7);

    $.ajax({
        method: 'POST',
        url: modernPaste.universal.URIController.uris.PasteSubmitURI,
        contentType: "application/json",
        data: JSON.stringify({
            'contents': this.pasteContents.getValue(),
            'user_id': null,
            'expiry_time': Date.parse(this.dateTimePicker.val()),
            'title': this.pasteTitle.text(),
            'language': this.languageSelector.val().toLowerCase(),
            'password': this.pastePassword.val() !== '' ? this.pastePassword.val() : null
        })
    })
    .done(modernPaste.paste.PostController.handleSubmitSuccess.bind(this))
    .fail(modernPaste.paste.PostController.handleSubmitFail.bind(this));
};

/**
 * On paste submission success, redirect the user to the URL to view the new paste
 */
modernPaste.paste.PostController.handleSubmitSuccess = function(data) {
    window.location.href = modernPaste.universal.URIController.formatURI(
        modernPaste.universal.URIController.uris.PasteViewInterfaceURI,
        {
            'paste_id': data.paste_id_repr
        }
    );
};

/**
 * On paste submission failure, simply display an error message to the user.
 */
modernPaste.paste.PostController.handleSubmitFail = function(data) {
    this.pasteSubmitSplash.css('opacity', 0);
    this.pasteSubmitSplash.css('visibility', 'hidden');
    this.submitButton.prop('disabled', false);

    var errorMessages = {
        'incomplete_params_failure': 'You can\'t submit an empty paste.',
        'auth_failure': 'You need to be logged in to post a non-anonymous paste.'
    };
    modernPaste.universal.AlertController.displayErrorAlert(
        modernPaste.universal.AlertController.selectErrorMessage(data, errorMessages)
    );
};


$(document).ready(function() {
    new modernPaste.paste.PostController();
});