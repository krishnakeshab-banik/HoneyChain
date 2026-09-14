import { Link } from "react-router-dom";
import { useAuth } from "../auth";
import { ROLE_HOME } from "../navConfig";
import { PrimaryButton, SectionHeading } from "../components/Ui";

export default function Forbidden() {
  const { role } = useAuth();
  return (
    <div>
      <SectionHeading
        kicker="403"
        title="You don't have access to this page."
        purpose="You are signed in, but this route belongs to another role. The sidebar only lists what you can use."
      />
      <Link to={ROLE_HOME[role] || "/"}>
        <PrimaryButton>Go to my dashboard</PrimaryButton>
      </Link>
    </div>
  );
}
