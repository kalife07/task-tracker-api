import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useState } from "react";

import TagInput from "./TagInput";

function TagInputHarness({ initialTags = [] }) {
  const [tags, setTags] = useState(initialTags);
  return <TagInput tags={tags} onChange={setTags} />;
}

function getTagChips() {
  return Array.from(document.querySelectorAll(".tag-chip"));
}

async function addTag(user, tagName) {
  const input = screen.getByRole("textbox");
  await user.click(input);
  await user.clear(input);
  await user.type(input, tagName);
  await user.keyboard("{Enter}");
}

describe("TagInput", () => {
  test("creates a tag chip when the user types a value and presses Enter", async () => {
    const user = userEvent.setup();
    render(<TagInputHarness />);

    await addTag(user, "frontend");

    expect(screen.getByText("frontend")).toBeInTheDocument();
    expect(getTagChips()).toHaveLength(1);
  });

  test("prevents duplicate tags from being added", async () => {
    const user = userEvent.setup();
    render(<TagInputHarness />);

    await addTag(user, "bug");
    await addTag(user, "bug");

    expect(getTagChips()).toHaveLength(1);
    expect(screen.getAllByText("bug")).toHaveLength(1);
  });

  test("shows a validation error and rejects the 11th tag", async () => {
    const user = userEvent.setup();
    render(<TagInputHarness />);

    for (let index = 1; index <= 11; index += 1) {
      await addTag(user, `tag-${index}`);
    }

    expect(getTagChips()).toHaveLength(10);
    expect(screen.getByRole("alert")).toHaveTextContent(
      "You can add at most 10 tags."
    );
    expect(screen.queryByText("tag-11")).not.toBeInTheDocument();
  });
});
