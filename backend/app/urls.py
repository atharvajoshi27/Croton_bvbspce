from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name='index'),
    # path("stock/data/<str:ticker>", views.stock_info, name='stock-info'),
    # path("stock/predictions/<str:ticker>", views.stock_predictions, name='stock-predictions'),
    # path("stock/news/<str:ticker>", views.stock_news, name='stock-news'),
    # path("scheduled/table_update", views.cron_helper, name='cron-table-update'),
    # path("scheduled/train_models", views.cron_train_models, name='cron-train-models'),
    # path("api/all_tickers", views.StockInfoSerializerView.as_view(), name='all-tickers'),
    # path("api/<str:ticker>", views.RetrieveDataView.as_view(), name='my-api'),
    path("register", views.register, name='register'),
    path("login", views.log_in, name='login'),
    path("logout", views.log_out, name='logout'),
    # path("profile", views.profile, name='profile'),
    # path("faq", views.faq, name='faq'),
    # path("contact", views.contact, name='contact'),
    # path("add_ticker", views.add_ticker, name='add-ticker'),
    # path("remove_ticker", views.remove_ticker, name='remove-ticker'),
    # path("update_profile", views.update_profile, name='update-profile'),
    # path("change_password", views.change_password, name='change-password'),
]