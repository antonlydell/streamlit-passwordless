import { StreamlitPasswordlessError } from "./types";

/**
 * Converts an unexpected catch-block error into a StreamlitPasswordlessError
 * for serialization to the Python side.
 *
 * Only use this in catch blocks for errors that are not already a
 * StreamlitPasswordlessError or ProblemDetails — those are returned
 * directly from the normal flow and never thrown.
 *
 * @param error - The unknown value from a catch block.
 * @returns A StreamlitPasswordlessError with status 500.
 */
export function normalizeError(error: unknown): StreamlitPasswordlessError {
  const message = error instanceof Error ? error.message : String(error);
  return {
    type: "stp-unexpected-error",
    title: message,
    errorCode: "STP-000",
    status: 500,
    from: "client",
  };
}
