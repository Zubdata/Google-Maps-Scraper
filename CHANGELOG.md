# Changelog

All notable changes to this project will be documented in this file.


## [3.2.0] - 2025-01-19
### Added
- Implemented functionality to extract email addresses from location websites.
- Introduced setup automation scripts to streamline the scraper setup process.


## [3.1.0] - 2024-04-26
### Added
- Added additional data fields

### Fixed
- Fixed extraction of `Total Reviews` and `Website` data fields

### Changed
- Updated logic of parsing data fields
- Changed output data file name

## [3.0.0] - 2024-04-26

### Fixed
- Updated code to scrape and parse the latest frontend code of Google Maps.
- Fixed a dependency error ([HTTP Error 404: Not Found]) by updating the version of undetected_chromedriver in requirements.txt.

### Changed
- Refactored codebase to enhance modularity and robustness.
