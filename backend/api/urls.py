from django.urls import path
from .views import (home,home2,scorecard_info,resistance_info,isolation_info,login_page,signup_view, login_user, upload_dataset, dataset_upload, 
                mapping_dataset, isolation_burden_analysis, generate_isolation_graph,
                resistance_analysis, generate_resistance_graph, logout_view, scorecards, generate_scorecards, video, get_unique_values, get_columns_with_suffix, synthetic_dataset_creation, generate_synthetic_dataset, check_file_format, check_file_content, check_dataset_structure, check_mapping)

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
    path('video/', video, name='video'),
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
    # path('generate_scorecards_test/',generate_scorecards_test, name='generate_scorecards_test'),

    path('logout/', logout_view, name='logout'),
    path('get_unique_values/', get_unique_values, name='get_unique_values'),
    path('get_columns_with_suffix/', get_columns_with_suffix, name='get_columns_with_suffix'),
    path('synthetic_dataset_creation/', synthetic_dataset_creation, name='synthetic_dataset_creation'),
    path('generate_synthetic_dataset/', generate_synthetic_dataset, name='generate_synthetic_dataset'),
    path('api/check-file-format', check_file_format, name='check_file_format'),
    path('api/check-file-content', check_file_content, name='check_file_content'),
    path('api/check-dataset-structure', check_dataset_structure, name='check_dataset_structure'),
    path('api/check-mapping', check_mapping, name='check_mapping'),
]
