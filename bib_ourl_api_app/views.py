# -*- coding: utf-8 -*-

import datetime, json, logging, os, pprint, urllib
from . import settings_app
from bib_ourl_api_app.lib import info_helper
from django.conf import settings as project_settings
from django.contrib.auth import logout
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from bib_ourl_api_app.lib.openurl import bib_from_openurl, openurl_from_bib


log = logging.getLogger(__name__)


def ourl_to_bib( request ):
    """ Converts openurl to bibjson. """
    log.debug( '\n\n\nstarting ourl_to_bib()...' )
    log.debug( 'request.__dict__, ```%s```' % pprint.pformat(request.__dict__) )
    start = datetime.datetime.now()
    ourl = request.GET.get( 'ourl', None )
    if not ourl:
        return HttpResponseBadRequest( '400 / Bad Request -- no `ourl` openurl parameter')
    log.debug( 'ourl initially, ```%s```' % ourl )
    # ourl = urllib.parse.unquote( urllib.parse.unquote(ourl) )
    ourl = urllib.parse.unquote( ourl )
    log.debug( 'ourl decoded, ```%s```' % ourl )
    bib = bib_from_openurl( ourl )
    log.debug( 'type(bib), `%s`' % type(bib) )
    log.debug( 'bib, ```%s```' % bib )
    rtrn_dct = {
        'query': {
            'date_time': str( start ),
            'url': '{schm}://{hst}{uri}'.format( schm=request.scheme, hst=request.META['HTTP_HOST'], uri=request.META.get('REQUEST_URI', request.META['PATH_INFO']) )
        },
        'response': {
            'bib': bib,
            'decoded_openurl': ourl,
            'elapsed_time': str( datetime.datetime.now() - start )
        }
    }
    jsn = json.dumps( rtrn_dct, sort_keys=True, indent=2 )
    return HttpResponse( jsn, content_type='application/javascript; charset=utf-8' )


def bib_to_ourl( request ):
    """ Converts bibjson to openurl. """
    log.debug( '\n\n\nstarting bib_to_ourl()...' )
    start = datetime.datetime.now()
    bibjson = request.GET.get( 'bibjson', None )
    if not bibjson:
        return HttpResponseBadRequest( '400 / Bad Request -- no `bibjson` parameter')
    bibjson = urllib.parse.unquote( bibjson )
    bib = json.loads( bibjson )
    ourl = openurl_from_bib( bib )
    log.debug( 'ourl, ```%s```' % ourl )
    rtrn_dct = {
        'query': {
            'date_time': str( start ),
            'url': '{schm}://{hst}{uri}'.format( schm=request.scheme, hst=request.META['HTTP_HOST'], uri=request.META.get('REQUEST_URI', request.META['PATH_INFO']) )
        },
        'response': {
            'openurl': ourl,
            'elapsed_time': str( datetime.datetime.now() - start ),
            'decoded_bibjson': bibjson
        }
    }
    jsn = json.dumps( rtrn_dct, sort_keys=True, indent=2 )
    return HttpResponse( jsn, content_type='application/javascript; charset=utf-8' )


def info( request ):
    """ Returns basic data including branch & commit. """
    log.debug( 'user-agent, ```%s```; ip, ```%s```; referrer, ```%s```' %
        (request.META.get('HTTP_USER_AGENT', None), request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_REFERER', None)) )
    rq_now = datetime.datetime.now()
    commit = info_helper.get_commit()
    branch = info_helper.get_branch()
    info_txt = commit.replace( 'commit', branch )
    resp_now = datetime.datetime.now()
    taken = resp_now - rq_now
    context_dct = info_helper.make_context( request, rq_now, info_txt, taken )
    output = json.dumps( context_dct, sort_keys=True, indent=2 )
    return HttpResponse( output, content_type='application/json; charset=utf-8' )


def error_check( request ):
    """ For checking that admins receive error-emails. """
    if project_settings.DEBUG == True:
        1/0
    else:
        return HttpResponseNotFound( '<div>404 / Not Found</div>' )
