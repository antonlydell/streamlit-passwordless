import { Streamlit, RenderData } from "streamlit-component-lib";
import { Client } from '@passwordlessdev/passwordless-client';

let passwordlessClient: Client;
let clientInitialized: boolean = false;
let previousToken: string = '';

/**
 * Initialize an instance of the Bitwarden Passwordless frontend client.
 *
 * @param {string} apiKey - The public key of the Bitwarden Passwordless application.
 *
 * @returns {Client} - The Bitwarden Passwordless frontend client.
 */
function createPasswordlessClient(apiKey: string): Client {

  if (clientInitialized === false) {
    passwordlessClient = new Client({apiKey: apiKey});
    clientInitialized = true

    return passwordlessClient
  } else {
    return passwordlessClient
  }

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

  const client = createPasswordlessClient(apiKey)
  const {token, error} = client.register(registerToken, credentialNickname)

  if (previousToken !== registerToken) {
    previousToken = registerToken;
    Streamlit.setComponentValue([token, error]);
  }

}

// Attach our `onRender` handler to Streamlit's render event.
Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender);

// Tell Streamlit we're ready to start receiving data.
// We won't get our first RENDER_EVENT until we call this function.
Streamlit.setComponentReady();
