import sublime
import sublime_plugin


class MarkAndMoveListener(sublime_plugin.EventListener):
    def __init__(self):
        self.previous = None
        super(MarkAndMoveListener, self).__init__()

    def on_modified(self, view):
        mark_and_move_marks = view.get_regions('mark_and_move')

        if not mark_and_move_marks:
            return

        content = view.substr(sublime.Region(0, view.size()))
        self.previous = content


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


class MarkAndMoveRecallCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        mark_and_move_marks = self.view.get_regions('mark_and_move')
        if not mark_and_move_marks:
            return

        self.view.sel().clear()
        for region in mark_and_move_marks:
            self.view.sel().add(region)
        mark_and_move_marks = []
        self.view.erase_regions('mark_and_move')


class MarkAndMoveClearCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        mark_and_move_marks = self.view.get_regions('mark_and_move')
        if not mark_and_move_marks:
            return

        mark_and_move_marks = []
        self.view.erase_regions('mark_and_move')
