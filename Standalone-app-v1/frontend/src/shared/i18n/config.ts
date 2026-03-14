import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import HttpBackend from 'i18next-http-backend';

i18n
  .use(HttpBackend)
  .use(initReactI18next)
  .init({
    fallbackLng: 'it',
    lng: 'it', // Force Italian as default initially
    ns: ['common'],
    defaultNS: 'common',
    interpolation: {
      escapeValue: false, // React safe from XSS
    },
    backend: {
      loadPath: '/locales/{{lng}}/{{ns}}.json',
    },
  });

export default i18n;