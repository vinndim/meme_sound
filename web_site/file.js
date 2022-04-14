if (window.location.hash != '') {
  var hash = window.location.hash.substring(1);
  var accessToken = hash.substr(hash.indexOf('access_token=')).split('&')[0].split('=')[1];
  sessionStorage.setItem('access_token', accessToken);
  // для безопасности, из url лучше удалить access_token
  window.location.hash = '';
  // window.location.href = window.location.href.substr(0, window.location.href.indexOf('#'))
}

// и далее использовать сохраненный маркер доступа
var token = /access_token=([^&]+)/.exec(document.location.hash)[1];
console.log(currentAccessToken)