// iOS Safari does not fire :active on <a> taps without a touch listener present.
document.querySelectorAll('.btn').forEach(function (btn) {
  btn.addEventListener('touchstart', function () {}, { passive: true });
});
