goog.provide('modernPaste.paste.PostController');

goog.require('modernPaste.universal.AlertController');
goog.require('modernPaste.universal.CommonController');
goog.require('modernPaste.universal.URIController');


/**
 * This controller handles all events related to the paste post page.
 *
 * @constructor
 */
modernPaste.paste.PostController = function() {
    this.metadata = {
        'maxAttachmentSize': $('#metadata #max-attachment-size').data('max-attachment-size')
    };

    // Keep track of all the attachments selected by the user in a global variable.
    // This data is inserted into the AJAX request when submitting a paste.
    this.attachments = [];

    this.urlParams = modernPaste.universal.URIController.getURLParameters();

    this.alert = $('#alert');

    this.moreOptionsContainer = $('.more-options-container');
    this.moreOptionsArrow = $('.more-options-container .arrow');
    this.moreOptionsLink = $('.more-options-container .more-options-link');
    this.languageSelector = $('.language-selector');
    this.dateTimePicker = $('#date-time-picker');
    this.pastePassword = $('.more-options-container .paste-password');
    this.codeMirrorContainer = $('#paste-post-contents');
    this.lineCounter = $('#footer').find('.statistics-section .line-count');
    this.characterCounter = $('#footer').find('.statistics-section .character-count');
    this.pasteDownloadLink = $('#footer').find('.submit-section .paste-download-link');
    this.pasteDownloadContent = $('#footer').find('.submit-section .paste-download-content');
    this.pasteTitle = $('.paste-title-container').find('.paste-title');
    this.submitButton = $('#footer').find('.submit-section .submit-button');
    this.pasteSubmitSplash = $('.paste-submit-splash');
    this.attachmentsBrowseButton = $('.paste-attachments-container').find('.attachments-browse-button');
    this.attachmentsBrowseInput = $('.paste-attachments-container').find('#attachments-browse-input');
    this.attachmentsList = $('.paste-attachments-container').find('.attachments-list');
    this.attachmentItemTemplate = $('#attachment-item-template');
    this.attachmentUploadingStatus = $('.paste-submit-splash .uploading-status');

    this.submitButton.prop('disabled', false);
    this.dateTimePicker.datetimepicker({});
    this.pasteContents = CodeMirror(
        this.codeMirrorContainer[0],
        {
            'autofocus': true,
            'lineNumbers': true,
            'viewportMargin': Infinity,
            'lineWrapping': true,
            'mode': ''  // Start with plain text mode by default
        }
    );

    // If the user is forking a paste, load the forked contents rather than a blank box
    if (this.urlParams.hasOwnProperty('fork')) {
        modernPaste.paste.PostController.loadForkedPasteContents.bind(this)();
    }

    this.moreOptionsLink.on('click', modernPaste.paste.PostController.handleMoreOptionLinkClick.bind(this));
    this.languageSelector.on('change', modernPaste.paste.PostController.handleLanguageSelectorChange.bind(this));
    this.pasteContents.on('change', modernPaste.paste.PostController.handlePasteContentsChange.bind(this));
    this.pasteDownloadLink.on('click', modernPaste.paste.PostController.handlePasteDownloadLinkClick.bind(this));
    this.submitButton.on('click', modernPaste.paste.PostController.handleSubmitButtonClick.bind(this));
    this.attachmentsBrowseButton.on('click', modernPaste.paste.PostController.handleAttachmentsBrowseButtonClick.bind(this));
    this.attachmentsBrowseInput.on('change', modernPaste.paste.PostController.handleAttachmentsFileInput.bind(this));
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

    this.pasteDownloadContent.attr('download', this.pasteTitle.val() + '.txt');
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
    modernPaste.universal.SplashController.showSplash(this.pasteSubmitSplash);

    $.ajax({
        'xhr': function() {
            var xhr = new window.XMLHttpRequest();
            xhr.upload.addEventListener("progress", function(evt) {
                if (evt.lengthComputable) {
                    var percentComplete = 100.0 * evt.loaded / evt.total;
                    if (this.attachments.length > 0) {
                        this.attachmentUploadingStatus.text('UPLOADING ATTACHMENTS - ' + Math.round(percentComplete) + '%');
                    }
                }
           }.bind(this), false);
           return xhr;
        }.bind(this),
        'method': 'POST',
        'url': modernPaste.universal.URIController.uris.PasteSubmitURI,
        'contentType': 'application/json',
        'data': JSON.stringify({
            'contents': this.pasteContents.getValue(),
            'expiry_time': Math.round(Date.parse(this.dateTimePicker.val()) / 1000),
            'title': this.pasteTitle.val(),
            'language': this.languageSelector.val().toLowerCase(),
            'password': this.pastePassword.val() !== '' ? this.pastePassword.val() : null,
            'attachments': this.attachments
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
    modernPaste.universal.SplashController.hideSplash(this.pasteSubmitSplash);
    this.submitButton.prop('disabled', false);

    var errorMessages = {
        'incomplete_params_failure': 'You can\'t submit an empty paste.',
        'auth_failure': 'You need to be logged in to post a non-anonymous paste.',
        'unauthenticated_pastes_disabled_failure' : 'The server administrator has required that users be signed in to post a paste.',
        'paste_attachments_disabled_failure': 'The server administrator has disabled paste attachments.',
        'paste_attachment_too_large_failure': 'The size of one or more attachments is larger than the maximum allowable file size.'
    };
    modernPaste.universal.AlertController.displayErrorAlert(
        modernPaste.universal.AlertController.selectErrorMessage(data, errorMessages)
    );
};

/**
 * Open the file input dialog when the user clicks on the browse files button.
 */
modernPaste.paste.PostController.handleAttachmentsBrowseButtonClick = function(evt) {
    evt.preventDefault();
    this.attachmentsBrowseInput.click();
};

/**
 * When the user selects files to upload, read them as a base64-encoded string and keep track of it in a globally
 * accessible array. This will also create a listing that shows the name of the file in the user interface.
 */
modernPaste.paste.PostController.handleAttachmentsFileInput = function(evt) {
    var files = evt.target.files;
    if (files) {
        $.each(evt.target.files, function(_, attachment) {
            var reader = new FileReader();

            reader.onload = function(readerEvt) {
                this.attachments.push({
                    'name': attachment.name,
                    'mime_type': attachment.type,
                    'size': attachment.size,
                    'data': btoa(readerEvt.target.result)
                });

                // Indicate that this file is processed by removing its opacity fade and changing its loading icon
                var attachmentItem = this.attachmentsList.find('#' + modernPaste.universal.CommonController.escapeSelector(attachment.name));
                attachmentItem.removeClass('faded');
                attachmentItem.find('.delete-attachment-icon').removeClass('hidden');
                attachmentItem.find('.attachment-loading-icon').addClass('hidden');
            }.bind(this);

            // Only attempt to read the file if it isn't a duplicate
            var matchingNames = this.attachments.filter(function(existingAttachment) {
                return existingAttachment.name === attachment.name;
            });

            if (attachment.size > this.metadata.maxAttachmentSize * 1000 * 1000 && this.metadata.maxAttachmentSize > 0) {
                modernPaste.universal.AlertController.displayErrorAlert('This file\'s size exceeds the limit of ' + this.metadata.maxAttachmentSize + ' MB imposed by the server administrator.');
                return;
            }

            if (matchingNames.length > 0) {
                modernPaste.universal.AlertController.displayErrorAlert('This file name already exists as an attachment for this paste.');
                return;
            }

            // Async read the file and convert it to a base64-encoded string
            reader.readAsBinaryString(attachment);

            // The attachments list is hidden by default; it should be shown when an attachment is added.
            this.attachmentsList.removeClass('hidden');

            // Create an attachment item describing this file
            var attachmentItem = $(this.attachmentItemTemplate.html());
            attachmentItem.prop('id', attachment.name);
            attachmentItem
                .find('.attachment-name')
                .text(attachment.name + ' (' + modernPaste.universal.CommonController.formatFileSize(attachment.size) + ')');
            attachmentItem.find('.delete-attachment-icon').on('click', modernPaste.paste.PostController.handleAttachmentDeletion.bind(this, attachment));

            this.attachmentsList.append(attachmentItem);
        }.bind(this));
    }
};

/**
 * If the user clicks the delete button next to a file, it should be removed from the attachments upload queue
 * and the user interface.
 *
 * @param deletedAttachment The attachment to remove
 */
modernPaste.paste.PostController.handleAttachmentDeletion = function(deletedAttachment) {
    // Remove the element from the global list of attachments
    this.attachments = this.attachments.filter(function(existingAttachment) {
        return existingAttachment.name !== deletedAttachment.name;
    });

    // Remove the corresponding DOM element
    this.attachmentsList
        .find('#' + modernPaste.universal.CommonController.escapeSelector(deletedAttachment.name))
        .remove();

    // Hide the attachments list if there are no attachments left
    if (this.attachments.length === 0) {
        this.attachmentsList.addClass('hidden');
    }
};

/**
 * If the user is attempting to fork an existing paste, AJAX-load the existing paste's contents into
 * the code textarea.
 */
modernPaste.paste.PostController.loadForkedPasteContents = function() {
    $.ajax({
        'method': 'POST',
        'url': modernPaste.universal.URIController.uris.PasteDetailsURI,
        'contentType': 'application/json',
        'data': JSON.stringify({
            'paste_id': this.urlParams.fork
        })
    })
    .done(modernPaste.paste.PostController.insertForkedPaste.bind(this))
    .fail(modernPaste.paste.PostController.showPasteForkFail.bind(this));
};

/**
 * On successful retrieval of the forked paste details, set the language of the paste (as appropriate),
 * insert its full contents into the code textarea, and set the paste title.
 */
modernPaste.paste.PostController.insertForkedPaste = function(data) {
    this.pasteContents.setValue(data.details.contents);
    this.languageSelector.val(data.details.language.toLowerCase());
    this.pasteContents.setOption('mode', data.details.language.toLowerCase());
    this.pasteTitle.val('Fork of ' + data.details.title);
};

/**
 * Display an error alert if the paste fork fails.
 */
modernPaste.paste.PostController.showPasteForkFail = function(data) {
    var errorMessages = {
        'password_mismatch_failure': 'You cannot fork a password-protected paste.',
        'nonexistent_paste_failure': 'The paste you are trying to fork does not exist.'
    };
    modernPaste.universal.AlertController.displayErrorAlert(
        modernPaste.universal.AlertController.selectErrorMessage(data, errorMessages)
    );
};


$(document).ready(function() {
    new modernPaste.paste.PostController();
});
