goog.provide('modernPaste.paste.ArchiveController');

goog.require('modernPaste.universal.AlertController');
goog.require('modernPaste.universal.CommonController');
goog.require('modernPaste.universal.URIController');


/**
 * This controller handles the display of recent and top pastes in a paginated manner.
 *
 * @constructor
 */
modernPaste.paste.ArchiveController = function() {
    modernPaste.paste.ArchiveController.ARCHIVE_MODE_RECENT = 'archive_mode_recent';
    modernPaste.paste.ArchiveController.ARCHIVE_MODE_TOP = 'archive_mode_top';
    this.currentArchiveMode = modernPaste.paste.ArchiveController.ARCHIVE_MODE_RECENT;  // Default

    this.recentPastesLink = $('.archive-header-container .recent-pastes-link');
    this.topPastesLink = $('.archive-header-container .top-pastes-link');
    this.pasteListContainer = $('.archive-container .paste-list-container');
    this.pasteItemTemplate = $('.paste-item-template');
    this.previousButton = $('.archive-container .previous-button');
    this.nextButton = $('.archive-container .next-button');
    this.pageStatus = $('.archive-container .page-status');

    this.currentPage = 0;
    this.numPerPage = 20;

    modernPaste.paste.ArchiveController.loadPastes.bind(this)();

    this.recentPastesLink.on('click', modernPaste.paste.ArchiveController.changeMode.bind(this, modernPaste.paste.ArchiveController.ARCHIVE_MODE_RECENT));
    this.topPastesLink.on('click', modernPaste.paste.ArchiveController.changeMode.bind(this, modernPaste.paste.ArchiveController.ARCHIVE_MODE_TOP));
    this.previousButton.on('click', modernPaste.paste.ArchiveController.loadPreviousPage.bind(this));
    this.nextButton.on('click', modernPaste.paste.ArchiveController.loadNextPage.bind(this));
};

/**
 * Change the mode to either recent pastes or top pastes.
 *
 * @param mode One of the modernPaste.paste.ArchiveController.ARCHIVE_MODE_x constants
 */
modernPaste.paste.ArchiveController.changeMode = function(mode) {
    this.currentPage = 0;
    this.currentArchiveMode = mode;
    modernPaste.paste.ArchiveController.loadPastes.bind(this)();
};

/**
 * Load pastes for the current page number and the predefined number of results per page.
 * These constants are global variables that are modified outside this function.
 */
modernPaste.paste.ArchiveController.loadPastes = function() {
    var url = modernPaste.universal.URIController.uris.RecentPastesURI;
    if (this.currentArchiveMode == modernPaste.paste.ArchiveController.ARCHIVE_MODE_TOP) {
        url = modernPaste.universal.URIController.uris.TopPastesURI;
    }

    $.ajax({
        'method': 'POST',
        'url': url,
        'contentType': 'application/json',
        'data': JSON.stringify({
            'page_num': this.currentPage,
            'num_per_page': this.numPerPage
        })
    })
    .done(modernPaste.paste.ArchiveController.loadPastesIntoList.bind(this))
    .fail(modernPaste.paste.ArchiveController.showPasteLoadError.bind(this));
};

/**
 * When pastes have been successfully retrieved from the server, load them into the table.
 * If there are no pastes available to load, decrement the current page number and take no action.
 * This function will also hide or show the previous button appropriately.
 */
modernPaste.paste.ArchiveController.loadPastesIntoList = function(data) {
    if (data.pastes.length == 0) {
        // If there are no pastes on this page, change back to the prevent page index and do nothing.
        this.currentPage--;
        modernPaste.universal.AlertController.displayErrorAlert('There are no more pastes to display.');
        return;
    }

    // Hide or show the previous button accordingly
    this.currentPage <= 0 ? this.previousButton.fadeOut('fast') : this.previousButton.fadeIn('fast');

    // Update the text indicating the current entries being shown
    var pasteLowerBound = this.currentPage * this.numPerPage + 1;
    var pasteUpperBound = (this.currentPage + 1) * this.numPerPage;
    var modeNames = {};
    modeNames[modernPaste.paste.ArchiveController.ARCHIVE_MODE_RECENT] = 'RECENT';
    modeNames[modernPaste.paste.ArchiveController.ARCHIVE_MODE_TOP] = 'TOP';
    this.pageStatus.text(
        'SHOWING ' + modeNames[this.currentArchiveMode] + ' PASTES ' + pasteLowerBound + '-' + pasteUpperBound
    );

    this.pasteListContainer.empty();
    data.pastes.forEach(function(paste) {
        var pasteTableRow = $(this.pasteItemTemplate.html());
        pasteTableRow.find('.paste-title').text(paste.title);
        pasteTableRow.find('.paste-title').prop(
            'href',
            modernPaste.universal.URIController.formatURI(
                modernPaste.universal.URIController.uris.PasteViewInterfaceURI,
                {
                    'paste_id': paste.paste_id_repr
                }
            )
        );
        pasteTableRow.find('.paste-posted').text(
            modernPaste.universal.CommonController.unixTimestampToRelativeTime(paste.post_time)
        );
        pasteTableRow.find('.paste-views').text(paste.views);
        this.pasteListContainer.append(pasteTableRow);
    }.bind(this));
};

/**
 * Request pastes from the next page.
 */
modernPaste.paste.ArchiveController.loadNextPage = function() {
    this.currentPage++;
    modernPaste.paste.ArchiveController.loadPastes.bind(this)();
};

/**
 * Request pastes from the previous page.
 */
modernPaste.paste.ArchiveController.loadPreviousPage = function() {
    this.currentPage--;
    modernPaste.paste.ArchiveController.loadPastes.bind(this)();
};

/**
 * Indicate an undefined error if there was a server-side error retrieving pastes.
 */
modernPaste.paste.ArchiveController.showPasteLoadError = function() {
    modernPaste.universal.AlertController.displayErrorAlert(
        'There was an error retrieving pastes from the server. Please try again later.'
    );
};


$(document).ready(function() {
    new modernPaste.paste.ArchiveController();
});
