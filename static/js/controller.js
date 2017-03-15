/**
 * Handle window scroll events. When the window is not scrolled to the top, the "scroll to learn more" prompt should
 * disappear. When the intro page is almost scrolled out of view, the header title should appear.
 */
function handleWindowScroll() {
    var headerTitle = $('.mp-header .mp-title');
    var scrollPrompt = $('.intro .scroll-prompt');

    var height = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;

    if ($(window).scrollTop() > height - 200) {
        // Approximately scrolled past main intro title
        headerTitle.fadeIn();
    } else {
        headerTitle.fadeOut();
    }

    if ($(window).scrollTop() > 0) {
        // Not scrolled to the top
        scrollPrompt.fadeOut();
    } else {
        scrollPrompt.fadeIn();
    }
}


$(document).ready(function() {
    // Register event handlers
    $(window).on('scroll', handleWindowScroll);

    // Fancybox initialization
    $('.fancybox').fancybox({
        helpers: {
            overlay: {
                locked: false
            }
        }
    });

    // The header title should be hidden when the page loads
    $('.mp-header .mp-title').hide();
});
