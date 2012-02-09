MarkAndMove for Sublime Text 2
==================================

Allows for keyboard-only multiple selections.  Select some stuff, mark it, then move the cursor around and add more marks, recall marks, or move between marks.


Installation
------------

1. Using Package Control, install "MarkAndMove"

Or:

1. Open the Sublime Text 2 Packages folder

    - OS X: ~/Library/Application Support/Sublime Text 2/Packages/
    - Windows: %APPDATA%/Sublime Text 2/Packages/
    - Linux: ~/.Sublime Text 2/Packages/

2. clone this repo

TextCommands
------------

`mark_and_move_save`: Adds the current selection or cursor position to the list of marks.

`mark_and_move_next`: Moves to the next mark.  "Next mark" is defined as the first mark after the first current region, or the first mark if none are found (aka wraps).

`mark_and_move_prev`: Moves to the previous mark.  "Previous mark" is defined as the first mark before the first current region, or the last mark if none are found (aka wraps).

`mark_and_move_recall`: Selects and clears all the marks.

`mark_and_move_clear`: Removes the marks, but doesn't affect cursor position.

And the command with the mostest:

`mark_and_move_do_it_all`: Adds, recalls, and clears marks using one command.

The logic is this:

1. If the cursor(s) are not in the set of marks, add it (`mark_and_move_save`).
2. If *some* of the cursors are in the set, but not *all*, recall the marks (`mark_and_move_recall`)
3. If *all* the marks are already selected, clear them and leave the cursors (`mark_and_move_clear`)

So `ctrl+m` like crazy, and on the last one press `ctrl+m` twice, once to add it and once to select the marks.  Then press it a third time and *WHOOSH* the marks are cleared, ready to start anew.

WindowCommands
--------------

`mark_and_move_window_select`: Displays a picker so that you can bind two open files.  The two files must already be open.  Once the files are bound, opens the other file (`goto`: False disables the "auto-goto")

`mark_and_move_window_toggle`: If the current view is bound, it goes to the other view.  If it isn't bound, this command delegates to `mark_and_move_window_select`.
