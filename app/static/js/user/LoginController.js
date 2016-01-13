goog.provide('modernPaste.user.LoginController');

goog.require('modernPaste.universal.URIController');
goog.require('modernPaste.universal.AlertController');
goog.require('modernPaste.universal.SplashController');


/**
 * This controller handles logging in a user with a credentials pair via AJAX.
 *
 * @constructor
 */
modernPaste.user.LoginController = function() {
    this.loginSplash = $('.login-splash.splash');
    this.usernameField = $('.login-container .username-field');
    this.passwordField = $('.login-container .password-field');
    this.rememberMe = $('.login-container .remember-me-check');
    this.loginButton = $('.login-container .login-button');

    this.loginButton.on('click', modernPaste.user.LoginController.attemptUserLogin.bind(this));
};

/**
 * Attempt to log the user in.
 */
modernPaste.user.LoginController.attemptUserLogin = function(evt) {
    evt.preventDefault();

    modernPaste.universal.SplashController.showSplash(this.loginSplash);
    $.ajax({
        'method': 'POST',
        'url': modernPaste.universal.URIController.uris.LoginUserURI,
        'contentType': 'application/json',
        'data': JSON.stringify({
            'username': this.usernameField.val(),
            'password': this.passwordField.val(),
            'remember_me': this.rememberMe.is(':checked')
        })
    })
    .done(modernPaste.user.LoginController.handleLoginSuccess.bind(this))
    .fail(modernPaste.user.LoginController.handleLoginFail.bind(this));
};

/**
 * Redirect the user to the home page on successful login.
 */
modernPaste.user.LoginController.handleLoginSuccess = function(data) {
    window.location.href = modernPaste.universal.URIController.uris.HomeURI;
};

/**
 * Indicate login failure by displaying an error message.
 */
modernPaste.user.LoginController.handleLoginFail = function(data) {
    modernPaste.universal.SplashController.hideSplash(this.loginSplash);

    var errorMessages = {
        'incomplete_params_failure': 'You must supply both a username and password to authenticate.',
        'auth_failure': 'Your credentials aren\'t correct. Are you sure your username and password are correct?',
        'nonexistent_user_failure': 'That user doesn\'t seem to exist. Please register for an account if you don\'t have one yet.'
    };
    modernPaste.universal.AlertController.displayErrorAlert(
        modernPaste.universal.AlertController.selectErrorMessage(data, errorMessages)
    );
};


$(document).ready(function() {
    new modernPaste.user.LoginController();
});