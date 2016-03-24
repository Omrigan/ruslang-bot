import random, telegram
import datetime
import study_settings

params = {}






def doTrain(user, string):
    if user['train']['type']==0:
        user['train']['type']=1
        doMainTrain(user, string,overwrite=True)
    else:
        doMainTrain(user, string,overwrite=False)



def doMainTrain(user, string, overwrite=False):
    out_str = ""
    was_incorrect = False
    if(not overwrite):
        if string=='end':
            endTrain(user, string)
            return
        else:
            for w in user['words']:

                if w['word']==user['train']['word']:
                    if user['train']['word']!=string.lower():
                        out_str+='Word is uncastable to origina\n'
                        was_incorrect=True
                    else:
                        if user['train']['correct']==string:
                            out_str+="Correct\n"
                            if w['stage']<study_settings.max_stage:
                                w['stage']+=1
                            w['expiration_date'] = datetime.datetime.utcnow() + study_settings.stages[w['stage']]
                        else:
                            out_str+="Incorrect\nThe correct one is %s \n" %(w['correct'],)
                            if w['stage']>study_settings.min_stage:
                                w['stage']-=1
                            was_incorrect=True
    trainlist = list(filter(lambda w: w['expiration_date'] < datetime.datetime.utcnow(), user['words']))
    if len(trainlist)>1:
        if not was_incorrect:
            random.shuffle(trainlist)
            user['train']['word'] = trainlist[0]['word']
            user['train']['correct'] = trainlist[0]['correct']
        out_str += user['train']['word'] + "\n"

    else:
        out_str += "Not enough words\n"
        user['train']['type'] = 0

    telegram.sendMessage(user['chat_id'], out_str)




def endTrain(user, string):
    user['train']['type'] = 0
    telegram.sendMessage(user['chat_id'], "Train ended", reply_markup=telegram.hideKeyboard)
