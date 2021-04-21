// replace clientID with your Twitch Client ID
const twitch = require('twitch-m3u8');

twitch.getStream(process.argv[2], false)
  .then(data => console.log(data[0].url))
  .catch(err => console.error(err))
