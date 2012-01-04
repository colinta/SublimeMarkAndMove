import sublime
import sublime_plugin


class MarkAndMoveSaveCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if not self.view.mark_and_move_marks:
            self.view.mark_and_move_marks = []

        regions = [region for region in self.view.sel()]
        for region in regions:
            self.view.mark_and_move_marks.append(region)

        # sort by region.end() ASC
        def compare(region_a, region_b):
            return cmp(region_a.begin(), region_b.begin())
        self.view.mark_and_move_marks.sort(compare)

        self.view.add_regions(
          'mark_and_move',
          self.view.mark_and_move_marks,
          'entity.name.class',
          'dot',
          sublime.DRAW_OUTLINED
        )


class MarkAndMoveRotateCommand(sublime_plugin.TextCommand):
    def rotate(self, edit, direction):
        if not self.view.mark_and_move_marks:
            return

        for current_region in self.view.sel():
            break

        if direction > 0:
            next_region = self.view.mark_and_move_marks[0]
            find = self.view.mark_and_move_marks
        else:
            next_region = self.view.mark_and_move_marks[-1]
            find = self.view.mark_and_move_marks[::-1]

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


class MarkAndMoveRecallCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if not self.view.mark_and_move_marks:
            return
        self.view.sel().clear()
        for region in self.view.mark_and_move_marks:
            self.view.sel().add(region)
        self.view.mark_and_move_marks = []
        self.view.erase_regions('mark_and_move')


class MarkAndMoveClearCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if not self.view.mark_and_move_marks:
            return
        self.view.mark_and_move_marks = []
        self.view.erase_regions('mark_and_move')
