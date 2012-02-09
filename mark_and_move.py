import sublime
import sublime_plugin


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
          'entity.name.class',
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

        if len(self.view.sel()) > 1 and all(region_in(region, self.view.sel()) for region in mark_and_move_marks):
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

        for current_region in self.view.sel():
            break

        if direction > 0:
            next_region = mark_and_move_marks[0]
            find = mark_and_move_marks
        else:
            next_region = mark_and_move_marks[-1]
            find = mark_and_move_marks[::-1]

        for test_region in find:
            if direction > 0 and test_region.begin() > current_region.begin():
                next_region = test_region
                break
            elif direction < 0 and test_region.begin() < current_region.begin():
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
