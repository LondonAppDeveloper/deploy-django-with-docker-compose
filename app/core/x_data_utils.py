# pip install
## Django>=3.2.3,<3.3
## Markdown==3.6

from django.db import models
from core.models import UserIDList, Answers #core.models could change e.g. api.models
#from markdown import markdown # type: ignore
import uuid
import markdown

# copy to models.py the following lines and uncomment those lines
################ models.py ####################
# class UserIDList(models.Model):
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     userid = models.CharField(max_length=200)
#     def __str__(self):
#         return self.userid

# class Answers(models.Model):
#     userid = models.ForeignKey(UserIDList, on_delete=models.CASCADE)
#     question_type_id = models.PositiveIntegerField(default=1)
#     data = models.JSONField(default=list,null=True,blank=True)
#     def __str__(self):
#         return self.userid.userid
################## models.py end #####################

markdown_flag = True

### main function to set DB-data ###################### 
# http://127.0.0.1:8000/api/question/1/8/
def answer_post_view(question_type_id, question_id, action='getDBObject', userID="efd69e9c-3945-4885-9a06-c9216efec82b", answer=""):
    obj, config = get_interview_config_db({}, question_type_id, question_id, action=action, userID=userID) 
    obj = set_answer(obj, config, answer)
    return obj, config

def set_answer(object, config, answer):
    object.data[config['answer_label']] = answer
    object.save()
    return object

### main function to get DB-data ###################### 
# http://127.0.0.1:8000/api/question/1/8/
def get_interview_config_db(request, question_type_id, question_id, action='getDBObject', userID="efd69e9c-3945-4885-9a06-c9216efec82b"):
    # API-Access: use action='getDBObject' and the specific userID
    # otherwise use standard  
    userid = user_id(action, request, userID=userID)
    if not userid:
        return None, None
    answer = Answers.objects.filter(userid=userid, question_type_id=question_type_id)
    if not answer.exists():    
        interview_config = get_all_interview_data_db(question_type_id)
        Answers.objects.create(userid=userid, question_type_id=question_type_id, data={'interview_config': interview_config}) 
    object = Answers.objects.get(userid=userid, question_type_id=question_type_id)  
    config = get_interview_config(question_type_id, question_id, object=object) 
    return object, config

def user_id(action, request=[], userID="efd69e9c-3945-4885-9a06-c9216efec82b"):
    if action == "getDBObject":
        # Überprüfe, ob eine UserID mit der gegebenen userID existiert
        if UserIDList.objects.filter(userid=userID).exists():
            return UserIDList.objects.get(userid=userID)
        else:
            return None
    elif action == "create":
        # Erzeuge eine neue UserID
        userIDValue = str(uuid.uuid4())  # Generiere eine UUID
        return userIDValue  # Gib die neu generierte UserID zurück
    return None  # Falls ein ungültiger action-Wert übergeben wurde, gib None zurück

def get_interview_config(question_type_id, question_id, object=None):
    if not question_type_id:
        question_type_id = 1
    if not question_id:
        question_id = 1

    if object:
        interview_config = object.data['interview_config']
    else:
        interview_config = get_all_interview_data_db(question_type_id)    

    start_page = interview_config['start_page']
    end_page = interview_config['end_page']
    order = interview_config['order']

    real_num_of_questions = interview_config['real_num_of_questions']
    number_of_questions = interview_config['number_of_questions']
    institution = interview_config['institution']
    type = interview_config['type']
    
    real_question_nr = interview_config['real_question_nrs'][question_id-1] # starts with zero
    answer_label = order[question_id-1] # starts with zero
    io_type = interview_config[answer_label]['io_type']
    question_title = interview_config[answer_label]['question_title']
    question_title_description = interview_config[answer_label]['question_title_description']
    answer_template = interview_config[answer_label]['answer_template']
    if io_type == "selectable" and real_question_nr: #sort only questions analysis are ordered by fitting
        all_elements = sorted(interview_config[answer_label]['all_elements'])
    else:
        all_elements = interview_config[answer_label]['all_elements']

    # set properties which are not existent
    props_string = ["summary", "prompt_type", "prompt_type_ext", "add_detail", "source"]
    props_dict = ["branches", "generate"]
    props_list = []
    interview_config = set_missing_props(interview_config, answer_label, 
                                         props_string=props_string, 
                                         props_dict=props_dict, props_list=props_list)
    
    summary = interview_config[answer_label]['summary']
    prompt_type = interview_config[answer_label]['prompt_type']
    prompt_type_ext = interview_config[answer_label]['prompt_type_ext']
    add_detail = interview_config[answer_label]['add_detail']
    branches = interview_config[answer_label]['branches']
    source = interview_config[answer_label]['source']
    generate = get_generate_context_prop(interview_config[answer_label])
    menue_pages = interview_config['menue_pages']
    #print(f"{generate=}")

    selected_elements = []
    if io_type in ['numerical', 'editable','generated']:
         selected_elements = ""
    if object:
        if answer_label in object.data.keys():
            selected_elements = object.data[answer_label]

    question_id_prev, question_id_next = get_next_prev_id(question_id, order, source, branches, 
                                                          selected_elements)
    
    io_type_target="generated"
    # io_type_target and question not yet generated filters all ids
    ids = get_question_id_of_io_type(interview_config, io_type=io_type_target)
    next_io_type = ""
    prev_io_type = ""
    
    if question_id_next in ids:
        next_io_type = io_type_target

    if question_id_prev in ids:
        prev_io_type = io_type_target    
    
    # set language
    #if interview_config['lang'] != get_language():
    #    activate(interview_config['lang'])

    config = {'institution':institution, 'type': type, 'question_type_id': question_type_id, 'question_id': question_id, 
              'question_id_prev': question_id_prev, 'question_id_next': question_id_next, 'prompt_type': prompt_type,
              'answer_label': answer_label, 'all_elements': all_elements, 'answer_template': answer_template ,'number_of_questions': number_of_questions, 
              'io_type': io_type, 'question_title': question_title, 'question_title_description': question_title_description,
              'start_page': start_page, 'end_page':end_page, 'next_io_type': next_io_type, 'prev_io_type': prev_io_type, "summary": summary,
              "real_question_nr": real_question_nr, "real_num_of_questions": real_num_of_questions, 
              'question_title_exists': (question_title != ""), 'prompt_type_ext': prompt_type_ext, 'branches': branches,
              'add_detail': add_detail, 'order_length': len(order), 'selected_elements': selected_elements, 'generate': generate, 'menue_pages': menue_pages
              }
    # 'generate' is a dictionary
    # 'generate': {'title':'.....', 'title_description':'........', 'qa':[{'question':'......', 'answer',''}, {'question':'......', 'answer',''} ], 
    #               'body':'......','add_detail':'.....'}
    return config 

def set_missing_props(config, answer_label, props_string=[], props_dict=[], props_list=[]):
    for prop in props_dict:
        if prop not in config[answer_label].keys():
            config[answer_label][prop] = {}
    for prop in props_string:
        if prop not in config[answer_label].keys():
            config[answer_label][prop] = ""
    for prop in props_list:
        if prop not in config[answer_label].keys():
            config[answer_label][prop] = []
    return config

def get_next_prev_id(question_id, order, source, branches, selected_elements):
    question_id_prev = question_id-1
    question_id_next = question_id+1

    for dest in branches.keys(): 
        if branches[dest] == len(selected_elements): #we distiguish only the number of selected_elements
            question_id_next = index_in_list(order, dest)+1
    if source != "":
        question_id_prev = index_in_list(order, source)+1
    return question_id_prev, question_id_next

def index_in_list(myList, element):
    if element in myList:
        return myList.index(element)
    else:
        return None

def get_question_id_of_io_type(interview_config, io_type=""):
    question_ids=[]
    order = interview_config['order']
    for question_id in range(1, len(order)+1):
        answer_label = order[question_id-1]
        io_type_this = interview_config[answer_label]['io_type']
        if io_type == io_type_this and interview_config[answer_label]['question_title'] == "": #not yet generated
            question_ids.append(question_id)
    return question_ids       

def set_initial_generate_prop(config, answer_label, llm_answer=""):
    # prepare data
    if config[answer_label]['io_type'] != "selectable":         
        programs, fits = get_programs(config[answer_label]['all_elements'])
    else:
        programs = ["",""]
        fits = ["",""]
    ncs = get_ncs(config, answer_label, programs)
    data_keys = {"<PROGRAM1>": programs[0], "<PROGRAM2>": programs[1], "<FIT1>": fits[0], "<FIT2>":fits[1], "<NC1>":ncs[0], "<NC2>":ncs[1]} 
    title = replace_key_words(config[answer_label]['question_title'], data_keys, c="")
    title_description = replace_key_words(config[answer_label]['question_title_description'], data_keys, c="")
    add_detail = replace_key_words(config[answer_label]['add_detail'], data_keys, c="")
    if not isinstance(llm_answer, dict):
        if markdown_flag:
            body = llm_answer
        else:      
            body = markdown(llm_answer, extensions=['tables'])
        #body = body.replace("<table>",'<table class="table table-sm table-bordered table-responsive border-primary table-condensed">')
    else:
        body = ""

    prop = get_prop(programs)
    if prop not in config[answer_label]['generate']:
        config[answer_label]['generate'][prop]={}
    config[answer_label]['generate'][prop] = {"title": title, "title_description": title_description, 
                                              "add_detail": add_detail, 'llm_answer':llm_answer, 
                                              "body": body, "query": "", "qa": []} 
    return config

def replace_key_words(mystring, data_keys, c = '"'):
    for key in data_keys.keys():
        mystring = mystring.replace(key, c+data_keys[key]+c) 
    return mystring

def get_ncs(config, answer_label, programs):
    ncs=["",""]
    source = config[answer_label]['source']
    if source != "":
        source_answer = config[source]['generate']['all']['llm_answer']
        for idx, key in zip(range(len(programs)), programs):
            if key != "":
                if 'NC' in source_answer[key]:
                    ncs[idx] = source_answer[key]['NC']
            
    return ncs

def get_generate_context_prop(context):
    if context['io_type'] == "text_edit": 
        programs, fits = get_programs(context['all_elements'])
        prop = get_prop(programs)
    else:
        prop = 'all'    
    if prop not in context['generate']:
        context['generate'][prop] = {}
    return context['generate'][prop]  

def get_prop(programs):
    prop = ""
    for program in programs:
        if prop != "":
            if program != "":
                prop += f"_{program}"
        else:
            if program != "":
                prop += program
    if prop == "":
        prop = "all" 
    return prop         

def get_programs(my_list=['Management, Economics and Social Science: Gut','Volkswirtschaft: Gut']):
    # return always two programs and the resp. fits
    programs = ["", ""]
    fits = ["", ""]
    my_list = sorted(my_list)
    for idx, item in zip(range(len(my_list)),my_list):
        pos = item.rfind(':')
        if pos > -1:
            program = item[0:pos].strip()
            fit = item[pos+1::].strip()
        else:
            program = item
            fit = ""    
        programs[idx] = program
        fits[idx] = fit
    return programs, fits

def get_all_interview_data_db(question_type_id):
    data={"A1": [], 
            "A2": [], 
            "A3": [], 
            "A4": "", 
            "A5": "", 
            "A6": "", 
            "A7": [], 
            "A8": [], 
            "A9": "", 
            "P1": [], 
            "S1": [], 
            "ANALYSIS1": [], 
            "interview_config": {
                        "lang": "de", 
                        "type": "bachelor", 
                        "order": ["S1", "A1", "A2", "A3", "A4", "A5", "A6", "P1", "A7", "A8", "A9", "ANALYSIS1", "ANALYSIS2", "ANALYSIS3"], 
                        "end_page": "home", 
                        "start_page": "start", 
                        "institution": "WiSo Fakultät an der Universität zu Köln", 
                        "menue_pages": [{"id": 2, "no": 1, "title": "Welche Fächer haben dich in der Schule interessiert?"}, {"id": 3, "no": 2, "title": "Was macht dir Spaß?"}, {"id": 4, "no": 3, "title": "Was magst du nicht?"}, {"id": 5, "no": 4, "title": "Wo liegt dein (voraussichtlicher) Abiturnotendurchschnitt?"}, {"id": 6, "no": 5, "title": "Wie siehst du deine berufliche Zukunft?"}, {"id": 7, "no": 6, "title": "Gibt es noch etwas, das ich über dich wissen sollte?"}, {"id": 9, "no": 7, "title": "Über welche Themenfelder möchtest du in deinem Studium mehr erfahren?"}, {"id": 10, "no": 8, "title": "Was ist dir im Studium wichtig?"}, {"id": 11, "no": 9, "title": "'Individual Generated Question'"}, {"id": 12, "no": None, "title": "Deine passenden Studiengänge"}], 
                        "question_items": ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9"], 
                        "real_question_nrs": [None, 1, 2, 3, 4, 5, 6, None, 7, 8, 9, None, None, None], 
                        "number_of_questions": 11, 
                        "real_num_of_questions": 9,
                        "A1": {"source": "", "io_type": "selectable", "summary": "", "branches": {}, 
                                "generate": {"all": {}}, "add_detail": "", "prompt_type": "", 
                                "all_elements": ["Mathe", "Kunst", "Physik", "Sport", "Philosophie", "Englisch", "Religion", "Technologie", "Musik", "Biologie", "Wirtschaft", "Chemie", "Soziales", "Geschichte", "Geographie", "Sprachen", "Deutsch", "Pädagogik", "Recht", "Psychologie", "Ernährung", "Informatik"], 
                                "question_title": "Welche Fächer haben dich in der Schule interessiert?", "answer_template": "Die folgenden Fächer haben mich in der Schule interessiert: ", "prompt_type_ext": "", "question_title_description": ""}, 
                        "A2": {"source": "", "io_type": "selectable", "summary": "", "branches": {}, 
                               "generate": {"all": {}}, "add_detail": "", "prompt_type": "", 
                               "all_elements": ["Mathe anwenden", "Schwere Matheprobleme lösen", "Kurse geben", "Ethische Fragen diskutieren", "Anderen etwas beibringen", "Projekte leiten", "Präsentieren", "Umweltthemen diskutieren", "Unternehmen verstehen", "Theorien verstehen", "Soziale Probleme diskutieren", "Programmieren", "Events organisieren", "Aktienmärkte verstehen", "Wirtschaftspolitik verstehen", "Musik komponieren", "Literatur interpretieren", "Fremdsprachen sprechen", "Instrumente spielen", "Kulturen erforschen", "Soziale Interaktionen verstehen", "Geschichtliche Entwicklungen analysieren", "Philosophische Theorien verstehen", "KI ausprobieren", "Menschen unterstützen", "Gesetzgebung verstehen", "Chemische Experimente durchführen", "Mathematische Modelle entwickeln", "Biologische Prozesse erforschen", "Verhaltensmuster analysieren", "Anatomie verstehen", "Argumentationsstrategien entwickeln", "Zusammenhänge im Körper untersuchen", "Naturwissenschaftliche Zusammenhänge analysieren"], 
                               "question_title": "Was macht dir Spaß?", "answer_template": "Ich mag die folgenden Aktivitäten: ", 
                               "prompt_type_ext": "", 
                               "question_title_description": ""}, 
                        "A3": {"source": "", "io_type": "selectable", "summary": "", "branches": {}, 
                               "generate": {"all": {}}, "add_detail": "", "prompt_type": "", 
                               "all_elements": ["Mathe anwenden", "Schwere Matheprobleme lösen", "Kurse geben", "Ethische Fragen diskutieren", "Anderen etwas beibringen", "Projekte leiten", "Präsentieren", "Umweltthemen diskutieren", "Unternehmen verstehen", "Theorien verstehen", "Soziale Probleme diskutieren", "Programmieren", "Events organisieren", "Aktienmärkte verstehen", "Wirtschaftspolitik verstehen", "Musik komponieren", "Literatur interpretieren", "Fremdsprachen sprechen", "Instrumente spielen", "Kulturen erforschen", "Soziale Interaktionen verstehen", "Geschichtliche Entwicklungen analysieren", "Philosophische Theorien verstehen", "KI ausprobieren", "Menschen unterstützen", "Gesetzgebung verstehen", "Chemische Experimente durchführen", "Mathematische Modelle entwickeln", "Biologische Prozesse erforschen", "Verhaltensmuster analysieren", "Anatomie verstehen", "Argumentationsstrategien entwickeln", "Zusammenhänge im Körper untersuchen", "Naturwissenschaftliche Zusammenhänge analysieren"], 
                               "question_title": "Was magst du nicht?", "answer_template": "Folgende Aktivitäten lehne ich ab: ", "prompt_type_ext": "", "question_title_description": ""}, 
                        "A4": {"source": "", "io_type": "numerical", "summary": "", "branches": {}, 
                               "generate": {"all": {}}, "add_detail": "", "prompt_type": "", 
                               "all_elements": ["0", "1.0", "1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "1.7", "1.8", "1.9", "2.0", "2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7", "2.8", "2.9", "3.0", "3.1", "3.2", "3.3", "3.4", "3.5", "3.6", "3.7", "3.8", "3.9", "4.0"], 
                               "question_title": "Wo liegt dein (voraussichtlicher) Abiturnotendurchschnitt?", "answer_template": "Mein Abiturnotendurchschnitt = ", "prompt_type_ext": "", 
                               "question_title_description": "Bereich zwischen 1.0 und 4.0?"}, 
                        "A5": {"source": "", "io_type": "editable", "summary": "", "branches": {}, 
                               "generate": {"all": {}}, "add_detail": "", "prompt_type": "", 
                               "all_elements": [], 
                               "question_title": "Wie siehst du deine berufliche Zukunft?", "answer_template": "", "prompt_type_ext": "", 
                               "question_title_description": "Sag mir bitte, ob du einen konkreten Berufswunsch hast, ob dich gewisse Branchen interessieren und ob du konkrete Arbeitgeber im Blick hast. Oder möchtest du ein Startup gründen? Je mehr ich über deine Berufsziele weiß, desto besser kann ich dich beraten!"}, 
                        "A6": {"source": "", "io_type": "editable", "summary": "", "branches": {}, 
                               "generate": {"all": {}}, "add_detail": "", "prompt_type": "", 
                               "all_elements": [], 
                               "question_title": "Gibt es noch etwas, das ich über dich wissen sollte?", "answer_template": "", "prompt_type_ext": "", 
                               "question_title_description": "Gibt es weitere Dinge, die mir helfen, den passenden Studiengang für dich zu finden. Das könnte z.B. deine Stärken und Schwächen oder Interessen außerhalb der Schule sein."}, 
                        "A7": {"source": "", "io_type": "selectable", "summary": "", "branches": {}, 
                               "generate": {"all": {}}, "add_detail": "", "prompt_type": "", 
                               "all_elements": ["Datenanalyse", "Finanzmanagement", "Zivilrecht", "Marketingstrategien", "Verhaltensökonomie", "Internationale Wirtschaft", "Nachhaltigkeit & Umwelt", "Start-Up Gründung", "Sozialpsychologie", "Genetik", "IT Projektmanagement", "Algorithmen", "Strafrecht", "Gesundheitsmanagement", "Soziale Themen", "Unternehmensführung", "Literatur", "Geschichtsepochen", "Fremdsprachen", "Pädagogische Methodik", "Musikalische Strukturen", "Entwicklungspsychologie", "Medientheorie", "Spracherwerb", "Soziale Strukturen", "Umweltsysteme & Klima", "Materie und Energie", "Chemische Strukturen", "Medizinische Diagnostik", "Patientenversorgung", "Neurobiologie", "Molekularbiologie", "Internationales Recht und Handelsrecht", "Verhaltenspsychologie", "Soziale Interaktionen"], 
                               "question_title": "Über welche Themenfelder möchtest du in deinem Studium mehr erfahren?", "answer_template": "Ich bin an folgenden Themenfeldern interessiert: ", "prompt_type_ext": "", 
                               "question_title_description": ""}, 
                        "A8": {"source": "", "io_type": "selectable", "summary": "", "branches": {}, 
                               "generate": {"all": {}}, "add_detail": "", "prompt_type": "", 
                               "all_elements": ["Auf Englisch studieren", "Auf Deutsch studieren", "Auf Englisch und Deutsch studieren", "Auslandssemester einlegen", "Kontakte zu Unternehmen knüpfen", "Projekte mit Unternehmen durchführen", "In Studierendenteams arbeiten", "in Schulen arbeiten", "Laborexperimente durchführen", "Forschungsprojekte", "Exkursionen", "Praktika", "Praxiserfahrung sammeln"], 
                               "question_title": "Was ist dir im Studium wichtig?", "answer_template": "Mir ist folgendes wichtig: ", "prompt_type_ext": "", 
                               "question_title_description": ""}, 
                        "A9": {"source": "", "io_type": "generated", 
                               "summary": "Du hast einen Abiturnotendurchschnitt von 1.0, interessierst dich für Biologie, Chemie, Algorithmen, Datenanalyse, IT Projektmanagement und Start-Up Gründung. Du magst KI ausprobieren, mathematische Modelle entwickeln, Mathe anwenden, schwere Matheprobleme lösen und programmieren. Du möchtest Manager und langfristig CEO werden und legst Wert auf ein Studium in Englisch und Deutsch.", "branches": {}, 
                               "generate": {"all": {}}, "add_detail": "", "prompt_type": "generate_question", "all_elements": [], 
                               "question_title": "Möchtest du in deinem Studium auch wirtschaftliche und betriebswirtschaftliche Aspekte vertiefen?", "answer_template": "", "prompt_type_ext": "", 
                               "question_title_description": ""}, 
                        "P1": {"source": "", "io_type": "pause", "summary": "", "branches": {}, 
                               "generate": {"all": {}}, "add_detail": "", "prompt_type": "", 
                               "all_elements": [], 
                               "question_title": "Super, das war's schon mit dem ersten Teil!", "answer_template": "", "prompt_type_ext": "", 
                               "question_title_description": "Jetzt kommen noch drei Fragen zu deinen Studienwünschen."}, 
                        "S1": {"source": "", "io_type": "start", "summary": "", "branches": {}, 
                               "generate": {"all": {}}, "add_detail": "", "prompt_type": "", 
                               "all_elements": [], "question_title": "Ich stelle dir 9 Fragen \nüber dich und deine Studienwünsche.", "answer_template": "", "prompt_type_ext": "", 
                               "question_title_description": "Los geht's mit sechs Fragen zu dir!"}, 
                        "ANALYSIS1": {
                                "source": "", "io_type": "selectable", "summary": "", "branches": {"ANALYSIS2": 1, "ANALYSIS3": 2}, 
                                "generate": {"all": {
                                                "qa": [], "body": "", "query": "", 
                                                "title": "Deine passenden Studiengänge", "add_detail": "", 
                                                "llm_answer": {"Volkswirtschaft": {"NC": "2.5", "Fit": "Okay"}, 
                                                                    "Betriebswirtschaft": {"NC": "1.6", "Fit": "Gut"}, 
                                                                    "Gesundheitsökonomie": {"NC": "2.4", "Fit": "Eher nicht"}, 
                                                                    "Sozialwissenschaften": {"NC": "2.0", "Fit": "Eher nicht"}, 
                                                                    "Wirtschaftsinformatik": {"NC": "1.8", "Fit": "Sehr gut"}, 
                                                                    "Wirtschaftspädagogik": {"NC": "2.2", "Fit": "Eher nicht"}, 
                                                                    "Management, Economics and Social Sciences": {"NC": "1.0", "Fit": "Gut"}
                                                                    }, 
                                                "title_description": "Wähle einen Studiengang und klicke auf 'Details', um mehr über den Fit zu erfahren. \nOder wähle 2 Studiengänge zum 'Vergleich' für dich wichtiger Kriterien aus."
                                                }
                                            }, 
                                "add_detail": "", 
                                "prompt_type": "institution_fitting", 
                                "all_elements": ["Wirtschaftsinformatik: Sehr gut", "Management, Economics and Social Sciences: Gut", "Betriebswirtschaft: Gut", "Volkswirtschaft: Okay", "Gesundheitsökonomie: Eher nicht", "Sozialwissenschaften: Eher nicht", "Wirtschaftspädagogik: Eher nicht"], 
                                "question_title": "Deine passenden Studiengänge", "answer_template": "", "prompt_type_ext": "", 
                                "question_title_description": "Wähle einen Studiengang und klicke auf 'Details', um mehr über den Fit zu erfahren. \nOder wähle 2 Studiengänge zum 'Vergleich' für dich wichtiger Kriterien aus."
                                    }, 
                        "ANALYSIS2": {
                                "source": "ANALYSIS1", "io_type": "text_edit", "summary": "", "branches": {}, 
                                "generate": {"Wirtschaftsinformatik": {
                                                "qa": [], "body": "<p><strong>Einschätzung: Sehr gut</strong></p>\n<p>Deine Interessen an \"Algorithmen\", \"Datenanalyse\", \"IT Projektmanagement\" und \"Start-Up Gründung\" passen perfekt. \"Programmieren\" und \"Mathe anwenden\" sind zentrale Bestandteile. \"Auf Englisch und Deutsch studieren\" ist gegeben. Eventuell könnten technische Details herausfordernd sein.</p>", 
                                                "query": "", 
                                                "title": "Erläuterungen zum Studiengang: Wirtschaftsinformatik - Fit: Sehr gut", 
                                                "add_detail": "Der Studiengang Wirtschaftsinformatik hatte im letzten Jahr einen NC von 1.8. Der NC ist eines der Auswahlkriterien für dieses Programm und kann sich von Jahr zu Jahr ändern. Beachte: Wenn der Abiturnotendurchschnitt kleiner oder gleich dem NC-Wert ist, kannst du das Programm vermutlich studieren, wenn anders gegebenenfalls nicht. Ich habe mein Bestes gegeben, um deinen Fit gut einzuschätzen. Editiere gerne dein Profil über das Hauptmenü, wenn du mir mehr oder andere Informationen über dich geben möchtest, als ich habe. Du kannst mehr Details über Wirtschaftsinformatik erfahren. Dann gebe deine Fragen in die Eingabemaske ein. Um Wirtschaftsinformatik mit einem anderen Studiengang zu vergleichen, gehe zurück ('<back'), wähle ein zweiten Studiengang aus und klicke auf 'Vergleich'.", 
                                                "llm_answer": "**Einschätzung: Sehr gut**\n\nDeine Interessen an \"Algorithmen\", \"Datenanalyse\", \"IT Projektmanagement\" und \"Start-Up Gründung\" passen perfekt. \"Programmieren\" und \"Mathe anwenden\" sind zentrale Bestandteile. \"Auf Englisch und Deutsch studieren\" ist gegeben. Eventuell könnten technische Details herausfordernd sein.", 
                                                "title_description": "Du kannst diese Erläuterungen jederzeit erneut erzeugen - klicke 'generate again'. Oder stelle deine Fragen."
                                                }
                                            }, 
                                "add_detail": "Der Studiengang <PROGRAM1> hatte im letzten Jahr einen NC von <NC1>. Der NC ist eines der Auswahlkriterien für dieses Programm und kann sich von Jahr zu Jahr ändern. Beachte: Wenn der Abiturnotendurchschnitt kleiner oder gleich dem NC-Wert ist, kannst du das Programm vermutlich studieren, wenn anders gegebenenfalls nicht. Ich habe mein Bestes gegeben, um deinen Fit gut einzuschätzen. Editiere gerne dein Profil über das Hauptmenü, wenn du mir mehr oder andere Informationen über dich geben möchtest, als ich habe. Du kannst mehr Details über <PROGRAM1> erfahren. Dann gebe deine Fragen in die Eingabemaske ein. Um <PROGRAM1> mit einem anderen Studiengang zu vergleichen, gehe zurück ('<back'), wähle ein zweiten Studiengang aus und klicke auf 'Vergleich'.", "prompt_type": "program_detail", "all_elements": ["Wirtschaftsinformatik: Sehr gut"], "question_title": "Erläuterungen zum Studiengang: <PROGRAM1> - Fit: <FIT1>", "answer_template": "", 
                                "prompt_type_ext": "program_chat", 
                                "question_title_description": "Du kannst diese Erläuterungen jederzeit erneut erzeugen - klicke 'generate again'. Oder stelle deine Fragen."
                                      }, 
                        "ANALYSIS3": {
                                "source": "ANALYSIS1", "io_type": "text_edit", "summary": "", "branches": {}, 
                                "generate": {"Management, Economics and Social Sciences_Wirtschaftsinformatik": {
                                                "qa": [], "body": "Hier ein Vergleich der beiden Programme anhand von Kriterien, die für dich relevant sein müssten.\n\n| Kriterium                          | Management, Economics and Social Sciences | Wirtschaftsinformatik                |\n|------------------------------------|-------------------------------------------|--------------------------------------|\n| Manager short-term and CEO long-term | Gut für Management- und Führungspositionen | Gut für IT-Management und Führung    |\n| KI ausprobieren                    | Nicht spezifisch abgedeckt                | Gut abgedeckt durch IT und Algorithmen|\n| Mathematische Modelle entwickeln   | Teilweise abgedeckt                       | Gut abgedeckt durch Datenanalyse     |\n| Mathe anwenden                     | Gut abgedeckt                             | Sehr gut abgedeckt                   |\n| Schwere Matheprobleme lösen        | Teilweise abgedeckt                       | Sehr gut abgedeckt                   |\n| Programmieren                      | Nicht spezifisch abgedeckt                | Sehr gut abgedeckt                   |\n| Abiturnotendurchschnitt = 1.0      | NC = 1.0                                  | NC = 1.8                             |\n\nBeide Programme könnten für dich passen, aber \"Wirtschaftsinformatik\" scheint besser geeignet zu sein. Deine Interessen an \"KI ausprobieren\", \"Mathematische Modelle entwickeln\", \"Mathe anwenden\", \"Schwere Matheprobleme lösen\" und \"Programmieren\" werden in der \"Wirtschaftsinformatik\" sehr gut abgedeckt. Zudem bietet dieses Programm eine solide Grundlage für eine Karriere im IT-Management und als CEO eines Technologieunternehmens. \"Management, Economics and Social Sciences\" ist ebenfalls eine gute Wahl, besonders wenn du dich stärker auf Management und wirtschaftliche Aspekte konzentrieren möchtest.", 
                                                "query": "", 
                                                "title": "Paco's Vergleich der Studiengänge Management, Economics and Social Sciences  (Fit=Sehr gut) und Wirtschaftsinformatik (Fit=Sehr gut)", 
                                                "add_detail": "Die oben angegebenen NCs sind vom letzten Jahr. Der NC ist eines der Auswahlkriterien für die Programme und kann sich von Jahr zu Jahr ändern. Beachte: Wenn der Abiturnotendurchschnitt kleiner oder gleich dem NC-Wert ist, kannst du das Programm vermutlich studieren, wenn anders gegebenenfalls nicht. Gibt es andere Kriterien, anhand derer ich die Programme für dich vergleichen soll? Dann gebe deine Kriterien in der Eingabemaske ein.", 
                                                "llm_answer": "Hier ein Vergleich der beiden Programme anhand von Kriterien, die für dich relevant sein müssten.\n\n| Kriterium                          | Management, Economics and Social Sciences | Wirtschaftsinformatik                |\n|------------------------------------|-------------------------------------------|--------------------------------------|\n| Manager short-term and CEO long-term | Gut für Management- und Führungspositionen | Gut für IT-Management und Führung    |\n| KI ausprobieren                    | Nicht spezifisch abgedeckt                | Gut abgedeckt durch IT und Algorithmen|\n| Mathematische Modelle entwickeln   | Teilweise abgedeckt                       | Gut abgedeckt durch Datenanalyse     |\n| Mathe anwenden                     | Gut abgedeckt                             | Sehr gut abgedeckt                   |\n| Schwere Matheprobleme lösen        | Teilweise abgedeckt                       | Sehr gut abgedeckt                   |\n| Programmieren                      | Nicht spezifisch abgedeckt                | Sehr gut abgedeckt                   |\n| Abiturnotendurchschnitt = 1.0      | NC = 1.0                                  | NC = 1.8                             |\n\nBeide Programme könnten für dich passen, aber \"Wirtschaftsinformatik\" scheint besser geeignet zu sein. Deine Interessen an \"KI ausprobieren\", \"Mathematische Modelle entwickeln\", \"Mathe anwenden\", \"Schwere Matheprobleme lösen\" und \"Programmieren\" werden in der \"Wirtschaftsinformatik\" sehr gut abgedeckt. Zudem bietet dieses Programm eine solide Grundlage für eine Karriere im IT-Management und als CEO eines Technologieunternehmens. \"Management, Economics and Social Sciences\" ist ebenfalls eine gute Wahl, besonders wenn du dich stärker auf Management und wirtschaftliche Aspekte konzentrieren möchtest.", 
                                                "title_description": "Du kannst Pacos's Kriterien Vergleich immer wiederholen - klicke 'generate again'. Du kannst weitere Kriterien zum Vergleich nennen."                                                                                
                                                }
                                            }, 
                                "add_detail": "Die oben angegebenen NCs sind vom letzten Jahr. Der NC ist eines der Auswahlkriterien für die Programme und kann sich von Jahr zu Jahr ändern. Beachte: Wenn der Abiturnotendurchschnitt kleiner oder gleich dem NC-Wert ist, kannst du das Programm vermutlich studieren, wenn anders gegebenenfalls nicht. Gibt es andere Kriterien, anhand derer ich die Programme für dich vergleichen soll? Dann gebe deine Kriterien in der Eingabemaske ein.", "prompt_type": "program_compare", "all_elements": ["Wirtschaftsinformatik: Sehr gut", "Management, Economics and Social Sciences: Sehr gut"], "question_title": "Paco's Vergleich der Studiengänge <PROGRAM1>  (Fit=<FIT1>) und <PROGRAM2> (Fit=<FIT2>)", "answer_template": "", 
                                "prompt_type_ext": "program_compare_my_criteria", 
                                "question_title_description": "Du kannst Pacos's Kriterien Vergleich immer wiederholen - klicke 'generate again'. Du kannst weitere Kriterien zum Vergleich nennen."
                                }
                        }
    }
    return data