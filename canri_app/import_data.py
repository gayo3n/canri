import os
import logging
import datetime
from django_setup_def import djangoImportSetup
djangoImportSetup()
from CCapp.models import *
from CCapp.defs import makeDirFile,makeImportPath,logconfig,logException,logsOutput,readFile,executeFunction
from django.db import transaction

# ログの設定
def import_data_SettingLogs():
    logDir=os.path.join('logs')
    logFile=os.path.join(f'{logDir}/data_import.log')
    logconfig(logFile)
    logger=makeDirFile(logFile)
    return logger

#インスタンスの作成または取得結果
def queryResults(instanceDict):
    results=['処理結果\n']
    for instance,created in instanceDict.items():
        if created:
            results.append(f"新規作成: {instance.name}")
        else:
            results.append(f"既存データ取得: {instance.name}")
    return results

def outputQueryResults(instanceDict):
    results=queryResults(instanceDict)
    logsOutput(*results)

def area0(filePath):
    instanceDict={}
    def function():
        try:
            data=readFile(filePath)
            with transaction.atomic():
                for row in data:
                    regionName=row['name']
                    instance,created=Area0.objects.get_or_create(name=regionName)
                    instanceDict[instance]=created
        except FileNotFoundError:
            logException(logger,file_key,FileNotFoundError)
            print(f"ファイルが見つかりません: {filePath}")
        except Exception as e:
            logException(logger,file_key,e)
            print(f"エラーが発生しました: {e}")
    executeFunction(function)
    outputQueryResults(instanceDict)

def area1(filePath):
    instanceDict={}
    def function():
        try:
            data=readFile(filePath)
            with transaction.atomic():
                for row in data:
                    regionName,prefecture=row['region'], row['name']
                    region=Area0.objects.get(name=regionName)
                    instance,created=Area1.objects.get_or_create(name=prefecture,area0=region)
                    instanceDict[instance]=created
        except Area0.DoesNotExist:
            print(f"area0: {region} は存在しません")
        except FileNotFoundError:
            print(f"ファイルが見つかりません: {filePath}")
        except Exception as e:
            print(f"エラーが発生しました: {e}")
    executeFunction(function)
    outputQueryResults(instanceDict)

def area2(filePath):
    instanceDict={}
    def function():
        try:
            data=readFile(filePath)
            with transaction.atomic():
                for row in data:
                    prefecture_name,city_name=row['都道府県名（漢字）'],row['市区町村名（漢字）']
                    prefecture=Area1.objects.get(name=prefecture_name)
                    instance,created=Area2.objects.get_or_create(name=city_name,area1=prefecture)
                    instanceDict[instance]=created
        except Area1.DoesNotExist:
            print(f"area1: {prefecture_name} は存在しません")
        except FileNotFoundError:
            print(f"ファイルが見つかりません: {filePath}")
        except Exception as e:
            print(f"エラーが発生しました: {e}")
    executeFunction(function)
    outputQueryResults(instanceDict)

def tag(filePath):
    instanceDict={}
    def function():
        try:
            data=readFile(filePath)
            with transaction.atomic():
                for row in data:
                    tagName=row['name']
                    instance,created=Tag.objects.get_or_create(name=tagName)
                    instanceDict[instance]=created
        except FileNotFoundError:
            print(f"ファイルが見つかりません: {filePath}")
        except Exception as e:
            print(f"エラーが発生しました: {e}")
    executeFunction(function)
    outputQueryResults(instanceDict)

def category00(filePath):
    instanceDict={}
    def function():
        try:
            data=readFile(filePath)
            with transaction.atomic():
                for row in data:
                    categoryName=row['name']
                    instance,created=Category00.objects.get_or_create(name=categoryName)
                    instanceDict[instance]=created
        except FileNotFoundError:
            print(f"ファイルが見つかりません: {filePath}")
        except Exception as e:
            print(f"エラーが発生しました: {e}")
    executeFunction(function)
    outputQueryResults(instanceDict)

def category01(filePath):
    instanceDict={}
    def function():
        try:
            data=readFile(filePath)
            with transaction.atomic():
                for row in data:
                    category00Name, category01Name = row['category00name'], row['name']
                    category00= Category00.objects.get(name=category00Name)
                    instance,created=Category01.objects.get_or_create(name=category01Name,category00=category00)
                    instanceDict[instance]=created
        except Category00.DoesNotExist:
            print(f"category00: {category00Name} は存在しません")
        except FileNotFoundError:
            print(f"ファイルが見つかりません: {filePath}")
        except Exception as e:
            print(f"エラーが発生しました: {e}")
    executeFunction(function)
    outputQueryResults(instanceDict)

def category10(filePath):
    instanceDict={}
    def function():
        try:
            data=readFile(filePath)
            with transaction.atomic():
                for row in data:
                    categoryName = row['name']
                    instance,created=Category10.objects.get_or_create(name=categoryName)
                    instanceDict[instance]=created
        except FileNotFoundError:
            print(f"ファイルが見つかりません: {filePath}")
        except Exception as e:
            print(f"エラーが発生しました: {e}")
    executeFunction(function)
    outputQueryResults(instanceDict)

def category11(filePath):
    instanceDict={}
    def function():
        try:
            data=readFile(filePath)
            with transaction.atomic():
                for row in data:
                    category10Name, category11Name = row['category10name'], row['name']
                    category10=Category10.objects.get(name=category10Name)
                    instance,created=Category11.objects.get_or_create(name=category11Name,category10=category10)
                    instanceDict[instance]=created
        except Category10.DoesNotExist:
            print(f"{category10Name} は存在しません")
        except FileNotFoundError:
            print(f"ファイルが見つかりません: {filePath}")
        except Exception as e:
            print(f"エラーが発生しました: {e}")
    executeFunction(function)
    outputQueryResults(instanceDict)

def user(filePath):
    instanceDict={}
    def function():
        try:
            data=readFile(filePath)
            with transaction.atomic():
                for row in data:
                    name,mail,password,authority=row['name'],row['mail'],row['password'],row['authority']
                    instance,created=User.objects.get_or_create(name=name,mail=mail,password=password,authority=authority)
                    instanceDict[instance]=created
        except FileNotFoundError:
            print(f"ファイルが見つかりません: {filePath}")
        except Exception as e:
            print(f"エラーが発生しました: {e}")
    executeFunction(function)
    outputQueryResults(instanceDict)

def profile(filePath):
    instanceDict={}
    def function():
        try:
            data=readFile(filePath)
            with transaction.atomic():
                for row in data:
                    userId,nationality,birth,gender,graduation,school,sClass,sol,departments,tel,address,category00name,category01name,category10name,category11name,area1name,uOffer=row
                    ['userId'],row['nationality'],row['birth'].split('-'),row['gender'],row['graduation'],row['school'],row['class'],row['sol'],row['departments'],row['tel'],row['address'],row
                    ['category00name'],row['category01name'],row['category10name'],row['category11name'],row['area1name'],row['uOffer']
                    birth=datetime.date(birth)
                    user=User.objects.get(id=userId)
                    area1=Area1.objects.get(name=area1name)
                    category00=Category00.objects.get(name=category00name)
                    category01=Category01.objects.get(name=category01name)
                    category10=Category10.objects.get(name=category10name)
                    category11=Category11.objects.get(name=category11name)
                    instance,created=Profile.objects.get_or_create(user=user,nationality=nationality,birth=birth,gender=gender,graduation=graduation,uSchool=school,sClass=sClass,sol=sol,
                    departments=departments,uTel=tel,uAddress=address,category00=category00,category01=category01,category10=category10,category11=category11,area1=area1,uOffer=uOffer)
                    instanceDict[instance]=created
        except User.DoesNotExist:
            print(f"userID: {userId} は存在しません")
        except Area1.DoesNotExist:
            print(f'area1: {area1name} は存在しません')
        except Category00.DoesNotExist:
            print(f"category00: {category00name} は存在しません")
        except Category01.DoesNotExist:
            print(f"category01: {category01name} は存在しません")
        except Category10.DoesNotExist:
            print(f"category10: {category10name} は存在しません")
        except Category10.DoesNotExist:
            print(f"category11: {category11name} は存在しません")
        except FileNotFoundError:
            print(f"ファイルが見つかりません: {filePath}")
        except Exception as e:
            print(f"エラーが発生しました: {e}")
    executeFunction(function)
    outputQueryResults(instanceDict)

def question00(filePath):
    instanceDict={}
    def function():
        try:
            data=readFile(filePath)
            with transaction.atomic():
                for row in data:
                    questionName=row['name']
                    instance,created=Question00.objects.get_or_create(name=questionName)
                    instanceDict[instance]=created
        except FileNotFoundError:
            print(f"ファイルが見つかりません: {filePath}")
        except Exception as e:
            print(f"エラーが発生しました: {e}")
    executeFunction(function)
    outputQueryResults(instanceDict)

def question01(filePath):
    instanceDict={}
    def function():
        try:
            data=readFile(filePath)
            with transaction.atomic():
                for row in data:
                    question00Name,name=row['question00name'], row['name']
                    question00=Question00.objects.get(name=question00Name)
                    instance,created=Category11.objects.get_or_create(name=name,question00=question00)
                    instanceDict[instance]=created
        except Category10.DoesNotExist:
            print(f"{question00Name} は存在しません")
        except FileNotFoundError:
            print(f"ファイルが見つかりません: {filePath}")
        except Exception as e:
            print(f"エラーが発生しました: {e}")
    executeFunction(function)
    outputQueryResults(instanceDict)

def assessment(filePath):
    instanceDict={}
    def function():
        try:
            data=readFile(filePath)
            with transaction.atomic():
                for row in data:
                    userId,question01Name,answer=row['userID'],row['question01name'],row['answer']
                    user=User.objects.get(id=userId)
                    question01=Question01.objects.get(question01Name)
                    instance,created=User.objects.get_or_create(user=user,question01=question01,answer=answer)
                    instanceDict[instance]=created
        except User.DoesNotExist:
            print(f"userID: {userId} は存在しません")
        except Question01.DoesNotExist:
            print(f"questionName: {question01Name} は存在しません")
        except FileNotFoundError:
            print(f"ファイルが見つかりません: {filePath}")
        except Exception as e:
            print(f"エラーが発生しました: {e}")
    executeFunction(function)
    outputQueryResults(instanceDict)

def corporation(filePath):
    instanceDict = {}
    def function():
        try:
            data=readFile(filePath)
            with transaction.atomic():
                for row in data:
                    required_keys=['cId','name','address','mail','tel','url']
                    if not all(key in row for key in required_keys):
                        print(f"不足しているデータ: {row}")
                        continue
                    try:
                        cId,name,address,mail,tel,url=(row['cId'],row['name'],row['address'],row['mail'],row['tel'],row['url'])
                    except ValueError as ve:
                        print(f"データ変換エラー: {ve}, 行: {row}")
                        continue
                    instance,created=Corporation.objects.get_or_create(corp=cId,name=name,address=address,cMail=mail,cTel=tel,url=url)
                    instanceDict[instance]=created
        except FileNotFoundError:
            print(f"ファイルが見つかりません: {filePath}")
        except Exception as e:
            print(f"エラーが発生しました: {e}")
    executeFunction(function)
    outputQueryResults(instanceDict)


def dm(filePath):
    instanceDict={}
    def function():
        try:
            data=readFile(filePath)
            with transaction.atomic():
                for row in data:
                    title,detail,read,userId,corpId=row['title'],row['detail'],row['read'],row['userID'],row['corporationID']
                    user=User.objects.get(id=userId)
                    corp=Corporation.objects.get(id=corpId)
                    instance,created=Corporation.objects.get_or_create(name=title,detail=detail,read=read,user=user,corp=corp)
                    instanceDict[instance]=created
        except FileNotFoundError:
            print(f"ファイルが見つかりません: {filePath}")
        except User.DoesNotExist:
            print(f"userID: {userId} は存在しません")
        except Corporation.DoesNotExist:
            print(f'法人番号: {corpId} は存在しません')
        except Exception as e:
            print(f"エラーが発生しました: {e}")
    executeFunction(function)
    outputQueryResults(instanceDict)

def supportDM(filePath):
    instanceDict={}
    def function():
        try:
            data=readFile(filePath)
            with transaction.atomic():
                for row in data:
                    title,detail,read,userSendId,userReceiveId=row['title'],row['detail'],row['read'],row['sendUserID'],row['receiveUserID']
                    userSend,userReceive=User.objects.get(id=userSendId),User.objects.get(id=userReceiveId)
                    instance,created=Corporation.objects.get_or_create(name=title,detail=detail,read=read,userSend=userSend,userReceive=userReceive)
                    instanceDict[instance]=created
        except FileNotFoundError:
            print(f"ファイルが見つかりません: {filePath}")
        except User.DoesNotExist:
                print(f"userID: {userSend} または、userID: {userReceive} は存在しません")
        except Exception as e:
            print(f"エラーが発生しました: {e}")
    executeFunction(function)
    outputQueryResults(instanceDict)

def offer(filePath):
    instanceDict={}
    def function():
        try:
            data=readFile(filePath)
            with transaction.atomic():
                for row in data:
                    title,detail,solicitation,course,forms,roles,CoB,subject,NoP,departments,characteristic,pes,giving,allowances,salaryRaise,bonus,holiday,welfare,workingHours,area1name,category00name,category01name,category10name,category11name,corporationId,period,status=row
                    ['title'],row['detail'],row['solicitation'],row['course'],row['forms'],row['roles'],row['CoB'],row['subject'],row['NoP'],row['departments'],row['characteristic'],row
                    ['PES'],row['giving'],row['allowances'],row['salaryRaise'],row['bonus'],row['holiday'],row['welfare'],row['workingHours'],row['area0name'],row['area1name'],row
                    ['category00name'],row['category01name'],row['category10name'],row['category11name'],row['corporationID'],row['applicants'],row['period'],row['status']
                    area1=Area1.objects.get(name=area1name)
                    category00=Category00.objects.get(name=category00name)
                    category01=Category01.objects.get(name=category01name)
                    category10=Category10.objects.get(name=category10name)
                    category11=Category11.objects.get(name=category11name)
                    corporation=Corporation.objects.get(name=corporationId)
                    period=datetime.strptime(period,"%Y-%m-%d %H:%M")
                    instance,created=Corporation.objects.get_or_create(name=title,detail=detail,solicitation=solicitation,course=course,forms=forms,roles=roles,CoB=CoB,subject=subject,
                    NoP=NoP,departments=departments,characteristic=characteristic,PES=pes,giving=giving,allowances=allowances,salaryRaise=salaryRaise,bonus=bonus,holiday=holiday,
                    welfare=welfare,workingHours=workingHours,area1=area1,category00=category00,category01=category01,category10=category10,category11=category11,corporation=corporation,
                    applicants=None,period=period,status=status)
                    instanceDict[instance]=created
        except Area1.DoesNotExist:
            print(f"area1: {area1name} は存在しません")
        except Category00.DoesNotExist:
            print(f"category00: {category00name} は存在しません")
        except Category01.DoesNotExist:
            print(f"category01: {category01name} は存在しません")
        except Category10.DoesNotExist:
            print(f"category10: {category10name} は存在しません")
        except Category11.DoesNotExist:
            print(f"category11: {category11name} は存在しません")
        except FileNotFoundError:
            print(f"ファイルが見つかりません: {filePath}")
        except Exception as e:
            print(f"エラーが発生しました: {e}")
    executeFunction(function)
    outputQueryResults(instanceDict)

def offerEntry(filePath):
    instanceDict={}
    def function():
        try:
            data=readFile(filePath)
            with transaction.atomic():
                for offerData in data:
                    offerId=offerData['offerId']
                    offer=Offer.objects.get(id=offerId)
                    for userData in offerData['users']:
                        userId=userData['userId']
                        user=User.objects.get(id=userId)
                        _,created=OfferEntry.objects.get_or_create(offer=offer,user=user)
                        instanceDict[(offer.id,user.id)]=created
        except FileNotFoundError:
            print(f"ファイルが見つかりません: {filePath}")
        except Offer.DoesNotExist:
            print(f"offerID: {offerId} は存在しません")
        except User.DoesNotExist:
            print(f"userID: {userId} は存在しません")
        except Exception as e:
            print(f"エラーが発生しました: {e}")
    executeFunction(function)
    outputQueryResults(instanceDict)

# 実行
functionMap={
    'area0.csv':area0,
    'area1.csv':area1,
    'area2.csv':area2,
    'category00.csv':category00,
    'category01.csv':category01,
    'category10.csv':category10,
    'category11.csv':category11,
    'tag.csv':tag,
    'user.csv':user,
    # 'profile.csv':profile,
    'question00.csv':question00,
    'question01.csv':question01,
    # 'assessment.csv':assessment,
    'corporation.csv':corporation,
    # 'DM.csv':dm,
    # 'offer.csv':offer,
    # 'offerEntry.json':offerEntry,
    # 'supportDM.csv':supportDM,
}
logger=import_data_SettingLogs()

for file_key,function in functionMap.items():
    basePath='../setup/data/'
    file_path=makeImportPath(basePath,file_key)
    logger.info(f"Loading data for {file_key} from {file_path}...")
    function(file_path)

logging.info('Executed all.')