"""Steam launch-option policy helpers for the Minify fork."""

import re

# Match only the command shape Minify rc7 writes. The executable path may
# point at an older portable build, so matching is intentionally based on
# the Minify executable basename rather than current sys.executable.
_WINDOWS_PRELAUNCH = re.compile(
    r'cmd\s+/c\s+"(?:[^"\r\n]*[\\/])?Minify\.exe"\s+prelaunch\s*&&\s*',
    re.IGNORECASE,
)
_POSIX_PRELAUNCH = re.compile(
    r'bash\s+-c\s+"(?:[^"\r\n]*[\\/])?Minify(?:\.exe)?\s+prelaunch"\s*&&\s*',
    re.IGNORECASE,
)


def strip_minify_prelaunch_prefix(options):
    """Return ``(cleaned, changed)`` after undoing Minify's Steam wrapper.

    rc7's injector prepends both a Minify prelaunch command and a leading
    ``%command%`` token. Earlier fork cleanup could remove the command but
    leave that token behind, so orphaned leading ``%command%`` wrappers are
    also normalized when they are alone or followed only by ordinary Dota
    ``-``/``+`` launch arguments. User command wrappers are left intact.
    """
    original = "" if options is None else str(options)
    cleaned = original
    for pattern in (_WINDOWS_PRELAUNCH, _POSIX_PRELAUNCH):
        cleaned = pattern.sub("", cleaned)

    removed_prelaunch = cleaned != original
    candidate = cleaned.strip()

    command_prefix = re.compile(r"^(?:%command%\s*)+", re.IGNORECASE)
    match = command_prefix.match(candidate)
    removed_command_wrapper = False
    if match:
        remainder = candidate[match.end() :].lstrip()
        if not remainder:
            candidate = ""
            removed_command_wrapper = True
        else:
            first_token = remainder.split(None, 1)[0]
            if first_token.startswith(("-", "+")):
                candidate = remainder
                removed_command_wrapper = True
            elif removed_prelaunch:
                candidate = "%command% " + remainder

    changed = removed_prelaunch or removed_command_wrapper
    if not changed:
        return original, False
    return candidate, True
