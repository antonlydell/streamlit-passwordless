import { FrontendRenderer } from "@streamlit/component-v2-lib";

import {
  ComponentData,
  FrontendState,
  InstanceState,
  ParentElement,
  TriggerResult,
  Client,
} from "./types";
import { createClient } from "./client";
import { register } from "./register";
import { signIn } from "./sign_in";
import { normalizeError } from "./errors";

const instances: WeakMap<ParentElement, InstanceState> = new WeakMap();

/**
 * Run the appropriate function for the desired authentication action.

 * @param client - The Bitwarden Passwordless frontend client.
 * @param data - The data of the authentication action.
 * @returns - The result of the authentication action.
 */
async function dispatchAction(
  client: Client,
  data: ComponentData,
): Promise<TriggerResult> {
  switch (data.action) {
    case "register":
      return register(client, data.register_token, data.credential_nickname);
    case "sign_in":
      return signIn(
        client,
        data.alias,
        data.with_discoverable,
        data.with_autofill,
      );
  }
}

/**
 * Frontend renderer for the Passwordless Streamlit component.
 *
 * Called by the Streamlit component framework on every render cycle.
 * Responsible for synchronizing the button's visual state with the
 * latest `ComponentData` received from Python, managing the lifecycle
 * of the Bitwarden Passwordless client, and forwarding authentication
 * results back to the Streamlit session state.
 *
 * @remarks
 * **Instance caching** – A per-`parentElement` instance is stored in the
 * module-level `instances` Map so that the Bitwarden client survives
 * re-renders without being recreated. The client is only replaced when
 * `data.public_key` changes, avoiding unnecessary initialization overhead.
 *
 * **Button wiring** – Rather than accumulating event listeners,
 * `button.onclick` is replaced wholesale on every render.  This guarantees
 * exactly one active handler at all times and avoids listener leaks.
 *
 * **Error handling** – If the Bitwarden Passwordless operation throws, the
 * error is normalized and wrapped in a synthetic {@link TriggerResult} with
 * `ok: false`. The trigger is always fired — the Python side therefore
 * receives a result regardless of success or failure and never observes an
 * unhandled rejection.
 *
 * **Busy guard** – A `busy` flag on the instance (mirrored to Streamlit via
 * `setStateValue`) prevents concurrent invocations if the user clicks
 * while an operation is already in flight.
 *
 * @param args - Renderer arguments supplied by the Streamlit component
 *   framework, containing:
 *   - `parentElement` – The root DOM element owned by this component
 *     instance.  Must contain a child `<button class="bwp-button">`.
 *   - `data` – Typed component data from Python, including `public_key`,
 *     `action`, `label`, `button_type`, and `disabled`.
 *   - `setStateValue` – Writes a value to Streamlit component state
 *     (used here to expose the `busy` flag).
 *   - `setTriggerValue` – Fires a one-shot trigger back to Python
 *     (used here to deliver the `result` of the Passkey operation).
 *
 * @returns A cleanup function invoked when the component is unmounted.
 *   Nulls the button's click handler and removes the cached instance to
 *   prevent stale-closure and memory-leak issues.
 *
 * @throws {Error} If no element matching `.bwp-button` is found inside
 *   `parentElement`.  This indicates a template/DOM mismatch and is
 *   considered an unrecoverable programming error.
 */
const PasswordlessComponent: FrontendRenderer<FrontendState, ComponentData> = (
  args,
) => {
  const { parentElement, data, setStateValue, setTriggerValue } = args;

  const button = parentElement.querySelector<HTMLButtonElement>(".bwp-button");
  if (!button) {
    throw new Error("Unexpected: button with class bwp-button not found!");
  }

  let instance = instances.get(parentElement);
  const publicKey = data.public_key;
  const buttonType = data.button_type ?? "secondary";

  if (!instance) {
    instance = {
      publicKey,
      client: createClient(publicKey),
      buttonType,
      busy: false,
    };
  }

  if (instance.publicKey !== publicKey) {
    instance.client = createClient(publicKey);
  }
  instance.publicKey = publicKey;

  const prevButtonType = instance.buttonType;
  if (!button.classList.replace(prevButtonType, buttonType)) {
    button.classList.add(buttonType);
  }
  instance.buttonType = buttonType;

  button.textContent = data.label;

  const disabled = data.disabled ?? false;
  button.disabled = disabled || instance.busy;

  const handleClick: EventListener = async () => {
    if (instance.busy) {
      return;
    }

    instance.busy = true;
    button.disabled = true;
    setStateValue("busy", true);

    try {
      const result = await dispatchAction(instance.client, data);
      setTriggerValue("result", result);
    } catch (error) {
      const fallbackResult: TriggerResult = {
        action: data.action,
        ok: false,
        error: normalizeError(error),
      };
      setTriggerValue("result", fallbackResult);
    } finally {
      instance.busy = false;
      button.disabled = disabled;
      setStateValue("busy", false);
    }
  };

  button.onclick = handleClick;
  instances.set(parentElement, instance);

  return () => {
    // Clean up function that runs when component is dismounted.
    button.onclick = null;
    instances.delete(parentElement);
  };
};

export default PasswordlessComponent;
