cis-crowd
=========

Gene Transcription Factor Annotation Engine.


SETUP INSTRUCTIONS:

- Get web2py by cloning https://github.com/web2py/web2py/  
  Install it for example in a directory named web2py-ciscrowd.

- Apply this very important patch to web2py: 


diff --git a/gluon/contrib/login_methods/gae_google_account.py b/gluon/contrib/login_methods/gae_google_account.py
index 49b435b..ee3dd46 100644
--- a/gluon/contrib/login_methods/gae_google_account.py
+++ b/gluon/contrib/login_methods/gae_google_account.py
@@ -35,4 +35,5 @@ class GaeGoogleAccount(object):
         user = users.get_current_user()
         if user:
             return dict(nickname=user.nickname(), email=user.email(),
+                        registration_id=user.user_id(),
                         user_id=user.user_id(), source="google account")


- In the site-packages/ folder, install gae-pytz from https://code.google.com/p/gae-pytz/

- Install the code in this repository in the /applications folder, using for instance:
  git clone git@github.com:lucadealfaro/cis-crowd.git applications/ciscrowd
  (note that no dashes are allowed in application names).
  
- Copy the various files in applications/ciscrowd/gae-setup to the top level.

- Adjust app.yaml to reflect your app id and version you wish to deploy to.

- run it with:
  google_appengine/dev_appserver.py web2py-ciscrowd/
  where the argument is the directory where you have installed web2py.
