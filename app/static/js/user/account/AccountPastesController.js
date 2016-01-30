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
    this.numPastes = $('.pastes-settings .num-pastes');
    this.deactivateConfirmModal = $('.deactivate-confirm-modal');
    this.passwordRemoveConfirmModal = $('.password-remove-confirm-modal');
    this.passwordSetModal = $('.password-set-modal');

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
        pasteTableRow.find('.paste-download-icon').on(
            'click',
            modernPaste.user.account.AccountPastesController.downloadPaste.bind(this, paste, pasteTableRow.find('.paste-download-contents'))
        );
        pasteTableRow.find('.paste-set-password-icon').on(
            'click',
            modernPaste.user.account.AccountPastesController.setPastePasswordModal.bind(this, paste, pasteTableRow.find('.paste-download-contents'))
        );
        pasteTableRow.find('.paste-remove-password-icon').on(
            'click',
            modernPaste.user.account.AccountPastesController.removePastePasswordModal.bind(this, paste, pasteTableRow.find('.paste-download-contents'))
        );
        pasteTableRow.find('.paste-deactivate-icon').on(
            'click',
            modernPaste.user.account.AccountPastesController.deactivatePasteModal.bind(this, paste, pasteTableRow.find('.paste-download-contents'))
        );

        // Add element to DOM
        this.userPastesContainer.append(pasteTableRow);
    }.bind(this));

    // Number of total pastes
    this.numPastes.text('' + data.pastes.length + ' TOTAL ACTIVE PASTES');

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
modernPaste.user.account.AccountPastesController.downloadPaste = function(pasteDetails, pasteDownloadContents, clickedObject, evt) {
    evt.preventDefault();

    var fileExtension = modernPaste.universal.CommonController.getFileExtensionForType(pasteDetails.language);
    pasteDownloadContents.attr('download', pasteDetails.title + fileExtension);
    pasteDownloadContents.attr('href', 'data:text/plain;base64,' + window.btoa(pasteDetails.contents));
    pasteDownloadContents[0].click();
};

/**
 * Show the dialog prompting the user to enter a password to set for the paste.
 *
 * @param pasteDetails Object describing paste details for this particular paste.
 */
modernPaste.user.account.AccountPastesController.setPastePasswordModal = function(pasteDetails, clickedObject, evt) {
    evt.preventDefault();

    // Set modal text
    var pasteLink = '<a href="' +
        modernPaste.universal.URIController.formatURI(
            modernPaste.universal.URIController.uris.PasteViewInterfaceURI,
            {
                'paste_id': pasteDetails.paste_id_repr
            }
        ) +
        '">' + pasteDetails.title + '</a>';
    this.passwordSetModal.find('.set-password-text').html(
        'Enter the password to set for the paste ' + pasteLink + ' below. You will need to enter this password any time you want to view this paste.'
    );
    this.passwordSetModal.modal('show');

    // Cancel and deactivate event handlers
    this.passwordSetModal.find('.set-password-button').on(
        'click',
        modernPaste.user.account.AccountPastesController.setPastePassword.bind(this, pasteDetails)
    );
    this.passwordSetModal.find('.cancel-button').on(
        'click',
        modernPaste.user.account.AccountPastesController.hideModal.bind(this)
    );
};

/**
 * Request the server to set a password for this paste.
 *
 * @param pasteDetails Object describing paste details for this particular paste.
 */
modernPaste.user.account.AccountPastesController.setPastePassword = function(pasteDetails, evt) {
    evt.preventDefault();

    this.passwordSetModal.find('.set-password-button').prop('disabled', true);
    $.ajax({
        'method': 'POST',
        'url': modernPaste.universal.URIController.uris.PasteSetPasswordURI,
        'contentType': 'application/json',
        'data': JSON.stringify({
            'paste_id': pasteDetails.paste_id_repr,
            'password': this.passwordSetModal.find('.set-paste-password-field').val()
        })
    })
    .done(modernPaste.user.account.AccountPastesController.showPasteSetPasswordSuccess.bind(this, pasteDetails))
    .fail(modernPaste.user.account.AccountPastesController.showPasteSetPasswordFailure.bind(this));
};

/**
 * Display a generic success message if the paste password set was successful.
 *
 * @param pasteDetails Object describing paste details for this particular paste.
 */
modernPaste.user.account.AccountPastesController.showPasteSetPasswordSuccess = function(pasteDetails) {
    this.passwordSetModal.find('.set-password-button').prop('disabled', false);
    this.passwordSetModal.modal('hide');
    modernPaste.universal.AlertController.displaySuccessAlert(
        'The password for paste ' + modernPaste.universal.CommonController.truncateText(pasteDetails.title, 25) + ' was successfully changed.'
    );
};

/**
 * Display a generic error message if the paste password set fails.
 */
modernPaste.user.account.AccountPastesController.showPasteSetPasswordFailure = function() {
    this.passwordSetModal.find('.set-password-button').prop('disabled', false);
    this.passwordSetModal.modal('hide');
    modernPaste.universal.AlertController.displayErrorAlert(
        modernPaste.universal.AlertController.selectErrorMessage(
            data,
            {
                'nonexistent_paste_failure': 'This paste either does not exist or has been deactivated.',
                'auth_failure': 'You need to be logged in to the account that owns this paste in order to set its password.'
            }
        )
    );
};

/**
 * Show the modal for removing the passowrd from a password-protected paste, where the user can confirm or cancel.
 *
 * @param pasteDetails Object describing paste details for this particular paste.
 */
modernPaste.user.account.AccountPastesController.removePastePasswordModal = function(pasteDetails, clickedObject, evt) {
    evt.preventDefault();

    // Set modal text
    var pasteLink = '<a href="' +
        modernPaste.universal.URIController.formatURI(
            modernPaste.universal.URIController.uris.PasteViewInterfaceURI,
            {
                'paste_id': pasteDetails.paste_id_repr
            }
        ) +
        '">' + pasteDetails.title + '</a>';
    this.passwordRemoveConfirmModal.find('.remove-password-confirm-text').html(
        'You are about to remove the password from the paste ' + pasteLink + '. Are you sure you want to continue?'
    );
    this.passwordRemoveConfirmModal.modal('show');

    // Cancel and deactivate event handlers
    this.passwordRemoveConfirmModal.find('.remove-password-button').on(
        'click',
        modernPaste.user.account.AccountPastesController.removePastePassword.bind(this, pasteDetails)
    );
    this.passwordRemoveConfirmModal.find('.cancel-button').on(
        'click',
        modernPaste.user.account.AccountPastesController.hideModal.bind(this)
    );
};

/**
 * Request the server to remove the paste's password.
 *
 * @param pasteDetails Object describing paste details for this particular paste.
 */
modernPaste.user.account.AccountPastesController.removePastePassword = function(pasteDetails, evt) {
    evt.preventDefault();

    this.passwordRemoveConfirmModal.find('.remove-password-button').prop('disabled', true);
    $.ajax({
        'method': 'POST',
        'url': modernPaste.universal.URIController.uris.PasteSetPasswordURI,
        'contentType': 'application/json',
        'data': JSON.stringify({
            'paste_id': pasteDetails.paste_id_repr,
            'password': null
        })
    })
    .done(modernPaste.user.account.AccountPastesController.showPasteRemovePasswordSuccess.bind(this, pasteDetails))
    .fail(modernPaste.user.account.AccountPastesController.showPasteRemovePasswordFailure.bind(this));
};

/**
 * Display a generic success message if the paste password removal was successful.
 *
 * @param pasteDetails Object describing paste details for this particular paste.
 */
modernPaste.user.account.AccountPastesController.showPasteRemovePasswordSuccess = function(pasteDetails) {
    this.passwordRemoveConfirmModal.find('.remove-password-button').prop('disabled', false);
    this.passwordRemoveConfirmModal.modal('hide');
    modernPaste.universal.AlertController.displaySuccessAlert(
        'The password for paste ' + modernPaste.universal.CommonController.truncateText(pasteDetails.title, 25) + ' was successfully removed.'
    );
};

/**
 * Display a generic error message if the paste password removal fails.
 */
modernPaste.user.account.AccountPastesController.showPasteRemovePasswordFailure = function() {
    this.passwordRemoveConfirmModal.find('.remove-password-button').prop('disabled', false);
    this.passwordRemoveConfirmModal.modal('hide');
    modernPaste.universal.AlertController.displayErrorAlert(
        modernPaste.universal.AlertController.selectErrorMessage(
            data,
            {
                'nonexistent_paste_failure': 'This paste either does not exist or has been deactivated.',
                'auth_failure': 'You need to be logged in to the account that owns this paste in order to remove its password.'
            }
        )
    );
};

/**
 * Show the modal for deactivating a paste, where the user can confirm or cancel.
 *
 * @param pasteDetails Object describing paste details for this particular paste.
 */
modernPaste.user.account.AccountPastesController.deactivatePasteModal = function(pasteDetails, clickedObject, evt) {
    evt.preventDefault();

    // Set modal text
    var pasteLink = '<a href="' +
        modernPaste.universal.URIController.formatURI(
            modernPaste.universal.URIController.uris.PasteViewInterfaceURI,
            {
                'paste_id': pasteDetails.paste_id_repr
            }
        ) +
        '">' + pasteDetails.title + '</a>';
    this.deactivateConfirmModal.find('.deactivate-confirm-text').html(
        'You are about to deactivate the paste ' + pasteLink + '. Are you sure you want to continue?'
    );
    this.deactivateConfirmModal.modal('show');

    // Cancel and deactivate event handlers
    this.deactivateConfirmModal.find('.deactivate-button').on(
        'click',
        modernPaste.user.account.AccountPastesController.deactivatePaste.bind(this, pasteDetails)
    );
    this.deactivateConfirmModal.find('.cancel-button').on(
        'click',
        modernPaste.user.account.AccountPastesController.hideModal.bind(this)
    );
};

/**
 * Send a request to the server to deactivate the requested paste, after the user has confirmed the action.
 *
 * @param pasteDetails Object describing paste details for the paste to be deactivated.
 */
modernPaste.user.account.AccountPastesController.deactivatePaste = function(pasteDetails, evt) {
    evt.preventDefault();

    this.deactivateConfirmModal.find('.deactivate-button').prop('disabled', true);
    $.ajax({
        'method': 'POST',
        'url': modernPaste.universal.URIController.uris.PasteDeactivateURI,
        'contentType': 'application/json',
        'data': JSON.stringify({
            'paste_id': pasteDetails.paste_id_repr
        })
    })
    .done(modernPaste.user.account.AccountPastesController.showPasteDeactivationSuccess.bind(this, pasteDetails))
    .fail(modernPaste.user.account.AccountPastesController.showPasteDeactivationFailure.bind(this));
};

/**
 * Display an alert indicating paste deactivation success.
 *
 * @param pasteDetails Object describing paste details for the paste to be deactivated.
 */
modernPaste.user.account.AccountPastesController.showPasteDeactivationSuccess = function(pasteDetails) {
    this.deactivateConfirmModal.find('.deactivate-button').prop('disabled', false);
    this.deactivateConfirmModal.modal('hide');
    modernPaste.universal.AlertController.displaySuccessAlert(
        'Paste ' + modernPaste.universal.CommonController.truncateText(pasteDetails.title, 25) + ' was successfully deactivated.'
    );
    $('#' + pasteDetails.paste_id_repr.replace(/([ #;&,.+*~\':"!^$[\]()=>|\/@])/g,'\\$1')).fadeOut();
};

/**
 * Display an alert indicating paste deactivation failure.
 */
modernPaste.user.account.AccountPastesController.showPasteDeactivationFailure = function(data) {
    this.deactivateConfirmModal.find('.deactivate-button').prop('disabled', false);
    this.deactivateConfirmModal.modal('hide');
    modernPaste.universal.AlertController.displayErrorAlert(
        modernPaste.universal.AlertController.selectErrorMessage(
            data,
            {
                'nonexistent_paste_failure': 'This paste either does not exist or has already been deactivated.',
                'auth_failure': 'You need to be logged in to deactivate this paste.'
            }
        )
    );
};

/**
 * If the user chooses to cancel from any confirmation dialog, hide the modal.
 */
modernPaste.user.account.AccountPastesController.hideModal = function(evt) {
    evt.preventDefault();

    $('.modal').modal('hide');
};
