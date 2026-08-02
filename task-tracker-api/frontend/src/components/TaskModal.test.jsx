import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import TaskModal from "./TaskModal";

describe("TaskModal", () => {
  test("renders TagInput inside the open modal", async () => {
    const user = userEvent.setup();
    const onClose = jest.fn();
    const onSave = jest.fn().mockResolvedValue(undefined);

    render(
      <TaskModal
        isOpen
        mode="create"
        onClose={onClose}
        onSave={onSave}
      />
    );

    expect(screen.getByRole("dialog")).toBeInTheDocument();
    expect(screen.getByText("Tags")).toBeInTheDocument();

    const tagInput = screen.getByPlaceholderText(/type a tag and press enter/i);
    await user.type(tagInput, "frontend");
    await user.keyboard("{Enter}");

    expect(screen.getByText("frontend")).toBeInTheDocument();
  });
});
