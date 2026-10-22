## Summary

<!-- What changed, and why? Keep runtime and release-engineering changes separate. -->

## Type

- [ ] Plugin runtime / hook behavior
- [ ] Documentation (English and Russian)
- [ ] Tests / validation
- [ ] CI, release engineering, or repository metadata

## Validation

- [ ] `python3 scripts/package_release.py --check` passes
- [ ] `python3 tests/test_state_preservation.py` passes (or explain why it was not run)
- [ ] Plugin syntax compiles with Python 3.11
- [ ] CI passes

## Runtime evidence

<!-- Required for runtime changes: device/build, adb logcat lines, and screenshots. -->
<!-- Write "not applicable" for docs/CI-only changes. -->

- Exteraless build:
- Botile version:
- Device / Android:
- Relevant log lines:
- Screenshots:

## Release impact

- [ ] No version or tag change
- [ ] This PR is intended for the next release; version metadata is updated
- [ ] Tag/release instructions were followed; no tag is created by this PR
- [ ] No `dist/`, `__pycache__/`, secrets, tokens, or personal chat data are included

## Checklist

- [ ] English and Russian documentation are consistent for user-facing changes
- [ ] No runtime behavior was changed in a release-engineering-only PR
- [ ] No private data is included in logs or screenshots
