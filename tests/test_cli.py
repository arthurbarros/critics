# coding: utf-8
import json

import sys
from click.testing import CliRunner
import pytest

from critics import envvar_prefix
from critics.commands import cli


def test_no_locale():
    runner = CliRunner()
    result = runner.invoke(cli, ['--run-once'], env={'LC_CTYPE': '', 'LC_ALL': '', 'LANG': '', 'LANGUAGE': ''})
    exit_code = -1 if sys.version_info >= (3, 0) else 0  # click aborts if locale is not set up
    assert result.exit_code == exit_code


@pytest.mark.functional
def test_args(tmpdir):
    model = tmpdir.join("reviews.json")
    runner = CliRunner()
    result = runner.invoke(cli, ['--ios', '343200656',
                                 '--android', 'com.rovio.angrybirds',
                                 '--language', 'ru',
                                 '--model', model.strpath,
                                 '--run-once'],
                           env={'CRITICS_SLACK_WEBHOOK': 'http://httpbin.org/post',
                                'CRITICS_IOS_CHANNEL': '#ios',
                                'CRITICS_ANDROID_CHANNEL': '#android'},
                           auto_envvar_prefix=envvar_prefix)
    assert result.exit_code == 0

    # iOS rss feed returns either 10 or 0 reviews - probably a bug on Apple side,
    # sometimes the feed is just empty.
    num_reviews_ios = len(json.loads(model.read())['ios']['value'])
    num_reviews_android = len(json.loads(model.read())['android']['value'])

    assert num_reviews_ios in [0, 10]
    assert num_reviews_android == 10
    assert result.output == ('Languages: Russian\n'
                             'Tracking IOS apps: 343200656\n'
                             'Tracking Android apps: com.rovio.angrybirds\n'
                             'Transport: slack channels:   343200656 -> #ios   com.rovio.angrybirds -> #android\n'
                             'ios: 343200656: ru: Fetched %s reviews, %s new\n' % (num_reviews_ios, num_reviews_ios) +
                             'android: com.rovio.angrybirds: ru: Fetched 10 reviews, 10 new\n')


@pytest.mark.functional
def test_mutiple_languages(tmpdir):
    model = tmpdir.join("reviews.json")
    runner = CliRunner()
    result = runner.invoke(cli, ['--android', 'com.rovio.angrybirds',
                                 '--android', 'com.rovio.angrybirdsstarwarsii.ads',
                                 '--model', model.strpath,
                                 '--run-once', '--no-notify'],
                           env={'CRITICS_LANGUAGE': 'ru en'},
                           auto_envvar_prefix=envvar_prefix)
    assert result.exit_code == 0
    assert result.output == ('Languages: Russian, English\n'
                             'Tracking Android apps: com.rovio.angrybirds, com.rovio.angrybirdsstarwarsii.ads\n'
                             'android: com.rovio.angrybirds: ru: Fetched 10 reviews, 10 new\n'
                             'android: com.rovio.angrybirds: en: Fetched 10 reviews, 10 new\n'
                             'android: com.rovio.angrybirdsstarwarsii.ads: ru: Fetched 10 reviews, 10 new\n'
                             'android: com.rovio.angrybirdsstarwarsii.ads: en: Fetched 10 reviews, 10 new\n')
