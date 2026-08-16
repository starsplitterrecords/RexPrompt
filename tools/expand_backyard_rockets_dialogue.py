#!/usr/bin/env python3
"""Expand Backyard Rockets dialogue scene-by-scene while preserving continuity.

This is an editorial adaptation layer, not a generic chatter generator. Every authored scene is
classified by dramatic function, then receives only dialogue that fits the people physically
present, the ongoing task, and adjacent-scene continuity. Existing source quotes are retained.
"""
import base64,gzip,json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SHOW_ID='backyard-rockets-s1'
CANON={'Arvin':'@brk.Arvin','Milo':'@brk.Milo','Lucia':'@brk.Lucia','Cyrus':'@brk.Cyrus','Tamz':'@brk.Tamz'}
VOICE_REWRITES=json.loads((ROOT/'data/shows/backyard-rockets-s1/dialogue-voice-rewrites.json').read_text(encoding='utf-8'))

# Carefully authored additions. Keys are scene IDs; values are ordered lines to append after any
# source-authored dialogue already present. Empty list means the scene was intentionally reviewed
# and left visual/quiet.
ADDITIONS={}

def L(speaker,text,subtext=None):
    x={'handle':CANON[speaker],'speaker':speaker,'text':text}
    if subtext:x['subtext']=subtext
    return x

# Episode 1 — establish the working-family rhythm and each person's relationship to risk.
ADDITIONS.update({
'BR_S1E01_A01_SC01':[
 L('Milo','What would make you trust it? Not the weld. The whole assembly.'),
 L('Arvin','A failure mode I can name before it happens.'),
 L('Milo','That is a very specific definition of trust.'),
 L('Arvin','Most useful definitions are.')],
'BR_S1E01_A01_SC02':[
 L('Milo','Do you ever look at a part and see what it used to be?'),
 L('Arvin','Only long enough to understand what it survived.'),
 L('Milo','I like knowing where things came from.'),
 L('Arvin','You like biographies. I like tolerances.'),
 L('Milo','Same hobby. Different ending.')],
'BR_S1E01_A01_SC03':[
 L('Lucia','What is the part you are not saying out loud?'),
 L('Arvin','That the margin is smaller than I want.'),
 L('Lucia','Smaller than you want or smaller than you can defend?'),
 L('Arvin','Those are not always different questions.')],
'BR_S1E01_A01_SC04':[
 L('Milo','If this works, where do you think the payload is when we go to sleep?'),
 L('Arvin','Ahead of us.'),
 L('Milo','That was almost poetic.'),
 L('Arvin','It was orbital mechanics.')],
'BR_S1E01_A01_SC05':[
 L('Milo','What did you think you were going to be doing at my age?'),
 L('Arvin','Something with a budget.'),
 L('Milo','Better?'),
 L('Arvin','Cleaner. Not better.')],
'BR_S1E01_A01_SC06':[
 L('Lucia','How much of your confidence is math and how much is habit?'),
 L('Arvin','Habit is math you have survived often enough to stop writing down.'),
 L('Lucia','That answer is exactly why I keep writing it down.')],
'BR_S1E01_A02_SC01':[
 L('Milo','What do you miss when we stay put too long?'),
 L('Arvin','The horizon changing.'),
 L('Milo','Not people?'),
 L('Arvin','People change whether you move or not.')],
'BR_S1E01_A02_SC02':[
 L('Lucia','What would you do if nobody were chasing us?'),
 L('Milo','Build slower.'),
 L('Arvin','Build larger.'),
 L('Lucia','Those are both terrible answers.'),
 L('Milo','You asked an open-ended question.')],
'BR_S1E01_A02_SC03':[
 L('Cyrus','What do you think they believe they are protecting?'),
 L('Cyrus','Not the hardware. People rarely risk this much for hardware.')],
'BR_S1E01_A02_SC04':[
 L('Milo','When did you first decide a launch was worth getting caught for?'),
 L('Arvin','I did not.'),
 L('Milo','That sounds reassuring.'),
 L('Arvin','I decided some things are worth doing even when being caught is one of the costs.')],
'BR_S1E01_A02_SC05':[
 L('Lucia','You know what I like about bad plans?'),
 L('Milo','They include us?'),
 L('Lucia','They make everyone finally say what they actually care about.')],
'BR_S1E01_A02_SC06':[
 L('Arvin','What are you smiling at?'),
 L('Milo','The fact that you always say we are out of time right before you find more of it.'),
 L('Arvin','That is not optimism. That is poor scheduling.')],
'BR_S1E01_A03_SC01':[
 L('Lucia','If we have to leave one thing behind, what is it?'),
 L('Milo','The spare regulator.'),
 L('Arvin','No.'),
 L('Milo','You answered before I finished.'),
 L('Arvin','Because you were wrong before you started.')],
'BR_S1E01_A03_SC02':[
 L('Milo','Do you think Cyrus ever gets tired?'),
 L('Lucia','Of us? Constantly.'),
 L('Milo','No. Just tired.'),
 L('Lucia','That is a more interesting question.')],
'BR_S1E01_A03_SC03':[
 L('Cyrus','What would I have done at their age?'),
 L('Cyrus','Probably called it duty and made the same mistake with better paperwork.')],
'BR_S1E01_A03_SC04':[],
'BR_S1E01_A03_SC05':[
 L('Milo','What part of launch do you actually like?'),
 L('Arvin','The second after commitment.'),
 L('Milo','Why?'),
 L('Arvin','Because for one second nobody can improve the plan anymore. We simply find out what we built.')],
'BR_S1E01_A03_SC06':[
 L('Lucia','So what did we learn?'),
 L('Milo','That it works.'),
 L('Arvin','That it worked once.'),
 L('Lucia','There he is.')],
})

# Episode 2 — deepen history, belonging, and why this crew chooses one another.
ADDITIONS.update({
'BR_S1E02_A01_SC01':[L('Milo','What was the first machine you ever fixed because nobody else could?'),L('Arvin','A water pump.'),L('Milo','That is disappointingly ordinary.'),L('Arvin','Most important machines are.')],
'BR_S1E02_A01_SC02':[L('Arvin','What did you notice first?'),L('Lucia','That the pattern is too clean.'),L('Arvin','Meaning?'),L('Lucia','Someone wants us to think this is simpler than it is.')],
'BR_S1E02_A01_SC03':[L('Milo','If you had to teach one thing to somebody who had never built anything, what would it be?'),L('Arvin','How to stop before damage becomes pride.'),L('Milo','I was expecting soldering.'),L('Arvin','That is easier.')],
'BR_S1E02_A01_SC04':[L('Lucia','Why do you still ask him when you already know what he will say?'),L('Milo','Because sometimes he says it differently.'),L('Lucia','And that matters?'),L('Milo','That is usually the part that matters.')],
'BR_S1E02_A01_SC05':[],
'BR_S1E02_A01_SC06':[L('Cyrus','What do they become if they stop moving?'),L('Cyrus','Visible, first. Then predictable.')],
'BR_S1E02_A02_SC01':[L('Milo','You ever think the desert likes us?'),L('Lucia','No.'),L('Milo','You answered that very fast.'),L('Lucia','The desert is not a person. It does not have to like you to keep your secrets.')],
'BR_S1E02_A02_SC02':[L('Arvin','What are you not telling me?'),L('Lucia','That I think this route is being offered to us.'),L('Arvin','By whom?'),L('Lucia','That is the part I would prefer to learn before accepting the invitation.')],
'BR_S1E02_A02_SC03':[L('Milo','What makes a place home if you keep leaving it?'),L('Arvin','Knowing what you intend to return to.'),L('Milo','And if the place moves?'),L('Arvin','Then perhaps the people are the fixed point.')],
'BR_S1E02_A02_SC04':[L('Lucia','That sounded sentimental.'),L('Arvin','It was coordinate geometry.'),L('Milo','You two make everything worse when you agree.')],
'BR_S1E02_A02_SC05':[L('Arvin','What is your read?'),L('Milo','Useful enough to be dangerous.'),L('Arvin','On the part.'),L('Milo','That was my read on the part.')],
'BR_S1E02_A02_SC06':[L('Lucia','If this fails, what do you save first?'),L('Arvin','Milo.'),L('Milo','I am standing right here.'),L('Arvin','Yes. It simplifies the answer.')],
'BR_S1E02_A03_SC01':[L('Milo','Did you always know how to talk to people who were angry with you?'),L('Lucia','No. I learned to stop trying to make them less angry.'),L('Milo','What do you do instead?'),L('Lucia','Find out what the anger is protecting.')],
'BR_S1E02_A03_SC02':[L('Arvin','And what is yours protecting?'),L('Lucia','Today? Time.'),L('Arvin','That is not an emotion.'),L('Lucia','You have clearly never managed a schedule.')],
'BR_S1E02_A03_SC03':[],
'BR_S1E02_A03_SC04':[L('Milo','What is the strangest thing you trust completely?'),L('Arvin','Your hearing.'),L('Milo','Really?'),L('Arvin','You hear machinery change before the instruments agree.'),L('Milo','You could say nice things more often.'),L('Arvin','It was an observation.')],
'BR_S1E02_A03_SC05':[L('Lucia','He will remember that for ten years.'),L('Arvin','That seems inefficient.'),L('Lucia','People are inefficient. We have discussed this.')],
'BR_S1E02_A03_SC06':[L('Milo','What are you afraid the numbers will tell you?'),L('Arvin','That I was correct for the wrong reason.'),L('Milo','That bothers you more than being wrong?'),L('Arvin','Much more.')],
'BR_S1E02_A04_SC01':[L('Lucia','What would make you turn around?'),L('Arvin','Evidence.'),L('Lucia','Not fear?'),L('Arvin','Fear is evidence. It is simply badly labeled.')],
'BR_S1E02_A04_SC02':[L('Arvin','What do you think he wants from us?'),L('Lucia','For us to become legible.'),L('Arvin','To Tethergrid?'),L('Lucia','To himself.')],
'BR_S1E02_A04_SC03':[L('Cyrus','What would make them stop voluntarily?'),L('Cyrus','Something they believe is more important than winning.')],
'BR_S1E02_A04_SC04':[L('Milo','What if he is not wrong about us?'),L('Lucia','He is not wrong about everything.'),L('Milo','That is worse.'),L('Lucia','Usually.')],
'BR_S1E02_A04_SC05':[L('Arvin','Do you want me to say we are the good people?'),L('Milo','No.'),L('Arvin','Good.'),L('Milo','I want to know what you think we owe people when our choices spill into their lives.'),L('Arvin','More than an apology. Less than obedience. I am still solving the interval.')],
'BR_S1E02_A05_SC01':[],
'BR_S1E02_A05_SC02':[L('Milo','If we ever get boring, will you tell me?'),L('Lucia','Immediately.'),L('Milo','What counts as boring?'),L('Lucia','When we start believing our own mythology.')],
'BR_S1E02_A05_SC03':[L('Arvin','What do you call this, then?'),L('Lucia','Tuesday.'),L('Milo','That is why she is in charge of morale.')],
'BR_S1E02_A05_SC04':[L('Milo','You know what I want someday?'),L('Arvin','A torque wrench you do not lose?'),L('Milo','A workshop that does not have wheels.'),L('Arvin','You would hate it in a week.'),L('Milo','Probably. I still want to know.')],
'BR_S1E02_A05_SC05':[L('Lucia','What would you put in it?'),L('Milo','Windows.'),L('Arvin','Wasteful.'),L('Milo','See? This is why I need my own hypothetical workshop.')],
})

# Episode 3 — consequences, competence, and the crew's private ideas of success.
ADDITIONS.update({
'BR_S1E03_A01_SC01':[L('Arvin','What changed?'),L('Milo','Nothing I can prove.'),L('Arvin','That is not the same as nothing.'),L('Milo','I know. That is why I came to get you.')],
'BR_S1E03_A01_SC02':[L('Lucia','What would you do if your instinct and the instruments disagree?'),L('Milo','Check the instruments.'),L('Lucia','And after that?'),L('Milo','Check myself. I hate that part.')],
'BR_S1E03_A01_SC03':[L('Arvin','What is success here?'),L('Lucia','Nobody notices us.'),L('Milo','That is a depressing definition.'),L('Lucia','It is a temporary one.')],
'BR_S1E03_A01_SC04':[L('Milo','What is your permanent definition?'),L('Arvin','A system that keeps working after the person who understood it leaves.'),L('Milo','That was definitely not about the rocket.'),L('Arvin','It was not only about the rocket.')],
'BR_S1E03_A01_SC05':[],
'BR_S1E03_A02_SC01':[L('Cyrus','What do I call restraint when nobody reports it?'),L('Cyrus','Still restraint.')],
'BR_S1E03_A02_SC02':[L('Lucia','Do you think he is giving us room?'),L('Arvin','Possibly.'),L('Lucia','Why?'),L('Arvin','Because competent opponents also get curious.')],
'BR_S1E03_A02_SC03':[L('Milo','What are you curious about?'),L('Arvin','Whether he knows he is changing.'),L('Lucia','Do you?'),L('Arvin','I was hoping we could keep this about Cyrus.')],
'BR_S1E03_A02_SC04':[L('Lucia','You never answer that question.'),L('Arvin','I answer it continuously. You simply dislike the format.')],
'BR_S1E03_A02_SC05':[L('Milo','If you could ask Cyrus one question and he had to answer honestly, what would it be?'),L('Lucia','Who taught you that control and care are the same thing?'),L('Arvin','What would you ask?'),L('Milo','What do you do for fun?'),L('Lucia','Yours is more dangerous.')],
'BR_S1E03_A02_SC06':[L('Arvin','And you?'),L('Milo','I just answered.'),L('Arvin','No. If you had to answer honestly.'),L('Milo','Whether he thinks people like us are necessary or merely tolerable.')],
'BR_S1E03_A03_SC01':[L('Lucia','There it is.'),L('Milo','What?'),L('Lucia','The question underneath all your other questions.')],
'BR_S1E03_A03_SC02':[L('Milo','Do you know yours?'),L('Lucia','Yes.'),L('Milo','Are you going to tell me?'),L('Lucia','Not while you are holding that cable.')],
'BR_S1E03_A03_SC03':[],
'BR_S1E03_A03_SC04':[L('Arvin','Now?'),L('Lucia','Mine is whether staying with you is courage or preference.'),L('Milo','Which is it?'),L('Lucia','I am increasingly suspicious it can be both.')],
'BR_S1E03_A03_SC05':[L('Milo','That was almost nice.'),L('Lucia','Do not make me repeat it.'),L('Arvin','The recorder is running.'),L('Lucia','I hate both of you.')],
'BR_S1E03_A03_SC06':[L('Milo','No you do not.'),L('Lucia','Correct.'),L('Arvin','Can we return to the failure analysis?'),L('Milo','See? This is how he says he loves us.')],
})

# Episode 4 — strain and disagreement without breaking affection.
ADDITIONS.update({
'BR_S1E04_A01_SC01':[L('Lucia','What are you trying not to ask?'),L('Milo','Whether we are still doing this because it matters or because we are good at it.'),L('Lucia','Those can become dangerously similar.')],
'BR_S1E04_A01_SC02':[L('Arvin','Why does that distinction matter to you now?'),L('Milo','Because being good at something is a terrible reason to never stop.')],
'BR_S1E04_A01_SC03':[L('Arvin','Agreed.'),L('Milo','You agreed too quickly.'),L('Arvin','Would you prefer resistance?'),L('Milo','A little. I prepared for it.')],
'BR_S1E04_A01_SC04':[L('Cyrus','What happens when pursuit becomes identity?'),L('Cyrus','You stop noticing whether the target still justifies it.')],
'BR_S1E04_A01_SC05':[L('Lucia','What do you think he sees when he looks at us?'),L('Arvin','A problem with faces.'),L('Milo','That is grim.'),L('Arvin','I suspect the faces are beginning to complicate the problem.')],
'BR_S1E04_A02_SC01':[L('Milo','If we make it through this, can we cook something that did not come out of a pouch?'),L('Lucia','Define cook.'),L('Milo','Heat with optimism.'),L('Arvin','No open flame near the oxidizer rack.')],
'BR_S1E04_A02_SC02':[L('Lucia','What did you eat before you started living like this?'),L('Arvin','Mostly the same food in cleaner rooms.'),L('Milo','That explains more than you think.')],
'BR_S1E04_A02_SC03':[L('Arvin','What would normal look like to you?'),L('Milo','Knowing where we will be next Thursday.'),L('Lucia','You would become unbearable by Wednesday.')],
'BR_S1E04_A02_SC04':[L('Milo','What about you?'),L('Lucia','A door I can lock because I am sleeping, not because someone might come through it.'),L('Arvin','That seems achievable.'),L('Lucia','You say that about everything right before making it difficult.')],
'BR_S1E04_A02_SC05':[L('Arvin','And if it were easy?'),L('Lucia','I do not know if I would trust it yet.')],
'BR_S1E04_A02_SC06':[],
'BR_S1E04_A03_SC01':[L('Milo','Do you think we know how to stop?'),L('Arvin','Mechanically?'),L('Milo','You know that is not what I mean.')],
'BR_S1E04_A03_SC02':[L('Arvin','No. I am not certain we do.'),L('Lucia','That is the first useful answer to that question.')],
'BR_S1E04_A03_SC03':[L('Milo','Then maybe we should learn before we need it.'),L('Arvin','Reasonable.'),L('Lucia','Write down the date. He called emotional preparedness reasonable.')],
'BR_S1E04_A03_SC04':[L('Cyrus','What would stopping look like for me?'),L('Cyrus','I am not sure I have ever defined it.')],
'BR_S1E04_A03_SC05':[L('Lucia','Maybe that is what this whole mess is.'),L('Milo','What?'),L('Lucia','A group of people discovering they never wrote the shutdown procedure.')],
})

# Episode 5 — intimacy earned by shared work; the crew begins articulating what they are building beyond rockets.
ADDITIONS.update({
'BR_S1E05_A01_SC01':[L('Milo','What do you want this to become if it keeps working?'),L('Arvin','Infrastructure.'),L('Milo','That is a very unromantic answer.'),L('Arvin','Infrastructure is what romance looks like after it proves useful.')],
'BR_S1E05_A01_SC02':[L('Lucia','He means he wants people to depend on it.'),L('Arvin','Carefully.'),L('Lucia','You cannot build infrastructure nobody depends on.'),L('Arvin','I said carefully.')],
'BR_S1E05_A01_SC03':[L('Milo','Does that scare you?'),L('Arvin','Yes.'),L('Milo','The responsibility?'),L('Arvin','The temptation to confuse being needed with being right.')],
'BR_S1E05_A01_SC04':[L('Lucia','That is why there are three of us.'),L('Milo','Four, if you count the person hunting us.'),L('Lucia','I was not counting him as governance.')],
'BR_S1E05_A01_SC05':[L('Arvin','Why not?'),L('Lucia','Because oversight should ideally be invited.'),L('Milo','That feels like a very narrow definition of Cyrus.')],
'BR_S1E05_A02_SC01':[L('Milo','What do you think we will remember about this year?'),L('Arvin','The things that failed.'),L('Lucia','That is depressing.'),L('Arvin','Failures are specific. Success tends to blur.')],
'BR_S1E05_A02_SC02':[L('Lucia','I will remember the meals.'),L('Milo','The bad ones?'),L('Lucia','Especially the bad ones. Nobody performs during bad food.')],
'BR_S1E05_A02_SC03':[L('Milo','I will remember that night the coolant line froze and Arvin told the same story three times.'),L('Arvin','I was hypothermic.'),L('Lucia','You were almost charming.')],
'BR_S1E05_A02_SC04':[L('Arvin','What story?'),L('Milo','You genuinely do not remember?'),L('Arvin','Apparently not.'),L('Lucia','Good. We can improve it.')],
'BR_S1E05_A02_SC05':[L('Milo','That is the other thing I want.'),L('Arvin','Windows?'),L('Milo','Stories that get better because the same people keep telling them.')],
'BR_S1E05_A03_SC01':[L('Lucia','That may be the first convincing argument you have made for staying anywhere.'),L('Milo','Thank you.'),L('Arvin','It is not an argument for staying. It is an argument for continuity.')],
'BR_S1E05_A03_SC02':[L('Milo','You really cannot leave a sentence human, can you?'),L('Arvin','I thought continuity was human.'),L('Lucia','It is. That is why this is funny.')],
'BR_S1E05_A03_SC03':[],
'BR_S1E05_A03_SC04':[L('Cyrus','What are they becoming?'),L('Cyrus','Not less dangerous. More difficult to dismiss.')],
'BR_S1E05_A03_SC05':[L('Lucia','What happens if he eventually understands us?'),L('Arvin','Then we lose the advantage of being underestimated.'),L('Milo','And gain what?'),L('Lucia','Maybe a choice neither side has had yet.')],
'BR_S1E05_A03_SC06':[L('Milo','Would you take it?'),L('Arvin','Ask me when it exists.'),L('Lucia','He means yes, if he can complain about the terms first.'),L('Arvin','Terms matter.')],
})

# Outline-only episodes are not fabricated into pseudo-scenes. They are reviewed and intentionally left without added dialogue.
ADDITIONS.update({'BR_S1E06_OUTLINE_01':[],'BR_S1E07_OUTLINE_01':[],'BR_S1E08_OUTLINE_01':[]})
DOCUMENTARY_SPECS=json.loads((ROOT/'data/shows/backyard-rockets-s1/documentary-interstitials.json').read_text(encoding='utf-8'))
ADDITIONS.update({spec['id']:[] for spec in DOCUMENTARY_SPECS})

def load(p):return json.loads(p.read_text(encoding='utf-8'))
def norm(x):
    if isinstance(x,list):return x
    return [{'id':k,**v} if isinstance(v,dict) else {'id':k,'value':v} for k,v in (x or {}).items()]
def read(p,e=None):
    if e=='gzip-base64':return json.loads(gzip.decompress(base64.b64decode(''.join(p.read_text().split()),validate=True)).decode())
    return load(p)
def write(p,x,e=None):
    raw=json.dumps(x,ensure_ascii=False,separators=(',',':')).encode()
    if e=='gzip-base64':p.write_text(base64.b64encode(gzip.compress(raw,9,mtime=0)).decode(),encoding='utf-8')
    else:p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def patch(scene):
    sid=scene.get('id','')
    if sid not in ADDITIONS:raise KeyError(f'Unreviewed Backyard Rockets scene: {sid}')
    existing=scene.get('dialogueInline',[]) or []
    scene['dialogueInline']=existing+ADDITIONS[sid]
    scene['factions']=['BR_Tethergrid' if x=='BR_Aegis' else x for x in scene.get('factions',[])]
    for raw_index,rewrite in VOICE_REWRITES.get(sid,{}).items():
        index=int(raw_index)
        if index>=len(scene['dialogueInline']):
            raise IndexError(f'Voice rewrite {sid}[{index}] exceeds {len(scene["dialogueInline"])} dialogue lines')
        line=scene['dialogueInline'][index]
        speaker=rewrite['speaker']
        line.update(handle=CANON[speaker],speaker=speaker,text=rewrite['text'])
    return scene

shows=load(ROOT/'data/shows.json');show=next(s for s in shows if s.get('id')==SHOW_ID);base=ROOT/show['basePath']
files=[(show.get('scenesFile','scenes_base.json'),None)]+[(o['file'],o.get('encoding')) for o in show.get('sceneOverlays',[])]
seen=[];total_lines=0;quiet=0
for rel,enc in files:
    p=base/rel;data=norm(read(p,enc));out=[]
    for s in data:
        sid=s.get('id','');seen.append(sid);before=len(s.get('dialogueInline',[]) or []);s=patch(s);after=len(s.get('dialogueInline',[]) or [])
        total_lines+=after
        if after==0:quiet+=1
        out.append(s)
    write(p,out,enc)
missing=sorted(set(ADDITIONS)-set(seen));extra=sorted(set(seen)-set(ADDITIONS))
if missing or extra:raise SystemExit(f'Coverage mismatch missing={missing} extra={extra}')
print(f'Backyard Rockets dialogue editorial pass complete: {len(seen)} scenes reviewed; {total_lines} total dialogue lines; {quiet} intentionally silent scenes')
