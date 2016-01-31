goog.provide('modernPaste.user.account.AccountUserProfileController');

goog.require('modernPaste.universal.AlertController');
goog.require('modernPaste.universal.SplashController');
goog.require('modernPaste.universal.URIController');


/**
 * This controller handles updating the current user's user profile and password.
 *
 * @constructor
 */
modernPaste.user.account.AccountUserProfileController = function() {
    this.accountSplash = $('.account-splash');
    this.nameField = $('.user-profile-settings .name-field');
    this.emailField = $('.user-profile-settings .email-field');
    this.currentPasswordField = $('.user-profile-settings .current-password-field');
    this.newPasswordField = $('.user-profile-settings .new-password-field');
    this.confirmNewPasswordField = $('.user-profile-settings .confirm-new-password-field');
    this.saveButton = $('.user-profile-settings .save-user-profile-button');

    this.saveButton.on('click', modernPaste.user.account.AccountUserProfileController.saveSettings.bind(this));
};

/**
 * First check if the input is valid, then request the server to save the requested settings if it is.
 * Otherwise, display an error alert describing the error condition.
 */
modernPaste.user.account.AccountUserProfileController.saveSettings = function(evt) {
    evt.preventDefault();

    if (this.newPasswordField.val() !== this.confirmNewPasswordField.val()) {
        modernPaste.universal.AlertController.displayErrorAlert('The two passwords you entered do not match.');
        return;
    }
    if ((this.newPasswordField.val().length > 0 || this.confirmNewPasswordField.val().length > 0 || this.currentPasswordField.val().length > 0) && (this.newPasswordField.val().length === 0 || this.confirmNewPasswordField.val().length === 0 || this.currentPasswordField.val().length === 0)) {
        modernPaste.universal.AlertController.displayErrorAlert('To change your password, you must supply your current password, your new password, and a confirmation of your new password.');
        return;
    }

    this.saveButton.prop('disabled', true);
    modernPaste.universal.SplashController.showSplash(this.accountSplash);
    $.ajax({
        'method': 'POST',
        'url': modernPaste.universal.URIController.uris.UserUpdateDetailsURI,
        'contentType': 'application/json',
        'data': JSON.stringify({
            'name': this.nameField.val(),
            'email': this.emailField.val(),
            'current_password': this.currentPasswordField.val(),
            'new_password': this.newPasswordField.val()
        })
    })
    .done(modernPaste.user.account.AccountUserProfileController.showSaveSettingsSuccess.bind(this))
    .fail(modernPaste.user.account.AccountUserProfileController.showSaveSettingsFailure.bind(this))
};

/**
 * Show an error alert if the save operation succeeds.
 */
modernPaste.user.account.AccountUserProfileController.showSaveSettingsSuccess = function() {
    this.saveButton.prop('disabled', false);
    modernPaste.universal.SplashController.hideSplash(this.accountSplash);
    modernPaste.universal.AlertController.displaySuccessAlert('Your user profile settings were saved successfully!');
};

/**
 * Show an error alert if the save operation fails.
 */
modernPaste.user.account.AccountUserProfileController.showSaveSettingsFailure = function(data) {
    this.saveButton.prop('disabled', false);
    modernPaste.universal.SplashController.hideSplash(this.accountSplash);
    modernPaste.universal.AlertController.displayErrorAlert(
        modernPaste.universal.AlertController.selectErrorMessage(
            data,
            {
                'nonexistent_user_failure': 'The user for which you\'re updating settings no longer exists.',
                'invalid_email_failure': 'The email ' + this.emailField.val() + ' is not a valid email address.',
                'auth_failure': 'The current password you entered does not appear to be correct.'
            }
        )
    );
};
