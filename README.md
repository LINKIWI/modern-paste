Modern Paste
===========

[![Build Status](https://travis-ci.org/LINKIWI/modern-paste.svg?branch=dev)](https://travis-ci.org/LINKIWI/modern-paste) [![Coverage Status](https://coveralls.io/repos/LINKIWI/modern-paste/badge.svg?branch=dev&service=github)](https://coveralls.io/github/LINKIWI/modern-paste?branch=dev)

## About

**Modern Paste** is a self-hosted Pastebin alternative that is
+ Visually pleasing, with a contemporary and minimalistic user interface
+ Feature-rich
+ Mobile-friendly
+ Open source
+ Backed by a robust, RESTful API
+ Apache WSGI-friendly
+ Easy to install and highly configurable

[Live demo site](https://demo.modernpaste.com)

Modern Paste is intended for system administrators who wish to host their own installation of a code/text Pastebin on personal servers. It's free and open source: contributions from the developer community are encouraged and always welcome.

## Features

+ Modern user interface with a consistent design language
+ Syntax highlighting for [all languages supported by CodeMirror](https://codemirror.net/mode/)
+ Ability to set paste expiration dates
+ Ability to password-protect pastes
+ Full user account functionality
	+ Associate new pastes with a user account
	+ View, modify, or delete pastes posted with a user account
	+ Directly query the Modern Paste API with the account's API key/authtoken
+ Public archive of pastes, sorted reverse chronologically or by popularity
+ RESTful API for externally creating, reading, and managing pastes
+ Ability to enforce security restrictions: can configure that only authenticated users can post pastes (ideal for private, non-public-facing installations)
+ Ability to encrypt the front-facing-display of paste IDs (e.g. so that `/paste/1` might display as `/paste/9~AEygplxfCPHW4eJctbjMnRi-rYnlYzizqToCmG3BY=`)
