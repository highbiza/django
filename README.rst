======
Django
======

Django is a high-level Python Web framework that encourages rapid development
and clean, pragmatic design. Thanks for checking it out.

All documentation is in the "``docs``" directory and online at
https://docs.djangoproject.com/en/stable/. If you're just getting started,
here's how we recommend you read the docs:

* First, read ``docs/intro/install.txt`` for instructions on installing Django.

* Next, work through the tutorials in order (``docs/intro/tutorial01.txt``,
  ``docs/intro/tutorial02.txt``, etc.).

* If you want to set up an actual deployment server, read
  ``docs/howto/deployment/index.txt`` for instructions.

* You'll probably want to read through the topical guides (in ``docs/topics``)
  next; from there you can jump to the HOWTOs (in ``docs/howto``) for specific
  problems, and check out the reference (``docs/ref``) for gory details.

* See ``docs/README`` for instructions on building an HTML version of the docs.

Docs are updated rigorously. If you find any problems in the docs, or think
they should be clarified in any way, please take 30 seconds to fill out a
ticket here: https://code.djangoproject.com/newticket

To get more help:

* Join the ``#django`` channel on ``irc.libera.chat``. Lots of helpful people
  hang out there. See https://web.libera.chat if you're new to IRC.

* Join the django-users mailing list, or read the archives, at
  https://groups.google.com/group/django-users.

To contribute to Django:

* Check out https://docs.djangoproject.com/en/dev/internals/contributing/ for
  information about getting involved.

To run Django's test suite:

* Follow the instructions in the "Unit tests" section of
  ``docs/internals/contributing/writing-code/unit-tests.txt``, published online at
  https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/unit-tests/#running-the-unit-tests

Supporting the Development of Django
====================================

Django's development depends on your contributions. 

If you depend on Django, remember to support the Django Software Foundation: https://www.djangoproject.com/fundraising/

Backported Security Fixes
=========================

This fork is based on Django 3.2.26. The following security fixes have been
manually backported from newer Django versions since they were not included
in the official 3.2.x releases.

* **CVE-2024-39329** -- Standardized timing of verify_password() when checking unusable passwords. (`75e5369 <https://github.com/django/django/commit/75e53690cd>`_, `GHSA-x7q2-wr7g-xqmf <https://github.com/advisories/GHSA-x7q2-wr7g-xqmf>`_)
* **CVE-2024-39330** -- Added extra file name validation in Storage's save method. (`cd23775 <https://github.com/django/django/commit/cd237758d6>`_, `GHSA-7m5c-fgwf-mwph <https://github.com/advisories/GHSA-7m5c-fgwf-mwph>`_)
* **CVE-2024-39614** -- Mitigated potential DoS in get_supported_language_variant(). (`d8c27e0 <https://github.com/django/django/commit/d8c27e0751>`_, `GHSA-jmrc-ghpg-mf2w <https://github.com/advisories/GHSA-jmrc-ghpg-mf2w>`_)
* **CVE-2024-41989** -- Mitigated potential DoS in floatformat template filter. (`fc76660 <https://github.com/django/django/commit/fc76660f58>`_, `GHSA-jh75-99hh-qvx9 <https://github.com/advisories/GHSA-jh75-99hh-qvx9>`_)
* **CVE-2024-41990** -- Mitigated potential DoS in urlize and urlizetrunc template filters. (`d0a82e2 <https://github.com/django/django/commit/d0a82e26a7>`_, `GHSA-795c-9xpc-xw6g <https://github.com/advisories/GHSA-795c-9xpc-xw6g>`_)
* **CVE-2024-41991** -- Prevented potential ReDoS in django.utils.html.urlize() and AdminURLFieldWidget. (`efea1ef <https://github.com/django/django/commit/efea1ef7e2>`_, `GHSA-r836-hh6v-rg5g <https://github.com/advisories/GHSA-r836-hh6v-rg5g>`_)
* **CVE-2024-42005** -- Mitigated QuerySet.values() SQL injection attacks against JSON fields. (`f4af67b <https://github.com/django/django/commit/f4af67b9b4>`_, `GHSA-pv4p-cwwg-4rph <https://github.com/advisories/GHSA-pv4p-cwwg-4rph>`_)
* **CVE-2024-45230** -- Mitigated potential DoS in urlize and urlizetrunc template filters. (`d147a8e <https://github.com/django/django/commit/d147a8ebbd>`_, `GHSA-5hgc-2vfp-mqvc <https://github.com/advisories/GHSA-5hgc-2vfp-mqvc>`_)
* **CVE-2024-45231** -- Avoided server error on password reset when email sending fails. (`bf4888d <https://github.com/django/django/commit/bf4888d317>`_, `GHSA-rrqc-c2jx-6jgv <https://github.com/advisories/GHSA-rrqc-c2jx-6jgv>`_)
* **CVE-2024-53907** -- Mitigated potential DoS in strip_tags(). (`790eb05 <https://github.com/django/django/commit/790eb058b0>`_, `GHSA-8498-2h75-472j <https://github.com/advisories/GHSA-8498-2h75-472j>`_)
* **CVE-2024-53908** -- Prevented SQL injections in direct HasKeyLookup usage. (`7376bcb <https://github.com/django/django/commit/7376bcbf50>`_, `GHSA-m9g8-fxxm-xg86 <https://github.com/advisories/GHSA-m9g8-fxxm-xg86>`_)
* **CVE-2025-32873** -- Mitigated potential DoS in strip_tags() (second round). (`9cd8028 <https://github.com/django/django/commit/9cd8028f3e>`_, `GHSA-8j24-cjrq-gr2m <https://github.com/advisories/GHSA-8j24-cjrq-gr2m>`_)
* **CVE-2025-48432** -- Escaped formatting arguments in log_response() to prevent log injection. (`ac03c5e <https://github.com/django/django/commit/ac03c5e7df>`_, `GHSA-7xr5-9hcq-chf9 <https://github.com/advisories/GHSA-7xr5-9hcq-chf9>`_). Follow-ups: routed SuspiciousOperation and generic view logging through log_response() (`10ba3f7 <https://github.com/django/django/commit/10ba3f78da>`_, `b597d46 <https://github.com/django/django/commit/b597d46bb1>`_).
* **CVE-2025-57833** -- Protected FilteredRelation against SQL injection in column aliases. (`31334e6 <https://github.com/django/django/commit/31334e6965>`_, `GHSA-6w2r-r2m5-xq5w <https://github.com/advisories/GHSA-6w2r-r2m5-xq5w>`_)
* **CVE-2025-64458** -- Mitigated potential DoS in HttpResponseRedirect via URL length. (`770eea3 <https://github.com/django/django/commit/770eea38d7>`_, `GHSA-qw25-v68c-qjf3 <https://github.com/advisories/GHSA-qw25-v68c-qjf3>`_). Follow-up: increased redirect limit from 2048 to 16384 (`e697349 <https://github.com/django/django/commit/e697349037>`_).
* **CVE-2025-64459** -- Prevented SQL injections in Q/QuerySet via the _connector kwarg. (`59ae82e <https://github.com/django/django/commit/59ae82e670>`_, `GHSA-frmv-pr5f-9mcr <https://github.com/advisories/GHSA-frmv-pr5f-9mcr>`_). Follow-up: blocked _connector/_negated in QuerySet.filter() kwargs (`279f8b9 <https://github.com/django/django/commit/279f8b9557>`_).
* **CVE-2025-64460** -- Fixed quadratic inner text accumulation in XML deserializer. (`4d2b880 <https://github.com/django/django/commit/4d2b8803be>`_, `GHSA-vrcr-9hj9-jcg6 <https://github.com/advisories/GHSA-vrcr-9hj9-jcg6>`_)
* **CVE-2025-13372** -- Protected FilteredRelation against SQL injection in column aliases on PostgreSQL. (`f997037 <https://github.com/django/django/commit/f997037b23>`_, `GHSA-rqw2-ghq9-44m7 <https://github.com/advisories/GHSA-rqw2-ghq9-44m7>`_)

Test compatibility fixes:

* **tblib 3.2+ pickle test compat** -- Added ``__reduce__`` to test exception class. (`cd3b21b <https://github.com/django/django/commit/cd3b21bcaccf03a1dc49512bdb8efd796fba8100>`_)
* **Python HTMLParser behavior changes** -- Adjusted strip_tags tests for Python 3.10.19+ / 3.11.14+ / 3.12.12+ / 3.13.6+. (`c3f9871 <https://github.com/django/django/commit/c3f98718976820da5123169027612324d09a89d6>`_, `7b3e75f <https://github.com/django/django/commit/7b3e75f73186381a9ec1e7de64e8389aae2e3435>`_, `a28c3c7 <https://github.com/django/django/commit/a28c3c739564ccc2aabc7b20211f54d838c7b582>`_)
