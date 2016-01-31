goog.provide('modernPaste.universal.MenuController');


/**
 * This controller handles the left side-panel menu.
 *
 * @constructor
 */
modernPaste.universal.MenuController = function() {
    this.menuToggleButton = $('#header').find('.container .menu-button');
    this.menuPanel = $('#menu-panel');
    this.pageHeader = $('#header');
    this.pageFooter = $('#footer');
    this.mainPage = $('#main-page');
    this.userHeader = $('#header').find('.user-section .user-header');
    this.userHeaderDropdown = $('#user-header-dropdown');
    this.openSourceNote = this.menuPanel.find('.open-source-note');

    this.menuToggleButton.on('click', modernPaste.universal.MenuController.handleMenuToggleButtonClick.bind(this));
    $('html').on('click', modernPaste.universal.MenuController.handleWindowClick.bind(this));
    $(window).on('resize', modernPaste.universal.MenuController.toggleOpenSourceNoteVisibility.bind(this));
};

/**
 * Show or hide the menu panel's open source note depending on the available screen real estate.
 */
modernPaste.universal.MenuController.toggleOpenSourceNoteVisibility = function() {
    var height = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;
    height > 500 ? this.openSourceNote.show() : this.openSourceNote.hide();
};

/**
 * If the user clicks anywhere in the window, it should close the menu panel only if the menu panel is currently
 * expanded and the click lands outside the menu panel.
 */
modernPaste.universal.MenuController.handleWindowClick = function(evt) {
    if (modernPaste.universal.MenuController.isMenuPanelVisible.bind(this)() && this.menuPanel[0] !== $(evt.target)[0] && this.menuPanel.has($(evt.target)).length === 0) {
        // Panel is extended and visible, and the click location is outside of the menu
        modernPaste.universal.MenuController.hideMenuPanel.bind(this)();
    }
};

/**
 * Hide or show the menu panel when the user clicks on the menu button.
 */
modernPaste.universal.MenuController.handleMenuToggleButtonClick = function(evt) {
    evt.preventDefault();

    modernPaste.universal.MenuController.isMenuPanelVisible.bind(this)() ?
        modernPaste.universal.MenuController.hideMenuPanel.bind(this)() : modernPaste.universal.MenuController.showMenuPanel.bind(this)()
};

/**
 * Hide the menu panel.
 */
modernPaste.universal.MenuController.hideMenuPanel = function() {
    this.menuToggleButton.fadeOut(function() {
        $(this).attr('src', '/static/img/icons/menu.png');
        $(this).fadeIn();
    });
    this.menuPanel.css('margin-left', '-310px');
    this.pageHeader.css('margin-left', '0');
    this.mainPage.css('margin-left', '0');
    if (this.pageFooter.length > 0) {
        this.pageFooter.css('margin-left', '0');
    }
};

/**
 * Show the menu panel.
 */
modernPaste.universal.MenuController.showMenuPanel = function() {
    if (this.userHeaderDropdown.is(':visible')) {
        this.userHeader.click();
    }
    this.menuToggleButton.fadeOut(function() {
        $(this).attr('src', '/static/img/icons/cross.png');
        $(this).fadeIn();
    });
    this.menuPanel.css('margin-left', '0');
    this.pageHeader.css('margin-left', '310px');
    this.mainPage.css('margin-left', '310px');
    if (this.pageFooter.length > 0) {
        this.pageFooter.css('margin-left', '310px');
    }
};

/**
 * Determine if the menu panel is currently visible.
 *
 * @returns {boolean} true if the menu panel is extended and visible; false otherwise.
 */
modernPaste.universal.MenuController.isMenuPanelVisible = function() {
    return this.menuPanel.css('margin-left') === '0' || this.menuPanel.css('margin-left') === '0px';
};


$(document).ready(function() {
    new modernPaste.universal.MenuController();
});
