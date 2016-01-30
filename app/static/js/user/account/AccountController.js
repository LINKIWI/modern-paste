goog.provide('modernPaste.user.account.AccountController');

goog.require('modernPaste.user.account.AccountPastesController');
goog.require('modernPaste.user.account.AccountAPIKeyController');


/**
 * This main controller handles transitions between settings sections in the UI.
 * It also handles displaying the appropriate section given the history push state.
 * Other controllers under this main controller handle each individual settings section.
 *
 * @constructor
 */
modernPaste.user.account.AccountController = function() {
    this.settingsLinks = $('.settings-item');
    this.settingsSectionContainers = $('.settings-section-container');
    this.desktopSettingsListGroup = $('.account-section-container .account-settings-list-group');
    this.mobileSettingsListGroup = $('.account-section-container .mobile-account-settings-list-group');

    var settingsContainersObjects = this.settingsLinks.map(function(link) {
        // Each settings-item has a data-section field which is the name of the class of the settings container.
        // This goes through each of the settings items, and creates a JQuery object of the settings container.
        return $('.' + $(this.settingsLinks[link]).data('section'));
    }.bind(this));
    this.settingsContainers = Object.keys(settingsContainersObjects).filter(function(key) {
        // Only consider numbers: these are objected directly selected by JQuery's query
        return !isNaN(key);
    }).map(function(key) {
        // Easier to treat this as an array than an object.
        return settingsContainersObjects[key];
    }.bind(this));

    modernPaste.user.account.AccountController.changeListGroupView.bind(this)();

    this.settingsLinks.on('click', modernPaste.user.account.AccountController.switchSettingsSection.bind(this));
    $(window).resize(modernPaste.user.account.AccountController.changeListGroupView.bind(this));
};

/**
 * There is some admittedly very complicated logic going on here.
 */
modernPaste.user.account.AccountController.switchSettingsSection = function(evt) {
    evt.preventDefault();

    this.settingsLinks.removeClass('active sans-serif semibold');
    var clickedSettingsLink = $('.' + $(evt.target).attr('class').split(/\s+/)[0]);
    var correspondingSettingsContainer = $('.' + clickedSettingsLink.data('section'))[0];
    this.settingsContainers.forEach(function(container) {
        if (container[0] === correspondingSettingsContainer) {
            $(container).show();
            clickedSettingsLink.addClass('active sans-serif semibold');
        } else {
            $(container).hide();
        }
    });
};

/**
 * Change the list group view type (desktop/mobile) depending on the current browser width.
 */
modernPaste.user.account.AccountController.changeListGroupView = function() {
    var width = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
    if (width > 1250) {
        this.mobileSettingsListGroup.hide();
        this.desktopSettingsListGroup.show();
        this.settingsSectionContainers.css('margin-left', '400px');
    } else {
        this.mobileSettingsListGroup.show();
        this.desktopSettingsListGroup.hide();
        this.settingsSectionContainers.css('margin-left', 0);
    }
};


$(document).ready(function() {
    new modernPaste.user.account.AccountController();
    new modernPaste.user.account.AccountPastesController();
    new modernPaste.user.account.AccountAPIKeyController();
});
