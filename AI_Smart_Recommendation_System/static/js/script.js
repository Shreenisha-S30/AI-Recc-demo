$(document).ready(function() {
    const $themeToggle = $('#theme-toggle');
    const $body = $('body');
    const $icon = $themeToggle.find('i');

    function updateThemeIcon() {
        if ($body.hasClass('dark-mode')) {
            $icon.removeClass('fa-moon').addClass('fa-sun');
        } else {
            $icon.removeClass('fa-sun').addClass('fa-moon');
        }
    }

    $themeToggle.on('click', function() {
        $body.toggleClass('dark-mode');
        updateThemeIcon();
        
        // Save preference
        const isDark = $body.hasClass('dark-mode');
        localStorage.setItem('darkMode', isDark);
    });

    // Check saved preference
    const savedTheme = localStorage.getItem('darkMode');
    if (savedTheme === 'false') {
        $body.removeClass('dark-mode');
    }
    
    updateThemeIcon();
});