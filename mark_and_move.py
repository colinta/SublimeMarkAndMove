import os
import sublime
import sublime_plugin


class MarkAndMoveWindowCommand(sublime_plugin.WindowCommand):
    mark_and_move_views = {}


class MarkAndMoveWindowSelectCommand(MarkAndMoveWindowCommand):
    def run(self, goto=True):
        view = self.window.active_view()
        my_id = view.id()
        files = []
        views = []
        untitled_count = 1
        for v in view.window().views():
            if v.id() != my_id:
                views.append(v)
                if v.file_name():
                    files.append(v.file_name())
                elif v.name():
                    files.append(v.name())
                else:
                    files.append('untitled %d' % untitled_count)
                    untitled_count += 1

        def on_done(index):
            if index > -1 and len(views) > index:
                goto_view = views[index]
                self.mark_and_move_views[view.id()] = goto_view
                self.mark_and_move_views[goto_view.id()] = view
                if goto:
                    self.window.focus_view(goto_view)

        if len(files) == 1:
            on_done(0)
        else:
            menu_items = [os.path.basename(f) for f in files]
            view.window().show_quick_panel(menu_items, on_done)


class MarkAndMoveWindowToggleCommand(MarkAndMoveWindowCommand):
    def run(self, *args, **kwargs):
        view = self.window.active_view()
        if view.id() in self.mark_and_move_views:
            goto_view = self.mark_and_move_views[view.id()]
            self.window.focus_view(goto_view)
            if self.window.active_view().id() != goto_view.id():
                del self.mark_and_move_views[view.id()]
                del self.mark_and_move_views[goto_view.id()]
                self.window.run_command('mark_and_move_window_select', {'goto': True})
        else:
            self.window.run_command('mark_and_move_window_select', {'goto': True})


class MarkAndMoveSaveCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        mark_and_move_marks = self.view.get_regions('mark_and_move')

        regions = [region for region in self.view.sel()]
        for region in regions:
            mark_and_move_marks.append(region)

        # sort by region.end() ASC
        def compare(region_a, region_b):
            return cmp(region_a.begin(), region_b.begin())
        mark_and_move_marks.sort(compare)

        self.view.add_regions(
          'mark_and_move',
          mark_and_move_marks,
          'source',
          'dot',
          sublime.DRAW_OUTLINED
        )


class MarkAndMoveRecallCommand(sublime_plugin.TextCommand):
    def run(self, edit, clear=False):
        mark_and_move_marks = self.view.get_regions('mark_and_move')
        if not mark_and_move_marks:
            return

        self.view.sel().clear()
        for region in mark_and_move_marks:
            self.view.sel().add(region)

        if clear:
            mark_and_move_marks = []
            self.view.erase_regions('mark_and_move')


class MarkAndMoveSaveAndRecallCommand(sublime_plugin.TextCommand):
    def run(self, edit, clear=False):
        self.view.run_command('mark_and_move_save')
        self.view.run_command('mark_and_move_recall', {"clear": clear})


class MarkAndMoveClearCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        mark_and_move_marks = self.view.get_regions('mark_and_move')
        if not mark_and_move_marks:
            return

        mark_and_move_marks = []
        self.view.erase_regions('mark_and_move')


class MarkAndMoveDoItAllCommand(sublime_plugin.TextCommand):
    """
    If there is one region, and it is already in mark_and_move_marks, all marks are selected.
    If there are multiple selections and all of them are in mark_and_move_marks, all marks are removed.
    Otherwise all marks added.

    Makes it easy to have 'mark_and_move_save', 'mark_and_move_recall', and 'mark_and_move_clear' bound
    to the same command.
    """
    def run(self, edit):
        mark_and_move_marks = self.view.get_regions('mark_and_move')

        def region_in(region, marks):
            for mark in marks:
                if region.begin() == mark.begin() and region.end() == mark.end():
                    return True
            return False

        if len(self.view.sel()) > 1 and len(self.view.sel()) == len(mark_and_move_marks) \
                                    and all(region_in(region, mark_and_move_marks) for region in self.view.sel()):
            self.view.run_command('mark_and_move_clear')
        elif any(not region_in(region, mark_and_move_marks) for region in self.view.sel()):
            self.view.run_command('mark_and_move_save')
        else:
            self.view.run_command('mark_and_move_recall', {"clear": False})


class MarkAndMoveRotateCommand(sublime_plugin.TextCommand):
    def rotate(self, edit, direction):
        mark_and_move_marks = self.view.get_regions('mark_and_move')
        if not mark_and_move_marks:
            return

        current_region = self.view.sel()[0]

        if direction > 0:
            next_region = mark_and_move_marks[0]
            find = mark_and_move_marks
        else:
            next_region = mark_and_move_marks[-1]
            find = mark_and_move_marks[::-1]  # reversed

        for test_region in find:
            if direction > 0 and test_region != current_region and test_region.begin() >= current_region.begin():
                next_region = test_region
                break
            elif direction < 0 and test_region != current_region and test_region.begin() <= current_region.begin():
                next_region = test_region
                break

        self.view.sel().clear()
        self.view.sel().add(next_region)
        self.view.show(next_region.b)


class MarkAndMoveNextCommand(MarkAndMoveRotateCommand):
    def run(self, edit):
        return self.rotate(edit, +1)


class MarkAndMovePrevCommand(MarkAndMoveRotateCommand):
    def run(self, edit):
        return self.rotate(edit, -1)
