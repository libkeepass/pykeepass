# ---------- Find functions ---------------
# Use find_entries()/find_groups() instead

def find_groups_by_name(self, group_name, regex=False, flags=None,
                        group=None, first=False):
    return self.find_groups(
        name=group_name,
        regex=regex,
        flags=flags,
        group=group,
        first=first
    )

def find_groups_by_path(self, group_path_str=None, regex=False, flags=None,
                        group=None, first=False):
    return self.find_groups(
        path=group_path_str,
        regex=regex,
        flags=flags,
        group=group,
        first=first
    )

def find_groups_by_uuid(self, uuid, regex=False, flags=None,
                        group=None, history=False, first=False):
    return self.find_groups(
        uuid=uuid,
        regex=regex,
        flags=flags,
        group=group,
        history=history,
        first=first
    )

def find_groups_by_notes(self, notes, regex=False, flags=None,
                            group=None, history=False, first=False):
    return self.find_groups(
        notes=notes,
        regex=regex,
        flags=flags,
        group=group,
        history=history,
        first=first
    )

def find_entries_by_title(self, title, regex=False, flags=None,
                            group=None, history=False, first=False):
    return self.find_entries(
        title=title,
        regex=regex,
        flags=flags,
        group=group,
        history=history,
        first=first
    )

def find_entries_by_username(self, username, regex=False, flags=None,
                                group=None, history=False, first=False):
    return self.find_entries(
        username=username,
        regex=regex,
        flags=flags,
        group=group,
        history=history,
        first=first
    )

def find_entries_by_password(self, password, regex=False, flags=None,
                                group=None, history=False, first=False):
    return self.find_entries(
        password=password,
        regex=regex,
        flags=flags,
        group=group,
        history=history,
        first=first
    )

def find_entries_by_url(self, url, regex=False, flags=None,
                        group=None, history=False, first=False):
    return self.find_entries(
        url=url,
        regex=regex,
        flags=flags,
        group=group,
        history=history,
        first=first
    )

def find_entries_by_notes(self, notes, regex=False, flags=None,
                            group=None, history=False, first=False):
    return self.find_entries(
        notes=notes,
        regex=regex,
        flags=flags,
        group=group,
        history=history,
        first=first
    )

def find_entries_by_path(self, path, regex=False, flags=None,
                            group=None, history=False, first=False):
    return self.find_entries(
        path=path,
        regex=regex,
        flags=flags,
        group=group,
        history=history,
        first=first
    )

def find_entries_by_uuid(self, uuid, regex=False, flags=None,
                            group=None, history=False, first=False):
    return self.find_entries(
        uuid=uuid,
        regex=regex,
        flags=flags,
        group=group,
        history=history,
        first=first
    )

def find_entries_by_string(self, string, regex=False, flags=None,
                            group=None, history=False, first=False):
    return self.find_entries(
        string=string,
        regex=regex,
        flags=flags,
        group=group,
        history=history,
        first=first
    )
