MarkAndMove
===========

Allows for keyboard-only multiple selections.  Select some stuff, mark it, then move the cursor around and add more marks, recall marks, or move between marks.

Installation
------------

1. Using Package Control, install "MarkAndMove"

Or:

1. Open the Sublime Text Packages folder
    - OS X: ~/Library/Application Support/Sublime Text 3/Packages/
    - Windows: %APPDATA%/Sublime Text 3/Packages/
    - Linux: ~/.Sublime Text 3/Packages/ or ~/.config/sublime-text-3/Packages

2. clone this repo
3. Install keymaps for the commands (see Example.sublime-keymap for my preferred keys)

### Sublime Text 2

1. Open the Sublime Text 2 Packages folder
2. clone this repo, but use the `st2` branch

       git clone -b st2 git@github.com:colinta/SublimeMarkAndMove

Example
-------

In this video you can watch the user create 3 cursors (using `ctrl+m`), then
activate those three cursors by pressing `ctrl+m` again after the third cursor
is created.

![example](https://f.cloud.github.com/assets/168193/295050/8ab0536c-9446-11e2-86cf-a99e02067ee9.gif)

Thank you to @paradox460 for creating this GIF!

TextCommands
------------

`mark_and_move_save`

Adds the current selection or cursor position to the list of marks.

`mark_and_move_next`

Moves to the next mark.  "Next mark" is defined as the first mark after the first current region, or the first mark if none are found (aka wraps).

`mark_and_move_prev`

Moves to the previous mark.  "Previous mark" is defined as the first mark before the first current region, or the last mark if none are found (aka wraps).

`mark_and_move_recall`

Selects and clears all the marks.

`mark_and_move_clear`

Removes the marks, but doesn't affect cursor position.

And the command with the mostest:

`mark_and_move_do_it_all`

Adds, recalls, and clears marks using one command.

The logic is this:

1. If the cursor(s) are not in the set of marks, add it (`mark_and_move_save`).
2. If *some* of the cursors are in the set, but not *all*, recall the marks (`mark_and_move_recall`)
3. If *all* the marks are already selected, clear them and leave the cursors (`mark_and_move_clear`)

So `ctrl+m` like crazy, and on the last one press `ctrl+m` twice, once to add it and once to select the marks.
Then press it a third time and *WHOOSH* the marks are cleared, ready to start anew.


WindowCommands
--------------

`mark_and_move_window_select`

Displays a picker so that you can bind two open files.  The other file will be opened. `goto: false` disables this feature. The first time you do this, the two files will be bound to each other.  However, if the other file is *already bound*, it will not be bound to the current view.  You can create "rings" this way, or have multiple files point to one file.

If you have some text selected, it will bind those regions. For example, you might bind a django `views.py` file to the corresponding `models.py`, but you could bind specific view functions to templates, so depending on where the cursor is located you will go to a different file.

Bindings are stored on the window, so as long as you don't close the project, you should retain your bindings.

`mark_and_move_window_toggle`

If the current view is bound, it goes to the other view.  If it isn't bound, this command delegates to `mark_and_move_window_select`.

TODO
----

* Have file-to-file bindings persist between sessions.  Can this be stored in a project config?
