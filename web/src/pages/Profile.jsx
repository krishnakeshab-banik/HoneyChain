import { useAuth } from "../auth";
import { SectionHeading } from "../components/Ui";

export default function Profile() {
  const { user } = useAuth();
  return (
    <div>
      <SectionHeading
        kicker="PROFILE"
        title={user?.display_name}
        purpose="This is the account you signed in with. Language and logout live in the top bar."
      />
      <div className="card">
        <p>
          <strong>Username:</strong> {user?.username}
        </p>
        <p>
          <strong>Role:</strong> {user?.role}
        </p>
        {user?.beekeeper_id && (
          <p>
            <strong>Beekeeper ID:</strong> {user.beekeeper_id}
          </p>
        )}
        {user?.cluster && (
          <p>
            <strong>Cluster:</strong> {user.cluster}
          </p>
        )}
        {user?.region && (
          <p>
            <strong>Region:</strong> {user.region}
          </p>
        )}
      </div>
    </div>
  );
}
