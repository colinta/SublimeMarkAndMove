MarkAndMove for Sublime Text 2
==================================

Allows for keyboard-only multiple selections.  Select some stuff, mark it, then move the cursor around and add more marks, recall marks, or move between marks.


Installation
------------

1. Open the Sublime Text 2 Packages folder

    - OS X: ~/Library/Application Support/Sublime Text 2/Packages/
    - Windows: %APPDATA%/Sublime Text 2/Packages/
    - Linux: ~/.Sublime Text 2/Packages/

2. clone this repo

Commands
--------

`mark_and_move_save`: Adds the current selection or cursor position to the list of marks.

`mark_and_move_next`: Moves to the next mark.  "Next mark" is defined as the first mark after the first current region, or the first mark if none are found (aka wraps).

`mark_and_move_prev`: Moves to the previous mark.  "Previous mark" is defined as the first mark before the first current region, or the last mark if none are found (aka wraps).

`mark_and_move_recall`: Selects and clears all the marks.

`mark_and_move_clear`: Removes the marks, but doesn't affect cursor position.

