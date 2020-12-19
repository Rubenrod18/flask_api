"""Models registered in Swagger."""
from .auth import (auth_login_sw_model, auth_user_reset_password_sw_model,
                   auth_token_sw_model, auth_user_reset_password_token_sw_model)
from .core import (creator_sw_model, search_input_sw_model)
from .document import (document_sw_model, document_output_sw_model,
                       document_search_output_sw_model)
from .role import (role_sw_model, role_input_sw_model, role_output_sw_model,
                   role_search_output_sw_model)
from .user import (user_sw_model, user_input_sw_model, user_output_sw_model)
