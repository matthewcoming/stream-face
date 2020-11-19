// replace clientID with your Twitch Client ID
const twitch = require('./twitch-m3u8')('kimne78kx3ncx6brgo4mv6wki5h1ko');

twitch.getURL(process.argv[2], false)
  .then(data => console.log(data))
  .catch(err => console.error(err))
