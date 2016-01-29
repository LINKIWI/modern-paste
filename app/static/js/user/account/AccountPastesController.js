goog.provide('modernPaste.user.account.AccountPastesController');

goog.require('modernPaste.universal.AlertController');
goog.require('modernPaste.universal.CommonController');
goog.require('modernPaste.universal.URIController');


/**
 * This controller handles the loading and interaction of all the user's pastes.
 * This includes retrieving the pastes from the server and sending requests for downloading, forking,
 * setting the password, and deactivating existing pastes.
 *
 * @constructor
 */
modernPaste.user.account.AccountPastesController = function() {
    this.pasteItemTemplate = $('.paste-item-template');
    this.userPastesContainer = $('.pastes-settings .user-pastes-container');

    modernPaste.user.account.AccountPastesController.loadUserPastes.bind(this)();
};

/**
 * Request the server to return a reverse chronologically sorted list of all the user's pastes.
 */
modernPaste.user.account.AccountPastesController.loadUserPastes = function() {
    $.ajax({
        'method': 'POST',
        'url': modernPaste.universal.URIController.uris.PastesForUserURI
    })
    .done(modernPaste.user.account.AccountPastesController.loadPastesIntoList.bind(this))
    .fail(modernPaste.user.account.AccountPastesController.showPasteLoadError.bind(this));
};

/**
 * Load all the user's pastes into the table, setting all of its details fields and initializing
 * all event handlers related to actions on that particular paste.
 */
modernPaste.user.account.AccountPastesController.loadPastesIntoList = function(data) {
    data.pastes.forEach(function(paste) {
        var pasteTableRow = $(this.pasteItemTemplate.html());

        // ID this row to make it unique
        pasteTableRow.prop('id', paste.paste_id_repr);

        // Paste title - truncate
        pasteTableRow.find('.paste-title').text(
            modernPaste.universal.CommonController.truncateText(paste.title, 40)
        );

        // Link to paste in paste title
        pasteTableRow.find('.paste-title').prop(
            'href',
            modernPaste.universal.URIController.formatURI(
                modernPaste.universal.URIController.uris.PasteViewInterfaceURI,
                {
                    'paste_id': paste.paste_id_repr
                }
            )
        );

        // Relative time for paste post time
        pasteTableRow.find('.paste-posted').text(
            modernPaste.universal.CommonController.unixTimestampToRelativeTime(paste.post_time)
        );

        // Number of paste views
        pasteTableRow.find('.paste-views').text(paste.views);

        // Display appropriate icons based on password status
        if (paste.is_password_protected) {
            pasteTableRow.find('.paste-set-password-icon').remove();
            pasteTableRow.find('.paste-fork-icon').remove();  // Password-protected pastes can't be forked
        } else {
            pasteTableRow.find('.paste-remove-password-icon').remove();
        }

        // Fork URL
        pasteTableRow.find('.paste-fork-icon').prop(
            'href',
            modernPaste.universal.URIController.formatURI(
                modernPaste.universal.URIController.uris.PastePostInterfaceURI,
                {
                    'fork': paste.paste_id_repr
                }
            )
        );

        // Initialize icon event handlers
        // TODO: prevent default on all of these
        pasteTableRow.find('.paste-download-icon').on(
            'click',
            modernPaste.user.account.AccountPastesController.downloadPaste.bind(this, paste, pasteTableRow.find('.paste-download-contents'))
        );
        pasteTableRow.find('.paste-set-password-icon').on(
            'click',
            modernPaste.user.account.AccountPastesController.setPastePassword.bind(this, paste, pasteTableRow.find('.paste-download-contents'))
        );
        pasteTableRow.find('.paste-remove-password-icon').on(
            'click',
            modernPaste.user.account.AccountPastesController.removePastePassword.bind(this, paste, pasteTableRow.find('.paste-download-contents'))
        );
        pasteTableRow.find('.paste-deactivate-icon').on(
            'click',
            modernPaste.user.account.AccountPastesController.deactivatePaste.bind(this, paste, pasteTableRow.find('.paste-download-contents'))
        );

        this.userPastesContainer.append(pasteTableRow);
    }.bind(this));

    // Initialize all tooltips
    // This needs to be done after all the paste rows are completed loading.
    $('[data-toggle=\'tooltip\']').tooltip();
};

/**
 * Show a generic error message in case the user's pastes cannot be retrieved from the server.
 */
modernPaste.user.account.AccountPastesController.showPasteLoadError = function() {
    modernPaste.universal.AlertController.displayErrorAlert(
        'There was an error retrieving pastes from the server. Please try again later.'
    );
};

/**
 * Download the requested paste.
 *
 * @param pasteDetails An object describing the paste's details as returned by the API.
 * @param pasteDownloadContents A JQuery object representing a hidden link to temporarily store the
 *                              contents of the paste for download.
 */
modernPaste.user.account.AccountPastesController.downloadPaste = function(pasteDetails, pasteDownloadContents) {
    var fileExtension = modernPaste.universal.CommonController.getFileExtensionForType(pasteDetails.language);
    pasteDownloadContents.attr('download', pasteDetails.title + fileExtension);
    pasteDownloadContents.attr('href', 'data:text/plain;base64,' + window.btoa(pasteDetails.contents));
    pasteDownloadContents[0].click();
};

/**
 * TODO
 *
 * @param pasteDetails
 */
modernPaste.user.account.AccountPastesController.setPastePassword = function(pasteDetails) {

};

/**
 * TODO
 *
 * @param pasteDetails
 */
modernPaste.user.account.AccountPastesController.removePastePassword = function(pasteDetails) {

};

/**
 * TODO
 *
 * @param pasteDetails
 */
modernPaste.user.account.AccountPastesController.deactivatePaste = function(pasteDetails) {

};
