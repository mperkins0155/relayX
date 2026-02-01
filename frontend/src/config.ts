export const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? '' // Use relative URLs to go through nginx proxy
    : 'https://api.relayx.tech';
