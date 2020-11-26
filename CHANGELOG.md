# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Add a `next` query param on legal acceptance view to redirect user after acceptance to the route
  provided in this param.

- Add a `richie` view to redirect user to richie after login/registration

## [5.5.1] - 2020-10-22

### Fixed

- Log error but continue course updates when encountering invalid key error

## [5.5.0] - 2020-10-02

### Added

- Allow placing thumbnails related media files behind a CDN

## [5.4.2] - 2020-10-01

### Fixed

- Catch OS errors on thumbnail generation

## [5.4.1] - 2020-07-20

### Changed

- Improve teacher image for non-square geometry

## [5.4.0] - 2020-04-01

### Added

- Add a "browsable" status for courses

### Removed

- Remove deprecated `contact` application

## [5.3.1] - 2020-01-29

### Fixed

- Override edX's view for the home page to further accelerate it

## [5.3.0] - 2020-01-29

### Added

- Cache home page for authenticated users except staff

## [5.2.2] - 2020-01-22

### Fixed

- Use the static.url template tag where it is required

## [5.2.1] - 2020-01-21

### Fixed

- Rewrite constants related to fun's PDF certificates urls

[unreleased]: https://github.com/openfun/fun-apps/compare/v5.5.1...HEAD
[5.5.1]: https://github.com/openfun/fun-apps/compare/v5.5.0...v5.5.1
[5.5.0]: https://github.com/openfun/fun-apps/compare/v5.4.2...v5.5.0
[5.4.2]: https://github.com/openfun/fun-apps/compare/v5.4.0...v5.4.2
[5.4.1]: https://github.com/openfun/fun-apps/compare/v5.4.0...v5.4.1
[5.4.0]: https://github.com/openfun/fun-apps/compare/v5.3.1...v5.4.0
[5.3.1]: https://github.com/openfun/fun-apps/compare/v5.3.0...v5.3.1
[5.3.0]: https://github.com/openfun/fun-apps/compare/v5.2.2...v5.3.0
[5.2.2]: https://github.com/openfun/fun-apps/compare/v5.2.1...v5.2.2
[5.2.1]: https://github.com/openfun/fun-apps/releases/tag/v5.2.1
[5.2.1]: https://github.com/openfun/fun-apps/releases/tag/v5.2.1
