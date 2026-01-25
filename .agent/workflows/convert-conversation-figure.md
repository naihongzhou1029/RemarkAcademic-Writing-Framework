---
description: Convert a conversation screenshot figure into a styled text blockquote.
---

# Convert Conversation Figure to Blockquote

This workflow converts a screenshot of a conversation (User/AI) in a Markdown document into a styled text blockquote.

## 1. Verify Prerequisites
1.  Check the file header (YAML frontmatter `header-includes`) for the `mdframed` configuration.
    -   It should contain: `\usepackage{mdframed}`, `\usepackage{xcolor}`, and the `\surroundwithmdframed` block.
    -   **Style Requirements**:
        ```latex
        \surroundwithmdframed[
          linewidth=2pt,
          linecolor=gray,
          topline=false,
          rightline=false,
          bottomline=false,
          leftmargin=0pt,
          innerleftmargin=-0.8em,
          skipabove=12pt,
          skipbelow=12pt
        ]{quote}
        ```
    -   If missing or different, update the header to match this styling.

## 2. Identify Target
1.  Locate the image Markdown syntax at the user's cursor or specified location.
    -   Example: `![Alt Text](path/to/image.png){#fig:id}`
2.  Note the **Image Path** and the **Figure ID** (e.g., `#fig:image13` or just `image13`).

## 3. Transcribe Content
1.  Read the image content.
    -   **Option A**: Use `run_command` with `tesseract <image_path> stdout -l chi_tra+eng --psm 6` to perform OCR.
    -   **Option B**: If OCR is insufficient, interpret the image using your visual understanding to extract the conversation text accurately.
2.  Parse the text into **User** and **AI** (or System) roles.

## 4. Construct Blockquote
Format the transcribed text into the following Markdown pattern. Use standard Markdown blockquotes (`>`).

```markdown
> **User**：[User Question/Text]
>
> **AI**：[AI Response/Text]
```

*Formatting Rules:*
-   Use **bold** for the role names: `**User**` and `**AI**`.
-   Use a **full-width colon** (`：`) after the role name.
-   Ensure there is an empty blockquote line (`>`) between the User's input and the AI's response for visual separation.
-   Preserve formatting (bullets, numbered lists, bold text) within the response as much as possible to match the original image.

## 5. Apply Changes
1.  **Replace** the original image line (`![...](...){...}`) with the constructed blockquote.
2.  **Scan** the surrounding text (immediately following the image) for references to the old Figure ID (e.g., `[@fig:image13]`, `Figures 13`, etc.).
3.  **Update** these references to point to the text above.
    -   *Example*: Change "如「[@fig:image13]」" to "如上" (As above) or "Gemini 的回答如上" (Gemini's answer is as above).
    -   Ensure the text flows naturally after the removal of the figure reference.
