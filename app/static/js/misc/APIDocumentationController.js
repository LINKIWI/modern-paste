goog.provide('modernPaste.misc.APIDocumentationController');

goog.require('modernPaste.universal.URIController');


modernPaste.misc.APIDocumentationController = function() {
    hljs.initHighlightingOnLoad();
}


$(document).ready(function() {
    new modernPaste.misc.APIDocumentationController();
});
