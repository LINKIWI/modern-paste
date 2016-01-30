goog.provide('modernPaste.user.account.AccountAPIKeyController');

goog.require('modernPaste.universal.AlertController');
goog.require('modernPaste.universal.URIController');
goog.require('modernPaste.universal.SplashController');


/**
 * This controller handles UI elements and regeneration of user API keys.
 *
 * @constructor
 */
modernPaste.user.account.AccountAPIKeyController = function() {
    this.accountSplash = $('.account-splash');
    this.regenerateAPIKeyButton = $('.api-key-settings .regenerate-api-key-button');
    this.apiKeyField = $('.api-key-settings .api-key-field');

    this.apiKeyField.on('click', modernPaste.user.account.AccountAPIKeyController.selectAllAPIKey);
    this.regenerateAPIKeyButton.on(
        'click',
        modernPaste.user.account.AccountAPIKeyController.regenerateAPIKey.bind(this)
    );
};

/**
 * When the user clicks on the API key field, select all the text.
 */
modernPaste.user.account.AccountAPIKeyController.selectAllAPIKey = function() {
    $(this).select();
};

/**
 * Request the server to regenerate this user's API key.
 */
modernPaste.user.account.AccountAPIKeyController.regenerateAPIKey = function() {
    this.regenerateAPIKeyButton.prop('disabled', true);
    modernPaste.universal.SplashController.showSplash(this.accountSplash);

    $.ajax({
        'method': 'POST',
        'url': modernPaste.universal.URIController.uris.UserAPIKeyRegenerateURI
    })
    .done(modernPaste.user.account.AccountAPIKeyController.showRegenerationSuccess.bind(this))
    .fail(modernPaste.user.account.AccountAPIKeyController.showRegenerationFailure.bind(this));
};

/**
 * Display an alert indicating API key regeneration success.
 */
modernPaste.user.account.AccountAPIKeyController.showRegenerationSuccess = function(data) {
    modernPaste.universal.SplashController.hideSplash(this.accountSplash);
    this.regenerateAPIKeyButton.prop('disabled', false);
    this.apiKeyField.val(data.api_key);

    modernPaste.universal.AlertController.displaySuccessAlert(
        'A new API key was successfully generated! View your new key under "View API Key."'
    );
};

/**
 * Display an alert indicating API key regeneration failure.
 */
modernPaste.user.account.AccountAPIKeyController.showRegenerationFailure = function() {
    modernPaste.universal.SplashController.hideSplash(this.accountSplash)
    this.regenerateAPIKeyButton.prop('disabled', false);

    modernPaste.universal.AlertController.displayErrorAlert(
        'There was an undefined server-side error, and a new API key couldn\'t be generated. Please try again later.'
    );
};
