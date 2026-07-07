import { TriggerResult } from "./types";
import { StreamlitPasswordlessError, Client } from "./types";
import { normalizeError } from "./errors";

/**
 * Creates a {@link StreamlitPasswordlessError} when the register token is missing.
 *
 * @returns A {@link StreamlitPasswordlessError} with errorCode `STP-100`
 *   and HTTP status `400`.
 */
function missingRegisterTokenError(): StreamlitPasswordlessError {
  return {
    type: "stp-register-error",
    title: "register_token is required for action=register",
    errorCode: "STP-100",
    status: 400,
    from: "client",
  };
}

/**
 * Register a new user by creating and registring a passkey with the user's device.
 *
 * @param client - The Bitwarden Passwordless frontend client.
 * @param registerToken - The register token retrieved from the Bitwarden Passwordless backend.
 * @param credentialNickname - A nickname for the passkey credential being created.
 * @returns The result of the register process. On success, `ok` is `true` and
 *   `token` contains the verification token to validate on the Python side.
 *   On failure, `ok` is `false` and `error` contains the error details.
 */
export async function register(
  client: Client,
  registerToken: string,
  credentialNickname: string | undefined,
): Promise<TriggerResult> {
  if (!registerToken) {
    return {
      action: "register",
      ok: false,
      error: missingRegisterTokenError(),
    };
  }

  try {
    const { token, error } = await client.register(
      registerToken,
      credentialNickname,
    );

    if (error) {
      return {
        action: "register",
        ok: false,
        token,
        error,
      };
    }

    return {
      action: "register",
      ok: true,
      token,
    };
  } catch (error) {
    return {
      action: "register",
      ok: false,
      error: normalizeError(error),
    };
  }
}
