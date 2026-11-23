(function () {
  var stage = document.getElementById('stage');
  if (!stage) return;
  var thumbs = Array.prototype.slice.call(document.querySelectorAll('.thumb'));
  thumbs.forEach(function (btn) {
    btn.addEventListener('click', function () {
      var src = btn.getAttribute('data-src');
      if (!src || stage.getAttribute('src') === src) return;
      stage.classList.add('is-fading');
      var next = new Image();
      next.onload = function () {
        stage.setAttribute('src', src);
        stage.classList.remove('is-fading');
      };
      next.src = src;
      thumbs.forEach(function (b) { b.setAttribute('aria-current', 'false'); });
      btn.setAttribute('aria-current', 'true');
    });
  });
})();
