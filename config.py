config = [
     {
          'title': 'id',
          'field': 'evidence_id'
     },
     {
          'title': 'evidence_data',
          'field': 'evidence_data',
          'type' : 'list'
     },
     {
          'title': 'login_name',
          'field': 'login_name'
     },
     {
          'title': 'role',
          'field': 'role'
     },
     {
          'title': 'user_details',
          'field': 'user_details',
          'type': 'dict',
          'keys' : ['updated_at','id','email','first_name','anec','last_name','security'],#dict keys list
     },
    {
          'title': 'security',
          'field': 'security',
          'type': 'dict',
          'keys' : ['mfa_enabled','mfa_enforced'],#dict keys list
     }
]


# Dictionery =[ {
#      “evidence_id”: 1, 
#      “evidence_data”: [{“login_name”: “anecdotes-exercise”,
#                          “role”: “owner”,
#                          “user_details”: {“updated_at”: “2021-07-26T09:41:56Z”, id: 120000, email:
#                          “exercise@anecdotes.ai”, “first_name”: “anec”, “last_name”: “dotes”},
#                          “security”: {“mfa_enabled”:True, “mfa_enforced”: True}}]}]
