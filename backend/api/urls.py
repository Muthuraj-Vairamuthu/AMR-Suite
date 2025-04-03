from django.urls import path
from .views import (home,home2,scorecard_info,resistance_info,isolation_info,login_page,signup_view, login_user, upload_dataset, dataset_upload, 
                mapping_dataset, isolation_burden_analysis, generate_isolation_graph,
                resistance_analysis, generate_resistance_graph, logout_view, scorecards, generate_scorecards)

urlpatterns = [

    # path('', scorecard_info, name='scorecard_info'),
    # path('', resistance_info, name='resistance_info'),
    # path('', isolation_info, name='isolation_info'),
    path('', home, name='home'),

    path('home2', home2, name='home2'),
    path('login/', login_page, name='login'),
    path('signup/', signup_view, name='signup'), 
    path('login-user/', login_user, name='login_user'),
    path('isolation-info/', isolation_info, name='isolation_info'),
    path('resistance-info/', resistance_info, name='resistance_info'),
    path('scorecard-info/', scorecard_info, name='scorecard_info'),
 

    path('upload_dataset/', upload_dataset, name='upload_dataset'),
    path('dataset_upload', dataset_upload, name='dataset_upload'),
    path('process_mapping/', mapping_dataset, name='mapping_dataset'),
    path('isolation_burden_analysis', isolation_burden_analysis, name='isolation_burden_analysis'),
    path('generate_isolation_graph', generate_isolation_graph, name='generate_isolation_graph'),
    path('resistance_analysis', resistance_analysis, name='resistance_analysis'),
    path('generate_resistance_graph', generate_resistance_graph, name='generate_resistance_graph'),
    path('scorecards/', scorecards, name='scorecards'),
    path('generate_scorecards', generate_scorecards, name='generate_scorecards'),
    # path('check-scorecard-data/', check_scorecard_data, name='check_scorecard_data'),

    path('logout/', logout_view, name='logout'),
]
