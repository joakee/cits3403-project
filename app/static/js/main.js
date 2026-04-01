$(document).ready(function () {

    // ── Live search on listings index page ──────────────────────
    var searchTimer;
    $('#listings-search').on('input', function () {
        clearTimeout(searchTimer);
        var q = $(this).val();
        searchTimer = setTimeout(function () {
            $.getJSON('/listings/api/search', { q: q }, function (data) {
                var grid = $('#listings-grid');
                grid.empty();
                if (data.length === 0) {
                    grid.append(
                        '<div class="col-12"><div class="empty-state">' +
                        '<i class="bi bi-search"></i>' +
                        '<p>No listings found for "' + $('<span>').text(q).html() + '"</p>' +
                        '</div></div>'
                    );
                    return;
                }
                $.each(data, function (_, item) {
                    var imgHtml = item.image_url
                        ? '<img src="' + item.image_url + '" class="listing-img">'
                        : '<div class="listing-img-placeholder"><i class="bi bi-box-seam"></i></div>';
                    grid.append(
                        '<div class="col">' +
                        '<a href="/listings/' + item.id + '" class="listing-card card">' +
                        imgHtml +
                        '<div class="card-body p-3">' +
                        '<h6 class="card-title mb-1 text-truncate">' + $('<span>').text(item.title).html() + '</h6>' +
                        '<div class="listing-price">$' + parseFloat(item.price).toFixed(2) + '</div>' +
                        '<span class="category-badge mt-1 d-inline-block">' + $('<span>').text(item.category).html() + '</span>' +
                        '</div></a></div>'
                    );
                });
            });
        }, 300);
    });

});
