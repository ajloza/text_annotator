# Text Annotator

Terminal-based text annotation tool. Start from scratch or load from JSON. Select text spans, add annotations, link annotation, delete as needed, and save to JSON. Basic VIM keybindings for navigation

Supports:
1. overlapping spans
2. multiple labels per span
3. links between annotations
4. multiple links between same annotations
5. text is wrapped but the start/end values refer to character positions in the underlying text. The end value is not inclusive so when extrating a span `text[start:end]` will retrieve the appropriate full snippet
6. never need to leave your keyboard

![screenshot](screenshot.png)


```JSON
{
    "start": [
        0,
        934,
        1187,
        1252,
        712
    ],
    "end": [
        38,
        941,
        1201,
        1272,
        717
    ],
    "label": [
        "title",
        "year",
        "object",
        "person",
        "language"
    ],
    "links": [
        {
            "parent": 3,
            "child": 2,
            "label": "inventor of"
        }
    ]
}
```

## Workflow
1. `python annotator.py yourfile.txt`
2. if there is a corresponding yourfile.json, it will be loaded and annotations applied
3. Navigation
   1. arrow keys (shift to jump words, jump pages)
   2. standard vim hjkl and wb 
   3. find 'f' to jump to text
   4. mouse
4. Set start ('s') and end ('e') for annotation span 
5. shift-'A' to add text annotation
6. shift-'R' to remove annotation by index
7. shift-'L' to link annotations (parent, child, label)
8. shift-'S' to save current annotations to JSON


inspiration from https://github.com/maksimKorzh/code