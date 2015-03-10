# coding: utf-8
import codecs
import datetime
import responses
from critics.parsers import get_ios_reviews, get_android_reviews


@responses.activate
def test_ios():
    responses.add(responses.GET, 'https://itunes.apple.com/ru/rss/customerreviews/id=123/sortBy=mostRecent/xml',
                  body=codecs.open('tests/fixtures/itunes_fr.example', encoding='utf-8').read(),
                  content_type='application/xml; charset=UTF-8')
    reviews = get_ios_reviews(123)

    assert len(reviews) == 50

    review = reviews[0]
    assert review.id == u'1163882289'
    assert review.title == u'Leon, super jeu'
    assert review.rating == 5
    assert review.summary == u'Moi qui ne suis pas n grand amateur, j\'ai adoré ce jeu malin et intuitif.'
    assert review.url == u'https://itunes.apple.com/fr/review?id=400274934&type=Purple%20Software'
    assert review.author == u'Justine M18'
    assert review.date == datetime.datetime(2015, 3, 5, 20, 5)
    assert review.version == '1.7'

    assert str(review) == """Review (1163882289):
title=Leon, super jeu
rating=5
summary=Moi qui ne suis pas n grand amateur, j'ai adoré ce jeu malin et intuitif.
url=https://itunes.apple.com/fr/review?id=400274934&type=Purple%20Software
author=Justine M18
date=2015-03-05 20:05:00
version=1.7"""


@responses.activate
def test_android():
    responses.add(responses.POST, 'https://play.google.com/store/getreviews',
                  body=codecs.open('tests/fixtures/gp_ru.example', encoding='utf-8').read(),
                  content_type='application/json; charset=UTF-8')
    reviews = get_android_reviews('com.skype.raider', limit=10)

    assert len(reviews) == 10

    review = reviews[0]
    assert review.id == u'gp:AOqpTOGVTpUWQyZJhCbF6dpGfgWnmaj992am2upoCj8Iur1YoNKubAlN_W_BzRYHGh7pdxAe-HDIdOUEvaRfpw'
    assert review.title == u'Не работает'
    assert review.rating == 1
    assert review.summary == u'Не работает видео связь на nvidia shield'
    assert review.url == u'https://play.google.com/store/apps/details?id=com.skype.raider&reviewId=Z3A6QU9xcFRPR1ZUcFVXUXlaSmhDYkY2ZHBHZmdXbm1hajk5MmFtMnVwb0NqOEl1cjFZb05LdWJBbE5fV19CelJZSEdoN3BkeEFlLUhESWRPVUV2YVJmcHc'  # noqa
    assert review.author == u'Polar Alexander'
    assert review.date == u'7 марта 2015 г.'
    assert review.version is None