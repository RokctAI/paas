// project settings, you can change only PROJECT_NAME, BASE_URL and WEBSITE_URL otherwise it can break the app
export const PROJECT_NAME = 'Juvo Platforms';
export const BASE_URL =
  process.env.REACT_APP_BASE_URL || 'https://api.juvo.app';
export const WEBSITE_URL = 'https://web.juvo.app';
export const api_url = BASE_URL + '/api/v1/';
export const api_url_admin = BASE_URL + '/api/v1/dashboard/admin/';
export const api_url_admin_dashboard = BASE_URL + '/api/v1/dashboard/';
export const IMG_URL = '';
export const export_url = BASE_URL + '/storage/';
export const example = BASE_URL + '/';

// map api key, ypu can get it from https://console.cloud.google.com/apis/library
export const MAP_API_KEY = 'AIzaSyDJjLCq6HBCe7xae6l0D9DW1MWpE4900GU';

// firebase keys, do not forget to change to your own keys here and in file public/firebase-messaging-sw.js
export const VAPID_KEY =
  'BB51fvOx-TryBXR0r7K0O_EM4zmXMXsPyjc1jfQsWnjLpJzM2CLgGhpsoWELvZby7hH7oyt1sSGkkb_uvzqEJEM';

export const LAT = -22.34058;
export const LNG = 30.01341;

export const API_KEY = 'AIzaSyBtWjDrQdHtl628ZAQ1naWhPrsiidO18gg';
export const AUTH_DOMAIN = 'juvofood.firebaseapp.com';
export const PROJECT_ID = 'juvofood';
export const STORAGE_BUCKET = 'juvofood.appspot.com';
export const MESSAGING_SENDER_ID = '728921419683';
export const APP_ID = '1:728921419683:web:81a97b726ba3fa120db416';
export const MEASUREMENT_ID = 'G-PKYDE4B9DS';

// recaptcha key, you can get it from https://www.google.com/recaptcha/admin/create
export const RECAPTCHASITEKEY = '6LdDEyMnAAAAAHSvRnfnn_-u83pgjc890GuoNogU';

export const DEMO_SELLER = 334; // seller_id
export const DEMO_SELLER_UUID = '3566bdf6-3a09-4488-8269-70a19f871bd0'; // seller_id
export const DEMO_SHOP = 599; // seller_id
export const DEMO_DELIVERYMAN = 375; // deliveryman_id
export const DEMO_MANEGER = 114; // deliveryman_id
export const DEMO_MODERATOR = 297; // deliveryman_id
export const DEMO_ADMIN = 107; // deliveryman_id

export const SUPPORTED_FORMATS = [
  'image/jpg',
  'image/jpeg',
  'image/png',
  'image/svg+xml',
  'image/svg',
];
