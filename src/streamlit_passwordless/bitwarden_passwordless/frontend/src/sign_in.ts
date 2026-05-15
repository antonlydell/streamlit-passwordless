import { Client } from "./types";
import { TriggerResult, Action, StreamlitPasswordlessError } from "./types";
import { normalizeError } from "./errors";
import { ProblemDetails } from "@passwordlessdev/passwordless-client";

/**
 * Creates a {@link StreamlitPasswordlessError} for an invalid combination
 * of sign-in parameters supplied to the sign-in action.
 *
 * All parameter values are embedded in the error title so the Python side
 * can log or display the exact combination that triggered the error.
 *
 * @param alias - The username or alias provided for alias-based sign-in,
 *   or `undefined` if not supplied.
 * @param withDiscoverable - Whether discoverable-credential sign-in was
 *   requested, or `undefined` if not supplied.
 * @param withAutofill - Whether autofill-based sign-in was requested,
 *   or `undefined` if not supplied.
 * @param action - The action being performed when the invalid combination
 *   was detected.
 * @returns A {@link StreamlitPasswordlessError} with errorCode `STP-110`
 *   and HTTP status `400`.
 */
function invalidSignInCombinationError(
  alias: string | undefined,
  withDiscoverable: boolean | undefined,
  withAutofill: boolean | undefined,
  action: Action,
): StreamlitPasswordlessError {
  return {
    type: "stp-invalid-sign-in-combination-error",
    title: `action=${action}, alias=${alias}, withDiscoverable=${withDiscoverable}, withAutofill=${withAutofill}`,
    errorCode: "STP-110",
    status: 400,
    from: "client",
  };
}

/**
 * Signs in a user with a passkey using one of three methods, evaluated in
 * priority order:
 *
 * 1. **Alias** — signs in directly with the user's alias.
 * 2. **Discoverable** — prompts the browser's native passkey selection UI.
 * 3. **Autofill** — activates the browser's autofill UI for passkey selection.
 *
 * If none of the parameters resolve to a truthy value a
 * {@link StreamlitPasswordlessError} with errorCode `STP-110` is returned.
 * Unexpected errors are caught and returned as a {@link StreamlitPasswordlessError}
 * with errorCode `STP-000` rather than thrown.
 *
 * @param client - The Bitwarden Passwordless frontend client.
 * @param alias - The alias of the user to sign in with. Takes priority over
 *   `withDiscoverable` and `withAutofill` when truthy.
 * @param withDiscoverable - If `true`, prompts the browser's native passkey
 *   selection UI. Takes priority over `withAutofill` when truthy.
 * @param withAutofill - If `true`, activates the browser's autofill UI for
 *   passkey selection. Only used when both `alias` and `withDiscoverable`
 *   are falsy.
 * @returns The result of the sign-in attempt. On success, `ok` is `true` and
 *   `token` contains the verification token to validate on the Python side.
 *   On failure, `ok` is `false` and `error` contains the error details.
 */
export async function signIn(
  client: Client,
  alias: string | undefined,
  withDiscoverable: boolean | undefined,
  withAutofill: boolean | undefined,
): Promise<TriggerResult> {
  try {
    let token: string | undefined;
    let error: ProblemDetails | undefined;

    if (alias) {
      ({ token, error } = await client.signinWithAlias(alias));
    } else if (withDiscoverable) {
      ({ token, error } = await client.signinWithDiscoverable());
    } else if (withAutofill) {
      ({ token, error } = await client.signinWithAutofill());
    } else {
      return {
        action: "sign_in",
        ok: false,
        error: invalidSignInCombinationError(
          alias,
          withDiscoverable,
          withAutofill,
          "sign_in",
        ),
      };
    }

    if (error) {
      return { action: "sign_in", ok: false, error };
    }
    return { action: "sign_in", ok: true, token };
  } catch (error) {
    return {
      action: "sign_in",
      ok: false,
      error: normalizeError(error),
    };
  }
}
