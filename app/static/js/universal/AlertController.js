goog.provide('modernPaste.universal.AlertController');


/**
 * Encapsulates methods to handle and display error conditions in the frontend interface.
 *
 * @constructor
 */
modernPaste.universal.AlertController = function() {
    modernPaste.universal.AlertController.ALERT_TYPE_SUCCESS = 'alert_type_success';
    modernPaste.universal.AlertController.ALERT_TYPE_FAILURE = 'alert_type_failure';
};

/**
 * Display a transient alert on the page with the specified type and message.
 *
 * @param alertType One of the ALERT_TYPE constants defined in modernPaste.universal.AlertController
 * @param message The message to display
 */
modernPaste.universal.AlertController.displayAlert = function(alertType, message) {
    this.alertContainer = $('#alert');
    this.alertMessage = this.alertContainer.find('.alert-message');
    this.alertTitle = this.alertContainer.find('.alert-title');

    this.alertContainer.removeClass();
    if (alertType === this.ALERT_TYPE_SUCCESS) {
        this.alertTitle.text('');
        this.alertContainer.addClass('alert-success');
    } else if (alertType === this.ALERT_TYPE_FAILURE) {
        this.alertTitle.text('There was an error processing your request.');
        this.alertContainer.addClass('alert-error');
    }

    this.alertMessage.text(message);
    this.alertContainer.css('visibility', 'visible');
    this.alertContainer.css('opacity', 0.8);
    setTimeout(function() {
        this.alertContainer.css('opacity', 0);
        setTimeout(function() {
            // I'm not proud of this.
            this.alertContainer.css('visibility', 'hidden');
        }.bind(this), 600);
    }.bind(this), 4000);
};

/**
 * Wrapper for displayAlert to display a success alert.
 *
 * @param message The message to display
 */
modernPaste.universal.AlertController.displaySuccessAlert = function(message) {
    modernPaste.universal.AlertController.displayAlert(modernPaste.universal.AlertController.ALERT_TYPE_SUCCESS, message);
};

/**
 * Wrapper for displayAlert to display an error alert.
 *
 * @param message The message to display
 */
modernPaste.universal.AlertController.displayErrorAlert = function(message) {
    modernPaste.universal.AlertController.displayAlert(modernPaste.universal.AlertController.ALERT_TYPE_FAILURE, message);
};

/**
 * Given the server response and a mapping of failure names to error messages, this method picks the appropriate
 * error message for the response. If the server response indicates an internal error or no error message matches
 * the exact failure in the response, a generic error message is returned.
 *
 * @param data The raw server response object, e.g. as returned by the jQuery.ajax call
 * @param errorMessages An object mapping failure names to error messages
 */
modernPaste.universal.AlertController.selectErrorMessage = function(data, errorMessages) {
    var genericFailureMessage = 'There was an internal server-side error. Please try again later.';
    if (data.responseJSON === undefined || data.responseJSON.failure === undefined) {
        return genericFailureMessage;
    }
    if (errorMessages.hasOwnProperty(data.responseJSON.failure)) {
        return errorMessages[data.responseJSON.failure];
    } else {
        return genericFailureMessage;
    }
};


$(document).ready(function() {
    new modernPaste.universal.AlertController();
});
