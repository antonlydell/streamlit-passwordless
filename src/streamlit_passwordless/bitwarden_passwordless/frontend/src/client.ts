import { Client } from "./types";

/**
 * Create a new instance of the Bitwarden Passwordless client.
 *
 * @param publicKey - The public key of the Bitwarden Passwordless instance.
 */
export function createClient(publicKey: string): Client {
  return new Client({ apiKey: publicKey });
}
