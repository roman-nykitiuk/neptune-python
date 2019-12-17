(function($) {
  $(document).ready(function() {
    $('#searchbar').autocomplete({
      delay: 500,
      source: function(request, response) {
        $.getJSON(window.location.pathname + 'autocomplete/?term=' + request.term,
          function(data) {
            data = data.results.map(function(result) { return result.text});
            response(data);
          }
        )
      }
    });
  });
})(jQuery);
