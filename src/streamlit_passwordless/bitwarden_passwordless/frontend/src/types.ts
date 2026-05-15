import { FrontendRendererArgs } from "@streamlit/component-v2-lib";
import { Client } from "@passwordlessdev/passwordless-client";
export { Client };

export type Action = "register" | "sign_in" | "step_up";

export type TriggerResult = {
  action: Action;
  ok: boolean;
  token?: string;
  error?: unknown;
};

export type FrontendState = {
  busy: boolean;
  result?: TriggerResult;
};

export type ButtonType = "primary" | "secondary" | "tertiary";

export type BaseData = {
  action: Action;
  public_key: string;
  label: string;
  disabled?: boolean;
  button_type?: "primary" | "secondary" | "tertiary";
};

export type StreamlitPasswordlessError = {
  type: string;
  title: string;
  status: number;
  errorCode: string;
  traceId?: string;
  from: string;
};

export type RegisterData = BaseData & {
  action: "register";
  register_token: string;
  credential_nickname?: string;
};

export type SignInData = BaseData & {
  action: "sign_in";
  alias?: string;
  with_discoverable?: boolean;
  with_autofill?: boolean;
};

export type ComponentData = RegisterData | SignInData;

export type InstanceState = {
  publicKey: string;
  client: Client;
  busy: boolean;
  buttonType: ButtonType;
};

export type ParentElement = FrontendRendererArgs["parentElement"];
