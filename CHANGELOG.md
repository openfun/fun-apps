# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [5.14.0] - 2023-03-31

### Changed

- Replace FUN Mooc logo with new FUN logo into menu and footer
- Use the new OpenEdX logo in the footer

## [5.13.1] - 2022-05-31

### Fixed

- Fix admin register for universities app due to broken lms/cms detection

## [5.13.0] - 2022-01-24

### Added

- Add a server-to-server API endpoint to retrieve a student's grades

### Fixed

- Fix course run synchronization when triggered on enrollment

## [5.12.0] - 2022-01-17

### Added

- Add enrollment count to the course run synchronization hook payload

## [5.11.0] - 2021-08-17

### Changed

- Protect ourselves against VideoFront downtimes by trying to load the video
  object directly from S3 before falling back to querying the VideoFront API

### Fixed

- Fix hardcoded absolute url in payment email

## [5.10.1] - 2021-07-07

### Fixed

- Pin rsa dependency to 4.5

## [5.10.0] - 2021-07-07

### Removed

- Stop synchronizing Elasticsearch on each course publish

## [5.9.0] - 2021-04-12

### Added

- Redirect selected routes to the related Richie CMS View

### Changed

- Delegate course search to Richie

## [5.8.0] - 2021-02-23

### Added

- Add verified users to a cohort automatically after payment

## [5.7.3] - 2021-02-23

### Changed

- Enrich course run synchronization hook with course language

### Fixed

- Pin rsa dependency to 4.3

## [5.7.2] - 2021-01-18

### Fixed

- Fix `resource_link` in course run synchronization to point to LMS

## [5.7.1] - 2021-01-18

### Fixed

- Fix course run sync when one of the dates is not set

## [5.7.0] - 2021-01-06

### Added

- Allow synchronizing course runs via an external synchronization hook

### Fixed

- Fix "update_courses" command used in cron job for mass updates

## [5.6.0] - 2020-12-04

### Added

- Add a `next` query param on legal acceptance view to redirect user after
  acceptance to the route provided in this param.
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

[unreleased]: https://github.com/openfun/fun-apps/compare/v5.14.0...HEAD
[5.14.0]: https://github.com/openfun/fun-apps/compare/v5.13.1...v5.14.0
[5.13.1]: https://github.com/openfun/fun-apps/compare/v5.13.0...v5.13.1
[5.13.0]: https://github.com/openfun/fun-apps/compare/v5.12.0...v5.13.0
[5.12.0]: https://github.com/openfun/fun-apps/compare/v5.11.0...v5.12.0
[5.11.0]: https://github.com/openfun/fun-apps/compare/v5.10.1...v5.11.0
[5.10.1]: https://github.com/openfun/fun-apps/compare/v5.10.0...v5.10.1
[5.10.0]: https://github.com/openfun/fun-apps/compare/v5.9.0...v5.10.0
[5.9.0]: https://github.com/openfun/fun-apps/compare/v5.8.0...v5.9.0
[5.8.0]: https://github.com/openfun/fun-apps/compare/v5.7.3...v5.8.0
[5.7.3]: https://github.com/openfun/fun-apps/compare/v5.7.2...v5.7.3
[5.7.2]: https://github.com/openfun/fun-apps/compare/v5.7.1...v5.7.2
[5.7.1]: https://github.com/openfun/fun-apps/compare/v5.7.0...v5.7.1
[5.7.0]: https://github.com/openfun/fun-apps/compare/v5.6.0...v5.7.0
[5.6.0]: https://github.com/openfun/fun-apps/compare/v5.5.1...v5.6.0
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
