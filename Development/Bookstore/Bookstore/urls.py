from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    # Examples:
    # url(r'^$', 'Bookstore.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^store/', include('store.urls')),
    url(r'^account/',include('registration.backends.default.urls')),
    url(r'',include('social.apps.django_app.urls', namespace='social')),
    url(r'^admin/', include(admin.site.urls)),
]
