/* @TODO replace with your variables
 * ensure all variables on this page match your project
 */

// export const environment = {
//   production: false,
//   apiServerUrl: 'http://127.0.0.1:5000', // the running FLASK api server url
//   auth0: {
//     url: 'dev-cmc6p5k8.us', // the auth0 domain prefix
//     audience: 'coffeeshop', // the audience set for the auth0 app
//     clientId: 'POF9CZEDjhbGZPP6A64iKGErASZ1yyiU', // the client id generated for the auth0 app
//     callbackURL: 'http://127.0.0.1:8100/drinks', // the base url of the running ionic application. 
//   }
// };
export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:5000', // the running FLASK api server url
  auth0: {
    url: 'dev-cmc6p5k8.us', // the auth0 domain prefix
    audience: 'myapp', // the audience set for the auth0 app
    clientId: '8fi1YdvuKVJqNt1poUUYBbBlqOrRTygm', // the client id generated for the auth0 app
    callbackURL: 'http://127.0.0.1:8100', // the base url of the running ionic application. 
  }
};
