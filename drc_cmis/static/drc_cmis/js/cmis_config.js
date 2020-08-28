// Initialized before django.jQuery scope.
$(function() {
    // Runs after django.jQuery scope is available.
    (function($) {
        $.getJSON("api/connection", function(data) {
            $(".field-cmis_connection .readonly").text(data.status);
        });
    })(django.jQuery);
});
