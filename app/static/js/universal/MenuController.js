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

    this.menuToggleButton.on('click', modernPaste.universal.MenuController.handleMenuToggleButtonClick.bind(this));
};

/**
 * Hide or show the menu panel when the user clicks on the menu button.
 */
modernPaste.universal.MenuController.handleMenuToggleButtonClick = function(evt) {
    evt.preventDefault();

    if (this.menuPanel.css('margin-left') === '0' || this.menuPanel.css('margin-left') === '0px') {
        // Panel is extended and visible
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
    } else {
        // Panel is not visible
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
    }
};


$(document).ready(function() {
    new modernPaste.universal.MenuController();
});