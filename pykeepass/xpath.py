# FIXME python2
from __future__ import unicode_literals

attachment_xp = {
    False: {
        'id': '/Value[@Ref="{}"]/..',
        'filename': '/Key[text()="{}"]/..'
    },
    True: {
        'id': '/Value[matches(@Ref, "{}", "{flags}")]/..',
        'filename': '/Key[matches(text(), "{}", "{flags}")]/..'
    }
}

path_xp = {
    False: {
        'group': '/Group/Name[text()="{}"]/..',
        'entry': '/Entry/String/Key[text()="Title"]/../Value[text()="{}"]/../..',
    },
    True: {
        'group': '/Group/Name[matches(text(), "{}", "{flags}")]/..',
        'entry': '/Entry/String/Key[text()="Title"]/../Value[matches(text(), "{}", "{flags}")]/../..',
    }
}

entry_xp = {
    False: {
        'title': '/String/Key[text()="Title"]/../Value[text()="{}"]/../..',
        'username': '/String/Key[text()="UserName"]/../Value[text()="{}"]/../..',
        'password': '/String/Key[text()="Password"]/../Value[text()="{}"]/../..',
        'url': '/String/Key[text()="URL"]/../Value[text()="{}"]/../..',
        'notes': '/String/Key[text()="Notes"]/../Value[text()="{}"]/../..',
        'uuid': '/UUID[text()="{}"]/..',
        'tags': '/Tags[text()="{}"]/..',
        'string': '/String/Key[text()="{}"]/../Value[text()="{}"]/../..',
        'autotype_sequence': '/AutoType/DefaultSequence[text()="{}"]/../..',
        'autotype_enabled': '/AutoType/Enabled[text()="{}"]/../..',
    },
    True: {
        'title': '/String/Key[text()="Title"]/../Value[matches(text(), "{}", "{flags}")]/../..',
        'username': '/String/Key[text()="UserName"]/../Value[matches(text(), "{}", "{flags}")]/../..',
        'password': '/String/Key[text()="Password"]/../Value[matches(text(), "{}", "{flags}")]/../..',
        'url': '/String/Key[text()="URL"]/../Value[matches(text(), "{}", "{flags}")]/../..',
        'notes': '/String/Key[text()="Notes"]/../Value[matches(text(), "{}", "{flags}")]/../..',
        'uuid': '/UUID[matches(text(), "{}", "{flags}")]/..',
        'tags': '/Tags[matches(text(), "{}", "{flags}")]/..',
        'string': '/String/Key[text()="{}"]/../Value[matches(text(), "{}", "{flags}")]/../..',
        'autotype_sequence': '/AutoType/DefaultSequence[matches(text(), "{}", "{flags}")]/../..',
        'autotype_enabled': '/AutoType/Enabled[matches(text(), "{}", "{flags}")]/../..',
    }
}

group_xp = {
    False: {
        'name': '/Name[text()="{}"]/..',
        'uuid': '/UUID[text()="{}"]/..',
        'notes': '/Notes[text()="{}"]/..',
    },
    True: {
        'name': '/Name[matches(text(), "{}", "{flags}")]/..',
        'uuid': '/UUID[matches(text(), "{}", "{flags}")]/..',
        'notes': '/Notes[matches(text(), "{}", "{flags}")]/..',
    }
}
