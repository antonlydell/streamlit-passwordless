import { Streamlit, RenderData } from "streamlit-component-lib";
import { Client } from '@passwordlessdev/passwordless-client';

// The register/sign_in button
const button = document.body.appendChild(document.createElement("button"));

// Global variables

// common
let passwordlessClient: Client;
let buttonNrClicks: number = 0;

// register
let registerToken: string;
let credentialNickname: string;

// sign_in
let alias: string;
let withDiscoverable: boolean;
let withAutofill: boolean;


/**
 * Initialize an instance of the Bitwarden Passwordless frontend client.
 *
 * @param {string} apiKey - The public key of the Bitwarden Passwordless application.
 *
 * @returns {Client} - The Bitwarden Passwordless frontend client.
 */
function createPasswordlessClient(apiKey: string): Client {

  if (passwordlessClient === undefined) {
    passwordlessClient = new Client({apiKey: apiKey});
    console.log('Initialized client', passwordlessClient)
    return passwordlessClient
  }

  return passwordlessClient
}

/**
 * Register a new user by creating and registring a passkey with the user's device.
 *
 * @param {Client} client - The Bitwarden Passwordless frontend client.
 * @param {string} registerToken - The register token retrieved from the Bitwarden Passwordless backend.
 * @param {string} credentialNickname - A nickname for the passkey credential being created.
 *
 * @returns {[string, object]} - [The public key of the created passkey, An object with error info.]
 */
async function register(client: Client, registerToken: string, credentialNickname: string) {

  console.log('register device', credentialNickname);
  const {token, error} = await client.register(registerToken, credentialNickname);
  return [token, error]
}

/**
 * Start the sign in process.
 *
 * @param {Client} client - The Bitwarden Passwordless frontend client.
 * @param {string} alias - The alias of the user to sign in.
 * @param {boolean} withDiscoverable - If True the browser's native UI prompt will be used to select the
 *                                     passkey to use for signing in.
 * @param {boolean} withAutofill - If True the browser's native autofill UI will be used to select the passkey to use for signing in.
 *                                 This sign in method is overridden if `alias` is specified or `with_discoverable` is True.

 * @returns {[string, object]} - [The sign in verification token, An object with error info.]
 */
async function sign_in(client: Client, alias: string, withDiscoverable: boolean, withAutofill: boolean) {

  if (alias){
    console.log('signinWithAlias');
    const {token, error} = await client.signinWithAlias(alias);
    return [token, error]
  }
  else if (withDiscoverable === true){
    console.log('signinWithDiscoverable');
    const {token, error} = await client.signinWithDiscoverable();
    return [token, error]
  }
  else if (withAutofill === true){
    console.log('signinWithAutofill');
    const {token, error} = await client.signinWithAutofill();
    return [token, error]
  }
  else {
  console.log('No valid combination of sign in methods')
   const token = undefined;
   const error = {
    'type': 'streamlit-passwordless-sign-in-error',
    'title': 'No valid combination of sign in methods',
    'errorCode': 'STP-110',
    'status': 400,
    'detail': `alias=${alias}, withDiscoverable=${withDiscoverable}, withAutofill=${withAutofill}`,
    'from': 'client',
  };
    return [token, error]
  };

}

/**
 * The callback function to be triggered when the register button is clicked.
 */
function registerOnClick () {

  buttonNrClicks += 1;
  register(passwordlessClient, registerToken, credentialNickname).then(
    ([token, error])=>{
      Streamlit.setComponentValue([token, error, buttonNrClicks]);
    }
  ).catch(
    (error)=>{
      console.log('Error registring passkey credential', error);
      Streamlit.setComponentValue([undefined, error, buttonNrClicks]);
    }
  )
}

/**
 * The callback function to be triggered when the sign_in button is clicked.
 */
function signInOnClick() {

  buttonNrClicks += 1;
  sign_in(passwordlessClient, alias, withDiscoverable, withAutofill).then(
    ([token, error])=>{
      Streamlit.setComponentValue([token, error, buttonNrClicks]);
    }
  ).catch(
    (error)=>{
      console.log('Error signing in', error);
      Streamlit.setComponentValue([undefined, error, buttonNrClicks]);
    }
  )
}

/**
 * The render function that gets called every time the Streamlit Python component gets called.
 *
 * @param {Event} event - The input parameters from the Streamlit Python application.
 */
function onRender(event: Event): void {
  // Get the RenderData from the event
  const data = (event as CustomEvent<RenderData>).detail;

  const apiKey: string = data.args['public_key'];
  const action: string = data.args['action'];
  const disabled: boolean = data.args['disabled'];
  const button_type: string = data.args['button_type'];
  const button_label: string = data.args['label'];

  createPasswordlessClient(apiKey);
  console.log('passwordlessClient', passwordlessClient);
  console.log('isSecureContext', window.isSecureContext);

  button.disabled = disabled;
  button.className = button_type === 'primary' ? 'primary' : 'secondary';
  button.textContent = button_label;

  switch (action) {
    case 'register':
      console.log('register');
      registerToken = data.args['register_token'];
      credentialNickname = data.args['credential_nickname'];

      button.onclick = registerOnClick;
      console.log('button', button)

      break;
    case 'sign_in':
      console.log('sign_in');
      alias = data.args['alias'];
      withDiscoverable = data.args['with_discoverable'];
      withAutofill = data.args['with_autofill'];

      button.onclick = signInOnClick;
      console.log('button', button);

      break;
      default:
        const error = {
         'type': 'streamlit-passwordless-invalid-action-error',
         'title': 'Invalid action',
         'errorCode': 'STP-100',
         'status': 400,
         'detail': `action=${action} is invalid. Valid options are : register, sign_in`,
         'from': 'client',
       };
        console.log('Error : Invalid action', error);
        Streamlit.setComponentValue([undefined, error, -1]);
  }

  // We tell Streamlit to update our frameHeight after each render event, in
  // case it has changed. (This isn't strictly necessary for the example
  // because our height stays fixed, but this is a low-cost function, so
  // there's no harm in doing it redundantly.)
  Streamlit.setFrameHeight();
}

// Attach our `onRender` handler to Streamlit's render event.
Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender);

// Tell Streamlit we're ready to start receiving data.
// We won't get our first RENDER_EVENT until we call this function.
Streamlit.setComponentReady();

// Finally, tell Streamlit to update our initial height. We omit the
// `height` parameter here to have it default to our scrollHeight.
Streamlit.setFrameHeight();
