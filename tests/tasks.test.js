const request = require("supertest");

const BASE_URL = global.__TEST_BASE_URL__ || "http://127.0.0.1:8765";

async function resetTasks() {
  const response = await request(BASE_URL).post("/test/reset");
  expect(response.status).toBe(204);
}

function findValidationError(body, fieldName) {
  return body.detail.find(
    (entry) => Array.isArray(entry.loc) && entry.loc.includes(fieldName)
  );
}

async function createTask(payload) {
  const response = await request(BASE_URL).post("/tasks").send(payload);
  return response;
}

async function markTaskDone(taskId) {
  const inProgressResponse = await request(BASE_URL)
    .patch(`/tasks/${taskId}`)
    .send({ status: "InProgress" });
  expect(inProgressResponse.status).toBe(200);

  const doneResponse = await request(BASE_URL)
    .patch(`/tasks/${taskId}`)
    .send({ status: "Done" });
  expect(doneResponse.status).toBe(200);

  return doneResponse.body;
}

describe("Task Tracker API - Due Dates and Tags", () => {
  beforeEach(async () => {
    await resetTasks();
  });

  afterEach(async () => {
    await resetTasks();
  });

  describe("Due Dates Feature", () => {
    test("POST /tasks creates a task with a valid due_date", async () => {
      const response = await createTask({
        title: "Ship release",
        due_date: "2026-04-15",
      });

      expect([200, 201]).toContain(response.status);
      expect(response.body.due_date).toBe("2026-04-15");
      expect(response.body.title).toBe("Ship release");
    });

    test("PATCH /tasks/:id updates an existing task due_date", async () => {
      const created = await createTask({
        title: "Initial due date",
        due_date: "2026-04-15",
      });
      expect(created.status).toBe(201);

      const response = await request(BASE_URL)
        .patch(`/tasks/${created.body.id}`)
        .send({ due_date: "2026-08-20" });

      expect(response.status).toBe(200);
      expect(response.body.due_date).toBe("2026-08-20");
      expect(response.body.id).toBe(created.body.id);
    });

    test("GET /tasks?overdue=true returns only overdue incomplete tasks", async () => {
      const overdueIncomplete = await createTask({
        title: "Overdue and still open",
        due_date: "2026-01-10",
        status: "ToDo",
      });
      expect(overdueIncomplete.status).toBe(201);

      const futureTask = await createTask({
        title: "Future deadline",
        due_date: "2026-12-31",
        status: "ToDo",
      });
      expect(futureTask.status).toBe(201);

      const overdueDoneSeed = await createTask({
        title: "Overdue but finished",
        due_date: "2026-02-01",
        status: "ToDo",
      });
      expect(overdueDoneSeed.status).toBe(201);
      await markTaskDone(overdueDoneSeed.body.id);

      const response = await request(BASE_URL).get("/tasks").query({ overdue: true });

      expect(response.status).toBe(200);
      expect(response.body).toHaveLength(1);
      expect(response.body[0].id).toBe(overdueIncomplete.body.id);
      expect(response.body[0].title).toBe("Overdue and still open");
      expect(response.body[0].status).not.toBe("Done");
      expect(response.body[0].is_overdue).toBe(true);
    });

    test("POST /tasks rejects malformed due_date with 422 field error", async () => {
      const response = await createTask({
        title: "Bad date task",
        due_date: "invalid-date-format",
      });

      expect(response.status).toBe(422);

      const dueDateError = findValidationError(response.body, "due_date");
      expect(dueDateError).toBeDefined();
      expect(dueDateError.msg).toMatch(
        /due_date must be a valid ISO-8601 date string/i
      );
    });
  });

  describe("Tags Feature", () => {
    test("POST /tasks accepts tags, normalizes them, and returns trimmed values", async () => {
      const response = await createTask({
        title: "Tagged task",
        tags: [" frontend ", " bug "],
      });

      expect([200, 201]).toContain(response.status);
      expect(response.body.tags).toEqual(["frontend", "bug"]);
    });

    test("GET /tasks?tag=bug returns only tasks containing the bug tag", async () => {
      const bugTask = await createTask({
        title: "Fix login bug",
        tags: ["frontend", "bug"],
      });
      expect(bugTask.status).toBe(201);

      const otherTask = await createTask({
        title: "Write docs",
        tags: ["frontend", "docs"],
      });
      expect(otherTask.status).toBe(201);

      const response = await request(BASE_URL).get("/tasks").query({ tag: "bug" });

      expect(response.status).toBe(200);
      expect(response.body).toHaveLength(1);
      expect(response.body[0].id).toBe(bugTask.body.id);
      expect(response.body[0].tags).toContain("bug");
    });

    test("POST /tasks rejects more than 10 tags with 422 tag limit error", async () => {
      const tooManyTags = Array.from({ length: 11 }, (_, index) => `tag-${index + 1}`);

      const response = await createTask({
        title: "Too many tags",
        tags: tooManyTags,
      });

      expect(response.status).toBe(422);

      const tagsError = findValidationError(response.body, "tags");
      expect(tagsError).toBeDefined();
      expect(tagsError.msg).toMatch(/tags must contain at most 10 items/i);
    });
  });
});
