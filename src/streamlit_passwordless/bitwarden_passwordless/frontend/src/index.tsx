import { Streamlit, RenderData } from "streamlit-component-lib"

let previousOutput = ''

function onRender(event: Event): void {
  // Get the RenderData from the event
  const data = (event as CustomEvent<RenderData>).detail;
  const registerToken = data.args['token'];

  if (previousOutput !== registerToken) {
    previousOutput = registerToken;
    Streamlit.setComponentValue([registerToken, true]);
  }

}

// Attach our `onRender` handler to Streamlit's render event.
Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender);

// Tell Streamlit we're ready to start receiving data.
// We won't get our first RENDER_EVENT until we call this function.
Streamlit.setComponentReady();
