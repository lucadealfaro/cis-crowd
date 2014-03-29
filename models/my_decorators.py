# Decorator used to check whether the user is logged in.
# A user needs to be both logged in in the web2py sense,
# and in the google sense.  If a user is not logged in,
# the user is redirected to a special 'facade' page.
def requires_login(fn):
    def f():
        current.props = None
        if auth.user is None and get_user_email() is not None:
            # We need to renew the web2py session.
            if current.request.ajax:
                raise HTTP(401, 'Not authorized')
            elif current.request.is_restful:
                raise HTTP(403, "Not authorized")
            else:
                next = current.request.env.request_uri
                current.session.flash = current.response.flash
                return redirect(URL('default', 'user', args=['login'])
                        + '?_next=' + urllib.quote(next))            
        elif get_user_email() is None:
            # We go to the login page.
            if current.request.ajax:
                raise HTTP(401, 'Not authorized')
            elif current.request.is_restful:
                raise HTTP(403, "Not authorized")
            else:
                next = current.request.env.request_uri
                current.session.flash = current.response.flash
                return redirect(URL('default', 'login', vars=dict(next=next)))
        else:
            return fn()
    return f


# This decorator is similar to the above, but rather than requiring login,
# simply checks whether one is logged in.
def checks_login(fn):
    def f():
        current.props = None
        if auth.user is None and get_user_email() is not None:
            # We need to renew the web2py session.
            if current.request.ajax:
                raise HTTP(401, 'Not authorized')
            elif current.request.is_restful:
                raise HTTP(403, "Not authorized")
            else:
                next = current.request.env.request_uri
                current.session.flash = current.response.flash
                return redirect(URL('default', 'user', args=['login'])
                        + '?_next=' + urllib.quote(next))            
        elif get_user_email() is None:
            # Not logged in.
            return fn()
        else:
            return fn()
    return f


# This decorator forces users to complete their profile before proceeding.
def requires_first_last_name(fn):
    def f():
        if auth.user is not None:
            if (auth.user.first_name is None or auth.user.first_name == '' or
                auth.user.last_name is None or auth.user.last_name == ''):
                session.flash = T('Please complete your profile, entering your first and last names.')
                return redirect(URL('default', 'user', args=['profile'], 
                                    vars=dict(_next=current.request.env.request_uri)))
        return fn()
    return f
