import { EmptyHive } from "./Icons";

export default function EmptyState({ title, children }) {
  return (
    <div className="empty-state card">
      <EmptyHive />
      <strong>{title}</strong>
      <p className="muted">{children}</p>
    </div>
  );
}
