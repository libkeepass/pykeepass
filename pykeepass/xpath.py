# FIXME python2
from __future__ import unicode_literals

attachment_xp = {
    False: {
        'id': '/Value[@Ref="{}"]/..',
        'filename': '/Key[text()="{}"]/..'
    },
    True: {
        'id': '/Value[re:test(@Ref, "{}", "{flags}")]/..',
        'filename': '/Key[re:test(text(), "{}", "{flags}")]/..'
    }
}

path_xp = {
    False: {
        'group': '/Group/Name[text()="{}"]/..',
        'entry': '/Entry/String/Key[text()="Title"]/../Value[text()="{}"]/../..',
    },
    True: {
        'group': '/Group/Name[re:test(text(), "{}", "{flags}")]/..',
        'entry': '/Entry/String/Key[text()="Title"]/../Value[re:test(text(), "{}", "{flags}")]/../..',
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
        'title': '/String/Key[text()="Title"]/../Value[re:test(text(), "{}", "{flags}")]/../..',
        'username': '/String/Key[text()="UserName"]/../Value[re:test(text(), "{}", "{flags}")]/../..',
        'password': '/String/Key[text()="Password"]/../Value[re:test(text(), "{}", "{flags}")]/../..',
        'url': '/String/Key[text()="URL"]/../Value[re:test(text(), "{}", "{flags}")]/../..',
        'notes': '/String/Key[text()="Notes"]/../Value[re:test(text(), "{}", "{flags}")]/../..',
        'uuid': '/UUID[re:test(text(), "{}", "{flags}")]/..',
        'tags': '/Tags[re:test(text(), "{}", "{flags}")]/..',
        'string': '/String/Key[text()="{}"]/../Value[re:test(text(), "{}", "{flags}")]/../..',
        'autotype_sequence': '/AutoType/DefaultSequence[re:test(text(), "{}", "{flags}")]/../..',
        'autotype_enabled': '/AutoType/Enabled[re:test(text(), "{}", "{flags}")]/../..',
    }
}

group_xp = {
    False: {
        'name': '/Name[text()="{}"]/..',
        'uuid': '/UUID[text()="{}"]/..',
        'notes': '/Notes[text()="{}"]/..',
    },
    True: {
        'name': '/Name[re:test(text(), "{}", "{flags}")]/..',
        'uuid': '/UUID[re:test(text(), "{}", "{flags}")]/..',
        'notes': '/Notes[re:test(text(), "{}", "{flags}")]/..',
    }
}
