(function () {
  var socket;

  function connect() {
    console.log('[live-mod] Connecting to socket.io...');

    socket = io({
      transports: ['polling', 'websocket'],
      upgrade: false,
      timeout: 2000,
      reconnectionAttempts: 3
    });

    socket.on('connect', function () {
      console.log('[live-mod] Connected, sid:', socket.id);
    });

    socket.on('connect_error', function (err) {
      console.error('[live-mod] Connection error:', err.message);
    });

    socket.on('disconnect', function (reason) {
      console.warn('[live-mod] Disconnected:', reason);
    });

    socket.on('listing_removed', function (data) {
      console.log('[live-mod] listing_removed received:', data);
      var listingId = data.listing_id;

      var cards = document.querySelectorAll('[data-listing-id="' + listingId + '"]');
      console.log('[live-mod] Found', cards.length, 'matching elements');

      cards.forEach(function (el) {
        var col = el.closest('.col');
        if (col) {
          console.log('[live-mod] Removing card for listing', listingId);
          col.remove();
        }
      });

      var detailEl = document.getElementById('listing-detail');
      if (detailEl && detailEl.getAttribute('data-listing-id') === String(listingId)) {
        console.log('[live-mod] Updating detail page for listing', listingId);
        detailEl.innerHTML =
          '<div class="alert alert-warning text-center p-5">' +
          '<i class="bi bi-shield-exclamation" style="font-size:3rem;"></i>' +
          '<h4 class="mt-3">This listing has been removed by moderation.</h4>' +
          '<p>It is no longer available.</p>' +
          '<a href="/listings/" class="btn btn-primary mt-2">Browse Listings</a>' +
          '</div>';
      }
    });

    socket.on('listing_restored', function (data) {
      console.log('[live-mod] listing_restored received:', data);
      var toast = document.createElement('div');
      toast.className = 'alert alert-info alert-dismissible fade show position-fixed bottom-0 end-0 m-3';
      toast.style.zIndex = '9999';
      toast.innerHTML =
        'A listing has been restored by moderation. ' +
        '<a href="javascript:location.reload()" class="alert-link">Refresh</a> to see it.' +
        '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>';
      document.body.appendChild(toast);
    });

    socket.on('new_report', function (r) {
      var tbody = document.querySelector('.table tbody');

      if (!tbody) {
        var emptyMsg = document.querySelector('.text-center.py-5.text-muted');
        if (!emptyMsg) return;
        var wrapper = document.createElement('div');
        wrapper.className = 'table-responsive';
        var table = document.createElement('table');
        table.className = 'table table-hover align-middle';
        table.innerHTML = '<thead class="table-light"><tr>' +
          '<th>#</th><th>Type</th><th>Target</th><th>Reason</th>' +
          '<th>Reporter</th><th>Date</th><th>Status</th><th></th>' +
          '</tr></thead><tbody></tbody></table>';
        wrapper.appendChild(table);
        emptyMsg.parentNode.replaceChild(wrapper, emptyMsg);
        tbody = table.querySelector('tbody');
      }

      var targetUrl = r.target_type === 'listing'
        ? '/listings/' + r.target_id
        : '/user/' + r.target_id;
      var typeBadge = r.target_type === 'listing'
        ? '<span class="badge bg-info text-dark">Listing</span>'
        : '<span class="badge bg-secondary">User</span>';

      var tr = document.createElement('tr');
      tr.innerHTML =
        '<td>' + r.id + '</td>' +
        '<td>' + typeBadge + '</td>' +
        '<td><a href="' + targetUrl + '">' + escHtml(r.target_name) + '</a></td>' +
        '<td>' + escHtml(r.reason) + '</td>' +
        '<td>' + escHtml(r.reporter) + '</td>' +
        '<td>' + r.created_at + '</td>' +
        '<td><span class="badge bg-danger">Open</span></td>' +
        '<td><a href="/moderation/reports/' + r.id + '" class="btn btn-sm btn-outline-primary">View</a></td>';
      tbody.insertBefore(tr, tbody.firstChild);
    });
  }

  function escHtml(s) {
    var d = document.createElement('div');
    d.appendChild(document.createTextNode(s));
    return d.innerHTML;
  }

  window.addEventListener('pageshow', function (e) {
    if (e.persisted) {
      location.reload();
    }
  });

  if (document.readyState === 'complete') {
    setTimeout(connect, 0);
  } else {
    window.addEventListener('load', function () { setTimeout(connect, 0); });
  }
})();
