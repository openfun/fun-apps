# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Allow synchronizing course runs via an external synchronization hook

## [2.5.0+wb] - 2021-08-17

### Changed

- Protect ourselves against VideoFront downtimes by trying to load the video
  object directly from S3 before falling back to querying the VideoFront API

### Fixed

- Pin rsa dependency to 4.5

## [2.4.2+wb] - 2020-07-20

### Changed

- Improve teacher image for non-square geometry

## [2.4.1+wb] - 2020-04-17

### Fixed

- Fix email report recipient bug of "audit to honor" management command

## [2.4.0+wb] - 2020-04-01

### Changed

- Rewrite management command to change `audit` course enrollments to `honor`

## [2.3.1+wb] - 2020-02-18

### Fixed

- Add `videoproviders` missing migration (`0006`)

## [2.3.0+wb] - 2020-02-17

### Added

- Backport support for the bokecc video provider

## [2.2.1+wb] - 2020-01-22

### Fixed

- Use the static.url template tag where it is required

## [2.2.0+wb] - 2020-01-07

### Changed

- Set Videofront upload dashboard in read only mode

### Removed

- `selftest` application

[unreleased]: https://github.com/openfun/fun-apps/compare/v2.5.0+wb...eucalyptus.3-wb
[2.5.0+wb]: https://github.com/openfun/fun-apps/compare/v2.4.2+wb...v2.5.0+wb
[2.4.2+wb]: https://github.com/openfun/fun-apps/compare/v2.4.1+wb...v2.4.2+wb
[2.4.1+wb]: https://github.com/openfun/fun-apps/compare/v2.4.0+wb...v2.4.1+wb
[2.4.0+wb]: https://github.com/openfun/fun-apps/compare/v2.3.1+wb...v2.4.0+wb
[2.3.1+wb]: https://github.com/openfun/fun-apps/compare/v2.3.0+wb...v2.3.1+wb
[2.3.0+wb]: https://github.com/openfun/fun-apps/compare/v2.2.1+wb...v2.3.0+wb
[2.2.1+wb]: https://github.com/openfun/fun-apps/compare/v2.2.0+wb...v2.2.1+wb
[2.2.0+wb]: https://github.com/openfun/fun-apps/releases/tag/v2.2.0+wb
