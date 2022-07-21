import os
import sublime
import sublime_plugin


class MarkAndMoveWindowCommand(sublime_plugin.WindowCommand):
    mark_and_move_views = {}  # links view_id => goto_view_id
    mark_and_move_files = {}  # links view_id => file_name
    mark_and_move_selections = {}
    # 2207 => [2201, 2202]
    # mark_and_move_selections_2207_2201
    # mark_and_move_selections_2207_2202

    def remember_file_name(self, view, file_name):
        ids = [view_id for view_id in self.mark_and_move_files if self.mark_and_move_files[view_id] == file_name]
        if ids:
            new_view_id = view.id()
            old_view_id = ids[0]

            self.fix_ids(new_view_id, old_view_id)

    def lookup_view(self, from_view, goto_view_id):
        goto_view = None
        goto_views = [check_view for check_view in self.window.views() if check_view.id() == goto_view_id]
        if goto_views:
            goto_view = goto_views[0]
        elif goto_view_id in self.mark_and_move_files:
            file_name = self.mark_and_move_files[goto_view_id]
            if os.path.isfile(file_name):
                goto_view = self.window.open_file(file_name)

            if goto_view is None:
                return

            del self.mark_and_move_files[goto_view_id]
            self.mark_and_move_files[goto_view.id()] = file_name

            self.fix_ids(goto_view.id(), goto_view_id, from_view)
        return goto_view

    def fix_ids(self, new_view_id, old_view_id, from_view=None):
        # correct the views if they have different ids
        if new_view_id != old_view_id:
            if old_view_id in self.mark_and_move_views:
                self.mark_and_move_views[new_view_id] = self.mark_and_move_views[old_view_id]
                del self.mark_and_move_views[old_view_id]

            if from_view:
                for from_id, to_ids in self.mark_and_move_selections.iteritems():
                    new_ids = []
                    for to_id in to_ids:
                        if to_id == old_view_id:
                            new_ids.append(new_view_id)
                            from_view_id = from_view.id()
                            key = 'mark_and_move_selections_%i_%i' % (from_view_id, old_view_id)
                            new_key = 'mark_and_move_selections_%i_%i' % (from_view_id, new_view_id)
                            new_regions = from_view.get_regions(key)
                            from_view.add_regions(
                                new_key,
                                new_regions,
                                'source',
                                '',
                                sublime.HIDDEN
                                )
                            from_view.erase_regions(key)
                        else:
                            new_ids.append(to_id)
                    self.mark_and_move_selections[from_id] = new_ids
            else:
                # delete all selections that refer to old_view_id if the from_view is not given
                # this happens during remember_file_name()
                if old_view_id in self.mark_and_move_selections:
                    del self.mark_and_move_selections[old_view_id]
                for from_id, to_ids in self.mark_and_move_selections.iteritems():
                    new_ids = []
                    for to_id in to_ids:
                        if to_id == old_view_id:
                            new_ids.append(to_id)
                    self.mark_and_move_selections[from_id] = new_ids

            for from_id, to_id in self.mark_and_move_views.iteritems():
                if to_id == old_view_id:
                    self.mark_and_move_views[from_id] = new_view_id


class MarkAndMoveWindowSelectCommand(MarkAndMoveWindowCommand):
    def run(self, goto=True):
        view = self.window.active_view()
        if view.file_name():
            self.mark_and_move_files[view.id()] = view.file_name()

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

                if goto_view.id() not in self.mark_and_move_views:
                    self.mark_and_move_views[goto_view.id()] = view.id()
                    if goto_view.file_name():
                        self.mark_and_move_files[goto_view.id()] = goto_view.file_name()

                if all(region.empty() for region in view.sel()):
                    self.mark_and_move_views[view.id()] = goto_view.id()
                else:
                    # TODO: detect and remove overlapping regions
                    if view.id() not in self.mark_and_move_selections:
                        self.mark_and_move_selections[view.id()] = []

                    self.mark_and_move_selections[view.id()].append(goto_view.id())

                    regions = list(filter(bool, view.sel()))
                    # add existing regions
                    key = 'mark_and_move_selections_%i_%i' % (view.id(), goto_view.id())
                    regions.extend(view.get_regions(key))
                    view.add_regions(
                        key,
                        regions,
                        'source',
                        '',
                        sublime.HIDDEN
                        )

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

        if view.file_name() and any(view.id() != view_id and view.file_name() == file_name for view_id, file_name in self.mark_and_move_files.items()):
            self.remember_file_name(view, view.file_name())

        view_id = view.id()
        cursor = view.sel()[0].b
        if view_id in self.mark_and_move_selections:
            for goto_view_id in self.mark_and_move_selections[view_id]:
                key = 'mark_and_move_selections_%i_%i' % (view_id, goto_view_id)
                check_regions = view.get_regions(key)
                for check_region in check_regions:
                    if check_region.contains(cursor):
                        goto_view = self.lookup_view(view, goto_view_id)
                        if goto_view is not None:
                            self.window.focus_view(goto_view)
                            return

        if all(region.empty() for region in view.sel()) and view_id in self.mark_and_move_views:
            goto_view_id = self.mark_and_move_views[view_id]
            goto_view = self.lookup_view(view, goto_view_id)
            if goto_view is not None:
                self.window.focus_view(goto_view)
                if self.window.active_view().id() != goto_view.id():
                    del self.mark_and_move_views[view_id]
                    del self.mark_and_move_views[goto_view.id()]
                    self.window.run_command('mark_and_move_window_select', {'goto': True})
        else:
            self.window.run_command('mark_and_move_window_select', {'goto': True})


class MarkAndMoveSaveCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        mark_and_move_marks = self.view.get_regions('mark_and_move')

        for region in self.view.sel():
            mark_and_move_marks.append(region)

        self.view.add_regions(
          'mark_and_move',
          mark_and_move_marks,
          'source',
          'dot',
          sublime.DRAW_OUTLINED
        )


class MarkAndMoveRecallCommand(sublime_plugin.TextCommand):
    def run(self, edit, clear=False, append=False):
        mark_and_move_marks = self.view.get_regions('mark_and_move')
        if not mark_and_move_marks:
            return

        if not append:
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

        if any(not region_in(region, mark_and_move_marks) for region in self.view.sel()):
            self.view.run_command('mark_and_move_save')
        else:
            self.view.run_command('mark_and_move_recall', {"clear": True})


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
