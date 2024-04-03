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
 * The render function that gets called every time the Streamlit Python component gets called.
 *
 * @param {Event} event - The input parameters from the Streamlit Python application.
 */
function onRender(event: Event): void {
  // Get the RenderData from the event
  const data = (event as CustomEvent<RenderData>).detail;
  const apiKey: string = data.args['public_key'];
  const registerToken: string = data.args['register_token'];
  const credentialNickname: string = data.args['credential_nickname'];

  const client = createPasswordlessClient(apiKey);
  console.log('isSecureContext', window.isSecureContext);

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

}

// Attach our `onRender` handler to Streamlit's render event.
Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender);

// Tell Streamlit we're ready to start receiving data.
// We won't get our first RENDER_EVENT until we call this function.
Streamlit.setComponentReady();
