Search.setIndex({docnames:["api/cgnal","api/cgnal.config","api/cgnal.data","api/cgnal.data.layer","api/cgnal.data.layer.mongo","api/cgnal.data.layer.pandas","api/cgnal.data.model","api/cgnal.logging","api/cgnal.tests","api/cgnal.utils","api/modules","git","index","intro/README"],envversion:{"sphinx.domains.c":2,"sphinx.domains.changeset":1,"sphinx.domains.citation":1,"sphinx.domains.cpp":4,"sphinx.domains.index":1,"sphinx.domains.javascript":2,"sphinx.domains.math":2,"sphinx.domains.python":3,"sphinx.domains.rst":2,"sphinx.domains.std":2,sphinx:56},filenames:["api/cgnal.rst","api/cgnal.config.rst","api/cgnal.data.rst","api/cgnal.data.layer.rst","api/cgnal.data.layer.mongo.rst","api/cgnal.data.layer.pandas.rst","api/cgnal.data.model.rst","api/cgnal.logging.rst","api/cgnal.tests.rst","api/cgnal.utils.rst","api/modules.rst","git.rst","index.rst","intro/README.md"],objects:{"":{cgnal:[0,0,0,"-"]},"cgnal.config":{AuthConfig:[1,1,1,""],AuthService:[1,1,1,""],AuthenticationServiceConfig:[1,1,1,""],BaseConfig:[1,1,1,""],CheckService:[1,1,1,""],FileSystemConfig:[1,1,1,""],get_all_configuration_file:[1,4,1,""],joinPath:[1,4,1,""],load:[1,4,1,""],merge_confs:[1,4,1,""],path_constructor:[1,4,1,""]},"cgnal.config.AuthConfig":{filename:[1,2,1,""],method:[1,2,1,""],password:[1,2,1,""],user:[1,2,1,""]},"cgnal.config.AuthService":{check:[1,2,1,""],decode:[1,2,1,""],url:[1,2,1,""]},"cgnal.config.AuthenticationServiceConfig":{ap_name:[1,2,1,""],auth_service:[1,2,1,""],check_service:[1,2,1,""],cors:[1,2,1,""],jwt_free_endpoints:[1,2,1,""],secured:[1,2,1,""]},"cgnal.config.BaseConfig":{getValue:[1,3,1,""],safeGetValue:[1,3,1,""],sublevel:[1,3,1,""]},"cgnal.config.CheckService":{login:[1,2,1,""],logout:[1,2,1,""],url:[1,2,1,""]},"cgnal.config.FileSystemConfig":{getFile:[1,3,1,""],getFolder:[1,3,1,""],root:[1,2,1,""]},"cgnal.data":{exceptions:[2,0,0,"-"],layer:[3,0,0,"-"],model:[6,0,0,"-"]},"cgnal.data.exceptions":{NoTableException:[2,5,1,""]},"cgnal.data.layer":{Archiver:[3,1,1,""],DAO:[3,1,1,""],DatabaseABC:[3,1,1,""],EmptyDatabase:[3,1,1,""],TableABC:[3,1,1,""],Writer:[3,1,1,""],mongo:[4,0,0,"-"],pandas:[5,0,0,"-"]},"cgnal.data.layer.Archiver":{archive:[3,3,1,""],dao:[3,3,1,""],foreach:[3,3,1,""],map:[3,3,1,""],retrieve:[3,3,1,""],retrieveGenerator:[3,3,1,""]},"cgnal.data.layer.DAO":{computeKey:[3,3,1,""],get:[3,3,1,""],parse:[3,3,1,""]},"cgnal.data.layer.DatabaseABC":{table:[3,3,1,""]},"cgnal.data.layer.EmptyDatabase":{table:[3,3,1,""]},"cgnal.data.layer.TableABC":{to_df:[3,3,1,""],write:[3,3,1,""]},"cgnal.data.layer.Writer":{push:[3,3,1,""],table:[3,2,1,""]},"cgnal.data.layer.mongo":{MongoConfig:[4,1,1,""],archivers:[4,0,0,"-"],dao:[4,0,0,"-"]},"cgnal.data.layer.mongo.MongoConfig":{admin:[4,2,1,""],auth:[4,2,1,""],authSource:[4,2,1,""],db_name:[4,2,1,""],getCollection:[4,3,1,""],host:[4,2,1,""],port:[4,2,1,""]},"cgnal.data.layer.mongo.archivers":{MongoArchiver:[4,1,1,""]},"cgnal.data.layer.mongo.archivers.MongoArchiver":{aggregate:[4,3,1,""],archive:[4,3,1,""],archiveMany:[4,3,1,""],archiveOne:[4,3,1,""],first:[4,3,1,""],retrieve:[4,3,1,""],retrieveById:[4,3,1,""]},"cgnal.data.layer.mongo.dao":{DocumentDAO:[4,1,1,""],SeriesDAO:[4,1,1,""]},"cgnal.data.layer.mongo.dao.DocumentDAO":{computeKey:[4,3,1,""],conversion:[4,3,1,""],get:[4,3,1,""],inverse_mapping:[4,2,1,""],mapping:[4,6,1,""],parse:[4,3,1,""],translate:[4,3,1,""]},"cgnal.data.layer.mongo.dao.SeriesDAO":{computeKey:[4,3,1,""],get:[4,3,1,""],parse:[4,3,1,""]},"cgnal.data.layer.pandas":{archivers:[5,0,0,"-"],dao:[5,0,0,"-"],databases:[5,0,0,"-"]},"cgnal.data.layer.pandas.archivers":{CsvArchiver:[5,1,1,""],PandasArchiver:[5,1,1,""],PickleArchiver:[5,1,1,""],TableArchiver:[5,1,1,""]},"cgnal.data.layer.pandas.archivers.PandasArchiver":{archive:[5,3,1,""],archiveMany:[5,3,1,""],archiveOne:[5,3,1,""],commit:[5,3,1,""],data:[5,2,1,""],retrieve:[5,3,1,""],retrieveById:[5,3,1,""],retrieveGenerator:[5,3,1,""]},"cgnal.data.layer.pandas.dao":{DataFrameDAO:[5,1,1,""],DocumentDAO:[5,1,1,""],SeriesDAO:[5,1,1,""]},"cgnal.data.layer.pandas.dao.DataFrameDAO":{addName:[5,3,1,""],computeKey:[5,3,1,""],get:[5,3,1,""],parse:[5,3,1,""]},"cgnal.data.layer.pandas.dao.DocumentDAO":{computeKey:[5,3,1,""],get:[5,3,1,""],parse:[5,3,1,""]},"cgnal.data.layer.pandas.dao.SeriesDAO":{computeKey:[5,3,1,""],get:[5,3,1,""],parse:[5,3,1,""]},"cgnal.data.layer.pandas.databases":{Database:[5,1,1,""],Table:[5,1,1,""]},"cgnal.data.layer.pandas.databases.Database":{table:[5,3,1,""],tables:[5,2,1,""]},"cgnal.data.layer.pandas.databases.Table":{data:[5,2,1,""],filename:[5,2,1,""],write:[5,3,1,""]},"cgnal.data.model":{core:[6,0,0,"-"],ml:[6,0,0,"-"],text:[6,0,0,"-"]},"cgnal.data.model.core":{BaseRange:[6,1,1,""],CachedIterable:[6,1,1,""],CompositeRange:[6,1,1,""],DillSerialization:[6,1,1,""],IterGenerator:[6,1,1,""],Iterable:[6,1,1,""],LazyIterable:[6,1,1,""],PickleSerialization:[6,1,1,""],Range:[6,1,1,""],Serializable:[6,1,1,""]},"cgnal.data.model.core.BaseRange":{business_days:[6,2,1,""],days:[6,2,1,""],end:[6,2,1,""],minutes_15:[6,2,1,""],overlaps:[6,3,1,""],range:[6,3,1,""],start:[6,2,1,""]},"cgnal.data.model.core.CachedIterable":{batch:[6,3,1,""],cached:[6,2,1,""],filter:[6,3,1,""],items:[6,2,1,""],kfold:[6,3,1,""],load:[6,3,1,""],save:[6,3,1,""],take:[6,3,1,""]},"cgnal.data.model.core.CompositeRange":{end:[6,2,1,""],overlaps:[6,3,1,""],range:[6,3,1,""],simplify:[6,3,1,""],start:[6,2,1,""]},"cgnal.data.model.core.DillSerialization":{load:[6,3,1,""],write:[6,3,1,""]},"cgnal.data.model.core.IterGenerator":{iterator:[6,2,1,""]},"cgnal.data.model.core.Iterable":{batch:[6,3,1,""],cached:[6,2,1,""],filter:[6,3,1,""],foreach:[6,3,1,""],hold_out:[6,3,1,""],items:[6,2,1,""],kfold:[6,3,1,""],map:[6,3,1,""],take:[6,3,1,""]},"cgnal.data.model.core.LazyIterable":{batch:[6,3,1,""],cache:[6,3,1,""],cached:[6,2,1,""],filter:[6,3,1,""],items:[6,2,1,""],kfold:[6,3,1,""],take:[6,3,1,""],toCached:[6,3,1,""]},"cgnal.data.model.core.PickleSerialization":{load:[6,3,1,""],write:[6,3,1,""]},"cgnal.data.model.core.Range":{end:[6,2,1,""],overlaps:[6,3,1,""],range:[6,3,1,""],start:[6,2,1,""]},"cgnal.data.model.core.Serializable":{load:[6,3,1,""],write:[6,3,1,""]},"cgnal.data.model.ml":{CachedDataset:[6,1,1,""],Dataset:[6,1,1,""],IterableDataset:[6,1,1,""],LazyDataset:[6,1,1,""],MultiFeatureSample:[6,1,1,""],PandasDataset:[6,1,1,""],PandasTimeIndexedDataset:[6,1,1,""],Sample:[6,1,1,""],features_and_labels_to_dataset:[6,4,1,""]},"cgnal.data.model.ml.CachedDataset":{to_df:[6,3,1,""]},"cgnal.data.model.ml.Dataset":{createObject:[6,3,1,""],default_type:[6,2,1,""],features:[6,2,1,""],getFeaturesAs:[6,3,1,""],getLabelsAs:[6,3,1,""],labels:[6,2,1,""],samples:[6,2,1,""],union:[6,3,1,""],write:[6,3,1,""]},"cgnal.data.model.ml.IterableDataset":{checkNames:[6,3,1,""],createObject:[6,3,1,""],getFeaturesAs:[6,3,1,""],getLabelsAs:[6,3,1,""],samples:[6,2,1,""],union:[6,3,1,""]},"cgnal.data.model.ml.LazyDataset":{rebalance:[6,3,1,""],toCached:[6,3,1,""],withLookback:[6,3,1,""]},"cgnal.data.model.ml.PandasDataset":{createObject:[6,3,1,""],dropna:[6,3,1,""],from_sequence:[6,3,1,""],getFeaturesAs:[6,3,1,""],getLabelsAs:[6,3,1,""],index:[6,2,1,""],intersection:[6,3,1,""],load:[6,3,1,""],loc:[6,3,1,""],read:[6,3,1,""],samples:[6,2,1,""],take:[6,3,1,""],union:[6,3,1,""],write:[6,3,1,""]},"cgnal.data.model.ml.PandasTimeIndexedDataset":{createObject:[6,3,1,""]},"cgnal.data.model.text":{CachedDocuments:[6,1,1,""],Document:[6,1,1,""],Documents:[6,1,1,""],LazyDocuments:[6,1,1,""],generate_random_uuid:[6,4,1,""]},"cgnal.data.model.text.CachedDocuments":{to_df:[6,3,1,""]},"cgnal.data.model.text.Document":{addProperty:[6,3,1,""],author:[6,2,1,""],getOrThrow:[6,3,1,""],items:[6,3,1,""],language:[6,2,1,""],properties:[6,2,1,""],removeProperty:[6,3,1,""],setRandomUUID:[6,3,1,""],text:[6,2,1,""]},"cgnal.data.model.text.Documents":{documents:[6,2,1,""]},"cgnal.data.model.text.LazyDocuments":{toCached:[6,3,1,""]},"cgnal.logging":{LevelsDict:[7,1,1,""],LoggingConfig:[7,1,1,""],WithLoggingABC:[7,1,1,""],defaults:[7,0,0,"-"],simple:[7,0,0,"-"]},"cgnal.logging.LevelsDict":{CRITICAL:[7,6,1,""],DEBUG:[7,6,1,""],ERROR:[7,6,1,""],INFO:[7,6,1,""],NOTSET:[7,6,1,""],WARNING:[7,6,1,""]},"cgnal.logging.LoggingConfig":{capture_warnings:[7,2,1,""],default_config_file:[7,2,1,""],filename:[7,2,1,""],level:[7,2,1,""]},"cgnal.logging.WithLoggingABC":{logger:[7,2,1,""]},"cgnal.logging.defaults":{WithLogging:[7,1,1,""],configFromFile:[7,4,1,""],configFromFiles:[7,4,1,""],configFromJson:[7,4,1,""],configFromYaml:[7,4,1,""],getDefaultLogger:[7,4,1,""],logger:[7,4,1,""]},"cgnal.logging.defaults.WithLogging":{logResult:[7,3,1,""],logger:[7,2,1,""]},"cgnal.logging.simple":{Logger:[7,1,1,""],logger:[7,4,1,""]},"cgnal.logging.simple.Logger":{debug:[7,3,1,""],error:[7,3,1,""],info:[7,3,1,""],warn:[7,3,1,""],warning:[7,3,1,""]},"cgnal.tests":{core:[8,0,0,"-"]},"cgnal.tests.core":{TestCase:[8,1,1,""],logTest:[8,4,1,""]},"cgnal.tests.core.TestCase":{compareArrays:[8,3,1,""],compareDataFrames:[8,3,1,""],compareDicts:[8,3,1,""],compareLists:[8,3,1,""],compareSeries:[8,3,1,""],setUp:[8,3,1,""]},"cgnal.utils":{cloud:[9,0,0,"-"],decorators:[9,0,0,"-"],dict:[9,0,0,"-"],email:[9,0,0,"-"],fs:[9,0,0,"-"],pandas:[9,0,0,"-"]},"cgnal.utils.cloud":{CloudSync:[9,1,1,""],HTTPRequestHandler:[9,1,1,""]},"cgnal.utils.cloud.CloudSync":{create_base_directory:[9,3,1,""],get:[9,3,1,""],get_if_not_exists:[9,3,1,""],get_if_not_exists_decorator:[9,3,1,""],pathTo:[9,3,1,""],upload:[9,3,1,""]},"cgnal.utils.cloud.HTTPRequestHandler":{do_POST:[9,3,1,""]},"cgnal.utils.decorators":{Cached:[9,1,1,""],cache:[9,4,1,""],lazyproperty:[9,4,1,""],paramCheck:[9,4,1,""],param_check:[9,4,1,""]},"cgnal.utils.decorators.Cached":{clear_cache:[9,3,1,""],load_element:[9,3,1,""],save_element:[9,3,1,""],save_pickles:[9,3,1,""]},"cgnal.utils.dict":{filterNones:[9,4,1,""],flattenKeys:[9,4,1,""],groupBy:[9,4,1,""],groupIterable:[9,4,1,""],pairwise:[9,4,1,""],unflattenKeys:[9,4,1,""],union:[9,4,1,""]},"cgnal.utils.email":{EmailSender:[9,1,1,""]},"cgnal.utils.email.EmailSender":{send_mail:[9,3,1,""]},"cgnal.utils.fs":{create_dir_if_not_exists:[9,4,1,""],get_lexicographic_dirname:[9,4,1,""],mkdir:[9,4,1,""]},"cgnal.utils.pandas":{is_sparse:[9,4,1,""],loc:[9,4,1,""]},cgnal:{SupportsLessThan:[0,1,1,""],config:[1,0,0,"-"],data:[2,0,0,"-"],logging:[7,0,0,"-"],tests:[8,0,0,"-"],utils:[9,0,0,"-"]}},objnames:{"0":["py","module","Python module"],"1":["py","class","Python class"],"2":["py","property","Python property"],"3":["py","method","Python method"],"4":["py","function","Python function"],"5":["py","exception","Python exception"],"6":["py","attribute","Python attribute"]},objtypes:{"0":"py:module","1":"py:class","2":"py:property","3":"py:method","4":"py:function","5":"py:exception","6":"py:attribute"},terms:{"0":[7,13],"1":13,"10":7,"100":6,"10000":9,"20":7,"3":6,"30":7,"4":13,"40":7,"5":13,"50":7,"abstract":[3,6,7,13],"byte":6,"case":8,"catch":7,"class":[0,1,3,4,5,6,7,8,9],"default":[0,1,4,5,6,8,9,10],"do":7,"float":6,"function":9,"int":[4,6,9],"new":6,"return":[1,4,5,6,7,9],"static":[5,6,9],"true":[4,6,7,9],A:7,If:[4,6,7],In:6,It:13,The:[2,4,9,11],These:13,To:13,_dict:9,_id:4,_lib:6,_tmp:4,abc:[1,3,5,6,7],access:[3,5],accord:[4,6],act:12,add:[6,13],addnam:5,addproperti:6,address:9,admin:4,advisabil:13,after:11,aggreg:[4,6],all:[1,4,6,9,13],allow:13,allow_non:9,allowdiskus:4,also:13,an:[4,5,6,8],analyt:13,ani:[1,3,4,6,7,9,13],ap_nam:1,appli:4,applic:1,application_fil:1,appropri:5,ar:[6,11,13],archiv:[2,3],archivemani:[4,5],archiveon:[4,5],arg:[0,3,6,7],arrai:6,assign:6,associ:6,attach:9,auth:4,auth_protocol:9,auth_servic:1,authconfig:[1,4],authent:9,authenticationserviceconfig:1,author:6,authservic:1,authsourc:4,autom:13,automat:13,base:[0,1,2,3,4,5,6,7,8,9],baseconfig:[1,4,7],baseexcept:2,baserang:6,bash:13,batch:6,batch_siz:9,befor:8,belong:5,bool:[1,4,5,6,7,8,9],both:13,branch:11,bson:[3,4],business_dai:6,cach:[6,9],cacheddataset:6,cacheddocu:6,cachediter:6,callabl:[3,5,6,7,8,9],can:[4,6,13],captur:7,capture_warn:7,carri:11,catch_except:7,cfg_load:[1,4,7],cgnal:13,chang:6,changelog:12,check:1,check_servic:1,checknam:6,checkservic:1,chosen:6,classmethod:6,clean:13,clear:9,clear_cach:9,client_address:9,clone:13,close:[11,13],cloud:[0,10],cloudsync:9,collect:[1,3,4,5,6,13],come:13,command:13,commit:[5,13],compar:6,comparearrai:8,comparedatafram:8,comparedict:8,comparelist:8,compareseri:8,complet:[5,12],compositerang:6,computekei:[3,4,5],condit:[4,5],config:[0,4,7,10,13],config_fil:[1,7],configfromfil:7,configfromjson:7,configfromyaml:7,configur:[1,4,7,13],constructor:5,contain:[6,13],content:10,convers:4,cor:1,core:[0,2,3,4,5,9,10],correctli:13,correspond:13,coupl:6,creat:[6,7,8],create_base_directori:9,create_dir_if_not_exist:9,createobject:6,critic:7,csvarchiv:5,current:[6,13],d:4,dai:6,daili:6,dao:[2,3],data:[0,10,12],databas:[2,3],databaseabc:[3,5],datafram:[3,5,6,8,9],dataframedao:5,dataset:6,datav:[3,5],date:6,date_rang:6,datetim:6,datetimescalar:6,db:5,db_name:4,dbpath:4,debug:7,declar:13,decod:1,decor:[0,10],default_config_fil:7,default_typ:6,defin:[6,13],depend:13,design:9,destin:9,develop:[11,13],df:[3,5,9],dict:[0,3,4,6,7,8,10],dictionari:[4,6],differ:7,dillseri:6,direct:13,directori:[4,7,9],dirpath:9,disjoint:6,do_post:9,doc:5,document:[3,4,5,6,13],documentdao:[4,5],doe:[7,8],domain:13,drop:6,dropna:6,dure:13,e:13,each:[6,13],element:[4,6],email:[0,10],email_address:9,emailsend:9,empti:3,emptydatabas:3,enabl:[4,13],end:6,env:1,environ:[1,13],error:7,eventu:5,except:[0,7,10],exclud:6,execut:8,exercis:8,exist:[5,7],expand:1,extens:5,extract:1,f:[3,6,9],fals:[4,5,6,8,9],feattyp:6,featur:6,features_and_labels_to_dataset:6,features_col:6,field:6,filanam:6,file:[1,4,5,6,7,9,13],filehandl:7,filenam:[1,5,6,7,9,13],filesystemconfig:1,filter:[6,9],filternon:9,find:6,first:[4,6,8,9],fixtur:8,flattenkei:9,fold:6,folder:[9,13],follow:13,foreach:[3,6],format:5,frame:[3,5,6,8,9],framework:6,freq:6,frequenc:6,from:[1,3,4,5,6,7,13],from_sequ:6,fs:[0,10],fullload:1,func:9,futur:13,gener:[4,6,9],generate_random_uuid:6,generator_funct:6,get:[3,4,5,6,9],get_all_configuration_fil:1,get_if_not_exist:9,get_if_not_exists_decor:9,get_lexicographic_dirnam:9,getcollect:4,getdefaultlogg:7,getfeaturesa:6,getfil:1,getfold:1,getlabelsa:6,getorthrow:6,getvalu:1,git:[12,13],given:[1,2,4,6,9],global:13,groupbi:9,groupiter:9,guidelin:12,h:6,hand:13,handler:7,hashabl:[1,3,5,6],have:[8,13],hold_out:6,hook:[8,13],host:4,http:9,httprequesthandl:9,i:13,id:[4,6],idx:[6,9],implement:[5,13],includ:1,inclus:6,index:[5,6,9,12],indic:6,info:7,inform:6,ingest:13,inherit:7,init:13,initi:7,input:[5,6,9],input_dict:9,insert:4,instal:13,instanc:[4,6,7,8],instead:13,integr:5,intersect:6,invers:4,inverse_map:4,is_spars:9,item:6,iter:[3,4,5,6,9],iterabledataset:6,itergener:[3,5,6],its:[7,13],join:5,joinpath:1,json:[4,7],jwt_free_endpoint:1,k:4,keep:13,kei:[4,6,9],key_field:4,kfold:6,kwarg:[3,6,7],kwd:[0,6],label:6,labels_col:6,labtyp:6,languag:6,last:6,latest:11,layer:[0,2],lazydataset:6,lazydocu:6,lazyiter:6,lazyproperti:9,level:7,levelsdict:7,librari:13,list:[1,4,5,6,7,8,9],liter:[6,7],load:[1,6,9],load_el:9,loader:1,loc:[6,9],local:13,log:[0,5,8,9,10],logger:7,loggingconfig:7,login:1,logout:1,logresult:7,logtest:8,look:6,lookback:6,lst:9,made:6,mani:4,map:[3,4,6],master:11,match:1,memori:3,merg:[1,7,11],merge_conf:1,messag:[2,7],method:[1,5,8],methodnam:8,minimum:13,minutes_15:6,miss:[2,6],mkdir:9,ml:[0,2],model:[0,2,3,4,5,9,12],modifi:13,modul:[10,12],mongo:[2,3],mongoarchiv:4,mongoconfig:4,mongomock:4,more:[4,13],msg:[7,8],multifeaturesampl:6,multipl:6,must:13,n:6,na:6,name:[1,4,5,6,7,8],name_env:1,ndarrai:[6,8],necessari:7,need:13,newli:13,node:1,non:6,none:[3,4,5,6,7,8,9],notableexcept:2,note:12,notset:7,np:6,number:6,numpi:[6,8],obj:[3,4,5,9],object:[1,3,5,6,7,9],objectid:[3,4],obtain:7,one:[1,4,6],onli:[6,13],open:13,oper:4,option:[1,3,4,5,6,7,9,13],order:4,os:[1,5,6,7,9],other:[6,11,13],outer:5,output:[2,7],over:6,overlap:6,overwrit:5,p:5,packag:[10,11,12],page:12,pairwis:9,panda:[0,2,3,4,6,8,10],pandasarchiv:5,pandasdataset:6,pandastimeindexeddataset:6,param:[6,7],param_check:9,paramcheck:9,paramet:[1,2,4,5,6,7,9],pars:[3,4,5],password:[1,9],path:[1,5,7,9],path_constructor:1,path_to_fil:7,pathlik:[1,5,6,7,9],pathto:9,pd:[5,6],pickl:[5,6,9],picklearchiv:5,pickleseri:6,picklet:5,pip:13,pipelin:[4,13],port:[4,9],pre:13,present:6,print:7,prob:6,probabilit:6,probabl:6,procedur:13,properti:[1,3,4,5,6,7,9],propertli:9,protocol:[0,9],push:3,py:13,pymongo:4,queri:3,r:13,rais:8,random:6,rang:6,ratio:6,read:[1,5,6,9],rebal:6,rebalanc:6,refactor:13,reformat:6,remov:6,removeproperti:6,replac:1,repo:13,report:7,repositori:[11,13],repres:[6,13],represent:6,request:9,requir:13,requirements_dev:13,respect:4,respons:9,result:4,retriev:[1,3,4,5,6],retrievebyid:[4,5],retrievegener:[3,5],retriv:4,root:[1,7,9,13],row:[3,5],run:13,runtest:8,s0:9,s1:9,s2:9,s3:9,s:[4,5,9],safegetvalu:1,same:6,sampl:6,satisfi:4,save:[6,9],save_el:9,save_pickl:9,search:12,second:8,secur:1,select:6,selector:5,self:4,send:9,send_mail:9,sender:9,sep:[5,9],sequenc:6,seri:[3,4,5,6,8],serializ:6,seriesdao:[4,5],serv:11,server:9,set:[4,6,8,13],setrandomuuid:6,setup:[8,13],sever:11,sh:13,should:[11,13],simpl:[0,6,10,13],simplehttprequesthandl:9,simplifi:6,singl:6,size:6,smtp:9,smtp_address:9,sort:4,sort_bi:4,sourc:[3,5],space:6,spars:9,specif:1,specifi:[1,6,7,8],split:6,stabl:11,stage:4,standard:5,start:6,step:4,still:13,store:3,str:[1,2,3,4,5,6,7,8,9],strict:8,strictli:13,structur:12,subdirectori:4,subject:9,sublevel:1,submodul:[0,3,10],subpackag:10,subsequ:13,supportslessthan:[0,9],sync:13,system:1,t:[3,4,6,9],tabl:[2,3,5],table_nam:[3,5],tableabc:[3,5],tablearchiv:5,take:6,target:13,task:11,team:13,templat:13,templatedir:13,temporari:4,test:[0,6,10],testcas:8,text:[0,2,3,4,5,9],thei:13,thi:[6,9,12,13],those:13,thought:13,thu:13,timestamp:6,to_df:[3,6],tocach:6,tool:13,train:6,translat:4,tslib:6,tupl:[6,9],two:[6,13],txt:13,type:6,typing_extens:[0,6,7],unflattenkei:9,uninstal:13,union:[1,3,4,5,6,7,9],unittest:8,unsafeload:1,up:[6,8,13],updat:[4,13],update_pkg:13,updateresult:4,upload:9,url:[1,9],us:[4,5,6,7,8,9,12,13],user:1,usernam:9,util:[0,8,10],uuid:[4,5,6],v:4,valu:[1,4,6,9],valueerror:8,variabl:1,variou:11,version:[11,13],warn:7,well:9,when:[4,8,13],where:6,whether:[5,6,7],which:[5,9],whose:4,with_non:9,within:7,withlog:[5,7,8,9],withloggingabc:7,withlookback:6,without:6,work:[9,13],would:6,wrapper:9,write:[3,4,5,6],writer:3,x:6,y:6,yaml:[1,7,13],yet:7,yield:6,yml:1,you:13,zip:9},titles:["cgnal package","cgnal.config package","cgnal.data package","cgnal.data.layer package","cgnal.data.layer.mongo package","cgnal.data.layer.pandas package","cgnal.data.model package","cgnal.logging package","cgnal.tests package","cgnal.utils package","cgnal","Git Structure","Welcome to CGnal Core\u2019s documentation!","Core Package"],titleterms:{"default":7,archiv:[4,5],cgnal:[0,1,2,3,4,5,6,7,8,9,10,12],changelog:13,cloud:9,config:1,content:[0,1,2,3,4,5,6,7,8,9],core:[6,8,12,13],dao:[4,5],data:[2,3,4,5,6,13],databas:5,decor:9,develop:12,dict:9,document:12,email:9,except:2,fs:9,git:11,guid:12,indic:12,intro:12,layer:[3,4,5],log:7,ml:6,model:[6,13],modul:[0,1,2,3,4,5,6,7,8,9],mongo:4,note:13,packag:[0,1,2,3,4,5,6,7,8,9,13],panda:[5,9],s:12,simpl:7,structur:11,submodul:[2,4,5,6,7,8,9],subpackag:[0,2,3],tabl:12,test:8,text:6,user:12,util:9,welcom:12}})