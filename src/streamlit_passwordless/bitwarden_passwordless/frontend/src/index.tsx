import { Streamlit, RenderData } from "streamlit-component-lib";
import { Client } from '@passwordlessdev/passwordless-client';

let passwordlessClient: Client | undefined;

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
    console.log('signinWithAlias')
    const {token, error} = await client.signinWithAlias(alias);
    return [token, error]
  }
  else if (withDiscoverable === true){
    console.log('signinWithDiscoverable')
    const {token, error} = await client.signinWithDiscoverable();
    return [token, error]
  }
  else if (withAutofill === true){
    console.log('signinWithAutofill')
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
  }
    return [token, error]
  };

}

/**
 * The render function that gets called every time the Streamlit Python component gets called.
 *
 * @param {Event} event - The input parameters from the Streamlit Python application.
 */
function onRender(event: Event): void {
  // Get the RenderData from the event
  const data = (event as CustomEvent<RenderData>).detail;
  const action: string = data.args['action'];
  const apiKey: string = data.args['public_key'];

  const client = createPasswordlessClient(apiKey);
  console.log('isSecureContext', window.isSecureContext);

  switch (action) {
    case 'register':
      const registerToken: string = data.args['register_token'];
      const credentialNickname: string = data.args['credential_nickname'];

      register(client, registerToken, credentialNickname).then(
        ([token, error])=>{
          Streamlit.setComponentValue([token, error]);
        }
      ).catch(
        (error)=>{
          console.log('Error registring passkey credential', error)
          Streamlit.setComponentValue([undefined, error]);
        }
      )
      break;
    case 'sign_in':
      const alias: string = data.args['alias'];
      const withDiscoverable: boolean = data.args['with_discoverable'];
      const withAutofill: boolean = data.args['with_autofill'];

      sign_in(client, alias, withDiscoverable, withAutofill).then(
        ([token, error])=>{
          Streamlit.setComponentValue([token, error]);
        }
      ).catch(
        (error)=>{
          console.log('Error signing in', error)
          Streamlit.setComponentValue([undefined, error]);
        }
      )
      break;
      default:
        const error = {
         'type': 'streamlit-passwordless-invalid-action-error',
         'title': 'Invalid action',
         'errorCode': 'STP-100',
         'status': 400,
         'detail': `action=${action} is invalid. Valid options are : register, sign_in`,
         'from': 'client',
       }
        console.log('Error : Invalid action', error)
        Streamlit.setComponentValue([undefined, error]);
  }

}

// Attach our `onRender` handler to Streamlit's render event.
Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender);

// Tell Streamlit we're ready to start receiving data.
// We won't get our first RENDER_EVENT until we call this function.
Streamlit.setComponentReady();
