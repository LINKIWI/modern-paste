goog.provide('modernPaste.universal.URIController');


/**
 * Upon initialization, all URIs placed into the #uris div via the templating engine will be available in a
 * Javascript object modernPaste.universal.URIController.uris, indexed by the name of the class as it appears
 * in the Python uri module. This allows convenient access to URIs without having to worry about the actual string,
 * e.g. modernPaste.universal.URIController.uris.PasteSubmitURI
 *
 * @constructor
 */
modernPaste.universal.URIController = function() {
    var documentURIs = $('#uris');
    modernPaste.universal.URIController.uris = {};
    for (var i = 0; i < documentURIs.children().length; i++) {
        var uri = $(documentURIs.children()[i]);
        modernPaste.universal.URIController.uris[uri.attr('id')] = uri.text();
    }
};

/**
 * Format a URI in a Flask-friendly way. If the specified URI string has a <path> parameter, it will replace the value
 * of that embedded parameter with the value of that key in the params argument. Otherwise, it will append each
 * key-value pair in the params object in the standard way.
 *
 * modernPaste.universal.URIController.formatURI('/api/<key>/123', {key: 456}) -> '/api/456/123'
 * modernPaste.universal.URIController.formatURI('/api/123', {key: 456}) -> '/api/123?key=456'
 * modernPaste.universal.URIController.formatURI('/api/123', {key: 456, more: 789}) -> '/api/123?key=456&more=789'
 *
 * @param uri The URI string to format
 * @param params An object mapping keys to values with which to format the URI string
 */
modernPaste.universal.URIController.formatURI = function(uri, params) {
    var constructedURI = uri;
    var paramsString = [];
    for (var param in params) {
        if (params.hasOwnProperty(param)) {
            if (uri.indexOf('<' + param + '>') > 0) {
                // Embedded param
                constructedURI = constructedURI.split('<' + param + '>').join(params[param]);
            } else {
                // Normal param
                paramsString.push(param + '=' + params[param]);
            }
        }
    }
    if (paramsString.length > 0) {
        return constructedURI + '?' + paramsString.join('&');
    } else {
        return constructedURI;
    }
};


$(document).ready(function() {
    new modernPaste.universal.URIController();
});