goog.provide('modernPaste.user.RegisterController');

goog.require('modernPaste.universal.URIController');
goog.require('modernPaste.universal.AlertController');
goog.require('modernPaste.universal.SplashController');


/**
 * This controller handles user registration and all functionality related to the registration user interface.
 *
 * @constructor
 */
modernPaste.user.RegisterController = function() {
    modernPaste.user.RegisterController.EVENT_FIELD_UPDATED = 'field_updated';

    this.registerForm = $('.register-container .register-form');
    this.usernameField = $('.register-container .username-field');
    this.passwordField = $('.register-container .password-field');
    this.passwordConfirmField = $('.register-container .password-confirm-field');
    this.nameField = $('.register-container .name-field');
    this.emailField = $('.register-container .email-field');
    this.formGroups = $('.register-container .form-group');
    this.registerButton = $('.register-button');
    this.registerSplash = $('.register-splash');

    $('[data-toggle=\'tooltip\']').tooltip({
        'placement': 'right',
        'trigger': 'manual'  // Tooltips are triggered during focusout events when invalid inputs are supplied.
    });

    this.usernameField.on('focusin', modernPaste.user.RegisterController.clearFieldStatus);
    this.usernameField.on('focusout', modernPaste.user.RegisterController.checkUsernameAvailability.bind(this));
    this.passwordConfirmField.on('focusin', modernPaste.user.RegisterController.clearFieldStatus);
    this.passwordConfirmField.on('focusout', modernPaste.user.RegisterController.checkPasswordMatch.bind(this));
    this.nameField.on('focusin', modernPaste.user.RegisterController.clearFieldStatus);
    this.nameField.on('focusout', modernPaste.user.RegisterController.showFieldSuccess.bind(this, this.nameField));  // No validity criteria
    this.emailField.on('focusin', modernPaste.user.RegisterController.clearFieldStatus);
    this.emailField.on('focusout', modernPaste.user.RegisterController.validateEmailAddress.bind(this));
    this.registerForm.on(modernPaste.user.RegisterController.EVENT_FIELD_UPDATED, modernPaste.user.RegisterController.enableRegisterButton.bind(this));
    this.registerButton.on('click', modernPaste.user.RegisterController.registerUser.bind(this));
};

/**
 * Clear the success/error state of the current input field.
 */
modernPaste.user.RegisterController.clearFieldStatus = function() {
    // Call the parent to get the form-group rather than the input element
    $(this).parent().removeClass('has-error has-success');
    $(this).tooltip('hide');
};

/**
 * Check if the username is available, and indicate visually (via the input field) if it is or isn't.
 */
modernPaste.user.RegisterController.checkUsernameAvailability = function(evt) {
    evt.preventDefault();

    $.ajax({
        'method': 'POST',
        'url': modernPaste.universal.URIController.uris.CheckUsernameAvailabilityURI,
        'contentType': 'application/json',
        'data': JSON.stringify({
            'username': this.usernameField.val()
        })
    })
    .done(
        function(data) {
            if (data.is_available) {
                modernPaste.user.RegisterController.showFieldSuccess(this.usernameField);
            } else {
                modernPaste.user.RegisterController.showFieldFailure(this.usernameField, 'This username is not available.');
            }
        }.bind(this)
    );
};

/**
 * Ensure that the password and password confirm fields are identical, and indicate visually if it is or isn't.
 */
modernPaste.user.RegisterController.checkPasswordMatch = function() {
    if (this.passwordField.val() === this.passwordConfirmField.val()) {
        modernPaste.user.RegisterController.showFieldSuccess(this.passwordField);
        modernPaste.user.RegisterController.showFieldSuccess(this.passwordConfirmField);
    } else {
        modernPaste.user.RegisterController.showFieldFailure(this.passwordField, null);
        modernPaste.user.RegisterController.showFieldFailure(this.passwordConfirmField, 'Your passwords don\'t match.');
    }
};

/**
 * Check if the supplied email address is valid, and indicate visually if it is or isn't.
 */
modernPaste.user.RegisterController.validateEmailAddress = function(evt) {
    evt.preventDefault();

    $.ajax({
        'method': 'POST',
        'url': modernPaste.universal.URIController.uris.ValidateEmailAddressURI,
        'contentType': 'application/json',
        'data': JSON.stringify({
            'email': this.emailField.val()
        })
    })
    .done(
        function(data) {
            if (data.is_valid) {
                modernPaste.user.RegisterController.showFieldSuccess(this.emailField);
            } else {
                modernPaste.user.RegisterController.showFieldFailure(this.emailField, 'This email address isn\'t valid.');
            }
        }.bind(this)
    );
};

/**
 * Choose whether the registration submission button should be enabled: it should be disabled if the form is incomplete
 * or contains errors, and should be enabled when the bare minimum registration criteria are met and the inputs are valid.
 */
modernPaste.user.RegisterController.enableRegisterButton = function() {
    if (!this.formGroups.hasClass('has-error') && this.usernameField.val().length > 0 && this.passwordField.val().length > 0 && this.passwordConfirmField.val().length > 0) {
        this.registerButton.prop('disabled', false);
    }
};

/**
 * Show that the input in the specified field is valid.
 *
 * @param field A JQuery object representing the input field.
 */
modernPaste.user.RegisterController.showFieldSuccess = function(field) {
    if (field.val().length > 0) {
        field.parent().removeClass('has-error has-success').addClass('has-success');
    }
    $('.register-container .register-form').trigger(modernPaste.user.RegisterController.EVENT_FIELD_UPDATED);
};

/**
 * Show that the input in the specified field is invalid.
 *
 * @param field A JQuery object representing the input field.
 * @param message The message that should be displayed explaining the reason the input is invalid.
 */
modernPaste.user.RegisterController.showFieldFailure = function(field, message) {
    field.parent().removeClass('has-error has-success').addClass('has-error');
    if (message != null) {
        field.attr('title', message).tooltip('fixTitle').tooltip('show');
    }
    // Any field failure should prevent registration
    $('.register-container .register-button').prop('disabled', true);  // Yes, I duplicated a JQuery lookup, deal with it
    $('.register-container .register-form').trigger(modernPaste.user.RegisterController.EVENT_FIELD_UPDATED);
};

/**
 * Attempt to register the user with the supplied field values.
 */
modernPaste.user.RegisterController.registerUser = function(evt) {
    evt.preventDefault();

    modernPaste.universal.SplashController.showSplash(this.registerSplash);
    $.ajax({
        'method': 'POST',
        'url': modernPaste.universal.URIController.uris.UserCreateURI,
        'contentType': 'application/json',
        'data': JSON.stringify({
            'username': this.usernameField.val(),
            'password': this.passwordField.val(),
            'name': this.nameField.val(),
            'email': this.emailField.val()
        })
    })
    .done(modernPaste.user.RegisterController.handleRegistrationSuccess.bind(this))
    .fail(modernPaste.user.RegisterController.handleRegistrationFailure.bind(this));
};

/**
 * When the registration succeeds, simply redirect the user to the home page.
 */
modernPaste.user.RegisterController.handleRegistrationSuccess = function() {
    window.location.href = modernPaste.universal.URIController.uris.PastePostInterfaceURI;
};

/**
 * Display an error alert if the registration fails.
 */
modernPaste.user.RegisterController.handleRegistrationFailure = function(data) {
    modernPaste.universal.SplashController.hideSplash(this.registerSplash);
    var errorMessages = {
        'username_not_available_failure': 'The username you selected is not available.',
        'invalid_email_failure': 'The email address you supplied is not valid. Please use a valid email address.'
    };
    modernPaste.universal.AlertController.displayErrorAlert(
        modernPaste.universal.AlertController.selectErrorMessage(data, errorMessages)
    );
};


$(document).ready(function() {
    new modernPaste.user.RegisterController();
});