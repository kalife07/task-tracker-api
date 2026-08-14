import { render, screen } from "@testing-library/react";

import TaskCard from "./TaskCard";

const noop = () => {};

const baseTask = {
  id: "task-1",
  title: "Release checklist",
  description: "Prepare the launch tasks",
  priority: "Medium",
  status: "ToDo",
  assignee: null,
  tags: [],
};

describe("TaskCard", () => {
  test('formats due_date as "Due Apr 15, 2026"', () => {
    render(
      <TaskCard
        task={{ ...baseTask, due_date: "2026-04-15" }}
        onEdit={noop}
        onDragStart={noop}
        onDragEnd={noop}
      />
    );

    expect(screen.getByText("Due Apr 15, 2026")).toBeInTheDocument();
  });
});
