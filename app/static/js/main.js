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
                    
                    var currentUserId = window.CURRENT_USER_ID; // Need to set this in base.html if we want to conditionally render the heart
                    
                    var heartHtml = '';
                    if (currentUserId && currentUserId != item.seller_id) {
                        var iconClass = item.is_wishlisted ? 'bi-heart-fill' : 'bi-heart';
                        var csrfToken = $('meta[name="csrf-token"]').attr('content');
                        var countText = 'Saved by ' + item.wishlist_count + (item.wishlist_count === 1 ? ' person' : ' people');
                        heartHtml = '<form action="/listings/' + item.id + '/wishlist" method="POST" class="m-0 wishlist-form">' +
                                    '<input type="hidden" name="csrf_token" value="' + csrfToken + '">' +
                                    '<button type="submit" class="btn btn-sm btn-link text-danger p-0 text-decoration-none" title="Toggle Wishlist" style="line-height: 1;">' +
                                    '<i class="' + iconClass + '"></i>' +
                                    '<span class="wishlist-count ms-1 text-dark" style="font-size: 0.85em;">' + countText + '</span>' +
                                    '</button></form>';
                    } else {
                        var countText = 'Saved by ' + item.wishlist_count + (item.wishlist_count === 1 ? ' person' : ' people');
                        heartHtml = '<div class="text-danger" style="line-height: 1;">' +
                                    '<i class="bi-heart-fill"></i>' +
                                    '<span class="wishlist-count ms-1 text-dark" style="font-size: 0.85em;">' + countText + '</span>' +
                                    '</div>';
                    }

                    var sellerUrl = '/user/' + item.seller_id;
                    var sellerName = item.seller_username ? item.seller_username.split(' ')[0] : 'User';

                    grid.append(
                        '<div class="col">' +
                        '<div class="listing-card card">' +
                        imgHtml +
                        '<div class="card-body p-3">' +
                        '<div class="d-flex justify-content-between align-items-start mb-1 gap-2">' +
                        '<h6 class="card-title mb-0 text-truncate" title="' + $('<span>').text(item.title).html() + '" style="flex: 1;">' +
                        '<a href="/listings/' + item.id + '" class="stretched-link text-decoration-none text-dark">' + $('<span>').text(item.title).html() + '</a>' +
                        '</h6>' +
                        '<div class="position-relative" style="z-index: 2; white-space: nowrap;">' + heartHtml + '</div>' +
                        '</div>' +
                        '<div class="listing-price">$' + parseFloat(item.price).toFixed(2) + '</div>' +
                        '<div class="d-flex align-items-center justify-content-between mt-2">' +
                        '<span class="category-badge">' + $('<span>').text(item.category).html() + '</span>' +
                        '<small class="text-muted">' +
                        '<a href="' + sellerUrl + '" class="text-muted text-decoration-none position-relative" style="z-index:2">' +
                        $('<span>').text(sellerName).html() +
                        '</a></small>' +
                        '</div></div></div></div>'
                    );
                });
            });
        }, 300);
    });

    // ── AJAX Wishlist Toggle ──────────────────────
    $(document).on('submit', '.wishlist-form', function(e) {
        e.preventDefault();
        var $form = $(this);
        var url = $form.attr('action');
        var csrfToken = $('meta[name="csrf-token"]').attr('content');
        
        $.ajax({
            type: 'POST',
            url: url,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrfToken
            },
            success: function(response) {
                if (response.success) {
                    var $icon = $form.find('i');
                    var $btn = $form.find('button');
                    var $count = $form.find('.wishlist-count');
                    
                    if (response.count !== undefined) {
                        // In detail page buttons, we only show the number in parentheses "(3)" 
                        // But if it contains "Saved by", we update the whole text.
                        var currentText = $count.text();
                        if (currentText.indexOf('Saved by') !== -1 || currentText.indexOf('person') !== -1 || currentText.indexOf('people') !== -1) {
                            $count.text('Saved by ' + response.count + (response.count === 1 ? ' person' : ' people'));
                        } else {
                            $count.text(response.count);
                        }
                    }
                    
                    // If it's a detail page button (has text)
                    if ($btn.hasClass('btn-outline-danger') || $btn.hasClass('btn-outline-secondary')) {
                        var $text = $form.find('.wishlist-text');
                        if (response.added) {
                            $btn.removeClass('btn-outline-secondary').addClass('btn-outline-danger');
                            $icon.removeClass('bi-heart').addClass('bi-heart-fill');
                            $text.text('Saved');
                        } else {
                            $btn.removeClass('btn-outline-danger').addClass('btn-outline-secondary');
                            $icon.removeClass('bi-heart-fill').addClass('bi-heart');
                            $text.text('Save');
                        }
                    } else {
                        // Grid card icon
                        if (response.added) {
                            $icon.removeClass('bi-heart').addClass('bi-heart-fill');
                        } else {
                            $icon.removeClass('bi-heart-fill').addClass('bi-heart');
                        }
                    }
                }
            }
        });
    });

});
