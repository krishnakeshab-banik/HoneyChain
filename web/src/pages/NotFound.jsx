import { Link } from "react-router-dom";
import { PrimaryButton, SectionHeading } from "../components/Ui";

export default function NotFound() {
  return (
    <div>
      <SectionHeading kicker="404" title="This page is not on HoneyChain." purpose="The address does not match a public page or a role dashboard." />
      <Link to="/">
        <PrimaryButton>Back to home</PrimaryButton>
      </Link>
    </div>
  );
}
