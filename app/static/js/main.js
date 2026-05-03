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

                    var currentUserId = window.CURRENT_USER_ID;

                    var heartHtml = '';
                    if (currentUserId && currentUserId != item.seller_id) {
                        var iconClass = item.is_wishlisted ? 'bi-heart-fill' : 'bi-heart';
                        var countText = 'Saved by ' + item.wishlist_count + (item.wishlist_count === 1 ? ' person' : ' people');
                        heartHtml = '<button type="button"' +
                                    ' class="btn btn-sm btn-link text-danger p-0 text-decoration-none wishlist-btn"' +
                                    ' data-listing-id="' + item.id + '"' +
                                    ' data-is-saved="' + (item.is_wishlisted ? 'true' : 'false') + '"' +
                                    ' title="Save to Wishlist" style="line-height: 1;">' +
                                    '<i class="bi ' + iconClass + '"></i>' +
                                    '<span class="wishlist-count ms-1 text-dark" style="font-size: 0.85em;">' + countText + '</span>' +
                                    '</button>';
                    } else if (currentUserId) {
                        // seller view - just show count
                        var countText = 'Saved by ' + item.wishlist_count + (item.wishlist_count === 1 ? ' person' : ' people');
                        heartHtml = '<div class="text-danger" style="line-height: 1;">' +
                                    '<i class="bi bi-heart-fill"></i>' +
                                    '<span class="ms-1 text-dark" style="font-size: 0.85em;">' + countText + '</span>' +
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


    // ── Wishlist Popover (Save to list) ──────────────────────────
    var $wishlistPopover = null;
    var activeBtn = null;

    function buildPopoverContent(listingId, wishlists) {
        var html = '<div class="wishlist-popover-inner" style="min-width: 180px;">';
        html += '<p class="fw-semibold mb-2" style="font-size: 0.9em; color: #1d3557;">Save to wishlist</p>';
        wishlists.forEach(function(wl) {
            var checked = wl.checked ? 'checked' : '';
            html += '<div class="form-check mb-1">' +
                    '<input class="form-check-input wl-checkbox" type="checkbox" ' + checked +
                    ' id="wl-' + wl.id + '" data-wishlist-id="' + wl.id + '" data-listing-id="' + listingId + '">' +
                    '<label class="form-check-label" for="wl-' + wl.id + '" style="font-size: 0.9em;">' +
                    $('<span>').text(wl.name).html() + '</label></div>';
        });
        html += '<hr class="my-2">';
        // Inline new-list creation
        html += '<div class="d-flex gap-1 mt-1 wl-new-list-row">' +
                '<input type="text" class="form-control form-control-sm wl-new-name" placeholder="New list..." data-listing-id="' + listingId + '" style="font-size:0.8em;">' +
                '<button class="btn btn-sm btn-primary wl-new-create" style="font-size:0.75em; white-space:nowrap;">+ Add</button>' +
                '</div>';
        html += '<a href="/user/wishlist" class="btn btn-sm btn-outline-secondary w-100 mt-2" style="font-size: 0.8em;"><i class="bi bi-folder2-open me-1"></i>Manage Lists</a>';
        html += '</div>';
        return html;
    }

    function showWishlistPopover($btn, listingId) {
        // Close any open popover first
        if ($wishlistPopover) {
            $wishlistPopover.remove();
            if (activeBtn === $btn[0]) {
                $wishlistPopover = null;
                activeBtn = null;
                return;
            }
        }
        activeBtn = $btn[0];

        // Fetch wishlists for this listing
        $.getJSON('/listings/' + listingId + '/wishlists', function(data) {
            var content = buildPopoverContent(listingId, data.wishlists);

            // Append to body so overflow:hidden on cards doesn't clip it
            $wishlistPopover = $('<div class="wishlist-popup shadow rounded border bg-white p-3" style="position: fixed; z-index: 99999;"></div>').html(content);
            $('body').append($wishlistPopover);

            // Position below the button using its viewport coordinates
            var rect = $btn[0].getBoundingClientRect();
            var popW = $wishlistPopover.outerWidth();
            var left = rect.right - popW;
            var top  = rect.bottom + 6;

            // Keep inside viewport horizontally
            if (left < 8) left = 8;

            $wishlistPopover.css({ top: top + 'px', left: left + 'px' });

            // Update parent button state from data
            updateHeartBtn($btn, data.is_saved, data.save_count);
        });
    }

    function updateHeartBtn($btn, isSaved, saveCount) {
        var $icon = $btn.find('i');
        var $count = $btn.find('.wishlist-count');
        $btn.attr('data-is-saved', isSaved ? 'true' : 'false');

        if ($btn.hasClass('btn-outline-danger') || $btn.hasClass('btn-outline-secondary')) {
            // detail page button
            var $text = $btn.find('.wishlist-text');
            if (isSaved) {
                $btn.removeClass('btn-outline-secondary').addClass('btn-outline-danger');
                $icon.attr('class', 'bi bi-heart-fill me-1');
                if ($text.length) $text.text('Saved');
            } else {
                $btn.removeClass('btn-outline-danger').addClass('btn-outline-secondary');
                $icon.attr('class', 'bi bi-heart me-1');
                if ($text.length) $text.text('Save');
            }
            if ($count.length) $count.text(saveCount);
        } else {
            // grid card button
            if (isSaved) {
                $icon.attr('class', 'bi bi-heart-fill');
            } else {
                $icon.attr('class', 'bi bi-heart');
            }
            if ($count.length) {
                var countText = 'Saved by ' + saveCount + (saveCount === 1 ? ' person' : ' people');
                $count.text(countText);
            }
        }
    }

    // Click on a wishlist heart button
    $(document).on('click', '.wishlist-btn', function(e) {
        e.stopPropagation();
        var $btn = $(this);
        var listingId = $btn.data('listing-id');
        showWishlistPopover($btn, listingId);
    });

    // Click on a wishlist checkbox
    $(document).on('change', '.wl-checkbox', function() {
        var $cb = $(this);
        var wishlistId = $cb.data('wishlist-id');
        var listingId = $cb.data('listing-id');
        var csrfToken = $('meta[name="csrf-token"]').attr('content');

        $.ajax({
            type: 'POST',
            url: '/listings/' + listingId + '/wishlist/' + wishlistId,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrfToken
            },
            success: function(response) {
                if (response.success) {
                    $cb.prop('checked', response.checked);
                    // Update the trigger button
                    if (activeBtn) {
                        updateHeartBtn($(activeBtn), response.is_saved, response.save_count);
                    }
                    // Also update any other heart buttons for the same listing on page
                    $('.wishlist-btn[data-listing-id="' + listingId + '"]').each(function() {
                        if (this !== activeBtn) {
                            updateHeartBtn($(this), response.is_saved, response.save_count);
                        }
                    });
                }
            }
        });
    });

    // Close popover when clicking outside
    $(document).on('click', function(e) {
        if ($wishlistPopover && !$(e.target).closest('.wishlist-popup, .wishlist-btn').length) {
            $wishlistPopover.remove();
            $wishlistPopover = null;
            activeBtn = null;
        }
    });

    // ── Inline "+ Add" new list inside popover ───────────────────
    function createNewListFromPopover($row) {
        var $input = $row.find('.wl-new-name');
        var listingId = $input.data('listing-id');
        var name = $input.val().trim();
        if (!name) return;
        var csrfToken = $('meta[name="csrf-token"]').attr('content');
        $.ajax({
            type: 'POST',
            url: '/user/wishlist/create',
            contentType: 'application/json',
            data: JSON.stringify({ name: name }),
            headers: { 'X-CSRFToken': csrfToken, 'X-Requested-With': 'XMLHttpRequest' },
            success: function(data) {
                // Auto-check into new list
                var csrfToken2 = $('meta[name="csrf-token"]').attr('content');
                $.ajax({
                    type: 'POST',
                    url: '/listings/' + listingId + '/wishlist/' + data.id,
                    headers: { 'X-CSRFToken': csrfToken2, 'X-Requested-With': 'XMLHttpRequest' },
                    success: function(resp) {
                        // Add new checkbox row to popover
                        var newRow = '<div class="form-check mb-1">' +
                            '<input class="form-check-input wl-checkbox" type="checkbox" checked' +
                            ' id="wl-' + data.id + '" data-wishlist-id="' + data.id + '" data-listing-id="' + listingId + '">' +
                            '<label class="form-check-label" for="wl-' + data.id + '" style="font-size:0.9em;">' +
                            $('<span>').text(data.name).html() + '</label></div>';
                        $row.before(newRow);
                        $input.val('');
                        if (activeBtn) {
                            updateHeartBtn($(activeBtn), resp.is_saved, resp.save_count);
                        }
                    }
                });
            }
        });
    }

    $(document).on('click', '.wl-new-create', function(e) {
        e.stopPropagation();
        createNewListFromPopover($(this).closest('.wl-new-list-row'));
    });
    $(document).on('keydown', '.wl-new-name', function(e) {
        e.stopPropagation();
        if (e.key === 'Enter') createNewListFromPopover($(this).closest('.wl-new-list-row'));
    });

});
