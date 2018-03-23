# FUN-MOOC

This repo holds the source code of the [FUN-MOOC](https://fun-mooc.fr/)
website. FUN-MOOC is an initiative of the French Ministry of Higher Education
to provide free MOOCs from the best French universities.

## Code organization

There are three main components to FUN:

1. The Open edX platform that the FUN team has slightly modified with a couple
   bugfixes: the code for this fork is available in the
   [edx-platform](https://github.com/openfun/edx-platform/) repository.
2. The FUN layer that defines a visual theme and adds features on top of Open edX. (this repo)
3. The production configuration files, which are not disclosed for obvious security reasons.

## Install

`fun-apps` is supposed to be installed in an Open edX instance. As Open edX is
quite complex to setup, we invite you to ease your life by using
[fun-platform](https://github.com/openfun/fun-platform)'s base docker images to
integrate fun-apps (see `fun-platform` documentation).

Once your Open edX instance is fully functionnal, to install `fun-apps`, you
will need to use `pip` with FUN's python packages index server:

```bash
$ pip install --extra-index-url https://pypi.fury.io/openfun fun-apps
```

## How to contribute?

FUN is open to external contributions. If you find a bug on the platform, you
should feel free to run FUN on your own computer, modify the code and offer
your contributions back to us. To do so, just open a Github pull request on our
`dev` branch.

If you have found a bug but you are not able to contribute to FUN directly, you
should open a new [issue](https://github.com/openfun/fun-apps/issues) in this
repository. Please describe in details how to reproduce the problem, what
behaviour is expected and what behaviour is observed. If possible, include a
URL.

As a rule of thumb, new pull requests should come with the corresponding unit
tests. If you have trouble running the tests or writing new tests, please say
so in your PR and the FUN team will help you improve your pull request. For
more important contributions, please ask the FUN team **in advance** to make sure
that the feature is relevant and that your approach to solve the problem is the
right one.

## FAQ

* **Is the content of the courses included in this repository?** No, the
  courses that are run on FUN are "free" as in "free beer" but not "libre".
* **I love this project! How can I help?** Go [follow a
  course](https://fun-mooc.fr/cours/)! And then come back to us with the issues
  you have found :-) Either open a ticket or create a pull request.
* **Pourquoi ce document est-il rédigé en anglais, et pas en français ?** Le
  code de FUN est ouvert aux contributions des développeurs du monde entier et
  pour ce faire il est nécessaire de documenter ce projet en anglais.

## License

The fun-apps code is licensed under the [AGPL
v3](http://www.gnu.org/licenses/agpl.html). External dependencies packaged with
fun-apps have their own license.
