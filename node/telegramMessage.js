const fetch = require('isomorphic-fetch');
const querystring = require('querystring');

/**
 * Send a message from a Telegram bot to group chat.
 *
 * Create a telegram group chat and bot first (https://core.telegram.org/bots).
 *
 * @param {string} botToken - The bot's token, e.g. 19234689:ASD23mkSDDFDsd-as34da_j4j334n.
 * @param {string} chatId - ID of the group chat, e.g. -15668993.
 * @param {string} text - Plain text message to send, e.g. 'Hello, you suck.'.
 */

async function sendTelegramMessage(botToken, chatId, text) {
  try {
    const data = {
      chat_id: chatId,
      text: `[node example app]: ${text}`,
    };
    const query = querystring.encode(data);
    const result = await fetch(`https://api.telegram.org/bot${botToken}/sendMessage?${query}`);
    if (result.status === 200) {
      console.log(`Sent telegram message: ${text}`);
    } else {
      throw new Error(`Unexpected response from Telegram ${result.status}`);
    }
  } catch (e) {
    console.error('Error sending message: ', e);
  }
}

module.exports = sendTelegramMessage;
