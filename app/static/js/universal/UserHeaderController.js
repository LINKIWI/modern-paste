goog.provide('modernPaste.universal.UserHeaderController');


/**
 * This controller handles the behavior for the user header indicating whether a user is logged in.
 *
 * @constructor
 */
modernPaste.universal.UserHeaderController = function() {
    this.userHeader = $('#header').find('.user-section .user-header');
    this.userMenuArrow = this.userHeader.find('.user-menu-arrow');
    this.userHeaderDropdown = $('#user-header-dropdown');

    this.userHeader.on('click', modernPaste.universal.UserHeaderController.toggleDropdownVisibility.bind(this));
};

/**
 * If the dropdown is not currently visible, slide it down and rotate the arrow.
 * Otherwise, slide the dropdown up and rotate the arrow accordingly.
 */
modernPaste.universal.UserHeaderController.toggleDropdownVisibility = function(evt) {
    evt.preventDefault();

    if (this.userHeaderDropdown.is(':visible')) {
        this.userMenuArrow.css('transform', 'rotate(90deg)');
        this.userHeaderDropdown.slideUp({
            'duration': 600,
            'easing': 'easeOutQuint'
        });
    } else {
        this.userMenuArrow.css('transform', 'rotate(-90deg)');
        this.userHeaderDropdown.slideDown({
            'duration': 600,
            'easing': 'easeOutQuint'
        });
    }
};


$(document).ready(function() {
    new modernPaste.universal.UserHeaderController();
});
