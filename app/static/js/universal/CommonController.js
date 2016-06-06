goog.provide('modernPaste.universal.CommonController');


/**
 * This controller contains utility functions common to all controllers.
 *
 * @constructor
 */
modernPaste.universal.CommonController = function() {};

/**
 * Convert a UNIX timestamp to a relative time, e.g. "3 hours ago."
 * This function will return units of days, hours, minutes, and seconds.
 *
 * @param unixTimestampString Timestamp as a string
 * @returns {string} A string representing a relative time.
 */
modernPaste.universal.CommonController.unixTimestampToRelativeTime = function(unixTimestampString) {
    // Convert the string to a plural form, as necessary, depending on num.
    var pluralForm = function(string, num) {
        return num === 1 ? string : string + 's';
    };

    var timestampDate = new Date(parseInt(unixTimestampString, 10) * 1000);
    var currentDate = new Date();
    var deltaDate = currentDate - timestampDate;

    var deltaSeconds = deltaDate / 1000.0;
    var deltaMinutes = deltaSeconds / 60.0;
    var deltaHours = deltaMinutes / 60.0;
    var deltaDays = deltaHours / 24.0;
    var deltaMonths = deltaDays / 30.0;
    var deltaYears = deltaMonths / 12.0;

    if (deltaYears >= 1 ) {
        return Math.round(deltaYears) + pluralForm(' year', Math.round(deltaYears)) + ' ago';
    } else if (deltaMonths >= 1) {
        return Math.round(deltaMonths) + pluralForm(' month', Math.round(deltaMonths)) + ' ago';
    } else if (deltaDays >= 1) {
        return Math.round(deltaDays) + pluralForm(' day', Math.round(deltaDays)) + ' ago';
    } else if (deltaHours >= 1) {
        return Math.round(deltaHours) + pluralForm(' hour', Math.round(deltaHours)) + ' ago';
    } else if (deltaMinutes >= 1) {
        return Math.round(deltaMinutes) + pluralForm(' minute', Math.round(deltaMinutes)) + ' ago';
    } else {
        return Math.round(deltaSeconds) + pluralForm(' second', Math.round(deltaSeconds)) + ' ago';
    }
};

/**
 * Truncate the input text to to the desired character limit, adding ellipsis if it exceeds the limit.
 *
 * @param text String to possibly truncate
 * @param characterLimit Integer limit for the string length
 * @returns {string} The input string, possibly truncated with ellipsis at the end
 */
modernPaste.universal.CommonController.truncateText = function(text, characterLimit) {
    return text.length > characterLimit ? text.substring(0, characterLimit) + '...' : text;
};

/**
 * Get the file extension for the given file type.
 *
 * @param fileType A string representing the paste language.
 * @returns {string} A string representing the associated file extension.
 */
modernPaste.universal.CommonController.getFileExtensionForType = function(fileType) {
    // Necessary to determine the appropriate file extension
    // This mapping is obviously not exhaustive, but covers popular languages
    var fileExtensions = {
        'text': '.txt',
        'coffeescript': '.coffee',
        'css': '.css',
        'htmlmixed': '.html',
        'javascript': '.js',
        'jinja2': '.html',
        'markdown': '.md',
        'php': '.php',
        'python': '.py',
        'sass': '.scss',
        'sql': '.sql',
        'verilog': '.v',
        'yaml': '.yml'
    };

    // If the file extension is unknown, default to having no file extension.
    var fileExtension = '';
    if (fileExtensions.hasOwnProperty(fileType.toLowerCase())) {
        fileExtension = fileExtensions[fileType.toLowerCase()];
    }

    return fileExtension;
};

/**
 * Convert the number of bytes to a human-readable representation in either B, KB, MB, or GB.
 *
 * @param numB The number of bytes
 * @param numDecimalPlaces The number of decimal places to round the result to; defaults to 2
 * @returns {string} A human-readable string representation of the input number of bytes
 */
modernPaste.universal.CommonController.formatFileSize = function(numB, numDecimalPlaces) {
    if (numDecimalPlaces === undefined) {
        // Default to 2 decimal places, unless otherwise specified
        numDecimalPlaces = 2;
    }

    var numKB = numB / 1000.0;
    var numMB = numKB / 1000.0;
    var numGB = numMB / 1000.0;

    if (numGB >= 1) {
        return numGB.toFixed(numDecimalPlaces) + ' GB';
    } else if (numMB >= 1) {
        return numMB.toFixed(numDecimalPlaces) + ' MB';
    } else if (numKB >= 1) {
        return numKB.toFixed(numDecimalPlaces) + ' KB';
    } else {
        return numB.toFixed(numDecimalPlaces) + ' B';
    }
};

/**
 * Escape all characters necessary for generating a jQuery ID selector.
 *
 * @param selector Raw selector string, with characters unescaped
 * @returns {string} Escaped version of the input safe to use as a jQuery selector
 */
modernPaste.universal.CommonController.escapeSelector = function(selector) {
    return selector.replace( /(:|\.|\[|\]|,)/g, "\\$1");
};


$(document).ready(function() {
    new modernPaste.universal.CommonController();
});
