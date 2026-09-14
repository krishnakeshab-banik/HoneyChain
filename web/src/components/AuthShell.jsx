import { useState } from "react";
import { BeeDoodle, Sprig } from "./Decor";

export default function AuthShell({ kicker, title, lead, children }) {
  return (
    <div className="auth-shell">
      <aside className="auth-panel">
        <Sprig className="auth-sprig" />
        <p className="brand">HONEYCHAIN</p>
        <h2>From hive to trusted jar</h2>
        <p>Sensors, a lab check, and a hash-chain — so a buyer can believe the label.</p>
        <BeeDoodle className="auth-bee" />
      </aside>
      <div className="auth-form">
        <p className="page-kicker">{kicker}</p>
        <h1>{title}</h1>
        <p className="purpose">{lead}</p>
        {children}
      </div>
    </div>
  );
}

export function FieldError({ message }) {
  if (!message) {
    return null;
  }
  return <p className="field-error">{message}</p>;
}

export function PasswordField({ id, value, onChange, label, autoComplete = "current-password" }) {
  const [show, setShow] = useState(false);
  return (
    <div>
      <label htmlFor={id}>{label}</label>
      <div className="password-wrap">
        <input id={id} type={show ? "text" : "password"} value={value} onChange={onChange} autoComplete={autoComplete} />
        <button type="button" className="ghost" onClick={() => setShow((v) => !v)}>
          {show ? "Hide" : "Show"}
        </button>
      </div>
    </div>
  );
}
