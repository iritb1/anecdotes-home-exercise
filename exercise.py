import json

import uvicorn
import logging
from fastapi import FastAPI, Request  
from fastapi.templating import Jinja2Templates 
from fastapi_utils.tasks import repeat_every
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from fastapi.openapi.docs import get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html
from fastapi.responses import HTMLResponse

from config import *


app = FastAPI(title="anecdotes", description="receive a collected raw evidence",
              version="1.0.6", docs_url="/doc", redoc_url="/redoc")

# Add Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


logger = logging.getLogger("welcome")
logger.setLevel(logging.DEBUG)
STATIC_FOLDER = 'static' 

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/evidence", response_class=HTMLResponse)
async def evidence(request: Request):
     #axios.get("api/evidence",{evidence:[{},{},{} ...]})
     evidence_payload = json.loads(await request.body())['evidences'] #loads json from client
     
     
     # evidence_payload = [ {
     # 'evidence_id': 1, 
     # 'evidence_data': [{'login_name': 'anecdotes-exercise',
     #                     'role': 'owner',
     #                     'user_details': {'updated_at': '2021-07-26T09:41:56Z', 'id': 120000, 'email':
     #                     'exercise@anecdotes.ai', 'first_name': 'anec', 'last_name': 'dotes'},
     #                     'security': {'mfa_enabled':True, 'mfa_enforced': True}}]
     #                     },
                         
     #                     {
     # 'evidence_id': 2, 
     # 'evidence_data': [{'login_name': 'anecdotes-exercise',
     #                     'role': 'owner',
     #                     'user_details': {'updated_at': '2021-07-26T09:41:56Z', 'id': 1000, 'email':
     #                     'exercise@andsdotes.ai', 'first_name': 'anec', 'last_name': 'dotes'},
     #                     'security': {'mfa_enabled':True, 'mfa_enforced': True}}]
     #                     }
     #                     ]
     
     new_config = {}

     #map config file
     for item in config:
          new_config[item['field']] = item
     
     data_list = []
     for evidence in evidence_payload:
          keys = evidence.keys()
          for key in keys:
               if key in new_config:
                    # if 'type' in new_config[key] and new_config[key]['type'] == 'list':
                    #checking if val is id 
                    evidance_id = evidence['evidence_id']

                    if isinstance( evidence[key], list):
                         for evidence_data in evidence[key]:
                              data = []
                              #creating value list
                              for k,v in evidence_data.items():
                                   if isinstance(v ,dict):
                                        data = data + list(v.values()) #combine between lists
                                   else:
                                        data.append(v)

                              data.append(evidance_id)
                              data_list.append(data)

               else:
                    print("key in not in map config")


     text = '''<html>
               <header>
               <table border=1 style='text-align:center'>
               <tr>
          '''

     for header in config:
          if header['title'] == 'evidence_data':
               continue

          if 'keys' in header:
               for key in header['keys']:
                    if key != 'security':
                         text = text + f"""<th>{key}</th>"""
          else:
               text = text + f"""<th>{header['title']}</th>"""
     text = text + "</tr>"
          

     table = ""
     for sub_list in data_list:
          table = table + "<tr>"
          for item in sub_list:
               table = table + f"""<td>{item}</td>"""
          table = table + "</tr>"

     text = text + table + '</table> </header> </html>'

     return text



@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=True)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()



# Offline Serving of API Docs 
@app.get("/docs", include_in_schema=True)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/html/swagger-ui-bundle.js",
        swagger_css_url="/html/swagger-ui.css",
    )


##
#   Background Process
##
counter = 0
@app.on_event("startup")
@repeat_every(seconds=300, logger=logger, wait_first=True)
def periodic():
    global counter
    print('background worker called ' + str(counter))
    counter += 1


# Startup
@app.on_event("startup")
def startup():
    print('running startup')


# Shutdown
@app.on_event("shutdown")
def shutdown():
    print('shutting down')

app.mount('/', StaticFiles(directory=STATIC_FOLDER), name=STATIC_FOLDER)
templates = Jinja2Templates(directory=STATIC_FOLDER)




if __name__=='__main__':
    uvicorn.run(app, host='0.0.0.0', port=5000)






