goog.provide('modernPaste.user.account.AccountDeactivateController');

goog.require('modernPaste.user.account.AccountPastesController');
goog.require('modernPaste.universal.AlertController');
goog.require('modernPaste.universal.SplashController');
goog.require('modernPaste.universal.URIController');


/**
 * This controller handles the account deactivation UI.
 *
 * @constructor
 */
modernPaste.user.account.AccountDeactivateController = function() {
    this.accountSplash = $('.account-splash');
    this.deactivateAccountButton = $('.deactivate-settings .deactivate-account-button');
    this.accountDeactivateModal = $('.user-deactivate-confirm-modal');

    this.deactivateAccountButton.on(
        'click',
        modernPaste.user.account.AccountDeactivateController.showDeactivateAccountModal.bind(this)
    );
};

/**
 * Show modal asking the user to confirm deactivation of the account.
 */
modernPaste.user.account.AccountDeactivateController.showDeactivateAccountModal = function(evt) {
    evt.preventDefault();

    this.accountDeactivateModal.modal('show');
    this.accountDeactivateModal.find('.user-deactivate-button').on(
        'click',
        modernPaste.user.account.AccountDeactivateController.deactivateAccount.bind(this)
    );
    this.accountDeactivateModal.find('.cancel-button').on(
        'click',
        modernPaste.user.account.AccountPastesController.hideModal.bind(this)
    );
};

/**
 * Request the server to deactivate the current account.
 */
modernPaste.user.account.AccountDeactivateController.deactivateAccount = function() {
    this.deactivateAccountButton.prop('disabled', true);
    modernPaste.universal.SplashController.showSplash(this.accountSplash);

    $.ajax({
        'method': 'POST',
        'url': modernPaste.universal.URIController.uris.UserDeactivateURI
    })
    .done(modernPaste.user.account.AccountDeactivateController.onDeactivateSuccess.bind(this))
    .fail(modernPaste.user.account.AccountDeactivateController.showDeactivateFailure.bind(this));
};

/**
 * Show a success message if deactivation is successful, then redirect to the logout page in 5 seconds.
 */
modernPaste.user.account.AccountDeactivateController.onDeactivateSuccess = function() {
    this.deactivateAccountButton.prop('disabled', false);
    this.accountDeactivateModal.modal('hide');
    modernPaste.universal.SplashController.hideSplash(this.accountSplash);

    modernPaste.universal.AlertController.displaySuccessAlert(
        'Your account has been deactivated. You will be redirected in 5 seconds.'
    );

    setTimeout(function() {
        window.location.href = modernPaste.universal.URIController.uris.UserLogoutInterfaceURI;
    }, 5000);
};

/**
 * Show a generic error message if the deactivation is unsuccessful.
 */
modernPaste.user.account.AccountDeactivateController.showDeactivateFailure = function() {
    this.deactivateAccountButton.prop('disabled', false);
    this.accountDeactivateModal.modal('hide');
    modernPaste.universal.SplashController.hideSplash(this.accountSplash);

    modernPaste.universal.AlertController.displayErrorAlert(
        'There was an undefined server-side error, and you account wasn\'t deactivated. Please try again later.'
    );
};
