# Text Annotator

CLI tool for text annotation with vim navigation. Start from scratch or load from JSON. Select text spans, add annotations, delete as needed, and save to JSON. Basic highlighting.

Supports:
1. overlapping spans
2. multiple labels per span
3. text is wrapped but newlines are included in the span (the start/end values refer to character positions). The end value is not inclusive so `text[start:stop]` will retrieve the appropriate snippet
4. never need to leave your keyboard

TODO:
- [ ] links
- [ ] some better colors

![screenshot](screenshot.png)


```JSON
{
    "start": [
        0,
        1252,
        934
    ],
    "end": [
        38,
        1272,
        941
    ],
    "label": [
        "title",
        "person",
        "year"
    ]
}
```

## Workflow
1. `python annotator.py yourfile.txt`
2. if there is a corresponding yourfile.json, it will be loaded and annotations applied
3. Set start ('s') and end ('e') for annotation span 
   1. nagivate with arrow keys (shift to jump words, jump pages)
   2. standard vim hjkl and wb 
   3. mouse
4. shift-'A' to add text annotation
5. shift-'R' to remove annotation by index
6. shift-'S' to save current annotations to JSON


inspiration from https://github.com/maksimKorzh/code