"""
AjaxNavMiddleware
-----------------
When a request carries  X-Ajax-Nav: 1  (our AJAX navigation header),
the server renders the full page normally but then strips it down to
only the parts the client actually needs and returns a compact JSON
response (~90 % smaller than full HTML).

The HTML is annotated with sentinel comments in base.html:
    <!--AX:BC-->   body-class   <!--/AX:BC-->
    <!--AX:TITLE-->  page title <!--/AX:TITLE-->
    <!--AX:NAVT-->  topbar title  <!--/AX:NAVT-->
    <!--AX:NAVA-->  topbar actions <!--/AX:NAVA-->
    <!--AX:MAIN-->  main-content div <!--/AX:MAIN-->
    <!--AX:MSGS-->  flash messages  <!--/AX:MSGS-->
"""

import json
import re

from django.http import HttpResponse

# Pre-compiled sentinel patterns — O(n) scan, run once per AJAX request
_PATTERNS = {
    'title':   re.compile(r'<!--AX:TITLE-->(.*?)<!--/AX:TITLE-->',   re.DOTALL),
    'bc':      re.compile(r'<!--AX:BC-->(.*?)<!--/AX:BC-->',         re.DOTALL),
    'navT':    re.compile(r'<!--AX:NAVT-->(.*?)<!--/AX:NAVT-->',     re.DOTALL),
    'navA':    re.compile(r'<!--AX:NAVA-->(.*?)<!--/AX:NAVA-->',     re.DOTALL),
    'main':    re.compile(r'<!--AX:MAIN-->(.*?)<!--/AX:MAIN-->',     re.DOTALL),
    'msgs':    re.compile(r'<!--AX:MSGS-->(.*?)<!--/AX:MSGS-->',     re.DOTALL),
}


def _extract(pattern, html):
    m = pattern.search(html)
    return m.group(1).strip() if m else ''


class AjaxNavMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if (request.headers.get('X-Ajax-Nav') != '1'
                or response.status_code != 200
                or 'text/html' not in response.get('Content-Type', '')):
            return response

        html = response.content.decode('utf-8', errors='replace')

        payload = json.dumps({
            'title': _extract(_PATTERNS['title'], html),
            'bc':    _extract(_PATTERNS['bc'],    html),
            'navT':  _extract(_PATTERNS['navT'],  html),
            'navA':  _extract(_PATTERNS['navA'],  html),
            'main':  _extract(_PATTERNS['main'],  html),
            'msgs':  _extract(_PATTERNS['msgs'],  html),
        }, ensure_ascii=False)

        compact = HttpResponse(payload, content_type='application/json; charset=utf-8')
        # Forward session/auth cookies so login state is preserved
        for key in ('Set-Cookie', 'Vary'):
            if key in response:
                compact[key] = response[key]
        return compact
