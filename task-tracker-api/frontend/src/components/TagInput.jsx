import { useState } from "react";

const MAX_TAGS = 10;
const MAX_TAG_LENGTH = 30;

export default function TagInput({ tags, onChange, disabled = false }) {
  const [inputValue, setInputValue] = useState("");
  const [limitMessage, setLimitMessage] = useState("");

  function normalizeTag(rawTag) {
    return rawTag.trim().slice(0, MAX_TAG_LENGTH);
  }

  function tagExists(nextTag) {
    const normalized = nextTag.toLowerCase();
    return tags.some((tag) => tag.toLowerCase() === normalized);
  }

  function addTag(rawTag) {
    const trimmed = normalizeTag(rawTag);
    if (!trimmed) {
      return;
    }

    if (tags.length >= MAX_TAGS) {
      setLimitMessage(`You can add at most ${MAX_TAGS} tags.`);
      return;
    }

    if (tagExists(trimmed)) {
      setInputValue("");
      setLimitMessage("");
      return;
    }

    setLimitMessage("");
    onChange([...tags, trimmed]);
    setInputValue("");
  }

  function removeTag(index) {
    setLimitMessage("");
    onChange(tags.filter((_, tagIndex) => tagIndex !== index));
  }

  function handleKeyDown(event) {
    if (event.key === "Enter" || event.key === ",") {
      event.preventDefault();
      addTag(inputValue);
    } else if (event.key === "Backspace" && !inputValue && tags.length > 0) {
      removeTag(tags.length - 1);
    }
  }

  function handleBlur() {
    if (inputValue.trim()) {
      addTag(inputValue);
    }
  }

  return (
    <div className="tag-input-field">
      <div className={`tag-input${disabled ? " tag-input-disabled" : ""}`}>
        {tags.map((tag, index) => (
          <span className="tag-chip" key={`${tag}-${index}`}>
            <span>{tag}</span>
            <button
              type="button"
              className="tag-chip-remove"
              aria-label={`Remove tag ${tag}`}
              onClick={() => removeTag(index)}
              disabled={disabled}
            >
              ×
            </button>
          </span>
        ))}
        <input
          type="text"
          className="tag-input-text"
          value={inputValue}
          placeholder={tags.length === 0 ? "Type a tag and press Enter" : "Add another tag"}
          onChange={(event) => {
            setInputValue(event.target.value);
            if (limitMessage && tags.length < MAX_TAGS) {
              setLimitMessage("");
            }
          }}
          onKeyDown={handleKeyDown}
          onBlur={handleBlur}
          disabled={disabled}
          maxLength={MAX_TAG_LENGTH}
        />
      </div>
      {limitMessage ? (
        <p className="field-error" role="alert">
          {limitMessage}
        </p>
      ) : null}
      <p className="field-hint">
        Press Enter or comma to add a tag. {tags.length}/{MAX_TAGS} used.
      </p>
    </div>
  );
}
